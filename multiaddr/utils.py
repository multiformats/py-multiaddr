import ipaddress
import socket
from typing import Any

import psutil

from .multiaddr import Multiaddr
from .protocols import P_IP4, P_IP6, P_TCP, P_UDP, Protocol

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
    protos: list[Protocol] = list(ma.protocols())
    if not protos:
        return None
    first = protos[0]
    if first.code in (P_IP4, P_IP6):
        val = ma.value_for_protocol(first.code)
        if val:
            try:
                return ipaddress.ip_address(val)
            except ValueError:
                pass
    return None


def is_thin_waist(ma: Multiaddr) -> bool:
    """Check if a multiaddr is a thin waist address (ip4/ip6 optionally followed by tcp/udp)."""
    protos: list[Protocol] = list(ma.protocols())
    if not protos:
        return False
    if protos[0].code not in (P_IP4, P_IP6):
        return False
    if len(protos) == 1:
        return True
    if len(protos) == 2 and protos[1].code in (P_TCP, P_UDP):
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
    return bool(ip and ip.version == 6 and ip.is_link_local)


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


def interface_multiaddrs() -> list[Multiaddr]:
    """Return local interface addresses as Multiaddr objects.

    Uses :func:`get_network_addrs` for IPv4 and IPv6. Loopback and link-local
    addresses are excluded (same filtering as ``get_network_addrs``).
    """
    result: list[Multiaddr] = []
    for host in get_network_addrs(4):
        result.append(Multiaddr(f"/ip4/{host}"))
    for host in get_network_addrs(6):
        result.append(Multiaddr(f"/ip6/{host}"))
    return result


def dial_args(ma: Multiaddr) -> tuple[str, str]:
    """Convert a multiaddr to ``(network, address)`` for ``socket.connect()``.

    Examples:
        >>> dial_args(Multiaddr("/ip4/1.2.3.4/tcp/80"))
        ('tcp4', '1.2.3.4:80')
        >>> dial_args(Multiaddr("/ip6/::1/tcp/80"))
        ('tcp6', '[::1]:80')
        >>> dial_args(Multiaddr("/unix/var/run/docker.sock"))
        ('unix', '/var/run/docker.sock')
    """
    opts = get_multiaddr_options(ma)
    if opts is None:
        protos = list(ma.protocols())
        if protos and protos[0].name == "unix":
            path = ma.value_for_protocol("unix")
            if path is None:
                raise ValueError(f"{ma} is missing a unix path")
            return ("unix", path if path.startswith("/") else f"/{path}")
        raise ValueError(f"{ma} is not a 'thin waist' address")

    family_suffix = "4" if opts["family"] == 4 else "6"
    network = f"{opts['transport']}{family_suffix}"

    if opts["family"] == 6:
        address = f"[{opts['host']}]:{opts['port']}"
    else:
        address = f"{opts['host']}:{opts['port']}"

    return (network, address)


def from_net_addr(
    addr: tuple[Any, ...],
    *,
    transport: str = "tcp",
) -> Multiaddr:
    """Convert a socket address tuple to a Multiaddr.

    Args:
        addr: A socket address tuple such as ``(host, port)`` or an IPv6
            ``(host, port, flowinfo, scope_id)`` tuple.
        transport: ``"tcp"`` or ``"udp"`` (default ``"tcp"``).

    Examples:
        >>> from_net_addr(("1.2.3.4", 80))
        Multiaddr('/ip4/1.2.3.4/tcp/80')
        >>> from_net_addr(("::1", 53), transport="udp")
        Multiaddr('/ip6/::1/udp/53')
    """
    if transport not in ("tcp", "udp"):
        raise ValueError(f"unsupported transport: {transport!r}")
    if not addr or len(addr) < 2:
        raise ValueError("addr must be a (host, port[, ...]) tuple")

    host, port = addr[0], addr[1]
    if not isinstance(host, str):
        raise TypeError("host must be a string")
    if not isinstance(port, int):
        raise TypeError("port must be an integer")

    ip = ipaddress.ip_address(host)
    ip_proto = "ip4" if isinstance(ip, ipaddress.IPv4Address) else "ip6"
    return Multiaddr(f"/{ip_proto}/{host}/{transport}/{port}")


def to_net_addr(ma: Multiaddr) -> tuple[str, int]:
    """Convert a thin-waist Multiaddr to a ``(host, port)`` socket address tuple.

    Examples:
        >>> to_net_addr(Multiaddr("/ip4/1.2.3.4/tcp/80"))
        ('1.2.3.4', 80)
    """
    opts = get_multiaddr_options(ma)
    if opts is None:
        raise ValueError(f"{ma} is not a thin waist address")
    return (opts["host"], opts["port"])
