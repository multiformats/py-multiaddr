from typing import Any
from urllib.parse import quote, unquote

from ..codecs import CodecBase
from ..exceptions import BinaryParseError

IS_PATH = True
SIZE = -1  # LengthPrefixedVarSize


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto: Any, string: str) -> bytes:
        """
        Convert an HTTP path string to bytes
        Unescape URL-encoded characters, validated non-empty, then encode
        as UTF-8
        """

        try:
            unescaped = unquote(string)
        except Exception:
            raise ValueError(f"Invalid HTTP path string: {string}")

        if len(unescaped) == 0:
            raise ValueError("empty http path is not allowed")

        return unescaped.encode("utf-8")

    def to_string(self, proto: Any, buf: bytes) -> str:
        """
        Convert bytes to an HTTP path string
        Encode as UTTF-8 and URL-escape
        """
        if len(buf) == 0:
            raise BinaryParseError("Empty http path is not allowed", buf, "http-path")

        return quote(buf.decode("utf-8"))

    def validate(self, b: bytes) -> None:
        """
        Validate an HTTP path buffer.
        Just check non-empty.
        """
        if len(b) == 0:
            raise ValueError("Empty http path is not allowed")
