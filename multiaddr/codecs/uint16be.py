from ..codecs import CodecBase

SIZE = 16
IS_PATH = False


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, string):
        try:
            n = int(string, 10)
        except ValueError:
            raise ValueError("invalid base 10 integer")
        if n < 0 or n >= 65536:
            raise ValueError("integer not in range [0, 65536)")
        return n.to_bytes(2, byteorder="big")

    def to_string(self, proto, buf):
        if len(buf) != 2:
            raise ValueError("buffer length must be 2 bytes")
        return str(int.from_bytes(buf, byteorder="big"))
