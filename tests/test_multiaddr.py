#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from multiaddr.multiaddr import Multiaddr
from multiaddr.multiaddr import ProtocolNotFoundException
from multiaddr.protocols import protocol_with_name
from multiaddr.protocols import protocols_with_string
from multiaddr.protocols import P_IP4
from multiaddr.protocols import P_IP6
from multiaddr.protocols import P_P2P
from multiaddr.protocols import P_UTP
from multiaddr.protocols import P_TCP
from multiaddr.protocols import P_UDP
from multiaddr.protocols import P_UNIX
from multiaddr.util import split
from multiaddr.util import join


@pytest.mark.parametrize(
    "addr_str",
    ["/ip4",
     "/ip4/::1",
     "/ip4/fdpsofodsajfdoisa",
     "/ip6",
     "/udp",
     "/tcp",
     "/sctp",
     "/udp/65536",
     "/tcp/65536",
     "/onion/9imaq4ygg2iegci7:80",
     "/onion/aaimaq4ygg2iegci7:80",
     "/onion/timaq4ygg2iegci7:0",
     "/onion/timaq4ygg2iegci7:-1",
     "/onion/timaq4ygg2iegci7",
     "/onion/timaq4ygg2iegci@:666",
     "/udp/1234/sctp",
     "/udp/1234/udt/1234",
     "/udp/1234/utp/1234",
     "/ip4/127.0.0.1/udp/jfodsajfidosajfoidsa",
     "/ip4/127.0.0.1/udp",
     "/ip4/127.0.0.1/tcp/jfodsajfidosajfoidsa",
     "/ip4/127.0.0.1/tcp",
     "/ip4/127.0.0.1/p2p",
     "/ip4/127.0.0.1/p2p/tcp",
     "/unix",
     "/ip4/1.2.3.4/tcp/80/unix",
     "/ip4/127.0.0.1/tcp/9090/http/p2p-webcrt-direct"])
def test_invalid(addr_str):
    with pytest.raises(ValueError):
        Multiaddr(addr_str)


@pytest.mark.parametrize(
    "addr_str",
    ["/ip4/1.2.3.4",
     "/ip4/0.0.0.0",
     "/ip6/::1",
     "/ip6/2601:9:4f81:9700:803e:ca65:66e8:c21",
     "/onion/timaq4ygg2iegci7:1234",
     "/onion/timaq4ygg2iegci7:80/http",
     "/udp/0",
     "/tcp/0",
     "/sctp/0",
     "/udp/1234",
     "/tcp/1234",
     "/sctp/1234",
     "/udp/65535",
     "/tcp/65535",
     "/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC",
     "/udp/1234/sctp/1234",
     "/udp/1234/udt",
     "/udp/1234/utp",
     "/tcp/1234/http",
     "/tcp/1234/https",
     "/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234",
     "/ip4/127.0.0.1/udp/1234",
     "/ip4/127.0.0.1/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234",
     "/unix/a/b/c/d/e",
     "/unix/stdio",
     "/ip4/1.2.3.4/tcp/80/unix/a/b/c/d/e/f",
     "/ip4/127.0.0.1/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234/unix/stdio",
     "/ip4/127.0.0.1/tcp/9090/http/p2p-webrtc-direct"])  # nopep8
def test_valid(addr_str):
    ma = Multiaddr(addr_str)
    assert str(ma) == addr_str.rstrip("/")


def test_eq():
    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")
    m2 = Multiaddr("/ip4/127.0.0.1/tcp/1234")
    m3 = Multiaddr("/ip4/127.0.0.1/tcp/1234")
    m4 = Multiaddr("/ip4/127.0.0.1/tcp/1234/")

    assert m1 != m2
    assert m2 != m1

    assert m2 == m3
    assert m3 == m2

    assert m1 == m1

    assert m2 == m4
    assert m4 == m2
    assert m3 == m4
    assert m4 == m3


@pytest.mark.parametrize(
    'test_vals',
    [("/ip4/1.2.3.4/udp/1234", ["/ip4/1.2.3.4", "/udp/1234"]),
     ("/ip4/1.2.3.4/tcp/1/ip4/2.3.4.5/udp/2",
      ["/ip4/1.2.3.4", "/tcp/1", "/ip4/2.3.4.5", "/udp/2"]),
     ("/ip4/1.2.3.4/utp/ip4/2.3.4.5/udp/2/udt",
      ["/ip4/1.2.3.4", "/utp", "/ip4/2.3.4.5", "/udp/2", "/udt"])])
def test_bytes_split_and_join(test_vals):
    string, expected = test_vals
    mm = Multiaddr(string)
    split_m = split(mm)
    for i, addr in enumerate(split_m):
        assert str(addr) == expected[i]
    joined = join(split_m)
    assert mm == joined


def test_protocols():
    ma = Multiaddr("/ip4/127.0.0.1/udp/1234")
    protos = ma.protocols()
    assert protos[0].code == protocol_with_name("ip4").code
    assert protos[1].code == protocol_with_name("udp").code


@pytest.mark.parametrize(
    'proto_string,expected',
    [("/ip4", [protocol_with_name("ip4")]),
     ("/ip4/tcp", [protocol_with_name("ip4"), protocol_with_name("tcp")]),
     ("ip4/tcp/udp/ip6",
      [protocol_with_name("ip4"),
       protocol_with_name("tcp"),
       protocol_with_name("udp"),
       protocol_with_name("ip6")]),
     ("////////ip4/tcp",
      [protocol_with_name("ip4"), protocol_with_name("tcp")]),
     ("ip4/udp/////////",
      [protocol_with_name("ip4"), protocol_with_name("udp")]),
     ("////////ip4/tcp////////",
      [protocol_with_name("ip4"), protocol_with_name("tcp")])])
def test_protocols_with_string(proto_string, expected):
    protos = protocols_with_string(proto_string)
    assert protos == expected


@pytest.mark.parametrize(
    'proto_string',
    ["dsijafd",
     "/ip4/tcp/fidosafoidsa",
     "////////ip4/tcp/21432141/////////",
     "////////ip4///////tcp/////////"])
def test_invalid_protocols_with_string(proto_string):
    with pytest.raises(ValueError):
        protocols_with_string(proto_string)


def test_encapsulate():
    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")
    m2 = Multiaddr("/udp/5678")

    encapsulated = m1.encapsulate(m2)
    assert str(encapsulated) == "/ip4/127.0.0.1/udp/1234/udp/5678"

    m3 = Multiaddr("/udp/5678")
    decapsulated = encapsulated.decapsulate(m3)
    assert str(decapsulated) == "/ip4/127.0.0.1/udp/1234"

    m4 = Multiaddr("/ip4/127.0.0.1")
    decapsulated_2 = decapsulated.decapsulate(m4)
    assert str(decapsulated_2) == ""

    m5 = Multiaddr("/ip6/::1")
    decapsulated_3 = decapsulated.decapsulate(m5)

    assert str(decapsulated_3) == "/ip4/127.0.0.1/udp/1234"


def assert_value_for_proto(multi, proto, expected):
    assert multi.value_for_protocol(proto) == expected


def test_get_value():
    ma = Multiaddr(
        "/ip4/127.0.0.1/utp/tcp/5555/udp/1234/utp/"
        "p2p/QmbHVEEepCi7rn7VL7Exxpd2Ci9NNB6ifvqwhsrbRMgQFP")

    assert_value_for_proto(ma, P_IP4, "127.0.0.1")
    assert_value_for_proto(ma, P_UTP, "")
    assert_value_for_proto(ma, P_TCP, "5555")
    assert_value_for_proto(ma, P_UDP, "1234")
    assert_value_for_proto(
        ma, P_P2P, "QmbHVEEepCi7rn7VL7Exxpd2Ci9NNB6ifvqwhsrbRMgQFP")

    with pytest.raises(ProtocolNotFoundException):
        ma.value_for_protocol(P_IP6)

    a = Multiaddr("/ip4/0.0.0.0")  # only one addr
    assert_value_for_proto(a, P_IP4, "0.0.0.0")

    a = Multiaddr("/ip4/0.0.0.0/ip4/0.0.0.0/ip4/0.0.0.0")  # same sub-addr
    assert_value_for_proto(a, P_IP4, "0.0.0.0")

    a = Multiaddr("/ip4/0.0.0.0/udp/12345/utp")  # ending in a no-value one.
    assert_value_for_proto(a, P_IP4, "0.0.0.0")
    assert_value_for_proto(a, P_UDP, "12345")
    assert_value_for_proto(a, P_UTP, "")

    a = Multiaddr("/ip4/0.0.0.0/unix/a/b/c/d")  # ending in a path one.
    assert_value_for_proto(a, P_IP4, "0.0.0.0")
    assert_value_for_proto(a, P_UNIX, "/a/b/c/d")

    a = Multiaddr("/unix/studio")
    assert_value_for_proto(a, P_UNIX, "/studio")  # only a path.


def test_bad_initialization_no_params():
    with pytest.raises(TypeError):
        Multiaddr()


def test_bad_initialization_too_many_params():
    with pytest.raises(TypeError):
        Multiaddr("/ip4/0.0.0.0", "")


def test_bad_initialization_wrong_type():
    with pytest.raises(ValueError):
        Multiaddr(42)


def test_get_value_too_many_fields_protocol(monkeypatch):
    """
    This test patches the Multiaddr's string representation to return
    an invalid string in order to test that value_for_protocol properly
    throws a ValueError.  This avoids some of the error checking in
    the constructor and is easier to patch, thus the actual values
    that the constructor specifies is ignored by the test.
    """
    monkeypatch.setattr("multiaddr.multiaddr.Multiaddr.__str__",
                        lambda ignore: '/udp/1234/5678')
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    with pytest.raises(ValueError):
        a.value_for_protocol(P_UDP)


def test_value_for_protocol_argument_wrong_type():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    with pytest.raises(ValueError):
        a.value_for_protocol('str123')


def test_multi_addr_str_corruption():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    a._bytes = b"047047047"

    with pytest.raises(ValueError):
        str(a)


def test_decapsulate_corrupted_bytes(monkeypatch):
    def raiseException(self, other):
        raise Exception

    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    u = Multiaddr("/udp/1234")
    monkeypatch.setattr("multiaddr.multiaddr.Multiaddr.__init__",
                        raiseException)

    with pytest.raises(ValueError):
        a.decapsulate(u)


def test__repr():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    assert(repr(a) == "<Multiaddr %s>" % str(a))
