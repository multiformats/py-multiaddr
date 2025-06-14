"""DNS resolver implementation for multiaddr."""

import socket
import re
from typing import List, Optional, Dict, Any

import trio
import base58

from ..exceptions import ResolutionError, RecursionLimitError
from ..multiaddr import Multiaddr
from ..protocols import P_DNS, P_DNS4, P_DNS6, P_DNSADDR
from . import Resolver


class DNSResolver(Resolver):
    """DNS resolver for multiaddr."""

    MAX_RECURSIVE_DEPTH = 32

    def __init__(self):
        """Initialize the DNS resolver."""
        pass

    async def resolve(self, ma: 'Multiaddr', options: Optional[Dict[str, Any]] = None) -> List['Multiaddr']:
        """Resolve a DNS multiaddr to its actual addresses.

        Args:
            ma: The multiaddr to resolve
            options: Optional configuration for resolution
                - max_recursive_depth: Maximum depth for recursive resolution (default: 32)
                - signal: Optional signal for cancellation

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            RecursionLimitError: If maximum recursive depth is reached
            trio.Cancelled: If the operation is cancelled
        """
        if not options:
            options = {}

        # Check for cancellation
        signal = options.get("signal")
        if signal and signal.aborted:
            return []

        # Get the first protocol
        protocols = ma.protocols()
        if not protocols:
            raise ResolutionError("empty multiaddr")

        first_protocol = protocols[0]
        if first_protocol.code not in (P_DNS, P_DNS4, P_DNS6, P_DNSADDR):
            return [ma]

        # Get the hostname and clean it of quotes
        hostname = ma.value_for_protocol(first_protocol.code)
        if not hostname:
            return [ma]

        # Remove quotes from hostname
        hostname = self._clean_quotes(hostname)

        # Check for cancellation again
        if signal and signal.aborted:
            return []

        try:
            if first_protocol.code == P_DNSADDR:
                return await self._resolve_dnsaddr(hostname, ma, options.get("max_recursive_depth", self.MAX_RECURSIVE_DEPTH), options)
            else:
                return await self._resolve_dns(hostname, first_protocol.code, options)
        except RecursionLimitError as e:
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
        return re.sub(r'[\'"\s]+', '', text)

    async def _resolve_dnsaddr(self, hostname: str, original_ma: 'Multiaddr', 
                             max_depth: int, options: Dict[str, Any]) -> List['Multiaddr']:
        """Resolve a DNSADDR record.

        Args:
            hostname: The hostname to resolve
            original_ma: The original multiaddr being resolved
            max_depth: Maximum depth for recursive resolution
            options: Resolution options

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            RecursionLimitError: If maximum recursive depth is reached
            trio.Cancelled: If the operation is cancelled
        """
        if max_depth <= 0:
            raise RecursionLimitError(f"Maximum recursive depth exceeded for {hostname}")

        # Check for cancellation
        signal = options.get("signal")
        if signal and signal.aborted:
            return []

        # Get the peer ID if present
        peer_id = None
        try:
            peer_id = original_ma.get_peer_id()
        except Exception:
            # If there's no peer ID, that's fine - we'll just resolve the address
            pass

        # Resolve the hostname
        try:
            addrinfo = await trio.to_thread.run_sync(
                socket.getaddrinfo,
                hostname,
                None,
                socket.AF_UNSPEC,
                socket.SOCK_STREAM,
            )
        except socket.gaierror as e:
            # Check for cancellation before raising error
            signal = options.get("signal")
            if signal and signal.aborted:
                return []
            raise ResolutionError(f"Failed to resolve DNSADDR {hostname}: {e!s}")
        except Exception as e:
            # Check for cancellation before raising error
            signal = options.get("signal")
            if signal and signal.aborted:
                return []
            raise ResolutionError(f"Failed to resolve DNSADDR {hostname}: {e!s}")

        # Check for cancellation immediately after DNS resolution
        signal = options.get("signal")
        if signal and signal.aborted:
            return []

        # Process the results
        results = []
        for family, _, _, _, sockaddr in addrinfo:
            if family == socket.AF_INET:
                ip = sockaddr[0]
                ma = Multiaddr(f"/ip4/{ip}")
            elif family == socket.AF_INET6:
                ip = sockaddr[0]
                ma = Multiaddr(f"/ip6/{ip}")
            else:
                continue

            # Helper to validate peer ID (CIDv0 base58btc or CIDv1)
            def is_valid_peer_id(peer_id):
                try:
                    # Try base58 decode (CIDv0)
                    decoded = base58.b58decode(peer_id)
                    if len(decoded) in (34, 36, 38, 42, 46):  # common multihash lengths
                        return True
                except Exception:
                    pass
                # Try CIDv1 (should start with 'b' or 'z' and be base32)
                if peer_id.startswith(('b', 'z')) and len(peer_id) > 40:
                    return True
                return False

            # Only encapsulate /p2p/peer_id if peer_id is present, valid, and not already in the multiaddr
            if peer_id and is_valid_peer_id(peer_id) and not any(p.name == "p2p" for p in ma.protocols()):
                try:
                    ma = ma.encapsulate(f"/p2p/{peer_id}")
                except Exception:
                    # If encapsulation fails, skip this result
                    continue

            results.append(ma)

        return results

    async def _resolve_dns(self, hostname: str, protocol_code: int, options: Dict[str, Any]) -> List['Multiaddr']:
        """Resolve a DNS record.

        Args:
            hostname: The hostname to resolve
            protocol_code: The protocol code (DNS, DNS4, or DNS6)
            options: Resolution options

        Returns:
            A list of resolved multiaddrs

        Raises:
            ResolutionError: If resolution fails
            trio.Cancelled: If the operation is cancelled
        """
        # Check for cancellation
        signal = options.get("signal")
        if signal and signal.aborted:
            return []

        # Determine the address family
        if protocol_code == P_DNS4:
            family = socket.AF_INET
        elif protocol_code == P_DNS6:
            family = socket.AF_INET6
        else:  # P_DNS
            family = socket.AF_UNSPEC  # Both IPv4 and IPv6

        # Resolve the hostname
        try:
            addrinfo = await trio.to_thread.run_sync(
                socket.getaddrinfo,
                hostname,
                None,
                family,
                socket.SOCK_STREAM,
            )
        except socket.gaierror as e:
            # Check for cancellation before raising error
            signal = options.get("signal")
            if signal and signal.aborted:
                return []
            raise ResolutionError(f"Failed to resolve DNS {hostname}: {e!s}")
        except Exception as e:
            # Check for cancellation before raising error
            signal = options.get("signal")
            if signal and signal.aborted:
                return []
            raise ResolutionError(f"Failed to resolve DNS {hostname}: {e!s}")

        # Check for cancellation again
        if signal and signal.aborted:
            return []

        # Process the results
        results = []
        for family, _, _, _, sockaddr in addrinfo:
            if family == socket.AF_INET:
                ip = sockaddr[0]
                results.append(Multiaddr(f"/ip4/{ip}"))
            elif family == socket.AF_INET6:
                ip = sockaddr[0]
                results.append(Multiaddr(f"/ip6/{ip}"))
            else:
                continue

        # Check for cancellation after DNS resolution
        signal = options.get("signal")
        if signal and signal.aborted:
            return []

        return results


__all__ = ["DNSResolver"]
