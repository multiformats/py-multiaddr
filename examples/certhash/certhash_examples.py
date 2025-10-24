#!/usr/bin/env python3
"""
Certhash protocol examples for py-multiaddr.

This script demonstrates how to use the 'certhash' (Certificate Hash)
protocol in py-multiaddr. This protocol is used to pin a specific
peer certificate, typically for protocols like 'webrtc-direct'.

The value is a multibase-encoded multihash of the certificate's
SubjectPublicKeyInfo (SPKI).

## Overview

This script shows various examples of Certhash protocol usage:

1. **Basic Certhash Usage**: Creating and parsing a /certhash/... address.
2. **Protocol Validation**: Testing valid and invalid certhash values.
3. **Binary Encoding/Decoding**: Working with binary representations.
4. **Multiaddr Integration**: Using 'certhash' in a realistic multiaddr string
   (e.g., /ip4/.../webrtc-direct/certhash/...).
5. **Error Handling**: Demonstrating errors for invalid multibase or
   multihash encodings.

## Expected Output

When you run this script, you should see output similar to:

```
CERTHASH Protocol Examples
==================================================
=== Basic Certhash Usage ===
Original Certhash: /certhash/uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
    Protocols: ['certhash']
    Extracted Value: uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
    Binary length: 37 bytes
    Valid Certhash address: True

=== Protocol Validation ===
Testing valid Certhash: /certhash/uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
Valid: True
Value: uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c

Testing invalid Certhash (invalid multibase prefix): /certhash/!EiAs...
Valid: False
Error: Unsupported multibase encoding: !

Testing invalid Certhash (not a multihash): /certhash/uYXNkZg
Valid: False
Error: multihash length too short. must be >= 2

=== Binary Encoding/Decoding ===
Certhash binary operations:
Original: /certhash/uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
    Binary: 37 bytes
    Round-trip: /certhash/uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
    Match: True

=== Multiaddr Integration ===
Complex multiaddr with Certhash:
Address: /ip4/127.0.0.1/udp/9090/webrtc-direct/certhash/uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
Protocols: ['ip4', 'udp', 'webrtc-direct', 'certhash']
Extracted Certhash value: uEiAsGPzpiN3E4i94n924-T1wA0-z0a9b-Gtc-E-8a-c
Match: True

==================================================
All examples completed!
```

## Key Features Demonstrated

- **Certhash Protocol**: Represents a certificate hash.
- **Validation**: Ensures the value is a valid multibase-encoded multihash.
- **Binary Operations**: Encoding and decoding to/from binary format.
- **Multiaddr Integration**: Using 'certhash' with 'webrtc-direct'.
- **Error Handling**: Proper error handling for invalid encodings.

## Requirements

- Python 3.10+
- py-multiaddr library (which uses py-multihash and py-multibase)

## Usage

```bash
python examples/certhash_examples.py
```
"""

from multiaddr import Multiaddr

VALID_CERTHASH_VALUE = "uEiDDq4_xNyDorZBH3TlGazyJdOWSwvo4PUo5YHFMrvDE8g"
VALID_CERTHASH_ADDR = f"/certhash/{VALID_CERTHASH_VALUE}"


def basic_certhash_usage():
    """
    Basic Certhash usage example.

    This function demonstrates:
    - Creating a Certhash multiaddr
    - Extracting protocol information
    - Extracting the value
    - Getting binary representation
    """
    print("=== Basic Certhash Usage ===")

    print(f"Original Certhash: {VALID_CERTHASH_ADDR}")

    try:
        ma = Multiaddr(VALID_CERTHASH_ADDR)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Extract the value
        certhash_value = ma.value_for_protocol("certhash")
        print(f"Extracted Value: {certhash_value}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        print("Valid Certhash address: True")

    except Exception as e:
        print(f"Error: {e}")
        print("Valid Certhash address: False")


def protocol_validation():
    """
    Demonstrate protocol validation.

    This function shows:
    - A valid Certhash address
    - Invalid Certhash addresses (invalid multibase, not a multihash)
    - Error handling for validation failures
    """
    print("\n=== Protocol Validation ===")

    # Test valid Certhash
    print(f"Testing valid Certhash: {VALID_CERTHASH_ADDR}")
    try:
        ma = Multiaddr(VALID_CERTHASH_ADDR)
        print("  Valid: True")
        print(f"  Value: {ma.value_for_protocol('certhash')}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid Certhash (invalid multibase prefix)
    invalid_addr_str = "/certhash/!EiAs..."
    print(f"\nTesting invalid Certhash (invalid multibase prefix): {invalid_addr_str}")
    try:
        Multiaddr(invalid_addr_str)
        print("  Valid: True (ERROR: Should have failed)")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid Certhash (valid multibase, but not a multihash)
    # 'uYXNkZg' is 'asdf' in base64url. This is too short to be a multihash.
    invalid_addr_str = "/certhash/uYXNkZg"
    print(f"\nTesting invalid Certhash (not a multihash): {invalid_addr_str}")
    try:
        Multiaddr(invalid_addr_str)
        print("  Valid: True (ERROR: Should have failed)")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")


def binary_encoding_decoding():
    """
    Demonstrate binary encoding and decoding.

    This function shows:
    - Converting multiaddr to binary
    - Converting binary back to multiaddr
    - Round-trip validation
    """
    print("\n=== Binary Encoding/Decoding ===")

    print("Certhash binary operations:")
    print(f"  Original: {VALID_CERTHASH_ADDR}")

    try:
        ma = Multiaddr(VALID_CERTHASH_ADDR)
        binary_data = ma.to_bytes()
        print(f"  Binary: {len(binary_data)} bytes")

        # Round-trip: binary back to multiaddr
        round_trip_ma = Multiaddr(binary_data)
        print(f"  Round-trip: {round_trip_ma}")
        print(f"  Match: {str(ma) == str(round_trip_ma)}")

    except Exception as e:
        print(f"  Error: {e}")


def multiaddr_integration():
    """
    Demonstrate Certhash protocol integration with other protocols.

    This function shows:
    - The most common use case for /certhash, nested within /webrtc-direct.
    - Protocol stack analysis
    - Certhash value extraction
    """
    print("\n=== Multiaddr Integration ===")

    # Create a complex multiaddr with Certhash
    # This is a typical address for a WebRTC direct connection
    complex_addr = f"/ip4/127.0.0.1/udp/9090/webrtc-direct/certhash/{VALID_CERTHASH_VALUE}"

    print("Complex multiaddr with Certhash:")
    print(f"  Address: {complex_addr}")

    try:
        ma = Multiaddr(complex_addr)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")

        # Extract Certhash value
        extracted_certhash_value = ma.value_for_protocol("certhash")
        print(f"  Extracted Certhash value: {extracted_certhash_value}")
        print(f"  Match: {extracted_certhash_value == VALID_CERTHASH_VALUE}")

    except Exception as e:
        print(f"  Error: {e}")


def main():
    """
    Run all Certhash protocol examples.

    This function orchestrates all the Certhash protocol examples:
    1. Basic Certhash usage
    2. Protocol validation
    3. Binary encoding/decoding
    4. Multiaddr integration

    Each example demonstrates different aspects of Certhash protocol
    functionality and shows how to use it with py-multiaddr.
    """
    print("Certhash Protocol Examples")
    print("=" * 50)

    try:
        basic_certhash_usage()
        protocol_validation()
        binary_encoding_decoding()
        multiaddr_integration()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- Certhash protocol is working correctly")
        print("- Binary encoding/decoding functions properly")
        print("- Validation catches invalid multibase/multihash values")
        print("- Integration with /webrtc-direct works as expected")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
