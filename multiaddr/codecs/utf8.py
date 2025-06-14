import urllib.parse
import varint
from . import CodecBase
from ..exceptions import BinaryParseError

class Codec(CodecBase):
    SIZE = 0  # Variable size
    IS_PATH = False

    def __init__(self):
        super().__init__()
        # Set IS_PATH to True for ip6zone protocol
        self._is_path = False

    @property
    def IS_PATH(self) -> bool:
        return self._is_path

    def to_bytes(self, proto, value: str) -> bytes:
        """Convert a UTF-8 string to its binary representation."""
        if not value:
            raise ValueError("String cannot be empty")

        # Set IS_PATH based on protocol
        self._is_path = proto.name == "ip6zone"

        # URL decode the string to handle special characters
        value = urllib.parse.unquote(value)
        
        # For ip6zone, ensure no leading/trailing whitespace
        if proto.name == "ip6zone":
            value = value.strip()
            if not value:
                raise ValueError("Zone identifier cannot be empty after stripping whitespace")
        
        # Encode as UTF-8
        encoded = value.encode("utf-8")
        
        # Add varint length prefix for variable-size values
        return varint.encode(len(encoded)) + encoded

    def to_string(self, proto, buf: bytes) -> str:
        """Convert a binary UTF-8 string to its string representation."""
        if not buf:
            raise ValueError("Buffer cannot be empty")

        # Set IS_PATH based on protocol
        self._is_path = proto.name == "ip6zone"

        # Decode from UTF-8 and URL encode special characters
        try:
            value = buf.decode("utf-8")
            # For ip6zone, ensure no leading/trailing whitespace
            if proto.name == "ip6zone":
                value = value.strip()
                if not value:
                    raise ValueError("Zone identifier cannot be empty after stripping whitespace")
            # Avoid double-encoding percent signs
            return urllib.parse.quote(value, safe='%')
        except UnicodeDecodeError as e:
            raise BinaryParseError(f"Invalid UTF-8 encoding: {str(e)}", buf, proto.name, e)
