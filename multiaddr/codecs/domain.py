import idna

from ..codecs import CodecBase
from ..exceptions import BinaryParseError

SIZE = -1
IS_PATH = False


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, string):
        return string.encode('utf-8')

    def to_string(self, proto, buf):
        try:
            string = buf.decode("utf-8")
            for label in string.split("."):
                idna.check_label(label)
            return string
        except (ValueError, UnicodeDecodeError) as e:
            raise BinaryParseError(str(e), buf, proto)


def to_bytes(proto, string):
    return idna.uts46_remap(string).encode("utf-8")


def to_string(proto, buf):
    string = buf.decode("utf-8")
    for label in string.split("."):
        idna.check_label(label)
    return string
