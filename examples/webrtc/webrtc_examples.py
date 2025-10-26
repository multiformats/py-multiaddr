#!/usr/bin/env python3
"""
WebRTC and WebRTC-Direct protocol examples for py-multiaddr.

This script demonstrates how to use the 'webrtc' and 'webrtc-direct'
protocols in py-multiaddr. Both are "tag" protocols that take no arguments.

## Overview

This script shows various examples of WebRTC protocol usage:

1. **Basic `webrtc-direct` Usage**: Creating and parsing /webrtc-direct.
2. **Basic `webrtc` Usage**: Creating and parsing /webrtc.
3. **Protocol Validation**: Testing valid (tag-only) and invalid (with value)
   addresses for both protocols.
4. **Binary Encoding/Decoding**: Working with binary representations.
5. **Multiaddr Integration**:
   - Using 'webrtc-direct' in a peer-to-peer stack.
   - Using 'webrtc' in a relayed (p2p-circuit) stack.
6. **Error Handling**: Demonstrating errors when a value is incorrectly
   provided.

## Expected Output

When you run this script, you should see output similar to:

```
WebRTC/WebRTC-Direct Protocol Examples
==================================================

=== Basic webrtc-direct Usage ===
Original: /webrtc-direct
    Protocols: ['webrtc-direct']
    Binary length: 2 bytes
    Valid address: True

=== Basic webrtc Usage ===
Original: /webrtc
    Protocols: ['webrtc']
    Binary length: 2 bytes
    Valid address: True

=== Protocol Validation ===
Testing valid /webrtc-direct:
    Valid: True
    Protocols: ['webrtc-direct']

Testing invalid /webrtc-direct (with value): /webrtc-direct/value
    Valid: False
    Error: Protocol 'webrtc-direct' does not take an argument

Testing valid /webrtc:
        Valid: True
        Protocols: ['webrtc']

Testing invalid /webrtc (with value): /webrtc/value
    Valid: False
    Error: Protocol 'webrtc' does not take an argument

=== Binary Encoding/Decoding ===
webrtc-direct binary operations:
Original: /webrtc-direct
    Binary: 2 bytes
    Round-trip: /webrtc-direct
    Match: True

webrtc binary operations:
Original: /webrtc
    Binary: 2 bytes
    Round-trip: /webrtc
    Match: True

=== Multiaddr Integration ===
Complex multiaddr with webrtc-direct:
    Address: /ip4/1.2.3.4/udp/9090/webrtc-direct/certhash/uEiAsGP...
    Protocols: ['ip4', 'udp', 'webrtc-direct', '`certhash`']
    Has 'webrtc-direct' protocol: True

Complex multiaddr with webrtc (relayed):
    Address: /dns4/relay.com/tcp/443/wss/p2p/QmRelay/p2p-circuit/webrtc
    Protocols: ['dns4', 'tcp', 'wss', 'p2p', 'p2p-circuit', 'webrtc']
    Has 'webrtc' protocol: True

==================================================
All examples completed!
```
## Key Features Demonstrated

- **`webrtc-direct` Protocol**: Represents a direct, peer-to-peer WebRTC
  connection.
- **`webrtc` Protocol**: Represents a relayed WebRTC connection.
- **Tag Protocols**: Both are tag-only and take no arguments.
- **Validation**: Ensures no value is provided to either protocol.
- **Binary Operations**: Encoding and decoding to/from binary format.
- **Multiaddr Integration**: Using both protocols in realistic stacks.
- **Error Handling**: Proper error handling for invalid formats.

## Requirements

- Python 3.10+
- py-multiaddr library

## Usage

```bash
python examples/webrtc_examples.py
```
"""

from multiaddr import Multiaddr

WEBRTC_DIRECT_ADDR = "/webrtc-direct"
WEBRTC_ADDR = "/webrtc"


def basic_webrtc_direct_usage():
    """
    Basic webrtc-direct usage example.

    This function demonstrates:
    - Creating a `webrtc-direct` multiaddr
    - Extracting protocol information
    - Getting binary representation
    """
    print("=== Basic `webrtc-direct` Usage ===")
    print(f"Original: {WEBRTC_DIRECT_ADDR}")

    try:
        ma = Multiaddr(WEBRTC_DIRECT_ADDR)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        print("Valid address: True")

    except Exception as e:
        print(f"Error: {e}")
        print("Valid address: False")


def basic_webrtc_usage():
    """
    Basic webrtc usage example.

    This function demonstrates:
    - Creating a `webrtc` multiaddr
    - Extracting protocol information
    - Getting binary representation
    """
    print("\n=== Basic `webrtc` Usage ===")
    print(f"Original: {WEBRTC_ADDR}")

    try:
        ma = Multiaddr(WEBRTC_ADDR)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        print("Valid address: True")

    except Exception as e:
        print(f"Error: {e}")
        print("Valid address: False")


def protocol_validation():
    """
    Demonstrate protocol validation for both protocols.

    This function shows:
    - Valid tag-only addresses
    - Invalid addresses (with a value)
    - Error handling for validation failures
    """
    print("\n=== Protocol Validation ===")

    # Test valid `webrtc-direct`
    print("Testing valid /webrtc-direct:")
    try:
        ma = Multiaddr(WEBRTC_DIRECT_ADDR)
        print("  Valid: True")
        print(f"  Protocols: {[p.name for p in ma.protocols()]}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid `webrtc-direct` (with a value)
    invalid_addr_str = "/webrtc-direct/value"
    print(f"Testing invalid /webrtc-direct (with value): {invalid_addr_str}")
    try:
        Multiaddr(invalid_addr_str)
        print("  Valid: True (ERROR: Should have failed)")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test valid `webrtc`
    print("Testing valid /webrtc:")
    try:
        ma = Multiaddr(WEBRTC_ADDR)
        print("  Valid: True")
        print(f"  Protocols: {[p.name for p in ma.protocols()]}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid `webrtc` (with a value)
    invalid_addr_str = "/webrtc/value"
    print(f"Testing invalid /webrtc (with value): {invalid_addr_str}")
    try:
        Multiaddr(invalid_addr_str)
        print("  Valid: True (ERROR: Should have failed)")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")


def binary_encoding_decoding():
    """
    Demonstrate binary encoding and decoding for both protocols.

    This function shows:
    - Converting multiaddr to binary
    - Converting binary back to multiaddr
    - Round-trip validation
    """
    print("\n=== Binary Encoding/Decoding ===")

    print("`webrtc-direct` binary operations:")
    try:
        ma = Multiaddr(WEBRTC_DIRECT_ADDR)
        binary_data = ma.to_bytes()
        print(f"  Original: {WEBRTC_DIRECT_ADDR}")
        print(f"  Binary: {len(binary_data)} bytes")
        round_trip_ma = Multiaddr(binary_data)
        print(f"  Round-trip: {round_trip_ma}")
        print(f"  Match: {str(ma) == str(round_trip_ma)}")
    except Exception as e:
        print(f"  Error: {e}")

    print("`webrtc` binary operations:")
    try:
        ma = Multiaddr(WEBRTC_ADDR)
        binary_data = ma.to_bytes()
        print(f"  Original: {WEBRTC_ADDR}")
        print(f"  Binary: {len(binary_data)} bytes")
        round_trip_ma = Multiaddr(binary_data)
        print(f"  Round-trip: {round_trip_ma}")
        print(f"  Match: {str(ma) == str(round_trip_ma)}")
    except Exception as e:
        print(f"  Error: {e}")


def multiaddr_integration():
    """
    Demonstrate WebRTC protocol integration with other protocols.

    This function shows:
    - Using /webrtc-direct in a P2P stack with /certhash.
    - Using /webrtc in a relayed (p2p-circuit) stack.
    """
    print("\n=== Multiaddr Integration ===")

    # Example 1: `webrtc-direct`
    # A typical address for a direct peer-to-peer WebRTC connection
    certhash = "uEiDDq4_xNyDorZBH3TlGazyJdOWSwvo4PUo5YHFMrvDE8g"
    complex_addr_direct = f"/ip4/1.2.3.4/udp/9090/webrtc-direct/certhash/{certhash}"

    print("Complex multiaddr with `webrtc-direct`:")
    print(f"  Address: /ip4/1.2.3.4/udp/9090/webrtc-direct/certhash/{certhash}")

    try:
        ma = Multiaddr(complex_addr_direct)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")
        has_protocol = "webrtc-direct" in protocols
        print(f"  Has 'webrtc-direct' protocol: {has_protocol}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 2: `webrtc` (relayed)
    # A typical address for a browser connecting to a peer via a relay
    relay_id = "QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    complex_addr_relayed = f"/dns4/relay.com/tcp/443/wss/p2p/{relay_id}/p2p-circuit/webrtc"

    print("\nComplex multiaddr with `webrtc` (relayed):")
    print(f"  Address: {complex_addr_relayed}")

    try:
        ma = Multiaddr(complex_addr_relayed)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")
        has_protocol = "webrtc" in protocols
        print(f"  Has 'webrtc' protocol: {has_protocol}")
    except Exception as e:
        print(f"  Error: {e}")


def main():
    """
    Run all WebRTC and WebRTC-Direct protocol examples.
    """
    print("WebRTC / WebRTC-Direct Protocol Examples")
    print("=" * 50)

    try:
        basic_webrtc_direct_usage()
        basic_webrtc_usage()
        protocol_validation()
        binary_encoding_decoding()
        multiaddr_integration()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- `webrtc-direct` and `webrtc` protocols are working")
        print("- Binary encoding/decoding functions properly")
        print("- Validation catches invalid use (with a value)")
        print("- Integration with P2P stacks works as expected")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
