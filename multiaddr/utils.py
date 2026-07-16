import ipaddress
import socket
from typing import Any

import psutil

from .multiaddr import Multiaddr
from .protocols import P_IP4, P_IP6, P_TCP, P_UDP

IP4_LOOPBACK = Multiaddr("/ip4/127.0.0.1")
IP6_LOOPBACK = Multiaddr("/ip6/::1")
IP4_UNSPECIFIED = Multiaddr("/ip4/0.0.0.0")
IP6_UNSPECIFIED = Multiaddr("/ip6/::")

PRIVATE4 = [
    ipaddress.ip_network(cidr)
    for cidr in [
        "127.0.0.0/8",
        "10.0.0.0/8",
        "100.64.0.0/10",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "169.254.0.0/16",
    ]
]

PRIVATE6 = [
    ipaddress.ip_network(cidr)
    for cidr in [
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    ]
]


def _get_ip(ma: Multiaddr) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    protos = ma.protocols()
    if not protos:
        return None
    first = protos[0]
    if getattr(first, "code", None) in (P_IP4, P_IP6):
        val = ma.value_for_protocol(getattr(first, "code", None))
        if val:
            try:
                return ipaddress.ip_address(val)
            except ValueError:
                pass
    return None


def is_thin_waist(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a thin waist address (ip4/ip6 optionally followed by tcp/udp)."""
    protos = ma.protocols()
    if not protos:
        return False
    if getattr(protos[0], "code", None) not in (P_IP4, P_IP6):
        return False
    if len(protos) == 1:
        return True
    if len(protos) == 2 and getattr(protos[1], "code", None) in (P_TCP, P_UDP):
        return True
    return False


def is_ip_loopback(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a loopback IP address."""
    ip = _get_ip(ma)
    return ip.is_loopback if ip else False


def is_ip_unspecified(ma: Multiaddr) -> bool:
    """Check if a multiaddr is an unspecified IP address."""
    ip = _get_ip(ma)
    return ip.is_unspecified if ip else False


def is_ip6_link_local(ma: Multiaddr) -> bool:
    """Check if a multiaddr is an IPv6 link-local address."""
    ip = _get_ip(ma)
    return ip.version == 6 and ip.is_link_local if ip else False


def is_private_addr(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a private IP address."""
    ip = _get_ip(ma)
    if not ip:
        return False
    if ip.version == 4:
        return any(ip in net for net in PRIVATE4)
    else:
        return any(ip in net for net in PRIVATE6)


def is_public_addr(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a public IP address."""
    ip = _get_ip(ma)
    if not ip:
        return False
    return not is_ip_unspecified(ma) and not is_private_addr(ma)


def is_nat64_ipv4_converted_ipv6_addr(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a NAT64 converted IPv6 address."""
    ip = _get_ip(ma)
    if not ip or ip.version != 6:
        return False
    return ip in ipaddress.ip_network("64:ff9b::/96")


def is_wildcard(ip: str) -> bool:
    """Check if an IP address is a wildcard address."""
    return ip in ["0.0.0.0", "::"]


def get_network_addrs(family: int) -> list[str]:
    """Get all network addresses for a given IP family (4 for IPv4, 6 for IPv6)."""
    addresses = []
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if family == 4 and addr.family == socket.AF_INET:
                if addr.address != "127.0.0.1" and not is_link_local_ip(addr.address):
                    addresses.append(addr.address)
            elif family == 6 and addr.family == socket.AF_INET6:
                if not addr.address.startswith("::1") and not is_link_local_ip(addr.address):
                    # Remove the %scope_id if present
                    addresses.append(addr.address.split("%")[0])
    return addresses


def is_link_local_ip(ip: str) -> bool:
    """Check if an IP address is link-local."""
    if ":" in ip:  # IPv6
        return ip.startswith("fe80:")
    else:  # IPv4
        parts = ip.split(".")
        return len(parts) == 4 and parts[0] == "169" and parts[1] == "254"


def get_multiaddr_options(ma: Multiaddr) -> dict[str, Any] | None:
    """Extract options from a multiaddr (similar to toOptions() in JS).

    Returns a dictionary with 'family', 'host', 'transport', and 'port' keys,
    or None if the multiaddr doesn't represent a thin waist address.
    """
    if ma is None:
        return None

    # Parse the multiaddr to extract IP and transport information
    parts = str(ma).strip("/").split("/")

    if len(parts) < 4:
        return None

    # Look for IP protocol (ip4 or ip6)
    ip_proto = None
    ip_addr = None
    transport_proto = None
    port = None

    for i, part in enumerate(parts):
        if part in ["ip4", "ip6"]:
            if i + 1 < len(parts):
                ip_proto = part
                ip_addr = parts[i + 1]
        elif part in ["tcp", "udp"]:
            if i + 1 < len(parts):
                transport_proto = part
                try:
                    port = int(parts[i + 1])
                except (ValueError, IndexError):
                    return None

    if not all([ip_proto, ip_addr, transport_proto, port]):
        return None

    family = 4 if ip_proto == "ip4" else 6

    return {"family": family, "host": ip_addr, "transport": transport_proto, "port": port}


def get_thin_waist_addresses(
    ma: Multiaddr | None = None, port: int | None = None
) -> list[Multiaddr]:
    """Get all thin waist addresses on the current host that match the family of the
    passed multiaddr and optionally override the port.

    Wildcard IP4/6 addresses will be expanded into all available interfaces.

    Args:
        ma: The multiaddr to process. If None, returns empty list.
        port: Optional port to override the port in the multiaddr.

    Returns:
        List of Multiaddr objects representing thin waist addresses.
    """
    if ma is None:
        return []

    options = get_multiaddr_options(ma)
    if options is None:
        return []

    # Use provided port or fall back to the one in the multiaddr
    target_port = port if port is not None else options["port"]

    ip_proto = "ip4" if options["family"] == 4 else "ip6"

    if is_wildcard(options["host"]):
        # Expand wildcard addresses to all available interfaces
        addrs = []
        for host in get_network_addrs(options["family"]):
            if not is_link_local_ip(host):
                # Correct multiaddr format: /ip4/host/tcp/port or /ip6/host/tcp/port
                addr_str = f"/{ip_proto}/{host}/{options['transport']}/{target_port}"
                addrs.append(Multiaddr(addr_str))
        return addrs
    else:
        # Return the specific address
        addr_str = f"/{ip_proto}/{options['host']}/{options['transport']}/{target_port}"
        return [Multiaddr(addr_str)]
