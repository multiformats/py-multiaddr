import multiaddr

EXPECTED_EXPORTS = {
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
    "is_link_local_ip",
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
        protocol_with_name,
    )

    assert protocol_with_name("tcp").code == P_TCP
    assert isinstance(Multiaddr("/ip4/127.0.0.1/tcp/80"), Multiaddr)
    assert get_thin_waist_addresses is not None
    assert REGISTRY is not None
    assert issubclass(StringParseError, Exception)
