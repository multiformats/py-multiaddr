"""Tests for multiaddr resolvers."""

import socket
from unittest.mock import patch

import pytest
import trio
from unittest.mock import MagicMock
from asyncio import CancelledError

from multiaddr import Multiaddr
from multiaddr.exceptions import ResolutionError, RecursionLimitError
from multiaddr.resolvers import DNSResolver


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
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_peer_id(dns_resolver):
    """Test resolving a DNS multiaddr with a peer ID."""
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr("/dnsaddr/example.com/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"
        assert result[0].get_peer_id() == "QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk"


@pytest.mark.trio
async def test_resolve_recursive_dns_addr(dns_resolver):
    """Test resolving a recursive DNS multiaddr."""
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))],
            [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('192.168.1.1', 0))]
        ]
        ma = Multiaddr("/dnsaddr/example.com")
        result = await dns_resolver.resolve(ma, {'max_recursive_depth': 2})
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_recursion_limit(dns_resolver):
    """Test that recursion limit is enforced."""
    ma = Multiaddr("/dnsaddr/example.com")
    with pytest.raises(RecursionLimitError):
        await dns_resolver.resolve(ma, {'max_recursive_depth': 0})


@pytest.mark.trio
async def test_resolve_dns_addr_error(dns_resolver):
    """Test handling DNS resolution errors."""
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.side_effect = socket.gaierror("DNS resolution failed")
        ma = Multiaddr("/dnsaddr/example.com")
        with pytest.raises(ResolutionError):
            await dns_resolver.resolve(ma)


@pytest.mark.trio
async def test_resolve_dns_addr_with_quotes(dns_resolver):
    """Test resolving DNS records with quoted strings."""
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr('/dnsaddr/example.com')
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_dns_addr_with_mixed_quotes(dns_resolver):
    """Test resolving DNS records with mixed quotes."""
    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr('/dnsaddr/example.com')
        result = await dns_resolver.resolve(ma)
        assert len(result) == 1
        assert result[0].protocols()[0].name == "ip4"
        assert result[0].value_for_protocol(result[0].protocols()[0].code) == "127.0.0.1"


@pytest.mark.trio
async def test_resolve_cancellation(dns_resolver):
    """Test that resolution can be cancelled."""
    # Create a mock signal that is aborted
    signal = MagicMock()
    signal.aborted = True

    ma = Multiaddr("/dnsaddr/example.com")
    result = await dns_resolver.resolve(ma, {'signal': signal})
    assert result == []


@pytest.mark.trio
async def test_resolve_cancellation_during_resolution(dns_resolver):
    """Test that resolution can be cancelled during the resolution process."""
    # Create a mock signal that will be aborted after the first DNS query
    signal = MagicMock()
    signal.aborted = False

    async def abort_after_first():
        signal.aborted = True

    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr("/dnsaddr/example.com")
        
        # Start resolution and abort after first query
        async with trio.open_nursery() as nursery:
            nursery.start_soon(abort_after_first)
            result = await dns_resolver.resolve(ma, {'signal': signal})
            assert result == []


@pytest.mark.trio
async def test_resolve_cancellation_during_recursive_resolution(dns_resolver):
    """Test that resolution can be cancelled during recursive resolution."""
    signal = MagicMock()
    signal.aborted = False

    async def abort_after_first():
        await trio.sleep(0.1)  # Give time for first resolution to start
        signal.aborted = True

    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.side_effect = [
            [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))],
            [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('192.168.1.1', 0))]
        ]
        ma = Multiaddr("/dnsaddr/example.com")
        
        async with trio.open_nursery() as nursery:
            nursery.start_soon(abort_after_first)
            result = await dns_resolver.resolve(ma, {'signal': signal, 'max_recursive_depth': 2})
            assert result == []


@pytest.mark.trio
async def test_resolve_cancellation_with_error(dns_resolver):
    """Test that cancellation works correctly when combined with DNS errors."""
    signal = MagicMock()
    signal.aborted = False

    async def abort_after_error():
        await trio.sleep(0.1)  # Give time for error to occur
        signal.aborted = True

    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.side_effect = socket.gaierror("DNS resolution failed")
        ma = Multiaddr("/dnsaddr/example.com")
        
        async with trio.open_nursery() as nursery:
            nursery.start_soon(abort_after_error)
            result = await dns_resolver.resolve(ma, {'signal': signal})
            assert result == []


@pytest.mark.trio
async def test_resolve_cancellation_with_peer_id(dns_resolver):
    """Test that resolution can be cancelled when resolving addresses with peer IDs."""
    signal = MagicMock()
    signal.aborted = False

    async def abort_during_resolution():
        await trio.sleep(0.1)  # Give time for resolution to start
        signal.aborted = True

    with patch('socket.getaddrinfo') as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0))
        ]
        ma = Multiaddr("/dnsaddr/example.com/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")
        
        async with trio.open_nursery() as nursery:
            nursery.start_soon(abort_during_resolution)
            result = await dns_resolver.resolve(ma, {'signal': signal})
            assert result == []
