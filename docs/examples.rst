Examples
========

This section provides practical examples of how to use the multiaddr library for various use cases.

DNS Resolution Examples
-----------------------

The `examples/dns/` directory contains comprehensive examples demonstrating DNS-based address resolution.

.. code-block:: python

    # Basic DNS resolution with multiple protocols
    from multiaddr import Multiaddr
    import trio

    async def main():
        # Standard DNS resolution
        ma = Multiaddr("/dns/example.com")
        resolved = await ma.resolve()
        print(f"Resolved: {resolved}")

        # DNS4 (IPv4-specific) resolution
        ma_dns4 = Multiaddr("/dns4/example.com/tcp/443")
        resolved_dns4 = await ma_dns4.resolve()
        print(f"DNS4 resolved: {resolved_dns4}")

        # DNS6 (IPv6-specific) resolution
        ma_dns6 = Multiaddr("/dns6/example.com/tcp/443")
        resolved_dns6 = await ma_dns6.resolve()
        print(f"DNS6 resolved: {resolved_dns6}")

    trio.run(main)

Key features demonstrated:
- Standard DNS resolution for both IPv4 and IPv6
- Protocol-specific DNS resolution (dns4/dns6)
- Peer ID preservation during resolution
- Bootstrap node resolution using real libp2p nodes
- Error handling and timeout management

See `examples/dns/dns_examples.py` for the complete implementation.

DNSADDR Examples
----------------

The `examples/dnsaddr/` directory shows how to work with DNSADDR records for libp2p bootstrap nodes.

.. code-block:: python

    from multiaddr import Multiaddr
    import trio

    async def main():
        # DNSADDR resolution with peer ID
        ma = Multiaddr("/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN")
        resolved = await ma.resolve()

        for addr in resolved:
            print(f"Bootstrap node: {addr}")
            peer_id = addr.get_peer_id()
            print(f"  Peer ID: {peer_id}")

    trio.run(main)

This example demonstrates:
- DNSADDR record parsing and resolution
- Peer ID extraction and preservation
- Bootstrap node discovery
- TXT record processing

See `examples/dnsaddr/dnsaddr.py` for the complete implementation.

Thin Waist Address Examples
---------------------------

The `examples/thin_waist/` directory demonstrates thin waist address validation and network interface discovery.

.. code-block:: python

    from multiaddr import Multiaddr
    from multiaddr.utils import get_thin_waist_addresses

    # Network interface discovery
    addr = Multiaddr("/ip4/0.0.0.0/tcp/8080")
    interfaces = get_thin_waist_addresses(addr)

    print("Available interfaces:")
    for i, interface in enumerate(interfaces, 1):
        print(f"  {i}. {interface}")

    # IPv6 wildcard expansion
    addr_ipv6 = Multiaddr("/ip6/::/tcp/8080")
    interfaces_ipv6 = get_thin_waist_addresses(addr_ipv6)

    print("IPv6 interfaces:")
    for interface in interfaces_ipv6:
        print(f"  {interface}")

This example shows:
- Network interface discovery
- Wildcard address expansion
- IPv4 and IPv6 support
- Port management
- Server binding scenarios

See `examples/thin_waist/thin_waist_example.py` for the complete implementation.

Decapsulate Code Examples
-------------------------

The `examples/decapsulate/` directory demonstrates how to use the `decapsulate_code` method for protocol layer manipulation.

.. code-block:: python

    from multiaddr import Multiaddr
    from multiaddr.protocols import P_TCP, P_TLS

    # Remove specific protocol layers by code
    ma = Multiaddr("/ip4/192.168.1.1/tcp/8080/tls/p2p/QmPeer")
    print(f"Original: {ma}")

    # Remove TLS layer
    without_tls = ma.decapsulate_code(P_TLS)
    print(f"Without TLS: {without_tls}")

    # Remove TCP and everything after
    base_addr = ma.decapsulate_code(P_TCP)
    print(f"Base address: {base_addr}")

This example demonstrates:
- Protocol code-based layer removal
- Protocol stack analysis
- Address transformation
- Error handling for edge cases
- Practical network configuration scenarios

See `examples/decapsulate/decapsulate_example.py` for the complete implementation.

Running the Examples
--------------------

All examples can be run directly with Python:

.. code-block:: bash

    # DNS examples
    python examples/dns/dns_examples.py

    # DNSADDR examples
    python examples/dnsaddr/dnsaddr.py

    # Thin waist examples
    python examples/thin_waist/thin_waist_example.py

    # Decapsulate examples
    python examples/decapsulate/decapsulate_example.py

Note: Some examples require network connectivity and may take a few seconds to complete due to DNS resolution.
