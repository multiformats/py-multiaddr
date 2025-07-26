#!/usr/bin/env python3
"""
Simple QUIC Protocol Usage Examples

This shows the most common ways to use QUIC and QUIC-v1 protocols
in the py-multiaddr implementation.
"""

from multiaddr import Multiaddr
from multiaddr.protocols import P_QUIC1


def main():
    print("Simple QUIC Protocol Usage Examples")
    print("=" * 40)

    # 1. Basic QUIC addresses
    print("\n1. Basic QUIC Addresses:")

    # QUIC over UDP
    quic_addr = Multiaddr("/ip4/127.0.0.1/udp/4001/quic")
    print(f"   QUIC: {quic_addr}")

    # QUIC-v1 over UDP (newer version)
    quic_v1_addr = Multiaddr("/ip4/127.0.0.1/udp/4001/quic-v1")
    print(f"   QUIC-v1: {quic_v1_addr}")

    # IPv6 with QUIC
    quic_ipv6 = Multiaddr("/ip6/::1/udp/4001/quic-v1")
    print(f"   IPv6 QUIC: {quic_ipv6}")

    # 2. QUIC with peer IDs (libp2p style)
    print("\n2. QUIC with Peer IDs (libp2p):")

    quic_with_peer = Multiaddr(
        "/ip4/127.0.0.1/udp/4001/quic-v1/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    )
    print(f"   Address: {quic_with_peer}")
    print(f"   Peer ID: {quic_with_peer.get_peer_id()}")

    # 3. Protocol analysis
    print("\n3. Protocol Analysis:")

    protocols = list(quic_v1_addr.protocols())
    print(f"   Protocol stack for {quic_v1_addr}:")
    for i, proto in enumerate(protocols):
        print(f"     {i + 1}. {proto.name} (code: {proto.code})")

    # 4. Address manipulation
    print("\n4. Address Manipulation:")

    # Encapsulation: add QUIC layer to existing address
    base = Multiaddr("/ip4/192.168.1.100/udp/4001")
    quic_layer = Multiaddr("/quic-v1")
    combined = base.encapsulate(quic_layer)
    print(f"   Base: {base}")
    print(f"   + QUIC: {quic_layer}")
    print(f"   = Result: {combined}")

    # Decapsulation: remove QUIC layer
    without_quic = combined.decapsulate_code(P_QUIC1)
    print(f"   Without QUIC: {without_quic}")

    # 5. Binary representation
    print("\n5. Binary Representation:")

    binary = quic_v1_addr.to_bytes()
    print(f"   String: {quic_v1_addr}")
    print(f"   Binary: {binary.hex()}")
    print(f"   Size: {len(binary)} bytes")

    # 6. Validation examples
    print("\n6. Validation Examples:")

    valid_examples = [
        "/ip4/127.0.0.1/udp/4001/quic",
        "/ip4/127.0.0.1/udp/4001/quic-v1",
        "/ip6/::1/udp/4001/quic-v1",
    ]

    print("   Valid QUIC addresses:")
    for addr_str in valid_examples:
        try:
            ma = Multiaddr(addr_str)
            print(f"     ✅ {ma}")
        except Exception as e:
            print(f"     ❌ {addr_str} - {e}")

    invalid_examples = [
        "/ip4/127.0.0.1/tcp/4001/quic",  # QUIC over TCP (invalid)
        "/ip4/127.0.0.1/udp/4001/quic/1234",  # QUIC with port (invalid)
    ]

    print("   Invalid QUIC addresses:")
    for addr_str in invalid_examples:
        try:
            ma = Multiaddr(addr_str)
            print(f"     ⚠️  {ma} (unexpectedly valid)")
        except Exception as e:
            print(f"     ❌ {addr_str} - {e}")

    print("\n" + "=" * 40)
    print("Key Points:")
    print("- QUIC protocols are flag protocols (no additional data)")
    print("- Must be used with UDP transport (not TCP)")
    print("- QUIC-v1 is the newer, recommended version")
    print("- Common in libp2p networks for secure communication")
    print("- Can be combined with peer IDs for P2P networking")


if __name__ == "__main__":
    main()
