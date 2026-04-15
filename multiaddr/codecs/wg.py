"""
WireGuard protocol codec.

Encode/decode a 32-byte Curve25519 public key as standard
base64 (the canonical format used by `wg(8)` tooling).

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
        try:
            raw = base64.b64decode(string, validate=True)
        except Exception as exc:
            raise ValueError(
                f"invalid base64 WireGuard public key: {exc}"
            ) from exc

        if len(raw) != WG_KEY_LENGTH:
            raise ValueError(
                f"WireGuard public key must be {WG_KEY_LENGTH} bytes, "
                f"got {len(raw)}"
            )
        return raw

    def to_string(self, proto: Any, buf: bytes) -> str:
        if len(buf) != WG_KEY_LENGTH:
            raise BinaryParseError(
                f"WireGuard public key must be {WG_KEY_LENGTH} bytes, "
                f"got {len(buf)}",
                buf,
                "wg",
            )
        return base64.b64encode(buf).decode("ascii")

    def validate(self, b: bytes) -> None:
        if len(b) != WG_KEY_LENGTH:
            raise ValueError(
                f"WireGuard public key must be {WG_KEY_LENGTH} bytes, "
                f"got {len(b)}"
            )
