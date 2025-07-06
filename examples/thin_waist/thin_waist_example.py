#!/usr/bin/env python3
"""
Thin Waist Address Validation Example

This example demonstrates how to use the get_thin_waist_addresses function
to process multiaddrs and expand wildcard addresses to all available interfaces.

Usage:
    python examples/thin_waist/thin_waist_example.py [--detailed]
"""

import sys

from multiaddr import Multiaddr
from multiaddr.utils import get_network_addrs, get_thin_waist_addresses


def show_network_info():
    """Display available network interfaces."""
    print("=== Network Interface Information ===")

    # Get all IPv4 addresses
    ipv4_addrs = get_network_addrs(4)
    print(f"Available IPv4 addresses: {ipv4_addrs}")

    # Get all IPv6 addresses
    ipv6_addrs = get_network_addrs(6)
    print(f"Available IPv6 addresses: {ipv6_addrs}")
    print()


def basic_examples():
    """Show basic thin waist address validation examples."""
    print("=== Basic Examples ===")

    # Example 1: Specific address (no expansion)
    print("\n1. Specific IP address:")
    addr = Multiaddr("/ip4/192.168.1.100/tcp/8080")
    print(f"   Input:  {addr}")
    result = get_thin_waist_addresses(addr)
    print(f"   Output: {result}")

    # Example 2: IPv4 wildcard expansion
    print("\n2. IPv4 wildcard expansion:")
    addr = Multiaddr("/ip4/0.0.0.0/tcp/8080")
    print(f"   Input:  {addr}")
    result = get_thin_waist_addresses(addr)
    print("   Output:")
    for i, expanded in enumerate(result, 1):
        print(f"     {i}. {expanded}")

    # Example 3: IPv6 wildcard expansion
    print("\n3. IPv6 wildcard expansion:")
    addr = Multiaddr("/ip6/::/tcp/8080")
    print(f"   Input:  {addr}")
    result = get_thin_waist_addresses(addr)
    print("   Output:")
    for i, expanded in enumerate(result, 1):
        print(f"     {i}. {expanded}")

    # Example 4: Port override
    print("\n4. Port override:")
    addr = Multiaddr("/ip4/0.0.0.0/tcp/8080")
    print(f"   Input:  {addr} (override port to 9000)")
    result = get_thin_waist_addresses(addr, port=9000)
    print("   Output:")
    for i, expanded in enumerate(result, 1):
        print(f"     {i}. {expanded}")

    # Example 5: No input
    print("\n5. No input:")
    result = get_thin_waist_addresses()
    print(f"   Output: {result}")


def detailed_examples():
    """Show detailed examples with more edge cases and explanations."""
    print("\n=== Detailed Examples ===")

    # Example: UDP transport
    print("\n6. UDP transport:")
    addr = Multiaddr("/ip4/0.0.0.0/udp/1234")
    print(f"   Input:  {addr}")
    result = get_thin_waist_addresses(addr)
    print("   Output:")
    for i, expanded in enumerate(result, 1):
        print(f"     {i}. {expanded}")

    # Example: Port override on specific address
    print("\n7. Port override on specific address:")
    addr = Multiaddr("/ip4/192.168.1.100/tcp/8080")
    print(f"   Input:  {addr}")
    result = get_thin_waist_addresses(addr, port=9000)
    print(f"   Output: {result}")

    # Example: Error handling
    print("\n8. Error handling:")
    try:
        # Try to create an invalid multiaddr
        addr = Multiaddr("/ip4/192.168.1.100/udp/1234/webrtc")
        print(f"   Created address: {addr}")

        # This should return empty list for non-thin-waist addresses
        addrs = get_thin_waist_addresses(addr)
        print(f"   Thin waist addresses: {addrs}")

    except Exception as e:
        print(f"   Error creating invalid address: {e}")


def usage_examples():
    """Show practical usage examples."""
    print("\n=== Practical Usage Examples ===")

    print("\n9. Server binding scenario:")
    print("   When you want to bind a server to all interfaces:")
    wildcard = Multiaddr("/ip4/0.0.0.0/tcp/8080")
    interfaces = get_thin_waist_addresses(wildcard)
    print(f"   Wildcard: {wildcard}")
    print("   Available interfaces:")
    for i, interface in enumerate(interfaces, 1):
        print(f"     {i}. {interface}")

    print("\n10. Port configuration scenario:")
    print("    When you need to change the port dynamically:")
    original = Multiaddr("/ip4/0.0.0.0/tcp/8080")
    new_port = 9000
    updated = get_thin_waist_addresses(original, port=new_port)
    print(f"    Original: {original}")
    print(f"    New port: {new_port}")
    print("    Updated interfaces:")
    for i, interface in enumerate(updated, 1):
        print(f"      {i}. {interface}")


def main():
    """Run the thin waist address validation examples."""
    print("Thin Waist Address Validation Example")
    print("=" * 50)

    # Check for detailed mode
    detailed = "--detailed" in sys.argv

    # Show network information
    show_network_info()

    # Show basic examples
    basic_examples()

    # Show detailed examples if requested
    if detailed:
        detailed_examples()
        usage_examples()

    print("\n" + "=" * 50)
    print("Example completed!")
    if not detailed:
        print("Run with --detailed flag for more examples and edge cases.")


if __name__ == "__main__":
    main()
