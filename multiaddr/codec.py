import base58
import base64
import binascii
import six

from netaddr import IPAddress

from .protocols import code_to_varint
from .protocols import P_DCCP
from .protocols import P_IP4
from .protocols import P_IP6
from .protocols import P_P2P
from .protocols import P_ONION
from .protocols import protocol_with_code
from .protocols import protocol_with_name
from .protocols import P_SCTP
from .protocols import P_TCP
from .protocols import P_UDP
from .protocols import P_UNIX
from .protocols import read_varint_code


def string_to_bytes(string):
    if not string:
        return b''
    # consume trailing slashes
    if not string.startswith('/'):
        raise ValueError("invalid multiaddr, must begin with /")
    string = string.rstrip('/')
    sp = string.split('/')

    # skip the first element, since it starts with /
    sp.pop(0)
    bs = []
    while sp:
        element = sp.pop(0)
        proto = protocol_with_name(element)
        bs.append(code_to_varint(proto.code))
        if proto.size == 0:
            continue
        if len(sp) < 1:
            raise ValueError(
                "protocol requires address, none given: %s" % proto.name)
        if proto.path:
            sp = ["/" + "/".join(sp)]
        bs.append(address_string_to_bytes(proto, sp.pop(0)))
    return b''.join(bs)


def bytes_to_string(buf):
    st = ['']  # start with empty string so we get a leading slash on join()
    buf = binascii.unhexlify(buf)
    while buf:
        code, num_bytes_read = read_varint_code(buf)
        buf = buf[num_bytes_read:]
        proto = protocol_with_code(code)
        st.append(proto.name)
        size = size_for_addr(proto, buf)
        if size > 0:
            addr = address_bytes_to_string(proto, binascii.hexlify(buf[:size]))
            st.append(addr)
        buf = buf[size:]
    return '/'.join(st)


int_to_hex = None
encode_big_endian_16 = None


def address_string_to_bytes(proto, addr_string):
    global int_to_hex
    if int_to_hex is None:
        from .util import int_to_hex

    global encode_big_endian_16
    if encode_big_endian_16 is None:
        from .util import encode_big_endian_16

    if proto.code == P_IP4:  # ipv4
        try:
            ip = IPAddress(addr_string)
            if ip.version != 4:
                raise ValueError("failed to parse ip4 addr: %s" % addr_string)
            return int_to_hex(int(ip), 8)
        except Exception:
            raise ValueError("failed to parse ip4 addr: %s" % addr_string)
    elif proto.code == P_IP6:  # ipv6
        try:
            ip = IPAddress(addr_string)
            if ip.version != 6:
                raise ValueError("failed to parse ip6 addr: %s" % addr_string)
            return int_to_hex(int(ip), 32)
        except Exception:
            raise ValueError("failed to parse ip6 addr: %s" % addr_string)
    # tcp udp dccp sctp
    elif proto.code in [P_TCP, P_UDP, P_DCCP, P_SCTP]:
        try:
            ip = int(addr_string)
        except ValueError as ex:
            raise ValueError("failed to parse %s addr: %s"
                             % (proto.name, str(ex)))

        if ip >= 65536:
            raise ValueError("failed to parse %s addr: %s" %
                             (proto.name, "greater than 65536"))
        return binascii.hexlify(encode_big_endian_16(ip))
    elif proto.code == P_ONION:
        addr = addr_string.split(":")
        if len(addr) != 2:
            raise ValueError(
                "failed to parse %s addr: %s does not contain a port number."
                % (proto.name, addr_string))

        # onion address without the ".onion" substring
        if len(addr[0]) != 16:
            raise ValueError(
                "failed to parse %s addr: %s not a Tor onion address."
                % (proto.name, addr_string))
        try:
            onion_host_bytes = binascii.hexlify(
                base64.b32decode(addr[0].upper()))
        except Exception as ex:
            raise ValueError(
                "failed to decode base32 %s addr: %s %s"
                % (proto.name, addr_string, str(ex)))

        # onion port number
        try:
            port = int(addr[1])
        except Exception as ex:
            raise ValueError("failed to parse %s addr: %s"
                             % (proto.name, str(ex)))
        if port >= 65536:
            raise ValueError("failed to parse %s addr: %s"
                             % (proto.name, "port greater than 65536"))
        if port < 1:
            raise ValueError("failed to parse %s addr: %s"
                             % (proto.name, "port less than 1"))

        return b''.join([onion_host_bytes,
                         binascii.hexlify(encode_big_endian_16(port))])
    elif proto.code == P_P2P:  # ipfs
        # the address is a varint prefixed multihash string representation
        try:
            mm = base58.b58decode(addr_string)
        except Exception as ex:
            raise ValueError("failed to parse p2p addr: %s %s"
                             % (addr_string, str(ex)))
        size = code_to_varint(len(mm))
        mm = binascii.hexlify(mm)
        if len(mm) < 10:
            # TODO - port go-multihash so we can do this correctly
            raise ValueError("invalid P2P multihash: %s" % mm)
        return b''.join([size, mm])
    elif proto.code == P_UNIX:
        addr_string_bytes = addr_string.encode("ascii")
        size = code_to_varint(len(addr_string_bytes))
        return b''.join([size, binascii.hexlify(addr_string_bytes)])
    else:
        raise ValueError("failed to parse %s addr: unknown" % proto.name)


decode_big_endian_16 = None


def address_bytes_to_string(proto, buf):
    global decode_big_endian_16
    if decode_big_endian_16 is None:
        from .util import decode_big_endian_16
    if proto.code == P_IP4:
        return str(IPAddress(int(buf, 16), 4).ipv4())
    elif proto.code == P_IP6:
        return str(IPAddress(int(buf, 16), 6).ipv6())
    elif proto.code in [P_TCP, P_UDP, P_DCCP, P_SCTP]:
        return str(decode_big_endian_16(binascii.unhexlify(buf)))
    elif proto.code == P_ONION:
        buf = binascii.unhexlify(buf)
        addr_bytes, port_bytes = (buf[:-2], buf[-2:])
        addr = base64.b32encode(addr_bytes).decode('ascii').lower()
        port = str(decode_big_endian_16(port_bytes))
        return ':'.join([addr, port])
    elif proto.code == P_P2P:
        buf = binascii.unhexlify(buf)
        size, num_bytes_read = read_varint_code(buf)
        buf = buf[num_bytes_read:]
        if len(buf) != size:
            raise ValueError("inconsistent lengths")
        return base58.b58encode(buf).decode()
    elif proto.code == P_UNIX:
        return binascii.unhexlify(buf).decode('ascii')
    raise ValueError("unknown protocol")


def size_for_addr(proto, buf):
    if proto.size > 0:
        return proto.size // 8
    elif proto.size == 0:
        return 0
    else:
        size, num_bytes_read = read_varint_code(buf)
        return size + num_bytes_read


def bytes_split(buf):
    ret = []
    buf = binascii.unhexlify(buf)
    while buf:
        code, num_bytes_read = read_varint_code(buf)
        proto = protocol_with_code(code)
        size = size_for_addr(proto, buf[num_bytes_read:])
        length = size + num_bytes_read
        ret.append(buf[:length])
        buf = buf[length:]
    return ret
