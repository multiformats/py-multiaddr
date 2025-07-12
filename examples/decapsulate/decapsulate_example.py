#!/usr/bin/env python3
"""
Decapsulate Code Examples

This example demonstrates how to use the decapsulate_code method to remove
specific protocol layers from multiaddrs by their protocol codes.

The decapsulate_code method is useful for:
- Network protocol analysis
- Protocol stack manipulation
- Address transformation
- Debugging multiaddr structures
"""

import sys

from multiaddr import Multiaddr
from multiaddr.protocols import P_IP4, P_IP6, P_TCP, P_TLS, P_UDP


def print_separator(title):
    """Print a formatted separator with title."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_multiaddr_info(ma, description=""):
    """Print multiaddr information in a formatted way."""
    if description:
        print(f"\n{description}:")
    print(f"  String: {ma}")
    print(f"  Protocols: {[p.name for p in ma.protocols()]}")
    print(f"  Protocol codes: {[p.code for p in ma.protocols()]}")


def basic_decapsulate_examples():
    """Demonstrate basic decapsulate_code usage."""
    print_separator("Basic Decapsulate Code Examples")

    # Example 1: Remove TCP layer
    ma1 = Multiaddr("/ip4/192.168.1.1/tcp/8080/udp/1234")
    print_multiaddr_info(ma1, "Original multiaddr")

    # Remove TCP (protocol code 6) and everything after it
    result1 = ma1.decapsulate_code(P_TCP)
    print_multiaddr_info(result1, "After decapsulating TCP (code 6)")

    # Example 2: Remove UDP layer
    ma2 = Multiaddr("/ip4/10.0.0.1/udp/1234/tcp/8080")
    print_multiaddr_info(ma2, "Original multiaddr")

    result2 = ma2.decapsulate_code(P_UDP)
    print_multiaddr_info(result2, "After decapsulating UDP (code 17)")

    # Example 3: Remove IP layer
    ma3 = Multiaddr(
        "/ip4/172.16.0.1/tcp/443/tls/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    )
    print_multiaddr_info(ma3, "Original multiaddr")

    result3 = ma3.decapsulate_code(P_IP4)
    print_multiaddr_info(result3, "After decapsulating IP4 (code 4)")


def protocol_stack_analysis():
    """Demonstrate protocol stack analysis using decapsulate_code."""
    print_separator("Protocol Stack Analysis")

    # Complex multiaddr with multiple layers
    ma = Multiaddr(
        "/ip4/192.168.1.100/tcp/8080/tls/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    )
    print_multiaddr_info(ma, "Complex multiaddr")

    print("\nProtocol stack analysis:")
    current = ma
    layer = 1

    while str(current) != "/":
        print(f"  Layer {layer}: {current}")
        protocols = list(current.protocols())
        if protocols:
            # Remove the last protocol layer
            last_protocol = protocols[-1]
            current = current.decapsulate_code(last_protocol.code)
            layer += 1
        else:
            break


def address_transformation():
    """Demonstrate address transformation scenarios."""
    print_separator("Address Transformation Examples")

    # Example 1: Convert secure to insecure
    secure_addr = Multiaddr(
        "/ip4/10.0.0.1/tcp/443/tls/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    )
    print_multiaddr_info(secure_addr, "Secure address")

    # Remove TLS layer to get insecure version
    insecure_addr = secure_addr.decapsulate_code(P_TLS)
    print_multiaddr_info(insecure_addr, "Insecure version (TLS removed)")

    # Example 2: Extract base network address
    full_addr = Multiaddr("/ip6/2001:db8::1/tcp/8080/udp/1234/sctp/5678")
    print_multiaddr_info(full_addr, "Full address")

    # Remove all transport layers to get just the IP address
    base_addr = full_addr.decapsulate_code(P_TCP)
    print_multiaddr_info(base_addr, "Base network address (transport removed)")

    # Example 3: IPv4 to IPv6 conversion simulation
    ipv4_addr = Multiaddr("/ip4/192.168.1.1/tcp/8080")
    print_multiaddr_info(ipv4_addr, "IPv4 address")

    # Simulate removing IPv4 to prepare for IPv6 replacement
    transport_only = ipv4_addr.decapsulate_code(P_IP4)
    print_multiaddr_info(transport_only, "Transport layer only (IP removed)")


def error_handling_examples():
    """Demonstrate error handling with decapsulate_code."""
    print_separator("Error Handling Examples")

    # Example 1: Protocol not found
    ma = Multiaddr("/ip4/192.168.1.1/tcp/8080")
    print_multiaddr_info(ma, "Original address")

    try:
        # Try to remove a protocol that doesn't exist
        result = ma.decapsulate_code(P_UDP)  # UDP not in this address
        print_multiaddr_info(result, "After removing non-existent UDP")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 2: Empty multiaddr
    empty_ma = Multiaddr("/")
    print_multiaddr_info(empty_ma, "Empty multiaddr")

    try:
        result = empty_ma.decapsulate_code(P_TCP)
        print_multiaddr_info(result, "After decapsulating from empty")
    except Exception as e:
        print(f"  Error: {e}")


def practical_use_cases():
    """Demonstrate practical use cases for decapsulate_code."""
    print_separator("Practical Use Cases")

    # Use case 1: Network configuration analysis
    print("Use Case 1: Network Configuration Analysis")
    configs = [
        "/ip4/0.0.0.0/tcp/8080",
        "/ip4/0.0.0.0/tcp/8080/tls",
        "/ip6/::/tcp/8080/tls/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
        "/ip4/192.168.1.1/udp/1234",
    ]

    for config in configs:
        ma = Multiaddr(config)
        print(f"\n  Config: {ma}")

        # Check if it's a server config (has wildcard IP)
        if "0.0.0.0" in str(ma) or "::" in str(ma):
            print("    Type: Server binding address")
            # Extract transport info
            transport = ma.decapsulate_code(
                P_IP4 if P_IP4 in [p.code for p in ma.protocols()] else P_IP6
            )
            print(f"    Transport: {transport}")
        else:
            print("    Type: Client address")

    # Use case 2: Protocol compatibility checking
    print("\nUse Case 2: Protocol Compatibility Checking")
    addresses = [
        "/ip4/192.168.1.1/tcp/8080",
        "/ip4/192.168.1.1/tcp/8080/tls",
        "/ip6/2001:db8::1/udp/1234",
    ]

    for addr_str in addresses:
        ma = Multiaddr(addr_str)
        print(f"\n  Address: {ma}")

        # Check if supports TLS
        if P_TLS in [p.code for p in ma.protocols()]:
            print("    TLS: Supported")
            insecure = ma.decapsulate_code(P_TLS)
            print(f"    Insecure version: {insecure}")
        else:
            print("    TLS: Not supported")

        # Check transport protocol
        if P_TCP in [p.code for p in ma.protocols()]:
            print("    Transport: TCP")
        elif P_UDP in [p.code for p in ma.protocols()]:
            print("    Transport: UDP")


def main():
    """Run all decapsulate_code examples."""
    print("Decapsulate Code Examples")
    print("Demonstrating multiaddr protocol layer manipulation")

    try:
        basic_decapsulate_examples()
        protocol_stack_analysis()
        address_transformation()
        error_handling_examples()
        practical_use_cases()

        print_separator("Summary")
        print("The decapsulate_code method provides fine-grained control")
        print("over multiaddr protocol layers, enabling:")
        print("- Protocol stack analysis")
        print("- Address transformation")
        print("- Network configuration management")
        print("- Protocol compatibility checking")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running examples: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
