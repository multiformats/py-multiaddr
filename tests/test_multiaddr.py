import pytest

from multiaddr.exceptions import (
    BinaryParseError,
    ProtocolLookupError,
    ProtocolNotFoundError,
    StringParseError,
)
from multiaddr.multiaddr import Multiaddr
from multiaddr.protocols import (
    P_DNS,
    P_IP4,
    P_IP6,
    P_P2P,
    P_TCP,
    P_UDP,
    P_UNIX,
    protocol_with_name,
    protocols_with_string,
)


@pytest.mark.parametrize(
    "addr_str",
    [
        "/ip4",
        "/ip4/::1",
        "/ip4/fdpsofodsajfdoisa",
        "/ip6",
        "/ip6zone",
        "/ip6zone/",
        "/ip6zone//ip6/fe80::1",
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
        "/onion3/9ww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd:80",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd7:80",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd:0",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd:a",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd:-1",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd",
        "/onion3/vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyy@:666",
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
        "/dns",
        "/dns4",
        "/dns6",
        "/cancer",
    ],
)
def test_invalid(addr_str):
    with pytest.raises(StringParseError):
        Multiaddr(addr_str)


@pytest.mark.parametrize(
    "addr_str",
    [
        "/ip4/1.2.3.4",
        "/ip4/0.0.0.0",
        "/ip6/::1",
        "/ip6/2601:9:4f81:9700:803e:ca65:66e8:c21",
        "/ip6zone/x/ip6/fe80::1",
        "/ip6zone/x%y/ip6/fe80::1",
        "/ip6zone/x%y/ip6/::",
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
        "/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234",
        "/ip4/127.0.0.1/udp/1234",
        "/ip4/127.0.0.1/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234",
        "/unix/a/b/c/d/e",
        "/unix/stdio",
        "/ip4/1.2.3.4/tcp/80/unix/a/b/c/d/e/f",
        "/ip4/127.0.0.1/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234/unix/stdio",
        "/dns/example.com",
        "/dns4/موقع.وزارة-الاتصالات.مصر",
    ],
)  # nopep8
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


def test_protocols():
    ma = Multiaddr("/ip4/127.0.0.1/udp/1234")
    protos = ma.protocols()
    # Convert to list to access elements by index
    proto_list = list(protos)
    assert proto_list[0].code == protocol_with_name("ip4").code
    assert proto_list[1].code == protocol_with_name("udp").code


@pytest.mark.parametrize(
    "proto_string,expected",
    [
        ("/ip4", [protocol_with_name("ip4")]),
        ("/ip4/tcp", [protocol_with_name("ip4"), protocol_with_name("tcp")]),
        (
            "ip4/tcp/udp/ip6",
            [
                protocol_with_name("ip4"),
                protocol_with_name("tcp"),
                protocol_with_name("udp"),
                protocol_with_name("ip6"),
            ],
        ),
        ("////////ip4/tcp", [protocol_with_name("ip4"), protocol_with_name("tcp")]),
        ("ip4/udp/////////", [protocol_with_name("ip4"), protocol_with_name("udp")]),
        ("////////ip4/tcp////////", [protocol_with_name("ip4"), protocol_with_name("tcp")]),
        ("////////ip4/////////tcp////////", [protocol_with_name("ip4"), protocol_with_name("tcp")]),
    ],
)
def test_protocols_with_string(proto_string, expected):
    protos = protocols_with_string(proto_string)
    assert protos == expected


@pytest.mark.parametrize(
    "addr,error",
    [
        ("dsijafd", ProtocolNotFoundError),
        ("/ip4/tcp/fidosafoidsa", StringParseError),
        ("////////ip4/tcp/21432141/////////", StringParseError),
    ],
)
def test_invalid_protocols_with_string(addr, error):
    with pytest.raises(error):
        protocols_with_string(addr)


@pytest.mark.parametrize(
    "proto_string,maxsplit,expected",
    [
        ("/ip4/1.2.3.4", -1, ("/ip4/1.2.3.4",)),
        ("/ip4/0.0.0.0", 0, ("/ip4/0.0.0.0",)),
        ("/ip6/::1", 1, ("/ip6/::1",)),
        (
            "/ip4/127.0.0.1/p2p/bafzbeigvf25ytwc3akrijfecaotc74udrhcxzh2cx3we5qqnw5vgrei4bm/tcp/1234",
            1,
            ("/ip4/127.0.0.1", "/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234"),
        ),
        (
            "/ip4/1.2.3.4/tcp/80/unix/a/b/c/d/e/f",
            -1,
            ("/ip4/1.2.3.4", "/tcp/80", "/unix/a/b/c/d/e/f"),
        ),
    ],
)
def test_split(proto_string, maxsplit, expected):
    assert tuple(map(str, Multiaddr(proto_string).split(maxsplit))) == expected


@pytest.mark.parametrize(
    "proto_parts,expected",
    [
        (("/ip4/1.2.3.4",), "/ip4/1.2.3.4"),
        ((Multiaddr("/ip4/0.0.0.0").to_bytes(),), "/ip4/0.0.0.0"),
        (("/ip6/::1",), "/ip6/::1"),
        (
            (
                Multiaddr("/ip4/127.0.0.1").to_bytes(),
                "/p2p/bafzbeigvf25ytwc3akrijfecaotc74udrhcxzh2cx3we5qqnw5vgrei4bm/tcp/1234",
            ),
            "/ip4/127.0.0.1/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/tcp/1234",
        ),
        (("/ip4/1.2.3.4", "/tcp/80", "/unix/a/b/c/d/e/f"), "/ip4/1.2.3.4/tcp/80/unix/a/b/c/d/e/f"),
    ],
)
def test_join(proto_parts, expected):
    assert str(Multiaddr.join(*proto_parts)) == expected


def test_encapsulate():
    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")
    m2 = Multiaddr("/udp/5678")

    encapsulated = m1.encapsulate(m2)
    assert str(encapsulated) == "/ip4/127.0.0.1/udp/1234/udp/5678"

    m3 = Multiaddr("/udp/5678")
    decapsulated = encapsulated.decapsulate(m3)
    assert str(decapsulated) == "/ip4/127.0.0.1/udp/1234"

    m4 = Multiaddr("/ip4/127.0.0.1")
    # JavaScript returns empty multiaddr when decapsulating a prefix
    assert str(decapsulated.decapsulate(m4)) == ""

    m5 = Multiaddr("/ip6/::1")
    with pytest.raises(ValueError):
        decapsulated.decapsulate(m5)


def assert_value_for_proto(multi, proto, expected):
    assert multi.value_for_protocol(proto) == expected


@pytest.mark.parametrize(
    "addr_str,proto,expected",
    [
        (
            "/ip4/127.0.0.1/tcp/4001/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC",
            "p2p",
            "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC",
        ),
        ("/ip4/127.0.0.1/tcp/4001", "tcp", "4001"),
        ("/ip4/127.0.0.1/tcp/4001", "ip4", "127.0.0.1"),
        ("/ip4/127.0.0.1/tcp/4001", "udp", None),
        ("/ip6/::1/tcp/1234", "ip6", "::1"),
        ("/ip6/::1/tcp/1234", "tcp", "1234"),
        ("/ip6/::1/tcp/1234", "udp", None),
    ],
)
def test_get_value(addr_str, proto, expected):
    m = Multiaddr(addr_str)
    if expected is None:
        with pytest.raises(ProtocolLookupError):
            m.value_for_protocol(proto)
    else:
        assert m.value_for_protocol(proto) == expected


def test_get_value_original():
    ma = Multiaddr(
        "/ip4/127.0.0.1/tcp/5555/udp/1234/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"
    )

    assert_value_for_proto(ma, P_IP4, "127.0.0.1")
    assert_value_for_proto(ma, P_TCP, "5555")
    assert_value_for_proto(ma, P_UDP, "1234")
    assert_value_for_proto(ma, P_P2P, "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC")
    assert_value_for_proto(ma, "ip4", "127.0.0.1")
    assert_value_for_proto(ma, "tcp", "5555")
    assert_value_for_proto(ma, "udp", "1234")
    assert_value_for_proto(ma, protocol_with_name("ip4"), "127.0.0.1")
    assert_value_for_proto(ma, protocol_with_name("tcp"), "5555")
    assert_value_for_proto(ma, protocol_with_name("udp"), "1234")

    with pytest.raises(ProtocolLookupError):
        ma.value_for_protocol(P_IP6)
    with pytest.raises(ProtocolLookupError):
        ma.value_for_protocol("ip6")
    with pytest.raises(ProtocolLookupError):
        ma.value_for_protocol(protocol_with_name("ip6"))

    a = Multiaddr(b"\x35\x03a:b")  # invalid protocol value
    with pytest.raises(BinaryParseError):
        a.value_for_protocol(P_DNS)

    a = Multiaddr("/ip4/0.0.0.0")  # only one addr
    assert_value_for_proto(a, P_IP4, "0.0.0.0")

    a = Multiaddr("/ip4/0.0.0.0/ip4/0.0.0.0/ip4/0.0.0.0")  # same sub-addr
    assert_value_for_proto(a, P_IP4, "0.0.0.0")

    a = Multiaddr("/ip4/0.0.0.0/unix/tmp/a/b/c/d")  # ending in a path one.
    assert_value_for_proto(a, P_IP4, "0.0.0.0")

    a = Multiaddr("/unix/studio")
    assert_value_for_proto(a, P_UNIX, "/studio")  # only a path.


def test_views():
    ma = Multiaddr(
        "/ip4/127.0.0.1/tcp/5555/udp/1234/"
        "p2p/bafzbeigalb34xlqdtvyklzqa5ibmn6pssqsdskc4ty2e4jxy2kamquh22y"
    )

    # Convert views to lists for indexing
    keys_list = list(ma.keys())
    values_list = list(ma.values())
    items_list = list(ma.items())

    for idx, (proto1, proto2, item, value) in enumerate(
        zip(ma, keys_list, items_list, values_list)
    ):
        assert (proto1, value) == (proto2, value) == item
        assert proto1 in ma
        assert proto2 in ma.keys()
        assert item in ma.items()
        assert value in ma.values()
        assert keys_list[idx] == keys_list[idx - len(ma)] == proto1 == proto2
        assert items_list[idx] == items_list[idx - len(ma)] == item
        assert values_list[idx] == values_list[idx - len(ma)] == ma[proto1] == value

    assert len(keys_list) == len(items_list) == len(values_list) == len(ma)
    assert len(list(ma.keys())) == len(ma.keys())
    assert len(list(ma.items())) == len(ma.items())
    assert len(list(ma.values())) == len(ma.values())

    # Test out of bounds
    with pytest.raises(IndexError):
        keys_list[len(ma)]
    with pytest.raises(IndexError):
        items_list[len(ma)]
    with pytest.raises(IndexError):
        values_list[len(ma)]


def test_bad_initialization_no_params():
    with pytest.raises(TypeError):
        Multiaddr()  # type: ignore


def test_bad_initialization_too_many_params():
    with pytest.raises(TypeError):
        Multiaddr("/ip4/0.0.0.0", "")  # type: ignore


def test_bad_initialization_wrong_type():
    with pytest.raises(TypeError):
        Multiaddr(42)  # type: ignore


def test_value_for_protocol_argument_wrong_type():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    with pytest.raises(ProtocolNotFoundError):
        a.value_for_protocol("str123")

    with pytest.raises(TypeError):
        a.value_for_protocol(None)


def test_multi_addr_str_corruption():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    a._bytes = b"047047047"

    with pytest.raises(BinaryParseError):
        str(a)


def test_decapsulate():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    u = Multiaddr("/udp/1234")
    assert a.decapsulate(u) == Multiaddr("/ip4/127.0.0.1")


def test__repr():
    a = Multiaddr("/ip4/127.0.0.1/udp/1234")
    assert repr(a) == "<Multiaddr %s>" % str(a)


def test_zone():
    ip6_string = "/ip6zone/eth0/ip6/::1"
    ip6_bytes = Multiaddr(ip6_string).to_bytes()
    maddr_from_str = Multiaddr(ip6_string)
    assert maddr_from_str.to_bytes() == ip6_bytes
    maddr_from_bytes = Multiaddr(ip6_bytes)
    assert str(maddr_from_bytes) == ip6_string


def test_hash():
    addr_bytes = Multiaddr("/ip4/127.0.0.1/udp/1234").to_bytes()

    assert hash(Multiaddr(addr_bytes)) == hash(addr_bytes)


def test_sequence_behavior():
    ma = Multiaddr("/ip4/127.0.0.1/udp/1234")
    proto1 = protocol_with_name("ip4")
    proto2 = protocol_with_name("udp")
    value1 = "127.0.0.1"
    value2 = "1234"
    item1 = (proto1, value1)
    item2 = (proto2, value2)

    # Test positive indices
    for idx, (proto, value, item) in enumerate(
        zip([proto1, proto2], [value1, value2], [item1, item2])
    ):
        assert proto in ma
        assert value in ma.values()
        assert item in ma.items()
        assert list(ma.keys())[idx] == list(ma.keys())[idx - len(ma)] == proto
        assert list(ma.items())[idx] == list(ma.items())[idx - len(ma)] == item
        assert list(ma.values())[idx] == list(ma.values())[idx - len(ma)] == value

    # Test negative indices
    for idx, (proto, value, item) in enumerate(
        zip([proto1, proto2], [value1, value2], [item1, item2])
    ):
        assert proto in ma
        assert value in ma.values()
        assert item in ma.items()
        assert list(ma.keys())[idx] == list(ma.keys())[idx - len(ma)] == proto
        assert list(ma.items())[idx] == list(ma.items())[idx - len(ma)] == item
        assert list(ma.values())[idx] == list(ma.values())[idx - len(ma)] == value

    # Test out of bounds
    with pytest.raises(IndexError):
        list(ma.keys())[len(ma)]
    with pytest.raises(IndexError):
        list(ma.items())[len(ma)]
    with pytest.raises(IndexError):
        list(ma.values())[len(ma)]


def test_circuit_peer_id_extraction():
    """Test that get_peer_id() returns the correct peer ID for circuit addresses."""

    # Basic circuit address - should return target peer ID
    ma = Multiaddr("/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC")
    assert ma.get_peer_id() == "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"

    # Circuit with relay - should return target peer ID, not relay peer ID
    ma = Multiaddr(
        "/ip4/0.0.0.0/tcp/8080/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"
    )
    assert ma.get_peer_id() == "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"

    # Circuit without target peer ID - should return None
    ma = Multiaddr(
        "/ip4/127.0.0.1/tcp/123/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit"
    )
    assert ma.get_peer_id() is None

    # Input: bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4 (CIDv1 Base32)
    # Expected: QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi (CIDv0 Base58btc)
    ma = Multiaddr("/p2p-circuit/p2p/bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4")
    assert ma.get_peer_id() == "QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"

    # Base58btc encoded identity multihash (no conversion needed)
    ma = Multiaddr("/p2p-circuit/p2p/12D3KooWNvSZnPi3RrhrTwEY4LuuBeB6K6facKUCJcyWG1aoDd2p")
    assert ma.get_peer_id() == "12D3KooWNvSZnPi3RrhrTwEY4LuuBeB6K6facKUCJcyWG1aoDd2p"


def test_circuit_peer_id_edge_cases():
    """Test edge cases for circuit peer ID extraction."""

    # Multiple circuits - should return the target peer ID after the last circuit
    # Input: bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4 (CIDv1 Base32)
    # Expected: QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi (CIDv0 Base58btc)
    ma = Multiaddr(
        "/ip4/1.2.3.4/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/p2p-circuit/p2p/bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4"
    )
    assert ma.get_peer_id() == "QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"

    # Circuit with multiple p2p components after it
    # Input: bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4 (CIDv1 Base32)
    # Expected: QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi (CIDv0 Base58btc)
    ma = Multiaddr(
        "/ip4/1.2.3.4/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC/p2p/bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4"
    )
    assert ma.get_peer_id() == "QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"

    # Circuit at the beginning (invalid but should handle gracefully)
    ma = Multiaddr("/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC")
    assert ma.get_peer_id() == "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"

    # No p2p components at all
    ma = Multiaddr("/ip4/127.0.0.1/tcp/1234")
    assert ma.get_peer_id() is None

    # Only relay peer ID, no target
    ma = Multiaddr(
        "/ip4/127.0.0.1/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit"
    )
    assert ma.get_peer_id() is None


def test_circuit_address_parsing():
    """Test that circuit addresses can be parsed correctly."""

    # Basic circuit address
    ma = Multiaddr("/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC")
    assert str(ma) == "/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"

    # Circuit with relay
    ma = Multiaddr(
        "/ip4/0.0.0.0/tcp/8080/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"
    )
    assert "p2p-circuit" in str(ma)
    assert "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC" in str(ma)

    # Input: bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4 (CIDv1 Base32)
    # Expected: QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi (CIDv0 Base58btc)
    ma = Multiaddr(
        "/ip4/127.0.0.1/tcp/1234/tls/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4"
    )
    assert (
        str(ma)
        == "/ip4/127.0.0.1/tcp/1234/tls/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"
    )


def test_circuit_address_manipulation():
    """Test circuit address manipulation (encapsulate/decapsulate)."""

    # Input: bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4 (CIDv1 Base32)
    # Expected: QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi (CIDv0 Base58btc)
    relay = Multiaddr("/ip4/127.0.0.1/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6")
    circuit = Multiaddr(
        "/p2p-circuit/p2p/bafzbeigweq4zr4x4ky2dvv7nanbkw6egutvrrvzw6g3h2rftp7gidyhtt4"
    )
    combined = relay.encapsulate(circuit)
    assert (
        str(combined)
        == "/ip4/127.0.0.1/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6/p2p-circuit/p2p/QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"
    )
    assert combined.get_peer_id() == "QmckZzdVd72h9QUFuJJpQqhsZqGLwjhh81qSvZ9BhB2FQi"

    # Decapsulate circuit
    decapsulated = combined.decapsulate("/p2p-circuit")
    assert (
        str(decapsulated)
        == "/ip4/127.0.0.1/tcp/1234/p2p/QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6"
    )
    assert decapsulated.get_peer_id() == "QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6"


def test_circuit_with_consistent_cid_format():
    """Test circuit functionality using consistent CIDv0 format for easier comparison."""

    # All peer IDs in CIDv0 Base58btc format for easy visual comparison
    relay_peer_id = "QmZR5a9AAXGqQF2ADqoDdGS8zvqv8n3Pag6TDDnTNMcFW6"
    target_peer_id = "QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC"

    # Basic circuit with consistent format
    ma = Multiaddr(f"/p2p-circuit/p2p/{target_peer_id}")
    assert ma.get_peer_id() == target_peer_id

    # Circuit with relay using consistent format
    ma = Multiaddr(f"/ip4/127.0.0.1/tcp/1234/p2p/{relay_peer_id}/p2p-circuit/p2p/{target_peer_id}")
    assert ma.get_peer_id() == target_peer_id

    # Test string representation preserves format
    assert (
        str(ma) == f"/ip4/127.0.0.1/tcp/1234/p2p/{relay_peer_id}/p2p-circuit/p2p/{target_peer_id}"
    )

    # Test encapsulate/decapsulate with consistent format
    relay = Multiaddr(f"/ip4/127.0.0.1/tcp/1234/p2p/{relay_peer_id}")
    circuit = Multiaddr(f"/p2p-circuit/p2p/{target_peer_id}")
    combined = relay.encapsulate(circuit)

    assert (
        str(combined)
        == f"/ip4/127.0.0.1/tcp/1234/p2p/{relay_peer_id}/p2p-circuit/p2p/{target_peer_id}"
    )
    assert combined.get_peer_id() == target_peer_id

    # Decapsulate should return relay address
    decapsulated = combined.decapsulate("/p2p-circuit")
    assert str(decapsulated) == f"/ip4/127.0.0.1/tcp/1234/p2p/{relay_peer_id}"
    assert decapsulated.get_peer_id() == relay_peer_id


def test_decapsulate_code():
    from multiaddr import Multiaddr
    from multiaddr.protocols import P_DNS4, P_IP4, P_P2P, P_TCP

    # Use a valid Peer ID (CID) for /p2p/
    valid_peer_id = "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk"
    ma = Multiaddr(f"/ip4/1.2.3.4/tcp/80/p2p/{valid_peer_id}")
    assert str(ma.decapsulate_code(P_P2P)) == "/ip4/1.2.3.4/tcp/80"
    assert str(ma.decapsulate_code(P_TCP)) == "/ip4/1.2.3.4"
    assert str(ma.decapsulate_code(P_IP4)) == ""
    # Not present: returns original
    assert str(ma.decapsulate_code(9999)) == str(ma)

    # Multiple occurrences
    ma2 = Multiaddr("/dns4/example.com/tcp/1234/dns4/foo.com/tcp/5678")
    assert str(ma2.decapsulate_code(P_DNS4)) == "/dns4/example.com/tcp/1234"
    # Remove the last tcp
    assert str(ma2.decapsulate_code(P_TCP)) == "/dns4/example.com/tcp/1234/dns4/foo.com"

    # No-op on empty
    ma3 = Multiaddr("")
    assert str(ma3.decapsulate_code(P_TCP)) == ""
