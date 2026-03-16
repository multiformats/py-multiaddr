"""DNS resolution support for multiaddr."""

from .base import Resolver
from .dns import DNSADDR_TXT_PREFIX, DNSResolver
from .util import addr_len, fqdn, is_fqdn, matches, offset_addr, resolve_all

__all__ = [
    "DNSADDR_TXT_PREFIX",
    "DNSResolver",
    "Resolver",
    "addr_len",
    "fqdn",
    "is_fqdn",
    "matches",
    "offset_addr",
    "resolve_all",
]
