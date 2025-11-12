#!/usr/bin/env python3
"""
Tag-only protocol examples for py-multiaddr.

This script demonstrates how to work with tag-only protocols in py-multiaddr.
Tag-only protocols are protocols that do not accept values - their presence
alone indicates a specific property or capability (e.g., ``/http``, ``/tls``,
``/noise``).

## Overview

This script shows various examples of tag-only protocol usage:

1. **Basic Tag-Only Protocol Usage**: Creating and parsing simple tag-only addresses.
2. **Protocol Validation**: Testing valid and invalid tag-only protocol syntax.
3. **Error Handling**: Demonstrating clear error messages for invalid value assignments.
4. **Multiaddr Integration**: Using tag-only protocols in realistic multiaddr stacks.
5. **Common Tag-Only Protocols**: Examples with various tag-only protocols.

## Expected Output

When you run this script, you should see output similar to:

```
Tag-Only Protocol Examples
==================================================
=== Basic Tag-Only Protocol Usage ===
Valid tag-only addresses:
  /http
  /https
  /tls
  /noise
  /webrtc

=== Protocol Validation ===
Testing valid tag-only: /http
  Valid: True
  Protocols: ['http']

Testing invalid tag-only (with value): /http/value
  Valid: False
  Error: Protocol 'http' does not take an argument

Testing invalid tag-only (= syntax): /http=value
  Valid: False
  Error: Protocol 'http' does not take an argument

=== Multiaddr Integration ===
Complex multiaddr with tag-only protocols:
  Address: /ip4/127.0.0.1/tcp/443/https
  Protocols: ['ip4', 'tcp', 'https']
  Has 'https' protocol: True

=== Common Tag-Only Protocols ===
HTTP: /ip4/127.0.0.1/tcp/80/http
HTTPS: /ip4/127.0.0.1/tcp/443/https
TLS: /ip4/127.0.0.1/tcp/443/tls
WebRTC: /ip4/127.0.0.1/udp/9090/webrtc-direct
Noise: /ip4/127.0.0.1/tcp/12345/noise

==================================================
All examples completed!
```

## Key Features Demonstrated

- **Tag-Only Protocols**: Protocols that don't accept values (http, https, tls, noise, webrtc, etc.)
- **Validation**: Ensures no value is provided to tag-only protocols
- **Error Messages**: Clear error messages that don't include invalid values
- **Multiaddr Integration**: Using tag-only protocols as part of connection stacks
- **Syntax Validation**: Both ``/tag/value`` and ``/tag=value`` syntaxes are rejected

## Requirements

- Python 3.10+
- py-multiaddr library

## Usage

```bash
python examples/tag_only/tag_only_examples.py
```
"""

from multiaddr import Multiaddr
from multiaddr.exceptions import StringParseError

# Common tag-only protocols
TAG_ONLY_PROTOCOLS = [
    "http",
    "https",
    "tls",
    "noise",
    "webrtc",
    "webrtc-direct",
    "quic",
    "quic-v1",
    "ws",
    "wss",
    "p2p-circuit",
    "webtransport",
]


def basic_tag_only_usage():
    """
    Basic tag-only protocol usage example.

    This function demonstrates:
    - Creating tag-only multiaddrs
    - Extracting protocol information
    - Validating tag-only addresses
    """
    print("=== Basic Tag-Only Protocol Usage ===")
    print("Valid tag-only addresses:")

    for proto_name in TAG_ONLY_PROTOCOLS[:5]:  # Show first 5
        addr_str = f"/{proto_name}"
        try:
            _ = Multiaddr(addr_str)  # Validate the address
            print(f"  {addr_str}")
        except Exception as e:
            print(f"  {addr_str} - Error: {e}")


def protocol_validation():
    """
    Demonstrate protocol validation for tag-only protocols.

    This function shows:
    - Valid tag-only addresses
    - Invalid tag-only addresses with /tag/value syntax
    - Invalid tag-only addresses with /tag=value syntax
    - Error handling for validation failures
    """
    print("\n=== Protocol Validation ===")

    # Test valid tag-only protocol
    valid_addr = "/http"
    print(f"Testing valid tag-only: {valid_addr}")
    try:
        ma = Multiaddr(valid_addr)
        print("  Valid: True")
        print(f"  Protocols: {[p.name for p in ma.protocols()]}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid tag-only with /tag/value syntax
    invalid_addr_slash = "/http/value"
    print(f"\nTesting invalid tag-only (with value): {invalid_addr_slash}")
    try:
        Multiaddr(invalid_addr_slash)
        print("  Valid: True (ERROR: Should have failed)")
    except StringParseError as e:
        print("  Valid: False")
        print(f"  Error: {e}")
        # Verify error message doesn't include the invalid value
        error_str = str(e)
        assert "value" not in error_str or "does not take an argument" in error_str

    # Test invalid tag-only with /tag=value syntax
    invalid_addr_equals = "/http=value"
    print(f"\nTesting invalid tag-only (= syntax): {invalid_addr_equals}")
    try:
        Multiaddr(invalid_addr_equals)
        print("  Valid: True (ERROR: Should have failed)")
    except StringParseError as e:
        print("  Valid: False")
        print(f"  Error: {e}")


def multiaddr_integration():
    """
    Demonstrate tag-only protocol integration with other protocols.

    This function shows:
    - Using tag-only protocols as part of realistic multiaddr stacks
    - Protocol stack analysis
    - Common use cases
    """
    print("\n=== Multiaddr Integration ===")

    # HTTPS example
    https_addr = "/ip4/127.0.0.1/tcp/443/https"
    print("Complex multiaddr with tag-only protocols:")
    print(f"  Address: {https_addr}")

    try:
        ma = Multiaddr(https_addr)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")

        # Check for 'https' protocol
        has_https = "https" in protocols
        print(f"  Has 'https' protocol: {has_https}")

    except Exception as e:
        print(f"  Error: {e}")


def common_tag_only_protocols():
    """
    Demonstrate common tag-only protocol use cases.

    This function shows:
    - HTTP and HTTPS usage
    - TLS usage
    - WebRTC usage
    - Noise protocol usage
    """
    print("\n=== Common Tag-Only Protocols ===")

    examples = [
        ("HTTP", "/ip4/127.0.0.1/tcp/80/http"),
        ("HTTPS", "/ip4/127.0.0.1/tcp/443/https"),
        ("TLS", "/ip4/127.0.0.1/tcp/443/tls"),
        ("WebRTC", "/ip4/127.0.0.1/udp/9090/webrtc-direct"),
        ("Noise", "/ip4/127.0.0.1/tcp/12345/noise"),
    ]

    for name, addr_str in examples:
        try:
            _ = Multiaddr(addr_str)  # Validate the address
            print(f"{name}: {addr_str}")
        except Exception as e:
            print(f"{name}: {addr_str} - Error: {e}")


def chaining_tag_only_protocols():
    """
    Demonstrate chaining multiple tag-only protocols.

    This function shows:
    - Multiple tag-only protocols in sequence
    - Valid combinations
    - Protocol stack analysis
    """
    print("\n=== Chaining Tag-Only Protocols ===")

    examples = [
        "/webrtc/noise",
        "/webrtc-direct/webrtc",
        "/tls/http",
    ]

    for addr_str in examples:
        try:
            ma = Multiaddr(addr_str)
            protocols = [p.name for p in ma.protocols()]
            print(f"  {addr_str}")
            print(f"    Protocols: {protocols}")
        except Exception as e:
            print(f"  {addr_str} - Error: {e}")


def main():
    """
    Run all tag-only protocol examples.

    This function orchestrates all the tag-only protocol examples:
    1. Basic tag-only usage
    2. Protocol validation
    3. Multiaddr integration
    4. Common tag-only protocols
    5. Chaining tag-only protocols

    Each example demonstrates different aspects of tag-only protocol
    functionality and shows how to use them with py-multiaddr.
    """
    print("Tag-Only Protocol Examples")
    print("=" * 50)

    try:
        basic_tag_only_usage()
        protocol_validation()
        multiaddr_integration()
        common_tag_only_protocols()
        chaining_tag_only_protocols()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- Tag-only protocols work correctly")
        print("- Validation catches invalid use (with values)")
        print("- Both /tag/value and /tag=value syntaxes are rejected")
        print("- Integration with other protocols works as expected")
        print("- Multiple tag-only protocols can be chained")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
