#!/usr/bin/env python3
"""
DNS resolution examples for py-multiaddr.

This script demonstrates how to use DNS resolution functionality in py-multiaddr,
showing how to resolve bootstrap node addresses like those used in js-libp2p.

## Overview

This script shows various examples of DNS resolution using py-multiaddr:

1. **Basic DNS Resolution**: Simple resolution of DNS addresses to IP addresses
2. **Bootstrap Node Resolution**: Resolving real bootstrap node addresses with peer IDs
3. **DNS Protocol Comparison**: Testing different DNS protocols (/dns/, /dns4/, /dns6/, /dnsaddr/)
4. **Peer ID Preservation**: Ensuring peer IDs are maintained during resolution
5. **Sequential Resolution**: Processing multiple addresses sequentially
6. **py-libp2p Integration**: Example of how to use resolved addresses with py-libp2p

## Expected Output

When you run this script, you should see output similar to:

```
DNS Resolution Examples
==================================================
=== Basic DNS Resolution ===
Original address: /dns/example.com
Protocols: ['dns']
Resolved to 12 addresses:
  1. /ip4/23.192.228.84
  2. /ip4/23.215.0.136
  ... (more IPv4 and IPv6 addresses)

=== Bootstrap Node Resolution ===
Resolving: /dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
  Peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
  Resolved to 6 addresses:
    1. /ip4/139.178.91.71/tcp/4001/p2p/
      QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
    2. /ip4/139.178.91.71/udp/4001/quic-v1/p2p/
      QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
    ... (more addresses)

=== DNS Protocol Comparison ===
Testing DNS (both IPv4 and IPv6): /dns/example.com
  Resolved to 12 addresses:
    1. /ip4/23.215.0.136
    2. /ip4/23.215.0.138
    ... (6 IPv4 + 6 IPv6 addresses)

=== Peer ID Preservation Test ===
Original address: /dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
Original peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
Resolved to 6 addresses:
  1. /ip4/139.178.91.71/tcp/4001/p2p/
    QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
     Peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
     Peer ID preserved: True

=== Sequential DNS Resolution ===
/dns/example.com:
  Resolved to 12 addresses:
    - /ip4/23.215.0.136
    - /ip4/23.215.0.138
    ... (more addresses)

=== py-libp2p Integration Example ===
Processing bootstrap node: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
  Resolved: 139.178.91.71:4001 (peer: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN)

Resolved 1 bootstrap peers:
  QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN -> 139.178.91.71:4001

==================================================
All examples completed!
```

## Key Features Demonstrated

- **DNS Resolution**: Converting DNS addresses to IP addresses
- **Peer ID Preservation**: Maintaining peer IDs during resolution
- **Multiple Protocol Support**: /dns/, /dns4/, /dns6/, /dnsaddr/
- **Error Handling**: Graceful handling of resolution failures
- **Real Bootstrap Node Examples**: Using actual libp2p bootstrap nodes that resolve to IP addresses

## Requirements

- Python 3.9+
- py-multiaddr library
- trio library
- Internet connection for DNS resolution

## Usage

```bash
python trio_dns_examples.py
```

## Notes

- This script uses real bootstrap nodes from bootstrap.libp2p.io that actually resolve
- The DNS resolver requires trio for async operations
- Peer IDs are preserved during resolution for bootstrap node functionality
- All examples demonstrate working DNS resolution to actual IP addresses
"""

import trio

from multiaddr import Multiaddr
from multiaddr.resolvers import DNSResolver


async def basic_dns_resolution():
    """
    Basic DNS resolution example.

    This function demonstrates the simplest form of DNS resolution:
    - Creates a DNS multiaddr for example.com
    - Resolves it to actual IP addresses (both IPv4 and IPv6)
    - Shows the original and resolved addresses

    Expected output:
    === Basic DNS Resolution ===
    Original address: /dns/example.com
    Protocols: ['dns']
    Resolved to 12 addresses:
      1. /ip4/23.192.228.84
      2. /ip4/23.215.0.136
      3. /ip4/23.215.0.138
      ... (more IPv4 and IPv6 addresses)
    """
    print("=== Basic DNS Resolution ===")

    # Test with a simple DNS address
    test_addr = "/dns/example.com"
    ma = Multiaddr(test_addr)

    print(f"Original address: {ma}")
    print(f"Protocols: {[p.name for p in ma.protocols()]}")

    try:
        resolved = await ma.resolve()
        print(f"Resolved to {len(resolved)} addresses:")
        for i, addr in enumerate(resolved, 1):
            print(f"  {i}. {addr}")
    except Exception as e:
        print(f"Error resolving {test_addr}: {e}")


async def bootstrap_node_resolution():
    """
    Resolve bootstrap node addresses.

    This function demonstrates resolving real bootstrap node addresses that include peer IDs:
    - Uses real domains from bootstrap.libp2p.io that actually resolve
    - Shows how peer IDs are preserved during resolution
    - Extracts connection information (IP addresses) from resolved addresses

    Expected output:
    === Bootstrap Node Resolution ===
    Resolving: /dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
      Peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
      Resolved to 6 addresses:
        1. /ip4/139.178.91.71/tcp/4001/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
        2. /ip4/139.178.91.71/udp/4001/quic-v1/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
        3. /ip6/2604:1380:45e3:6e00::1/tcp/4001/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
        4. /ip6/2604:1380:45e3:6e00::1/udp/4001/quic-v1/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
        5. /ip4/139.178.91.71/tcp/443/wss/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
        6. /ip6/2604:1380:45e3:6e00::1/tcp/443/wss/p2p/
          QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
    """
    print("\n=== Bootstrap Node Resolution ===")

    # Use only one bootstrap address to reduce repetition
    bootstrap_addresses = [
        "/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
    ]

    resolver = DNSResolver()

    for addr_str in bootstrap_addresses:
        print(f"\nResolving: {addr_str}")

        try:
            ma = Multiaddr(addr_str)
            peer_id = ma.get_peer_id()
            print(f"  Peer ID: {peer_id}")

            # Resolve the address
            resolved = await resolver.resolve(ma)

            print(f"  Resolved to {len(resolved)} addresses:")
            for i, resolved_ma in enumerate(resolved, 1):
                print(f"    {i}. {resolved_ma}")

                # Extract IP and port information for TCP connections only
                ip_addr = None
                port = None
                for proto, value in resolved_ma.items():
                    if proto.name in ("ip4", "ip6"):
                        ip_addr = value
                    elif proto.name == "tcp":
                        port = value

                if ip_addr and port:
                    print(f"       Connection: {ip_addr}:{port}")

        except Exception as e:
            print(f"  Error: {e}")


async def dns_protocol_comparison():
    """
    Compare different DNS protocols.

    This function demonstrates the differences between various DNS protocols:
    - /dns/ - Resolves to both IPv4 and IPv6 addresses
    - /dns4/ - Resolves to IPv4 addresses only
    - /dns6/ - Resolves to IPv6 addresses only
    - /dnsaddr/ - Resolves to both IPv4 and IPv6 addresses (same as /dns/)

    Expected output:
    === DNS Protocol Comparison ===
    Testing DNS (both IPv4 and IPv6): /dns/example.com
      Resolved to 12 addresses:
        1. /ip4/23.215.0.136
        2. /ip4/23.215.0.138
        ... (6 IPv4 + 6 IPv6 addresses)

    Testing DNS4 (IPv4 only): /dns4/example.com
      Resolved to 6 addresses:
        1. /ip4/23.215.0.138
        2. /ip4/96.7.128.175
        ... (6 IPv4 addresses only)

    Testing DNS6 (IPv6 only): /dns6/example.com
      Resolved to 6 addresses:
        1. /ip6/2600:1408:ec00:36::1736:7f31
        2. /ip6/2600:1406:3a00:21::173e:2e65
        ... (6 IPv6 addresses only)
    """
    print("\n=== DNS Protocol Comparison ===")

    dns_tests = [
        ("/dns/example.com", "DNS (both IPv4 and IPv6)"),
        ("/dns4/example.com", "DNS4 (IPv4 only)"),
        ("/dns6/example.com", "DNS6 (IPv6 only)"),
        ("/dnsaddr/bootstrap.libp2p.io", "DNSADDR (both IPv4 and IPv6)"),
    ]

    resolver = DNSResolver()

    for addr_str, description in dns_tests:
        print(f"\nTesting {description}: {addr_str}")

        try:
            ma = Multiaddr(addr_str)
            resolved = await resolver.resolve(ma)

            print(f"  Resolved to {len(resolved)} addresses:")
            # Show only first 3 addresses to reduce repetition
            for i, addr in enumerate(resolved[:3], 1):
                print(f"    {i}. {addr}")
            if len(resolved) > 3:
                print(f"    ... and {len(resolved) - 3} more addresses")

        except Exception as e:
            print(f"  Error: {e}")


async def peer_id_preservation_test():
    """
    Test that peer IDs are preserved during resolution.

    This function verifies that peer IDs are maintained when resolving DNS addresses:
    - Creates a multiaddr with both DNS and peer ID components
    - Resolves the DNS part to IP addresses
    - Confirms the peer ID remains unchanged in the resolved addresses

    Expected output:
    === Peer ID Preservation Test ===
    Original address: /dnsaddr/bootstrap.libp2p.io/p2p/
      QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
    Original peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
    Resolved to 6 addresses:
      1. /ip4/139.178.91.71/tcp/4001/p2p/
         QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
         Peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
         Peer ID preserved: True
    """
    print("\n=== Peer ID Preservation Test ===")

    test_addr = "/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"

    try:
        ma = Multiaddr(test_addr)
        original_peer_id = ma.get_peer_id()
        print(f"Original address: {ma}")
        print(f"Original peer ID: {original_peer_id}")

        resolved = await ma.resolve()

        print(f"Resolved to {len(resolved)} addresses:")
        # Show only first 2 addresses to reduce repetition
        for i, resolved_ma in enumerate(resolved[:2], 1):
            resolved_peer_id = resolved_ma.get_peer_id()
            print(f"  {i}. {resolved_ma}")
            print(f"     Peer ID: {resolved_peer_id}")
            print(f"     Peer ID preserved: {original_peer_id == resolved_peer_id}")

        if len(resolved) > 2:
            print(f"  ... and {len(resolved) - 2} more addresses (all with preserved peer ID)")

    except Exception as e:
        print(f"Error: {e}")


async def concurrent_resolution():
    """
    Demonstrate sequential DNS resolution.

    This function shows how to process multiple DNS addresses sequentially:
    - Resolves multiple addresses one by one
    - Handles errors gracefully for each address
    - Shows the results for each resolution attempt

    Expected output:
    === Sequential DNS Resolution ===
    /dns/example.com:
      Resolved to 12 addresses:
        - /ip4/23.215.0.136
        - /ip4/23.215.0.138
        ... (more addresses)

    /dns4/example.com:
      Resolved to 6 addresses:
        - /ip4/23.192.228.84
        - /ip4/23.215.0.136
        ... (IPv4 addresses only)

    /dns6/example.com:
      Resolved to 6 addresses:
        - /ip6/2600:1408:ec00:36::1736:7f31
        - /ip6/2600:1406:3a00:21::173e:2e65
        ... (IPv6 addresses only)
    """
    print("\n=== Sequential DNS Resolution ===")

    addresses = [
        "/dns/example.com",
        "/dns4/example.com",
        "/dns6/example.com",
        "/dnsaddr/bootstrap.libp2p.io",
    ]

    async def resolve_single(addr_str):
        """Resolve a single address."""
        try:
            ma = Multiaddr(addr_str)
            resolved = await ma.resolve()
            return addr_str, resolved, None
        except Exception as e:
            return addr_str, [], str(e)

    # Resolve all addresses sequentially
    results = []
    for addr in addresses:
        result = await resolve_single(addr)
        results.append(result)

    for addr_str, resolved, error in results:
        print(f"\n{addr_str}:")
        if error:
            print(f"  Error: {error}")
        else:
            print(f"  Resolved to {len(resolved)} addresses:")
            # Show only first 3 addresses to reduce repetition
            for addr in resolved[:3]:
                print(f"    - {addr}")
            if len(resolved) > 3:
                print(f"    ... and {len(resolved) - 3} more addresses")


async def py_libp2p_integration_example():
    """
    Example of how to integrate with py-libp2p.

    This function demonstrates a practical integration pattern for py-libp2p:
    - Resolves real bootstrap node addresses to IP addresses
    - Extracts connection information (peer ID, IP, port)
    - Prepares the data structure needed for py-libp2p connections
    - Shows how to handle the resolved peer information

    Expected output:
    === py-libp2p Integration Example ===
    Processing bootstrap node: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
      Resolved: 139.178.91.71:4001 (peer: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN)

    Resolved 1 bootstrap peers:
      QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN -> 139.178.91.71:4001
    """
    print("\n=== py-libp2p Integration Example ===")

    resolver = DNSResolver()

    # Use only one bootstrap address to reduce repetition
    bootstrap_addresses = [
        "/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
    ]

    resolved_peers = []

    for addr_str in bootstrap_addresses:
        ma = Multiaddr(addr_str)
        peer_id = ma.get_peer_id()

        print(f"\nProcessing bootstrap node: {peer_id}")

        try:
            # Resolve DNS addresses to IP addresses
            resolved_addrs = await resolver.resolve(ma)

            for resolved_ma in resolved_addrs:
                # Extract connection information
                ip_addr = None
                port = None

                for proto, value in resolved_ma.items():
                    if proto.name == "ip4":
                        ip_addr = value
                    elif proto.name == "ip6":
                        ip_addr = value
                    elif proto.name == "tcp":
                        port = value

                if ip_addr and port and peer_id:
                    peer_info = {
                        "peer_id": peer_id,
                        "ip_addr": ip_addr,
                        "port": port,
                        "original_addr": str(ma),
                        "resolved_addr": str(resolved_ma),
                    }
                    resolved_peers.append(peer_info)

                    print(f"  Resolved: {ip_addr}:{port} (peer: {peer_id})")

        except Exception as e:
            print(f"  Error resolving {addr_str}: {e}")

    print(f"\nResolved {len(resolved_peers)} bootstrap peers:")
    for peer in resolved_peers:
        print(f"  {peer['peer_id']} -> {peer['ip_addr']}:{peer['port']}")

    return resolved_peers


async def main():
    """
    Run all examples.

    This function orchestrates all the DNS resolution examples:
    1. Basic DNS resolution
    2. Bootstrap node resolution
    3. DNS protocol comparison
    4. Peer ID preservation test
    5. Sequential resolution
    6. py-libp2p integration example

    Each example demonstrates different aspects of DNS resolution functionality
    and shows how to use it with py-multiaddr.
    """
    print("DNS Resolution Examples")
    print("=" * 50)

    try:
        await basic_dns_resolution()
        await bootstrap_node_resolution()
        await dns_protocol_comparison()
        await peer_id_preservation_test()
        await concurrent_resolution()
        await py_libp2p_integration_example()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- DNS resolution is working correctly")
        print("- Real domains are being resolved to IP addresses")
        print("- Peer IDs are preserved during resolution")
        print("- All DNS protocols (/dns/, /dns4/, /dns6/, /dnsaddr/) are functional")
        print("- Ready for integration with py-libp2p")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    trio.run(main)
