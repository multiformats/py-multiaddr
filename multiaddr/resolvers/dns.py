"""DNS resolver implementation for multiaddr."""

import re
from typing import Optional, cast

import base58
import dns.asyncresolver
import dns.rdataclass
import dns.rdtypes.IN.A
import dns.rdtypes.IN.AAAA
import dns.resolver
import trio

from ..exceptions import RecursionLimitError, ResolutionError
from ..multiaddr import Multiaddr
from ..protocols import P_DNS, P_DNS4, P_DNS6, P_DNSADDR, Protocol
from .base import Resolver


class DNSResolver(Resolver):
    """DNS resolver for multiaddr."""

    MAX_RECURSIVE_DEPTH = 32
    DEFAULT_TIMEOUT = 5.0  # 5 seconds timeout

    def __init__(self):
        """Initialize the DNS resolver."""
        self._resolver = dns.asyncresolver.Resolver()

    async def resolve(
        self, maddr: "Multiaddr", options: Optional[dict] = None
    ) -> list["Multiaddr"]:
        """Resolve a DNS multiaddr to its actual addresses.

        Args:
            maddr: The multiaddr to resolve
            options: Optional configuration options

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            RecursionLimitError: If maximum recursive depth is reached
            trio.Cancelled: If the operation is cancelled
        """
        protocols: list[Protocol] = list(maddr.protocols())
        if not protocols:
            raise ResolutionError("empty multiaddr")

        first_protocol = protocols[0]
        if first_protocol.code not in (P_DNS, P_DNS4, P_DNS6, P_DNSADDR):
            return [maddr]

        # Get the hostname and clean it of quotes
        hostname = maddr.value_for_protocol(first_protocol.code)
        if not hostname:
            return [maddr]

        # Remove quotes from hostname
        hostname = self._clean_quotes(hostname)

        # Get max recursive depth from options or use default
        max_depth = (
            options.get("max_recursive_depth", self.MAX_RECURSIVE_DEPTH)
            if options else self.MAX_RECURSIVE_DEPTH
        )

        # Get signal from options if provided
        signal = options.get("signal") if options else None

        try:
            if first_protocol.code == P_DNSADDR:
                resolved = await self._resolve_dnsaddr(
                    hostname,
                    maddr,
                    max_depth,
                    signal,
                )
                return resolved if resolved else [maddr]
            else:
                resolved = await self._resolve_dns(hostname, first_protocol.code, signal)
                return resolved if resolved else [maddr]
        except RecursionLimitError:
            # Do not wrap RecursionLimitError so tests can catch it
            raise
        except Exception as e:
            raise ResolutionError(f"Failed to resolve {hostname}: {e!s}")

    def _clean_quotes(self, text: str) -> str:
        """Remove quotes from a string.

        Args:
            text: The text to clean

        Returns:
            The cleaned text without quotes
        """
        # Remove all types of quotes (single, double, mixed)
        return re.sub(r'[\'"\s]+', "", text)

    async def _resolve_dnsaddr(
        self,
        hostname: str,
        original_ma: "Multiaddr",
        max_depth: int,
        signal: Optional[trio.CancelScope] = None,
    ) -> list["Multiaddr"]:
        """Resolve a DNSADDR record.

        Args:
            hostname: The hostname to resolve
            original_ma: The original multiaddr being resolved
            max_depth: Maximum depth for recursive resolution
            signal: Optional signal for cancellation

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            RecursionLimitError: If maximum recursive depth is reached
            trio.Cancelled: If the operation is cancelled
        """
        if max_depth <= 0:
            raise RecursionLimitError(f"Maximum recursive depth exceeded for {hostname}")

        # Get the peer ID if present
        peer_id = None
        try:
            peer_id = original_ma.get_peer_id()
        except Exception:
            # If there's no peer ID, that's fine - we'll just resolve the address
            pass

        # Resolve the hostname with timeout and cancellation support
        try:
            if signal:
                # Use the provided signal for cancellation
                with signal:
                    results = []
                    # Try both A and AAAA records
                    for record_type, fam in [("A", "ip4"), ("AAAA", "ip6")]:
                        try:
                            answer = await self._resolver.resolve(hostname, record_type)
                            for rdata in answer:
                                # Cast to the specific DNS record type to access address
                                if record_type == "A":
                                    address = str(cast(dns.rdtypes.IN.A.A, rdata).address)
                                else:  # AAAA
                                    address = str(cast(dns.rdtypes.IN.AAAA.AAAA, rdata).address)
                                ma = Multiaddr(f"/{fam}/{address}")
                                def is_valid_peer_id(peer_id):
                                    try:
                                        decoded = base58.b58decode(peer_id)
                                        if len(decoded) in (34, 36, 38, 42, 46):
                                            return True
                                    except Exception:
                                        pass
                                    if peer_id.startswith(("b", "z")) and len(peer_id) > 40:
                                        return True
                                    return False
                                if peer_id and is_valid_peer_id(peer_id):
                                    try:
                                        ma = ma.encapsulate(f"/p2p/{peer_id}")
                                        return [ma]
                                    except Exception:
                                        continue
                                results.append(ma)
                        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                            continue
                    return results
            else:
                # Use default timeout-based cancellation
                with trio.CancelScope() as cancel_scope:  # type: ignore[call-arg]
                    # Set a timeout for DNS resolution
                    cancel_scope.deadline = trio.current_time() + self.DEFAULT_TIMEOUT
                    cancel_scope.cancelled_caught = True

                    results = []
                    # Try both A and AAAA records
                    for record_type, fam in [("A", "ip4"), ("AAAA", "ip6")]:
                        try:
                            answer = await self._resolver.resolve(hostname, record_type)
                            for rdata in answer:
                                # Cast to the specific DNS record type to access address
                                if record_type == "A":
                                    address = str(cast(dns.rdtypes.IN.A.A, rdata).address)
                                else:  # AAAA
                                    address = str(cast(dns.rdtypes.IN.AAAA.AAAA, rdata).address)
                                ma = Multiaddr(f"/{fam}/{address}")
                                def is_valid_peer_id(peer_id):
                                    try:
                                        decoded = base58.b58decode(peer_id)
                                        if len(decoded) in (34, 36, 38, 42, 46):
                                            return True
                                    except Exception:
                                        pass
                                    if peer_id.startswith(("b", "z")) and len(peer_id) > 40:
                                        return True
                                    return False
                                if peer_id and is_valid_peer_id(peer_id):
                                    try:
                                        ma = ma.encapsulate(f"/p2p/{peer_id}")
                                        return [ma]
                                    except Exception:
                                        continue
                                results.append(ma)
                        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                            continue
                    return results
        except Exception as e:
            raise ResolutionError(f"Failed to resolve DNSADDR {hostname}: {e!s}")

    async def _resolve_dns(
        self, hostname: str, protocol_code: int, signal: Optional[trio.CancelScope] = None
    ) -> list["Multiaddr"]:
        """Resolve a DNS record.

        Args:
            hostname: The hostname to resolve
            protocol_code: The protocol code (DNS, DNS4, or DNS6)
            signal: Optional signal for cancellation

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            trio.Cancelled: If the operation is cancelled
        """
        try:
            if signal:
                # Use the provided signal for cancellation
                with signal:
                    results = []
                    if protocol_code in (P_DNS, P_DNS4):
                        try:
                            answer = await self._resolver.resolve(hostname, "A")
                            for rdata in answer:
                                address = str(cast(dns.rdtypes.IN.A.A, rdata).address)
                                results.append(Multiaddr(f"/ip4/{address}"))
                        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                            pass
                    if protocol_code in (P_DNS, P_DNS6):
                        try:
                            answer = await self._resolver.resolve(hostname, "AAAA")
                            for rdata in answer:
                                address = str(cast(dns.rdtypes.IN.AAAA.AAAA, rdata).address)
                                results.append(Multiaddr(f"/ip6/{address}"))
                        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                            pass
                    return results
            else:
                # No signal provided, proceed without cancellation
                results = []
                if protocol_code in (P_DNS, P_DNS4):
                    try:
                        answer = await self._resolver.resolve(hostname, "A")
                        for rdata in answer:
                            address = str(cast(dns.rdtypes.IN.A.A, rdata).address)
                            results.append(Multiaddr(f"/ip4/{address}"))
                    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                        pass
                if protocol_code in (P_DNS, P_DNS6):
                    try:
                        answer = await self._resolver.resolve(hostname, "AAAA")
                        for rdata in answer:
                            address = str(cast(dns.rdtypes.IN.AAAA.AAAA, rdata).address)
                            results.append(Multiaddr(f"/ip6/{address}"))
                    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                        pass
                return results
        except Exception as e:
            raise ResolutionError(f"Failed to resolve DNS {hostname}: {e!s}")


__all__ = ["DNSResolver"]
