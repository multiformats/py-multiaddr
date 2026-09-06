import ipaddress

from multiaddr import Action, Filters, Multiaddr


def test_default_accept_allows_all():
    filters = Filters()
    assert filters.addr_blocked(Multiaddr("/ip4/1.2.3.4/tcp/80")) is False


def test_default_deny_blocks_all():
    filters = Filters(default_action=Action.DENY)
    assert filters.addr_blocked(Multiaddr("/ip4/1.2.3.4/tcp/80")) is True


def test_deny_network_blocks_matching_ip():
    filters = Filters()
    filters.add_filter("10.0.0.0/8", Action.DENY)
    assert filters.addr_blocked(Multiaddr("/ip4/10.1.2.3/tcp/80")) is True
    assert filters.addr_blocked(Multiaddr("/ip4/11.0.0.1/tcp/80")) is False


def test_last_matching_filter_wins():
    filters = Filters(default_action=Action.DENY)
    filters.add_filter("10.0.0.0/8", Action.ACCEPT)
    filters.add_filter("10.0.0.0/16", Action.DENY)
    assert filters.addr_blocked(Multiaddr("/ip4/10.0.1.1/tcp/1")) is True
    assert filters.addr_blocked(Multiaddr("/ip4/10.1.0.1/tcp/1")) is False


def test_remove_literal():
    filters = Filters()
    filters.add_filter("192.168.0.0/16", Action.DENY)
    assert filters.remove_literal("192.168.0.0/16") is True
    assert filters.addr_blocked(Multiaddr("/ip4/192.168.1.1/tcp/80")) is False
    assert filters.remove_literal("192.168.0.0/16") is False


def test_add_filter_replaces_same_network():
    filters = Filters()
    filters.add_filter(ipaddress.ip_network("127.0.0.0/8"), Action.DENY)
    filters.add_filter("127.0.0.0/8", Action.ACCEPT)
    assert filters.addr_blocked(Multiaddr("/ip4/127.0.0.1/tcp/80")) is False


def test_non_ip_uses_default_action():
    filters = Filters(default_action=Action.DENY)
    assert filters.addr_blocked(Multiaddr("/unix/tmp/socket")) is True


def test_ipv6_filter():
    filters = Filters()
    filters.add_filter("fe80::/10", Action.DENY)
    assert filters.addr_blocked(Multiaddr("/ip6/fe80::1/tcp/80")) is True
    assert filters.addr_blocked(Multiaddr("/ip6/2001:db8::1/tcp/80")) is False
