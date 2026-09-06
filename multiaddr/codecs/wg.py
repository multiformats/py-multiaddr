"""
WireGuard protocol codec.

Encode/decode a 32-byte Curve25519 public key as multibase base64url
(the ``u`` prefix form used by ``/certhash`` in go-multiaddr and
py-multiaddr). Standard base64 from ``wg(8)`` tooling may contain ``/``
and cannot be used directly in ``/``-delimited multiaddr strings.

The protocol code ``0x01C7`` is a draft allocation not yet present in
the upstream multicodec table:

- https://github.com/multiformats/multicodec/blob/master/table.csv
- https://github.com/multiformats/multiaddr/blob/master/protocols.csv

To convert a ``wg(8)`` public key for use in a multiaddr string::

    import base64
    import multibase

    raw = base64.b64decode(wg_tooling_key)
    safe = multibase.encode("base64url", raw).decode("ascii")
    # /ip4/1.2.3.4/udp/51820/wg/{safe}

See also the upstream multicodec addition process:
https://github.com/multiformats/multicodec?tab=readme-ov-file#adding-new-multicodecs-to-the-table
"""

from typing import Any

import multibase

from ..codecs import CodecBase

SIZE = 256  # 32 bytes * 8 bits
IS_PATH = False

WG_KEY_LENGTH = 32  # Curve25519 public key

_WG8_HINT = (
    "WireGuard keys from wg(8) use standard base64; convert with "
    "base64.b64decode(...) then multibase.encode('base64url', ...).decode('ascii') "
    "before embedding in a multiaddr"
)


def _looks_like_pasted_wg8_key(string: str) -> bool:
    """Return True when the string likely came from wg(8) tooling, not multibase."""
    if not string.startswith("u"):
        return False
    # Padded standard base64 often starts with 'u' after being pasted with prefix confusion,
    # or a multibase-looking string that still contains '+' or trailing '='.
    if "+" in string or string.endswith("=") or string.endswith("=="):
        return True
    return False


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def validate(self, b: bytes) -> None:
        if len(b) != WG_KEY_LENGTH:
            raise ValueError(f"WireGuard public key must be {WG_KEY_LENGTH} bytes, got {len(b)}")

    def to_bytes(self, proto: Any, string: str) -> bytes:
        if not string.startswith("u"):
            raise ValueError("wg public key must use base64url multibase prefix 'u'; " + _WG8_HINT)

        try:
            decoded = multibase.decode(string)
        except Exception as exc:
            if _looks_like_pasted_wg8_key(string) or "+" in string:
                raise ValueError(
                    f"invalid multibase WireGuard public key: {exc}; {_WG8_HINT}"
                ) from exc
            raise ValueError(f"invalid multibase WireGuard public key: {exc}") from exc

        decoded_bytes = decoded[1] if isinstance(decoded, tuple) else decoded
        if not isinstance(decoded_bytes, (bytes, bytearray)):
            raise ValueError("failed to decode multibase string to bytes")
        raw = bytes(decoded_bytes)
        self.validate(raw)
        return raw

    def to_string(self, proto: Any, buf: bytes) -> str:
        self.validate(buf)
        encoded_string = multibase.encode("base64url", buf)
        return encoded_string.decode("ascii")
