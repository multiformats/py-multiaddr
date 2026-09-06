import pytest

from multiaddr import Multiaddr, from_net_addr, to_net_addr


def test_from_net_addr_tcp4():
    assert str(from_net_addr(("1.2.3.4", 80))) == "/ip4/1.2.3.4/tcp/80"


def test_from_net_addr_udp6():
    assert str(from_net_addr(("::1", 53), transport="udp")) == "/ip6/::1/udp/53"


def test_from_net_addr_ipv6_tuple():
    assert str(from_net_addr(("2001:db8::1", 443, 0, 0))) == "/ip6/2001:db8::1/tcp/443"


def test_from_net_addr_rejects_bad_transport():
    with pytest.raises(ValueError, match="unsupported transport"):
        from_net_addr(("1.2.3.4", 80), transport="sctp")


def test_to_net_addr_roundtrip():
    ma = Multiaddr("/ip4/1.2.3.4/tcp/80")
    assert to_net_addr(ma) == ("1.2.3.4", 80)
    assert str(from_net_addr(to_net_addr(ma))) == str(ma)


def test_to_net_addr_rejects_non_thin_waist():
    with pytest.raises(ValueError, match="thin waist"):
        to_net_addr(Multiaddr("/unix/tmp/socket"))
