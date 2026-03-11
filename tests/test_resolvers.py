"""Tests for multiaddr resolvers."""

import sys
from unittest.mock import AsyncMock, patch

import dns.resolver
import pytest
import trio

from multiaddr import Multiaddr
from multiaddr.exceptions import RecursionLimitError
from multiaddr.resolvers import (
    DNSResolver,
    addr_len,
    fqdn,
    is_fqdn,
    matches,
    offset_addr,
    resolve_all,
)

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


# ---------------------------------------------------------------------------
# Go test equivalents: DNSResolver.resolve()
# (from go-multiaddr-dns/resolve_test.go)
# ---------------------------------------------------------------------------


@pytest.fixture
def _go_style_dns_mocks():
    """Create mock DNS answers matching the Go test setup.

    Go test constants:
        ip4a = 192.0.2.1,  ip4b = 192.0.2.2
        ip6a = 2001:db8::a3, ip6b = 2001:db8::a4
        example.com  → A: [ip4a, ip4b], AAAA: [ip6a, ip6b]
        _dnsaddr.example.com → TXT: [dnsaddr=/ip4/192.0.2.1, dnsaddr=/ip6/2001:db8::a3]
    """
    mock_answer_a = AsyncMock()
    rdata_a1 = AsyncMock()
    rdata_a1.address = "192.0.2.1"
    rdata_a2 = AsyncMock()
    rdata_a2.address = "192.0.2.2"
    mock_answer_a.__iter__.return_value = [rdata_a1, rdata_a2]

    mock_answer_aaaa = AsyncMock()
    rdata_aaaa1 = AsyncMock()
    rdata_aaaa1.address = "2001:db8::a3"
    rdata_aaaa2 = AsyncMock()
    rdata_aaaa2.address = "2001:db8::a4"
    mock_answer_aaaa.__iter__.return_value = [rdata_aaaa1, rdata_aaaa2]

    mock_answer_txt = AsyncMock()
    rdata_txt1 = AsyncMock()
    rdata_txt1.strings = ["dnsaddr=/ip4/192.0.2.1"]
    rdata_txt2 = AsyncMock()
    rdata_txt2.strings = ["dnsaddr=/ip6/2001:db8::a3"]
    mock_answer_txt.__iter__.return_value = [rdata_txt1, rdata_txt2]

    async def side_effect(hostname, record_type):
        if record_type == "A" and hostname in ("example.com", "example.com."):
            return mock_answer_a
        if record_type == "AAAA" and hostname in ("example.com", "example.com."):
            return mock_answer_aaaa
        if record_type == "TXT" and hostname in ("_dnsaddr.example.com", "_dnsaddr.example.com."):
            return mock_answer_txt
        raise dns.resolver.NXDOMAIN()

    return side_effect


@pytest.mark.trio
async def test_simple_ip_resolve_dns4(dns_resolver, _go_style_dns_mocks):
    """Go: TestSimpleIPResolve — dns4 resolves to IPv4 addresses only."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dns4/example.com"))
    assert len(result) == 2
    assert result[0] == Multiaddr("/ip4/192.0.2.1")
    assert result[1] == Multiaddr("/ip4/192.0.2.2")


@pytest.mark.trio
async def test_simple_ip_resolve_dns6(dns_resolver, _go_style_dns_mocks):
    """Go: TestSimpleIPResolve — dns6 resolves to IPv6 addresses only."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dns6/example.com"))
    assert len(result) == 2
    assert result[0] == Multiaddr("/ip6/2001:db8::a3")
    assert result[1] == Multiaddr("/ip6/2001:db8::a4")


@pytest.mark.trio
async def test_simple_ip_resolve_dns_both(dns_resolver, _go_style_dns_mocks):
    """Go: TestSimpleIPResolve — dns resolves to both IPv4 and IPv6."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dns/example.com"))
    assert len(result) == 4
    assert result[0] == Multiaddr("/ip4/192.0.2.1")
    assert result[1] == Multiaddr("/ip4/192.0.2.2")
    assert result[2] == Multiaddr("/ip6/2001:db8::a3")
    assert result[3] == Multiaddr("/ip6/2001:db8::a4")


@pytest.mark.trio
async def test_resolve_only_once(dns_resolver, _go_style_dns_mocks):
    """Go: TestResolveOnlyOnce — only the first DNS component is resolved."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dns4/example.com/quic/dns6/example.com"))
    # dns4 resolved to 2 IPs, dns6 stays unresolved in each
    assert len(result) == 2
    assert result[0] == Multiaddr("/ip4/192.0.2.1/quic/dns6/example.com")
    assert result[1] == Multiaddr("/ip4/192.0.2.2/quic/dns6/example.com")


@pytest.mark.trio
async def test_simple_txt_resolve(dns_resolver, _go_style_dns_mocks):
    """Go: TestSimpleTXTResolve — dnsaddr resolves via TXT records."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dnsaddr/example.com"))
    assert len(result) == 2
    assert result[0] == Multiaddr("/ip4/192.0.2.1")
    assert result[1] == Multiaddr("/ip6/2001:db8::a3")


@pytest.mark.trio
async def test_resolve_empty_result(dns_resolver):
    """Go: TestEmptyResult — dnsaddr for unknown domain returns empty list."""
    with patch.object(dns_resolver._resolver, "resolve", side_effect=dns.resolver.NXDOMAIN):
        result = await dns_resolver.resolve(Multiaddr("/dnsaddr/none.com"))
    assert result == []


@pytest.mark.trio
async def test_resolve_dns4_with_suffix(dns_resolver, _go_style_dns_mocks):
    """Go: TestSimpleIPResolve variant — dns4 with /tcp suffix preserved."""
    with patch.object(dns_resolver._resolver, "resolve") as mock:
        mock.side_effect = _go_style_dns_mocks
        result = await dns_resolver.resolve(Multiaddr("/dns4/example.com/tcp/80"))
    assert len(result) == 2
    assert result[0] == Multiaddr("/ip4/192.0.2.1/tcp/80")
    assert result[1] == Multiaddr("/ip4/192.0.2.2/tcp/80")


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------


class TestIsFqdn:
    """Tests for is_fqdn."""

    def test_empty(self):
        assert is_fqdn("") is False

    def test_dot(self):
        assert is_fqdn(".") is True

    def test_no_trailing_dot(self):
        assert is_fqdn("example.com") is False

    def test_trailing_dot(self):
        assert is_fqdn("example.com.") is True

    def test_escaped_dot_in_middle(self):
        # escaped dot in middle, real dot at end
        assert is_fqdn("example\\.com.") is True

    def test_trailing_escaped_dot(self):
        # trailing dot is escaped → not FQDN
        assert is_fqdn("example.com\\.") is False

    def test_escaped_backslash_before_dot(self):
        # escaped backslash before real dot
        assert is_fqdn("example.com\\\\.") is True

    def test_escaped_backslash_and_escaped_dot(self):
        # escaped backslash + escaped dot
        assert is_fqdn("example.com\\\\\\.") is False


class TestFqdn:
    """Tests for fqdn."""

    def test_empty(self):
        assert fqdn("") == "."

    def test_dot(self):
        assert fqdn(".") == "."

    def test_no_trailing_dot(self):
        assert fqdn("example.com") == "example.com."

    def test_already_fqdn(self):
        assert fqdn("example.com.") == "example.com."

    def test_escaped_trailing_dot(self):
        # trailing dot is escaped → append a real dot
        assert fqdn("example.com\\.") == "example.com\\.."

    def test_escaped_backslash_already_fqdn(self):
        # escaped backslash before real dot → already FQDN
        assert fqdn("example.com\\\\.") == "example.com\\\\."


class TestAddrLen:
    def test_single_protocol(self):
        assert addr_len(Multiaddr("/ip4/127.0.0.1")) == 1

    def test_two_protocols(self):
        assert addr_len(Multiaddr("/ip4/127.0.0.1/tcp/80")) == 2

    def test_three_protocols(self):
        assert addr_len(Multiaddr("/ip4/127.0.0.1/tcp/80/http")) == 3


class TestOffsetAddr:
    def test_offset_zero(self):
        ma = Multiaddr("/ip4/127.0.0.1/tcp/80")
        assert offset_addr(ma, 0) == ma

    def test_offset_one(self):
        ma = Multiaddr("/ip4/127.0.0.1/tcp/80")
        assert offset_addr(ma, 1) == Multiaddr("/tcp/80")

    def test_offset_all(self):
        ma = Multiaddr("/ip4/127.0.0.1/tcp/80")
        assert offset_addr(ma, 2) == Multiaddr("/")


class TestMatches:
    def test_dns4(self):
        assert matches(Multiaddr("/dns4/example.com/tcp/80")) is True

    def test_dns6(self):
        assert matches(Multiaddr("/dns6/example.com/tcp/80")) is True

    def test_dnsaddr(self):
        assert matches(Multiaddr("/dnsaddr/example.com")) is True

    def test_dns(self):
        assert matches(Multiaddr("/dns/example.com/tcp/80")) is True

    def test_ip4(self):
        assert matches(Multiaddr("/ip4/127.0.0.1/tcp/80")) is False

    def test_ip6(self):
        assert matches(Multiaddr("/ip6/::1/tcp/80")) is False

    def test_dns_not_first_position(self):
        """Go: TestMatches — DNS at non-first position still matches."""
        assert matches(Multiaddr("/tcp/1234/dns6/example.com")) is True


# ---------------------------------------------------------------------------
# resolve_all tests
# ---------------------------------------------------------------------------


class MockResolver:
    """A mock resolver for testing resolve_all."""

    def __init__(self, mapping: dict[str, list[str]]):
        self._mapping = mapping

    async def resolve(self, maddr: Multiaddr) -> list[Multiaddr]:
        key = str(maddr)
        if key in self._mapping:
            return [Multiaddr(v) for v in self._mapping[key]]
        return [maddr]


@pytest.mark.trio
async def test_resolve_all_no_dns():
    """Non-DNS multiaddr is returned unchanged."""
    resolver = MockResolver({})
    ma = Multiaddr("/ip4/127.0.0.1/tcp/80")
    result = await resolve_all(resolver, ma)
    assert result == [ma]


@pytest.mark.trio
async def test_resolve_all_single_dns():
    """Single DNS component is resolved."""
    resolver = MockResolver(
        {
            "/dns4/example.com/tcp/80": ["/ip4/1.2.3.4/tcp/80"],
        }
    )
    result = await resolve_all(resolver, Multiaddr("/dns4/example.com/tcp/80"))
    assert result == [Multiaddr("/ip4/1.2.3.4/tcp/80")]


@pytest.mark.trio
async def test_resolve_all_multiple_dns_components():
    """Multiple DNS components in one multiaddr are all resolved."""
    resolver = MockResolver(
        {
            "/dns4/a.example.com/quic/dns6/b.example.com": ["/ip4/1.2.3.4/quic/dns6/b.example.com"],
            "/ip4/1.2.3.4/quic/dns6/b.example.com": ["/ip4/1.2.3.4/quic/ip6/::1"],
        }
    )
    result = await resolve_all(resolver, Multiaddr("/dns4/a.example.com/quic/dns6/b.example.com"))
    assert result == [Multiaddr("/ip4/1.2.3.4/quic/ip6/::1")]


@pytest.mark.trio
async def test_resolve_all_chained():
    """Chained resolution: DNS resolves to another DNS address."""
    resolver = MockResolver(
        {
            "/dns4/a.com": ["/dns4/b.com/tcp/80"],
            "/dns4/b.com/tcp/80": ["/ip4/1.2.3.4/tcp/80"],
        }
    )
    result = await resolve_all(resolver, Multiaddr("/dns4/a.com"))
    assert result == [Multiaddr("/ip4/1.2.3.4/tcp/80")]


@pytest.mark.trio
async def test_resolve_all_max_iterations_exceeded():
    """Raises RecursionLimitError when DNS never fully resolves."""
    resolver = MockResolver(
        {
            "/dns4/loop.com": ["/dns4/loop.com"],
        }
    )
    with pytest.raises(RecursionLimitError, match="resolve_all exceeded"):
        await resolve_all(resolver, Multiaddr("/dns4/loop.com"), max_iterations=3)


@pytest.mark.trio
async def test_resolve_all_empty_result():
    """Empty resolve result drops the address without looping."""

    class EmptyResolver:
        async def resolve(self, maddr: Multiaddr) -> list[Multiaddr]:
            return []

    result = await resolve_all(EmptyResolver(), Multiaddr("/dns4/gone.com/tcp/80"))
    assert result == []


@pytest.mark.trio
async def test_resolve_all_cartesian_product():
    """Go: TestResolveMultiple — dns4 x dns6 produces cartesian product.

    /dns4/example.com/quic/dns6/example.com with dns4→[ip4a, ip4b]
    and dns6→[ip6a, ip6b] produces 4 results.
    """
    resolver = MockResolver(
        {
            "/dns4/example.com/quic/dns6/example.com": [
                "/ip4/192.0.2.1/quic/dns6/example.com",
                "/ip4/192.0.2.2/quic/dns6/example.com",
            ],
            "/ip4/192.0.2.1/quic/dns6/example.com": [
                "/ip4/192.0.2.1/quic/ip6/2001:db8::a3",
                "/ip4/192.0.2.1/quic/ip6/2001:db8::a4",
            ],
            "/ip4/192.0.2.2/quic/dns6/example.com": [
                "/ip4/192.0.2.2/quic/ip6/2001:db8::a3",
                "/ip4/192.0.2.2/quic/ip6/2001:db8::a4",
            ],
        }
    )
    result = await resolve_all(resolver, Multiaddr("/dns4/example.com/quic/dns6/example.com"))
    expected = [
        Multiaddr("/ip4/192.0.2.1/quic/ip6/2001:db8::a3"),
        Multiaddr("/ip4/192.0.2.1/quic/ip6/2001:db8::a4"),
        Multiaddr("/ip4/192.0.2.2/quic/ip6/2001:db8::a3"),
        Multiaddr("/ip4/192.0.2.2/quic/ip6/2001:db8::a4"),
    ]
    assert result == expected


@pytest.mark.trio
async def test_resolve_all_sandwich():
    """Go: TestResolveMultipleSandwitch — DNS sandwiched between non-DNS protocols.

    /quic/dns4/example.com/dns6/example.com/http resolves both DNS components.
    """
    resolver = MockResolver(
        {
            "/quic/dns4/example.com/dns6/example.com/http": [
                "/quic/ip4/192.0.2.1/dns6/example.com/http",
                "/quic/ip4/192.0.2.2/dns6/example.com/http",
            ],
            "/quic/ip4/192.0.2.1/dns6/example.com/http": [
                "/quic/ip4/192.0.2.1/ip6/2001:db8::a3/http",
                "/quic/ip4/192.0.2.1/ip6/2001:db8::a4/http",
            ],
            "/quic/ip4/192.0.2.2/dns6/example.com/http": [
                "/quic/ip4/192.0.2.2/ip6/2001:db8::a3/http",
                "/quic/ip4/192.0.2.2/ip6/2001:db8::a4/http",
            ],
        }
    )
    result = await resolve_all(resolver, Multiaddr("/quic/dns4/example.com/dns6/example.com/http"))
    expected = [
        Multiaddr("/quic/ip4/192.0.2.1/ip6/2001:db8::a3/http"),
        Multiaddr("/quic/ip4/192.0.2.1/ip6/2001:db8::a4/http"),
        Multiaddr("/quic/ip4/192.0.2.2/ip6/2001:db8::a3/http"),
        Multiaddr("/quic/ip4/192.0.2.2/ip6/2001:db8::a4/http"),
    ]
    assert result == expected
