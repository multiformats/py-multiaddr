"""
WireGuard protocol codec.

Encode/decode a 32-byte Curve25519 public key as URL-safe
base64 (RFC 4648 section 5, with padding).

`wg(8)` tooling renders keys as *standard* base64 whose
alphabet includes '/', a char which collides with the
multiaddr protocol delimiter and thus can't appear in a
multiaddr string segment. The URL-safe alphabet differs
only by two chars ('+' -> '-', '/' -> '_') so converting a
`wg(8)` key is a simple transliteration:

    tr '+/' '-_' <<< "$WG_PUBKEY"

The same alternate-alphabet approach is used by the
`garlic64` codec for i2p addrs.

The protocol code `0x01C7` is a draft allocation not yet
present in the upstream multicodec table:
- https://github.com/multiformats/multicodec/blob/master/table.csv
- https://github.com/multiformats/multiaddr/blob/master/protocols.csv
- https://multiformats.io/multiaddr/

See also the upstream multicodec addition process:
- https://github.com/multiformats/multicodec?tab=readme-ov-file#adding-new-multicodecs-to-the-table
"""

import base64
from typing import Any

from ..codecs import CodecBase
from ..exceptions import BinaryParseError

SIZE = 256  # 32 bytes * 8 bits
IS_PATH = False

WG_KEY_LENGTH = 32  # Curve25519 public key


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto: Any, string: str) -> bytes:
        # explicitly reject the standard-base64 alphabet:
        # '/' collides with the multiaddr delimiter, so keys
        # copied from `wg(8)` output must be transliterated
        # to the URL-safe alphabet first.
        if "+" in string or "/" in string:
            raise ValueError(
                "WireGuard public key must be URL-safe base64 "
                "(RFC 4648 section 5): replace '+' with '-' "
                "and '/' with '_'"
            )

        try:
            raw = base64.b64decode(string, altchars=b"-_", validate=True)
        except Exception as exc:
            raise ValueError(f"invalid base64 WireGuard public key: {exc}") from exc

        if len(raw) != WG_KEY_LENGTH:
            raise ValueError(f"WireGuard public key must be {WG_KEY_LENGTH} bytes, got {len(raw)}")
        return raw

    def to_string(self, proto: Any, buf: bytes) -> str:
        if len(buf) != WG_KEY_LENGTH:
            raise BinaryParseError(
                f"WireGuard public key must be {WG_KEY_LENGTH} bytes, got {len(buf)}",
                buf,
                "wg",
            )
        return base64.urlsafe_b64encode(buf).decode("ascii")

    def validate(self, b: bytes) -> None:
        if len(b) != WG_KEY_LENGTH:
            raise ValueError(f"WireGuard public key must be {WG_KEY_LENGTH} bytes, got {len(b)}")
