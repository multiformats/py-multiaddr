#!/usr/bin/env python3
"""
Resolver utility function examples for py-multiaddr.

This script demonstrates the utility functions available in
``multiaddr.resolvers`` that were ported from go-multiaddr-dns.

## Overview

1. **matches()**: Check if a multiaddr contains DNS components
2. **is_fqdn() / fqdn()**: FQDN detection and normalization
3. **addr_len()**: Count protocol components in a multiaddr
4. **offset_addr()**: Remove leading protocol components
5. **resolve_all()**: Iteratively resolve all DNS components

## Expected Output

When you run this script, you should see output similar to:

```
Resolver Utility Examples
==================================================

=== matches() ===
/dns4/example.com/tcp/80      -> True  (contains dns4)
/ip4/127.0.0.1/tcp/80         -> False (no DNS component)
/dnsaddr/bootstrap.libp2p.io  -> True  (contains dnsaddr)

=== is_fqdn() / fqdn() ===
is_fqdn("example.com")  -> False
is_fqdn("example.com.") -> True
fqdn("example.com")     -> example.com.
fqdn("example.com.")    -> example.com.

=== addr_len() ===
/ip4/127.0.0.1           -> 1 component(s)
/ip4/127.0.0.1/tcp/80    -> 2 component(s)
/ip4/1.2.3.4/udp/9/quic  -> 3 component(s)

=== offset_addr() ===
offset_addr(/ip4/127.0.0.1/tcp/80/http, 0) -> /ip4/127.0.0.1/tcp/80/http
offset_addr(/ip4/127.0.0.1/tcp/80/http, 1) -> /tcp/80/http
offset_addr(/ip4/127.0.0.1/tcp/80/http, 2) -> /http
offset_addr(/ip4/127.0.0.1/tcp/80/http, 3) -> /
```
"""

from multiaddr import Multiaddr
from multiaddr.resolvers import addr_len, fqdn, is_fqdn, matches, offset_addr


def main():
    print("Resolver Utility Examples")
    print("=" * 50)

    # --- matches() ---
    print("\n=== matches() ===")
    examples = [
        ("/dns4/example.com/tcp/80", "contains dns4"),
        ("/ip4/127.0.0.1/tcp/80", "no DNS component"),
        ("/dnsaddr/bootstrap.libp2p.io", "contains dnsaddr"),
    ]
    for addr_str, desc in examples:
        ma = Multiaddr(addr_str)
        result = matches(ma)
        print(f"  {addr_str:<35} -> {result!s:<6} ({desc})")

    # --- is_fqdn() / fqdn() ---
    print("\n=== is_fqdn() / fqdn() ===")
    for domain in ("example.com", "example.com."):
        print(f'  is_fqdn("{domain}") -> {is_fqdn(domain)}')
    for domain in ("example.com", "example.com."):
        print(f'  fqdn("{domain}")    -> {fqdn(domain)}')

    # --- addr_len() ---
    print("\n=== addr_len() ===")
    for addr_str in ("/ip4/127.0.0.1", "/ip4/127.0.0.1/tcp/80", "/ip4/1.2.3.4/udp/9/quic"):
        ma = Multiaddr(addr_str)
        print(f"  {addr_str:<30} -> {addr_len(ma)} component(s)")

    # --- offset_addr() ---
    print("\n=== offset_addr() ===")
    ma = Multiaddr("/ip4/127.0.0.1/tcp/80/http")
    for n in range(4):
        result = offset_addr(ma, n)
        print(f"  offset_addr({ma}, {n}) -> {result}")


if __name__ == "__main__":
    main()
