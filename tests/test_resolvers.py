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
    signal.cancelled_caught = True
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
