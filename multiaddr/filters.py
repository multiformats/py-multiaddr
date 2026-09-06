"""Accept/deny IP filtering for multiaddrs (go-multiaddr Filters parity)."""

from __future__ import annotations

import ipaddress
from enum import Enum

from .multiaddr import Multiaddr
from .protocols import P_IP4, P_IP6


class Action(Enum):
    """Filter action applied to a matching network."""

    ACCEPT = 1
    DENY = 2


def _extract_ip(ma: Multiaddr) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    for proto in ma.protocols():
        if proto.code in (P_IP4, P_IP6):
            value = ma.value_for_protocol(proto.code)
            if value is None:
                return None
            try:
                return ipaddress.ip_address(value)
            except ValueError:
                return None
    return None


class Filters:
    """Collection of accept/deny IP network rules.

    The last matching filter wins. If no filter matches, ``default_action`` applies.
    Non-IP multiaddrs are treated according to ``default_action``.
    """

    def __init__(self, default_action: Action = Action.ACCEPT) -> None:
        self.default_action = default_action
        self._filters: list[tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, Action]] = []

    def add_filter(
        self,
        network: str | ipaddress.IPv4Network | ipaddress.IPv6Network,
        action: Action,
    ) -> None:
        """Add or replace a filter for the given network."""
        if isinstance(network, str):
            net: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(
                network, strict=False
            )
        else:
            net = network

        for idx, (existing, _) in enumerate(self._filters):
            if existing == net:
                self._filters[idx] = (net, action)
                return
        self._filters.append((net, action))

    def remove_literal(self, network: str | ipaddress.IPv4Network | ipaddress.IPv6Network) -> bool:
        """Remove the filter for an exact network match. Returns whether something was removed."""
        if isinstance(network, str):
            net: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(
                network, strict=False
            )
        else:
            net = network
        for idx, (existing, _) in enumerate(self._filters):
            if existing == net:
                del self._filters[idx]
                return True
        return False

    def addr_blocked(self, ma: Multiaddr) -> bool:
        """Return True if the multiaddr should be denied."""
        ip = _extract_ip(ma)
        if ip is None:
            return self.default_action == Action.DENY

        action = self.default_action
        for network, filter_action in self._filters:
            if ip in network:
                action = filter_action
        return action == Action.DENY
