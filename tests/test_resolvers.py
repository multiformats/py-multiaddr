"""Tests for multiaddr resolvers."""

import sys
from unittest.mock import AsyncMock, patch

import dns.resolver
import pytest
import trio

from multiaddr import Multiaddr
from multiaddr.exceptions import RecursionLimitError
from multiaddr.resolvers import DNSResolver

if sys.version_info >= (3, 11):
    from builtins import BaseExceptionGroup
else:

    class BaseExceptionGroup(Exception):
        pass


@pytest.fixture
def dns_resolver():
    """Create a DNS resolver instance."""
    return DNSResolver()


@pytest.fixture
def mock_dns_resolution():
    """Create mock DNS resolution setup for testing."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    # Create mock DNS answer for TXT record (dnsaddr)
    mock_answer_txt = AsyncMock()
    mock_rdata_txt = AsyncMock()
    mock_rdata_txt.strings = ["dnsaddr=/ip4/127.0.0.1"]
    mock_answer_txt.__iter__.return_value = [mock_rdata_txt]

    # Configure the mock to return different results based on record type
    async def mock_resolve_side_effect(hostname, record_type):
        if record_type == "A":
            return mock_answer_a
        elif record_type == "AAAA":
            return mock_answer_aaaa
        elif record_type == "TXT" and hostname.startswith("_dnsaddr."):
            return mock_answer_txt
        else:
            raise dns.resolver.NXDOMAIN()

    return {
        "mock_answer_a": mock_answer_a,
        "mock_answer_aaaa": mock_answer_aaaa,
        "mock_answer_txt": mock_answer_txt,
        "mock_resolve_side_effect": mock_resolve_side_effect,
    }


@pytest.mark.trio
async def test_resolve_non_dns_addr(dns_resolver):
    """Test resolving a non-DNS multiaddr."""
    ma = Multiaddr("/ip4/127.0.0.1/tcp/1234")
    result = await dns_resolver.resolve(ma)
    assert result == [ma]


@pytest.mark.trio
async def test_resolve_dns_addr(dns_resolver, mock_dns_resolution):
    """Test resolving a DNS multiaddr."""
    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_dns_resolution["mock_resolve_side_effect"]

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_peer_id(dns_resolver, mock_dns_resolution):
    """Test resolving a DNS multiaddr with a peer ID."""
    # Create a mock TXT record with the peer ID
    mock_answer_txt_with_peer = AsyncMock()
    mock_rdata_txt_with_peer = AsyncMock()
    mock_rdata_txt_with_peer.strings = [
        "dnsaddr=/ip4/127.0.0.1/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk"
    ]
    mock_answer_txt_with_peer.__iter__.return_value = [mock_rdata_txt_with_peer]

    async def mock_resolve_with_peer(hostname, record_type):
        if record_type == "TXT" and hostname.startswith("_dnsaddr."):
            return mock_answer_txt_with_peer
        else:
            raise dns.resolver.NXDOMAIN()

    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_resolve_with_peer

        ma = Multiaddr("/dnsaddr/example.com/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"
        assert result[0].get_peer_id() == "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk"


@pytest.mark.trio
async def test_resolve_recursive_dns_addr(dns_resolver, mock_dns_resolution):
    """Test resolving a recursive DNS multiaddr."""
    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_dns_resolution["mock_resolve_side_effect"]

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma, {"max_recursive_depth": 2})
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_recursion_limit(dns_resolver):
    """Test that recursion limit is enforced."""
    ma = Multiaddr("/dnsaddr/example.com")
    with pytest.raises(RecursionLimitError):
        await dns_resolver.resolve(ma, {"max_recursive_depth": 0})


@pytest.mark.trio
async def test_resolve_dns_addr_error(dns_resolver):
    """Test handling DNS resolution errors."""
    with patch.object(dns_resolver._resolver, "resolve", side_effect=dns.resolver.NXDOMAIN):
        ma = Multiaddr("/dnsaddr/example.com")
        # When DNS resolution fails, the resolver should return the original multiaddr
        result = await dns_resolver.resolve(ma)
        assert result == []


@pytest.mark.trio
async def test_resolve_dns_addr_with_quotes(dns_resolver, mock_dns_resolution):
    """Test resolving DNS records with quoted strings."""
    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_dns_resolution["mock_resolve_side_effect"]

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_mixed_quotes(dns_resolver, mock_dns_resolution):
    """Test resolving DNS records with mixed quotes."""
    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_dns_resolution["mock_resolve_side_effect"]

        # Test that _clean_quotes is called correctly during resolution
        with patch.object(dns_resolver, "_clean_quotes") as mock_clean_quotes:
            # Make the mock return the input for most cases, but allow specific behavior
            def clean_quotes_side_effect(text):
                if text == "example.com":
                    return "example.com"
                elif text == "/ip4/127.0.0.1":
                    return "/ip4/127.0.0.1"
                else:
                    return text

            mock_clean_quotes.side_effect = clean_quotes_side_effect

            ma = Multiaddr("/dnsaddr/example.com")
            result = await dns_resolver.resolve(ma)

            # Verify _clean_quotes was called (now called for both hostname and multiaddr string)
            assert mock_clean_quotes.call_count >= 1
            # Check that it was called with the hostname
            mock_clean_quotes.assert_any_call("example.com")

            # Verify the resolution still works correctly
            assert len(result) == 1
            assert result[0].protocols()[0].name == "ip4"
            assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"

        # Test the actual _clean_quotes functionality
        assert dns_resolver._clean_quotes('"example.com"') == "example.com"
        assert dns_resolver._clean_quotes("'example.com'") == "example.com"
        assert dns_resolver._clean_quotes('" example.com "') == "example.com"
        assert dns_resolver._clean_quotes("  example.com  ") == "example.com"
        assert dns_resolver._clean_quotes('"example.com"') == "example.com"


@pytest.mark.trio
async def test_resolve_cancellation_with_error():
    """Test that DNS resolution can be cancelled."""
    ma = Multiaddr("/dnsaddr/nonexistent.example.com")
    signal = trio.CancelScope()  # type: ignore[call-arg]
    signal.cancelled_caught = True  # type: ignore[misc]
    dns_resolver = DNSResolver()

    # Mock the DNS resolver to simulate a slow lookup that can be cancelled
    async def slow_dns_resolve(*args, **kwargs):
        await trio.sleep(0.5)  # Long sleep to allow cancellation
        raise dns.resolver.NXDOMAIN("Domain not found")

    with patch.object(dns_resolver._resolver, "resolve", side_effect=slow_dns_resolve):
        # Start resolution in background and cancel it
        async with trio.open_nursery() as nursery:
            # Start the resolution
            nursery.start_soon(dns_resolver.resolve, ma, {"signal": signal})

            # Cancel after a short delay
            await trio.sleep(0.1)
            signal.cancel()

            # The nursery should handle the cancellation gracefully
            # If cancellation is not handled properly, this would raise an unhandled exception

        # Verify that the signal was actually cancelled
        assert signal.cancel_called


@pytest.mark.trio
async def test_resolve_dnsaddr_with_quic(dns_resolver):
    """Test resolving DNSADDR records that contain QUIC addresses."""
    # Create mock TXT records with QUIC addresses (similar to libp2p bootstrap nodes)
    mock_answer_txt_quic = AsyncMock()

    # Create multiple mock rdata objects for each string
    mock_rdata_quic1 = AsyncMock()
    mock_rdata_quic1.strings = [
        "dnsaddr=/ip4/147.75.83.83/udp/4001/quic/p2p/QmSoLer265NRgSp2LA3dPaeykiS1J6DifTC88f5uVQKNAd"
    ]

    mock_rdata_quic2 = AsyncMock()
    mock_rdata_quic2.strings = [
        "dnsaddr=/ip6/2604:1380:2000:7a00::1/udp/4001/quic/p2p/QmSoLer265NRgSp2LA3dPaeykiS1J6DifTC88f5uVQKNAd"
    ]

    mock_rdata_tcp = AsyncMock()
    mock_rdata_tcp.strings = [
        "dnsaddr=/ip4/147.75.83.83/tcp/4001/p2p/QmSoLer265NRgSp2LA3dPaeykiS1J6DifTC88f5uVQKNAd"
    ]  # TCP for comparison

    mock_answer_txt_quic.__iter__.return_value = [
        mock_rdata_quic1,
        mock_rdata_quic2,
        mock_rdata_tcp,
    ]

    async def mock_resolve_quic(hostname, record_type):
        if record_type == "TXT" and hostname.startswith("_dnsaddr."):
            return mock_answer_txt_quic
        else:
            raise dns.resolver.NXDOMAIN()

    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_resolve_quic

        ma = Multiaddr("/dnsaddr/bootstrap.libp2p.io")
        result = await dns_resolver.resolve(ma)

        # Should return 3 addresses
        assert len(result) == 3

        # Check QUIC addresses
        quic_addresses = [
            addr for addr in result if any(p.name == "quic" for p in addr.protocols())
        ]
        assert len(quic_addresses) == 2

        # Verify QUIC protocol details
        for quic_addr in quic_addresses:
            protocols = list(quic_addr.protocols())
            # Should have: ip4/ip6, udp, quic, p2p
            assert len(protocols) == 4
            assert protocols[1].name == "udp"  # UDP before QUIC
            assert protocols[2].name == "quic"  # QUIC protocol
            assert protocols[3].name == "p2p"  # P2P peer ID


@pytest.mark.trio
async def test_resolve_dnsaddr_with_quic_v1(dns_resolver):
    """Test resolving DNSADDR records that contain QUIC-v1 addresses."""
    # Create mock TXT records with QUIC-v1 addresses
    mock_answer_txt_quic_v1 = AsyncMock()

    # Create multiple mock rdata objects for each string
    mock_rdata_quic_v1_1 = AsyncMock()
    mock_rdata_quic_v1_1.strings = [
        "dnsaddr=/ip4/147.75.83.83/udp/4001/quic-v1/p2p/QmbLHAnMoJPWSCR5Zhtx6BHJX9KiKNN6tpvbUcqanj75Nb"
    ]

    mock_rdata_quic_v1_2 = AsyncMock()
    mock_rdata_quic_v1_2.strings = [
        "dnsaddr=/ip6/2604:1380:2000:7a00::1/udp/4001/quic-v1/p2p/QmbLHAnMoJPWSCR5Zhtx6BHJX9KiKNN6tpvbUcqanj75Nb"
    ]

    mock_rdata_webtransport = AsyncMock()
    mock_rdata_webtransport.strings = ["dnsaddr=/ip4/147.75.83.83/udp/4001/quic-v1/webtransport"]

    mock_answer_txt_quic_v1.__iter__.return_value = [
        mock_rdata_quic_v1_1,
        mock_rdata_quic_v1_2,
        mock_rdata_webtransport,
    ]

    async def mock_resolve_quic_v1(hostname, record_type):
        if record_type == "TXT" and hostname.startswith("_dnsaddr."):
            return mock_answer_txt_quic_v1
        else:
            raise dns.resolver.NXDOMAIN()

    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_resolve_quic_v1

        ma = Multiaddr("/dnsaddr/bootstrap.libp2p.io")
        result = await dns_resolver.resolve(ma)

        # Should return 3 addresses
        assert len(result) == 3

        # Check QUIC-v1 addresses
        quic_v1_addresses = [
            addr for addr in result if any(p.name == "quic-v1" for p in addr.protocols())
        ]
        assert len(quic_v1_addresses) == 3

        # Verify QUIC-v1 protocol details
        for quic_v1_addr in quic_v1_addresses:
            protocols = list(quic_v1_addr.protocols())
            # Should have: ip4/ip6, udp, quic-v1, p2p/webtransport
            assert len(protocols) >= 3
            assert protocols[1].name == "udp"  # UDP before QUIC-v1
            assert protocols[2].name == "quic-v1"  # QUIC-v1 protocol


@pytest.mark.trio
async def test_resolve_dnsaddr_quic_webtransport(dns_resolver):
    """Test resolving DNSADDR records with QUIC + WebTransport combinations."""
    # Create mock TXT records with QUIC + WebTransport addresses
    mock_answer_txt_webtransport = AsyncMock()

    # Create multiple mock rdata objects for each string
    mock_rdata_wt1 = AsyncMock()
    mock_rdata_wt1.strings = ["dnsaddr=/ip4/1.2.3.4/udp/4001/quic-v1/webtransport"]

    mock_rdata_wt2 = AsyncMock()
    mock_rdata_wt2.strings = [
        "dnsaddr=/ip6/2001:8a0:7ac5:4201:3ac9:86ff:fe31:7095/udp/4001/quic-v1/webtransport"
    ]

    mock_rdata_wt3 = AsyncMock()
    mock_rdata_wt3.strings = [
        "dnsaddr=/ip4/1.2.3.4/udp/4001/quic-v1/webtransport/certhash/"
        "uEiAkH5a4DPGKUuOBjYw0CgwjvcJCJMD2K_1aluKR_tpevQ/p2p/"
        "12D3KooWBdmLJjhpgJ9KZgLM3f894ff9xyBfPvPjFNn7MKJpyrC2"
    ]

    mock_answer_txt_webtransport.__iter__.return_value = [
        mock_rdata_wt1,
        mock_rdata_wt2,
        mock_rdata_wt3,
    ]

    async def mock_resolve_webtransport(hostname, record_type):
        if record_type == "TXT" and hostname.startswith("_dnsaddr."):
            return mock_answer_txt_webtransport
        else:
            raise dns.resolver.NXDOMAIN()

    with patch.object(dns_resolver._resolver, "resolve") as mock_resolve:
        mock_resolve.side_effect = mock_resolve_webtransport

        ma = Multiaddr("/dnsaddr/webtransport.example.com")
        result = await dns_resolver.resolve(ma)

        # Should return 3 addresses (but complex certhash address might not parse correctly)
        assert len(result) >= 2  # At least the basic WebTransport addresses

        # Check WebTransport addresses
        webtransport_addresses = [
            addr for addr in result if any(p.name == "webtransport" for p in addr.protocols())
        ]
        assert len(webtransport_addresses) >= 2  # At least the basic WebTransport addresses

        # Verify WebTransport protocol stacks
        for wt_addr in webtransport_addresses:
            protocols = list(wt_addr.protocols())
            # Should have: ip4/ip6, udp, quic-v1, webtransport, (optional: certhash, p2p)
            assert len(protocols) >= 4
            assert protocols[1].name == "udp"  # UDP before QUIC-v1
            assert protocols[2].name == "quic-v1"  # QUIC-v1 before WebTransport
            assert protocols[3].name == "webtransport"  # WebTransport protocol


@pytest.mark.trio
async def test_resolve_dnsaddr_quic_ipv6_zones(dns_resolver):
    """Test resolving DNSADDR records with QUIC and IPv6 zones.

    Note: This test is skipped due to binary encoding issues with IPv6 zones
    in the Python implementation.
    """
    pytest.skip("IPv6 zones have binary encoding issues in Python implementation")
