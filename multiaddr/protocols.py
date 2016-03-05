# -*- coding: utf-8 -*-
import six
import varint

# replicating table here to:
# 1. avoid parsing the csv
# 2. ensuring errors in the csv don't screw up code.
# 3. changing a number has to happen in two places.
P_IP4 = 4
P_TCP = 6
P_UDP = 17
P_DCCP = 33
P_IP6 = 41
P_SCTP = 132
P_UTP = 301
P_UDT = 302
P_IPFS = 421
P_HTTP = 480
P_HTTPS = 443
P_ONION = 444

_CODES = [
    P_IP4,
    P_TCP,
    P_UDP,
    P_DCCP,
    P_IP6,
    P_SCTP,
    P_UTP,
    P_UDT,
    P_IPFS,
    P_HTTP,
    P_HTTPS,
    P_ONION,
]


# These are special sizes
LENGTH_PREFIXED_VAR_SIZE = -1


class Protocol(object):
    __slots__ = [
        "code",   # int
        "size",   # int (-1 indicates a length-prefixed variable size)
        "name",   # string
        "vcode",  # bytes
    ]

    def __init__(self, code, size, name, vcode):
        if not isinstance(code, six.integer_types):
            raise ValueError("code must be an integer")
        if not isinstance(size, six.integer_types):
            raise ValueError("size must be an integer")
        if not isinstance(name, six.string_types):
            raise ValueError("name must be a string")
        if not isinstance(vcode, six.binary_type):
            raise ValueError("vcode must be binary")

        if code not in _CODES and code != 0:
            raise ValueError("Invalid code '%d'" % code)

        if size < -1 or size > 128:
            raise ValueError("Invalid size")
        self.code = code
        self.size = size
        self.name = name
        self.vcode = vcode

    def __eq__(self, other):
        return all(self.code == other.code,
                   self.size == other.size,
                   self.name == other.name,
                   self.vcode == other.vcode)


def code_to_varint(num):
    """Convert an integer to a varint-encoded []byte."""
    return varint.encode(num)


def varint_to_code(buf):
    return varint.decode_bytes(buf)


# Protocols is the list of multiaddr protocols supported by this module.
PROTOCOLS = [
    Protocol(P_IP4, 32, "ip4", code_to_varint(P_IP4)),
    Protocol(P_TCP, 16, "tcp", code_to_varint(P_TCP)),
    Protocol(P_UDP, 16, "udp", code_to_varint(P_UDP)),
    Protocol(P_DCCP, 16, "dccp", code_to_varint(P_DCCP)),
    Protocol(P_IP6, 128, "ip6", code_to_varint(P_IP6)),
    # these require varint:
    Protocol(P_SCTP, 16, "sctp", code_to_varint(P_SCTP)),
    Protocol(P_ONION, 80, "onion", code_to_varint(P_ONION)),
    Protocol(P_UTP, 0, "utp", code_to_varint(P_UTP)),
    Protocol(P_UDT, 0, "udt", code_to_varint(P_UDT)),
    Protocol(P_HTTP, 0, "http", code_to_varint(P_HTTP)),
    Protocol(P_HTTPS, 0, "https", code_to_varint(P_HTTPS)),
    Protocol(P_IPFS, LENGTH_PREFIXED_VAR_SIZE, "ipfs", code_to_varint(P_IPFS)),
]

NULL_PROTOCOL = Protocol(0, 0, "", b'')

_names_to_protocols = dict((proto.name, proto) for proto in PROTOCOLS)
_codes_to_protocols = dict((proto.code, proto) for proto in PROTOCOLS)


def add_protocol(proto):
    if proto.name in _names_to_protocols:
        raise ValueError("protocol by the name %s already exists" % proto.name)

    if proto.code in _codes_to_protocols:
        raise ValueError("protocol code %d already taken by %s" %
                         (proto.code, _codes_to_protocols[proto.code].name))

    PROTOCOLS.append(proto)
    _names_to_protocols[proto.name] = proto
    _codes_to_protocols[proto.code] = proto
    return None


def protocol_with_name(name):
    if name not in _names_to_protocols:
        return NULL_PROTOCOL
    return _names_to_protocols[name]


def protocol_with_code(code):
    if code not in _codes_to_protocols:
        return NULL_PROTOCOL
    return _codes_to_protocols[code]


def protocols_with_string(string):
    """Return a list of protocols matching given string."""
    if not string:
        return []

    s = string.strip("/")
    sp = s.split("/")
    if not sp or len(sp) == 0 or sp == ['']:
        return []

    ret = []
    for name in sp:
        proto = protocol_with_name(name)
        if proto is NULL_PROTOCOL:
            raise ValueError("No Protocol with name %s" % name)
        ret.append(proto)
    return ret
