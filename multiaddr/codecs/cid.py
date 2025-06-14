from typing import Dict, List

import base58
import cid
import varint

from ..codecs import CodecBase
from . import LENGTH_PREFIXED_VAR_SIZE
from ..exceptions import BinaryParseError

SIZE = LENGTH_PREFIXED_VAR_SIZE
IS_PATH = False


# Spec: https://github.com/libp2p/specs/blob/master/peer-ids/peer-ids.md#string-representation
CIDv0_PREFIX_TO_LENGTH: Dict[str, List[int]] = {
    # base58btc prefixes for valid lengths 1 - 42 with the identity "hash" function
    "12": [5, 12, 19, 23, 30, 41, 52, 56],
    "13": [9, 16, 34, 45],
    "14": [27, 38, 49, 60],
    "15": [3, 6, 20],
    "16": [3, 6, 13, 20, 31, 42, 53],
    "17": [3, 13, 42],
    "18": [3],
    "19": [3, 24, 57],
    "1A": [24, 35, 46],
    "1B": [35],
    "1D": [17],
    "1E": [10, 17],
    "1F": [10],
    "1G": [10, 28, 50],
    "1H": [28, 39],
    "1P": [21],
    "1Q": [21],
    "1R": [21, 54],
    "1S": [54],
    "1T": [7, 32, 43],
    "1U": [7, 32, 43],
    "1V": [7],
    "1W": [7, 14],
    "1X": [7, 14],
    "1Y": [7, 14],
    "1Z": [7, 14],
    "1f": [4],
    "1g": [4, 58],
    "1h": [4, 25, 58],
    "1i": [4, 25],
    "1j": [4, 25],
    "1k": [4, 25, 47],
    "1m": [4, 36, 47],
    "1n": [4, 36],
    "1o": [4, 36],
    "1p": [4],
    "1q": [4],
    "1r": [4],
    "1s": [4],
    "1t": [4],
    "1u": [4],
    "1v": [4],
    "1w": [4],
    "1x": [4],
    "1y": [4],
    "1z": [4, 18],
    # base58btc prefix for length 42 with the sha256 hash function
    "Qm": [46],
}

PROTO_NAME_TO_CIDv1_CODEC = {
    "p2p": "libp2p-key",
    "ipfs": "dag-pb",
}


def _is_binary_cidv0_multihash(buf: bytes) -> bool:
    """Check if the given bytes represent a CIDv0 multihash."""
    try:
        # CIDv0 is just a base58btc encoded multihash
        decoded = base58.b58decode(base58.b58encode(buf).decode("ascii"))
        return len(decoded) == len(buf) and decoded == buf
    except Exception:
        return False


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, value: str) -> bytes:
        """Convert a CID string to its binary representation."""
        if not value:
            raise ValueError("CID string cannot be empty")

        # First try to parse as CIDv0 (base58btc encoded multihash)
        try:
            decoded = base58.b58decode(value)
            if _is_binary_cidv0_multihash(decoded):
                # Add length prefix for CIDv0
                return varint.encode(len(decoded)) + decoded
        except Exception:
            pass

        # If not CIDv0, try to parse as CIDv1
        try:
            parsed = cid.make_cid(value)
            # Add length prefix for CIDv1
            return varint.encode(len(parsed.buffer)) + parsed.buffer
        except ValueError:
            raise ValueError(f"Invalid CID: {value}")

    def to_string(self, proto, buf: bytes) -> str:
        """Convert a binary CID to its string representation."""
        if not buf:
            raise ValueError("CID buffer cannot be empty")

        expected_codec = PROTO_NAME_TO_CIDv1_CODEC.get(proto.name)

        try:
            if _is_binary_cidv0_multihash(buf):  # CIDv0
                if not expected_codec:
                    # Simply encode as base58btc as there is nothing better to do
                    return base58.b58encode(buf).decode("ascii")

                # "Implementations SHOULD display peer IDs using the first (raw
                #  base58btc encoded multihash) format until the second format is
                #  widely supported."
                return base58.b58encode(buf).decode("ascii")
            else:  # CIDv1+
                parsed = cid.from_bytes(buf)

                # Ensure CID has correct codec for protocol
                if expected_codec and parsed.codec != expected_codec:
                    raise ValueError(
                        '"{0}" multiaddr CIDs must use the "{1}" multicodec'.format(
                            proto.name, expected_codec
                        )
                    )

                # "Implementations SHOULD display peer IDs using the first (raw
                #  base58btc encoded multihash) format until the second format is
                #  widely supported."
                if expected_codec and _is_binary_cidv0_multihash(parsed.multihash):
                    return base58.b58encode(parsed.multihash).decode("ascii")

                return parsed.encode("base32").decode("ascii")
        except Exception as e:
            raise BinaryParseError(str(e), buf, proto.name, e) from e
