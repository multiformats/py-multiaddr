from ..codecs import CodecBase

SIZE = -1
IS_PATH = True


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, string):
        if len(string) == 0:
            raise ValueError("{0} value must not be empty".format(proto.name))
        # Remove leading slash unless the path is just '/'
        if string != '/' and string.startswith('/'):
            string = string[1:]
        return string.encode('utf-8')

    def to_string(self, proto, buf):
        if len(buf) == 0:
            raise ValueError("invalid length (should be > 0)")
        string = buf.decode('utf-8')
        # Always add a single leading slash
        if not string.startswith('/'):
            string = '/' + string
        return string
