import netaddr

from ..codecs import CodecBase

SIZE = 32
IS_PATH = False


class Codec(CodecBase):
    SIZE = SIZE
    IS_PATH = IS_PATH

    def to_bytes(self, proto, string):
        return netaddr.IPAddress(string, version=4).packed

    def to_string(self, proto, buf):
        return str(netaddr.IPAddress(int.from_bytes(buf, byteorder='big'), version=4))
