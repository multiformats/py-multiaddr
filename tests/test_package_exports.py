import multiaddr

EXPECTED_EXPORTS = {
    "Action",
    "Filters",
    "PROTOCOLS",
    "P_DNS",
    "P_DNS4",
    "P_DNS6",
    "P_DNSADDR",
    "P_IP4",
    "P_IP6",
    "P_P2P",
    "P_TCP",
    "P_UDP",
    "REGISTRY",
    "IP4_LOOPBACK",
    "IP4_UNSPECIFIED",
    "IP6_LOOPBACK",
    "IP6_UNSPECIFIED",
    "PRIVATE4",
    "PRIVATE6",
    "BinaryParseError",
    "Multiaddr",
    "ParseError",
    "Protocol",
    "ProtocolExistsError",
    "ProtocolLookupError",
    "ProtocolNotFoundError",
    "ProtocolRegistryLocked",
    "RecursionLimitError",
    "ResolutionError",
    "StringParseError",
    "get_multiaddr_options",
    "get_network_addrs",
    "get_thin_waist_addresses",
    "from_net_addr",
    "to_net_addr",
    "is_ip6_link_local",
    "is_ip_loopback",
    "is_ip_unspecified",
    "is_link_local_ip",
    "is_nat64_ipv4_converted_ipv6_addr",
    "is_private_addr",
    "is_public_addr",
    "is_thin_waist",
    "is_wildcard",
    "protocol_with_code",
    "protocol_with_name",
}


def test_all_matches_expected_exports():
    assert set(multiaddr.__all__) == EXPECTED_EXPORTS


def test_top_level_imports():
    from multiaddr import (  # noqa: F401
        P_TCP,
        P_UDP,
        REGISTRY,
        Multiaddr,
        Protocol,
        StringParseError,
        get_thin_waist_addresses,
        is_ip_loopback,
        is_private_addr,
        protocol_with_name,
    )

    assert protocol_with_name("tcp").code == P_TCP
    assert isinstance(Multiaddr("/ip4/127.0.0.1/tcp/80"), Multiaddr)
    assert get_thin_waist_addresses is not None
    assert REGISTRY is not None
    assert issubclass(StringParseError, Exception)
    assert is_ip_loopback(Multiaddr("/ip4/127.0.0.1"))
    assert is_private_addr(Multiaddr("/ip4/192.168.1.1"))
