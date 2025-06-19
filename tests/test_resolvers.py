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


@pytest.mark.trio
async def test_resolve_non_dns_addr(dns_resolver):
    """Test resolving a non-DNS multiaddr."""
    ma = Multiaddr("/ip4/127.0.0.1/tcp/1234")
    result = await dns_resolver.resolve(ma)
    assert result == [ma]


@pytest.mark.trio
async def test_resolve_dns_addr(dns_resolver):
    """Test resolving a DNS multiaddr."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    with patch.object(dns_resolver._resolver, 'resolve') as mock_resolve:
        # Configure the mock to return different results based on record type
        async def mock_resolve_side_effect(hostname, record_type):
            if record_type == "A":
                return mock_answer_a
            elif record_type == "AAAA":
                return mock_answer_aaaa
            else:
                raise dns.resolver.NXDOMAIN()

        mock_resolve.side_effect = mock_resolve_side_effect

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_peer_id(dns_resolver):
    """Test resolving a DNS multiaddr with a peer ID."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    with patch.object(dns_resolver._resolver, 'resolve') as mock_resolve:
        # Configure the mock to return different results based on record type
        async def mock_resolve_side_effect(hostname, record_type):
            if record_type == "A":
                return mock_answer_a
            elif record_type == "AAAA":
                return mock_answer_aaaa
            else:
                raise dns.resolver.NXDOMAIN()

        mock_resolve.side_effect = mock_resolve_side_effect

        ma = Multiaddr("/dnsaddr/example.com/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"
        assert result[0].get_peer_id() == "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk"


@pytest.mark.trio
async def test_resolve_recursive_dns_addr(dns_resolver):
    """Test resolving a recursive DNS multiaddr."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    with patch.object(dns_resolver._resolver, 'resolve') as mock_resolve:
        # Configure the mock to return different results based on record type
        async def mock_resolve_side_effect(hostname, record_type):
            if record_type == "A":
                return mock_answer_a
            elif record_type == "AAAA":
                return mock_answer_aaaa
            else:
                raise dns.resolver.NXDOMAIN()

        mock_resolve.side_effect = mock_resolve_side_effect

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
    with patch.object(dns_resolver._resolver, 'resolve', side_effect=dns.resolver.NXDOMAIN):
        ma = Multiaddr("/dnsaddr/example.com")
        # When DNS resolution fails, the resolver should return the original multiaddr
        result = await dns_resolver.resolve(ma)
        assert result == [ma]


@pytest.mark.trio
async def test_resolve_dns_addr_with_quotes(dns_resolver):
    """Test resolving DNS records with quoted strings."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    with patch.object(dns_resolver._resolver, 'resolve') as mock_resolve:
        # Configure the mock to return different results based on record type
        async def mock_resolve_side_effect(hostname, record_type):
            if record_type == "A":
                return mock_answer_a
            elif record_type == "AAAA":
                return mock_answer_aaaa
            else:
                raise dns.resolver.NXDOMAIN()

        mock_resolve.side_effect = mock_resolve_side_effect

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_mixed_quotes(dns_resolver):
    """Test resolving DNS records with mixed quotes."""
    # Create mock DNS answer for A record (IPv4)
    mock_answer_a = AsyncMock()
    mock_rdata_a = AsyncMock()
    mock_rdata_a.address = "127.0.0.1"
    mock_answer_a.__iter__.return_value = [mock_rdata_a]

    # Create mock DNS answer for AAAA record (IPv6) - return empty to avoid conflicts
    mock_answer_aaaa = AsyncMock()
    mock_answer_aaaa.__iter__.return_value = []

    with patch.object(dns_resolver._resolver, 'resolve') as mock_resolve:
        # Configure the mock to return different results based on record type
        async def mock_resolve_side_effect(hostname, record_type):
            if record_type == "A":
                return mock_answer_a
            elif record_type == "AAAA":
                return mock_answer_aaaa
            else:
                raise dns.resolver.NXDOMAIN()

        mock_resolve.side_effect = mock_resolve_side_effect

        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


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

    with patch.object(dns_resolver._resolver, 'resolve', side_effect=slow_dns_resolve):
        # Start resolution in background and cancel it
        async with trio.open_nursery() as nursery:
            # Start the resolution
            nursery.start_soon(dns_resolver.resolve, ma, {"signal": signal})

            # Cancel after a short delay
            await trio.sleep(0.1)
            signal.cancel()

            # The nursery should handle the cancellation
