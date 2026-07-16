from multiaddr import Multiaddr
from multiaddr import utils


def test_is_thin_waist():
    assert utils.is_thin_waist(Multiaddr("/ip4/127.0.0.1"))
    assert utils.is_thin_waist(Multiaddr("/ip4/127.0.0.1/tcp/80"))
    assert utils.is_thin_waist(Multiaddr("/ip6/::1/udp/1234"))
    assert not utils.is_thin_waist(Multiaddr("/ip4/127.0.0.1/tcp/80/ws"))
    assert not utils.is_thin_waist(Multiaddr("/dns4/example.com"))
    assert not utils.is_thin_waist(Multiaddr("/unix/a/b/c"))


def test_is_ip_loopback():
    assert utils.is_ip_loopback(Multiaddr("/ip4/127.0.0.1/tcp/80"))
    assert utils.is_ip_loopback(Multiaddr("/ip6/::1"))
    assert not utils.is_ip_loopback(Multiaddr("/ip4/1.2.3.4"))
    assert not utils.is_ip_loopback(Multiaddr("/dns4/localhost"))


def test_is_ip_unspecified():
    assert utils.is_ip_unspecified(Multiaddr("/ip4/0.0.0.0/tcp/80"))
    assert utils.is_ip_unspecified(Multiaddr("/ip6/::/udp/1234"))
    assert not utils.is_ip_unspecified(Multiaddr("/ip4/127.0.0.1"))


def test_is_ip6_link_local():
    assert utils.is_ip6_link_local(Multiaddr("/ip6/fe80::1/tcp/80"))
    assert not utils.is_ip6_link_local(Multiaddr("/ip6/::1"))
    assert not utils.is_ip6_link_local(Multiaddr("/ip4/169.254.1.1"))  # ipv4


def test_is_private_addr():
    assert utils.is_private_addr(Multiaddr("/ip4/127.0.0.1"))
    assert utils.is_private_addr(Multiaddr("/ip4/10.0.0.1/tcp/80"))
    assert utils.is_private_addr(Multiaddr("/ip4/192.168.1.1"))
    assert utils.is_private_addr(Multiaddr("/ip4/172.16.0.1"))
    assert utils.is_private_addr(Multiaddr("/ip4/100.64.0.1"))
    assert utils.is_private_addr(Multiaddr("/ip4/169.254.0.1"))
    assert utils.is_private_addr(Multiaddr("/ip6/::1"))
    assert utils.is_private_addr(Multiaddr("/ip6/fc00::1"))
    assert utils.is_private_addr(Multiaddr("/ip6/fe80::1"))
    assert not utils.is_private_addr(Multiaddr("/ip4/8.8.8.8"))


def test_is_public_addr():
    assert utils.is_public_addr(Multiaddr("/ip4/8.8.8.8/tcp/80"))
    assert not utils.is_public_addr(Multiaddr("/ip4/127.0.0.1"))
    assert not utils.is_public_addr(Multiaddr("/ip4/10.0.0.1"))
    assert not utils.is_public_addr(Multiaddr("/ip4/0.0.0.0"))


def test_is_nat64_ipv4_converted_ipv6_addr():
    assert utils.is_nat64_ipv4_converted_ipv6_addr(Multiaddr("/ip6/64:ff9b::192.168.1.1"))
    assert not utils.is_nat64_ipv4_converted_ipv6_addr(Multiaddr("/ip6/::1"))
    assert not utils.is_nat64_ipv4_converted_ipv6_addr(Multiaddr("/ip4/192.168.1.1"))


def test_non_ip_addresses():
    ma = Multiaddr("/unix/var/run/docker.sock")
    assert not utils.is_ip_loopback(ma)
    assert not utils.is_ip_unspecified(ma)
    assert not utils.is_ip6_link_local(ma)
    assert not utils.is_private_addr(ma)
    assert not utils.is_public_addr(ma)
    assert not utils.is_nat64_ipv4_converted_ipv6_addr(ma)
