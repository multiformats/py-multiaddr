from ..codecs import CodecBase

SIZE = -1
IS_PATH = True


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, string):
        if not string:
            raise ValueError("empty string")
        return string.encode('utf-8')

    def to_string(self, proto, buf):
        if not buf:
            raise ValueError("empty buffer")
        return buf.decode('utf-8')
