import os
import urllib.parse
from . import CodecBase, LENGTH_PREFIXED_VAR_SIZE
from ..exceptions import BinaryParseError

SIZE = LENGTH_PREFIXED_VAR_SIZE
IS_PATH = True


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, value: str) -> bytes:
        """Convert a filesystem path to its binary representation."""
        if not value:
            raise ValueError("Path cannot be empty")

        # Normalize path separators
        value = value.replace("\\", "/")
        
        # Remove leading/trailing slashes
        value = value.strip("/")
        
        # Handle empty path after normalization
        if not value:
            raise ValueError("Path cannot be empty after normalization")
            
        # URL decode to handle special characters
        value = urllib.parse.unquote(value)
        
        # Encode as UTF-8
        return value.encode("utf-8")

    def to_string(self, proto, buf: bytes) -> str:
        """Convert a binary filesystem path to its string representation."""
        if not buf:
            raise ValueError("Path buffer cannot be empty")

        try:
            # Decode from UTF-8
            value = buf.decode("utf-8")
            
            # Normalize path separators
            value = value.replace("\\", "/")
            
            # Remove leading/trailing slashes
            value = value.strip("/")
            
            # Handle empty path after normalization
            if not value:
                raise ValueError("Path cannot be empty after normalization")
                
            # URL encode special characters
            return urllib.parse.quote(value)
        except UnicodeDecodeError as e:
            raise BinaryParseError(f"Invalid UTF-8 encoding: {str(e)}", buf, proto.name, e)
