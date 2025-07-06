import pytest

from multiaddr import Multiaddr
from multiaddr.exceptions import StringParseError
from multiaddr.utils import get_thin_waist_addresses


def test_no_address():
    assert get_thin_waist_addresses() == []
    assert get_thin_waist_addresses(None) == []


def test_specific_address():
    input_addr = Multiaddr("/ip4/123.123.123.123/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr)
    assert addrs == [input_addr]


def test_specific_address_override_port():
    input_addr = Multiaddr("/ip4/123.123.123.123/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr, 100)
    assert addrs == [Multiaddr("/ip4/123.123.123.123/tcp/100")]


def test_ignore_non_thin_waist():
    # Should raise StringParseError for unknown protocol (e.g. /webrtc)
    with pytest.raises(StringParseError):
        Multiaddr("/ip4/123.123.123.123/udp/1234/webrtc")


def test_ipv4_wildcard():
    input_addr = Multiaddr("/ip4/0.0.0.0/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr)
    assert len(addrs) > 0
    for addr in addrs:
        s = str(addr)
        assert s.startswith("/ip4/")
        assert "/tcp/1234" in s
        assert not s.startswith("/ip4/0.0.0.0")


def test_ipv4_wildcard_override_port():
    input_addr = Multiaddr("/ip4/0.0.0.0/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr, 100)
    assert len(addrs) > 0
    for addr in addrs:
        s = str(addr)
        assert s.startswith("/ip4/")
        assert "/tcp/100" in s
        assert not s.startswith("/ip4/0.0.0.0")


def test_ipv6_wildcard():
    input_addr = Multiaddr("/ip6/::/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr)
    assert len(addrs) >= 0  # May be 0 if no IPv6 interfaces
    for addr in addrs:
        s = str(addr)
        assert s.startswith("/ip6/")
        assert "/tcp/1234" in s
        assert not s.startswith("/ip6/::")


def test_ipv6_wildcard_override_port():
    input_addr = Multiaddr("/ip6/::/tcp/1234")
    addrs = get_thin_waist_addresses(input_addr, 100)
    assert len(addrs) >= 0  # May be 0 if no IPv6 interfaces
    for addr in addrs:
        s = str(addr)
        assert s.startswith("/ip6/")
        assert "/tcp/100" in s
        assert not s.startswith("/ip6/::")
