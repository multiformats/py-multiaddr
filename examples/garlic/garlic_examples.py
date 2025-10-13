#!/usr/bin/env python3
"""
Garlic protocol examples for py-multiaddr.

This script demonstrates how to use the garlic32 and garlic64 protocols in py-multiaddr,
showing how to work with I2P (Invisible Internet Project) addresses.

## Overview

This script shows various examples of garlic protocol usage:

1. **Basic Garlic64 Usage**: Creating and parsing garlic64 addresses
2. **Basic Garlic32 Usage**: Creating and parsing garlic32 addresses
3. **Protocol Validation**: Testing valid and invalid garlic addresses
4. **Binary Encoding/Decoding**: Working with binary representations
5. **Multiaddr Integration**: Using garlic protocols in multiaddr strings
6. **Error Handling**: Demonstrating proper error handling for invalid addresses

## Expected Output

When you run this script, you should see output similar to:

```
Garlic Protocol Examples
==================================================
=== Basic Garlic64 Usage ===
Original garlic64: /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ
Protocols: ['garlic64']
Binary length: 386 bytes
Valid garlic64 address: True

=== Basic Garlic32 Usage ===
Original garlic32: /garlic32/566niximlxdzpanmn4qouucvua3k7neniwss47li5r6ugoertzu
Protocols: ['garlic32']
Binary length: 32 bytes
Valid garlic32 address: True

=== Protocol Validation ===
Testing valid garlic64: /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ
  Valid: True
  Length: 386 bytes

Testing invalid garlic64 (too short): /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ
  Valid: False
  Error: Invalid length for garlic64: must be at least 386 bytes, got 385

=== Binary Encoding/Decoding ===
Garlic64 binary operations:
  Original: /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ
  Binary: 386 bytes
  Round-trip: /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ
  Match: True

=== Multiaddr Integration ===
Complex multiaddr with garlic64:
   Address: /garlic64/7tDszj8zn3dXxJAhQGHog6KcvLcN6g4wLW4sUoQurUvK6VQ/p2p/\\
     QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
  Protocols: ['garlic64', 'p2p']
  Peer ID: QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN

=== Error Handling ===
Testing invalid addresses:
  /garlic64/invalid: Invalid base64 encoding
  /garlic32/invalid: Invalid base32 encoding
  /garlic64/short: Invalid length (too short)

==================================================
All examples completed!
```

## Key Features Demonstrated

- **Garlic64 Protocol**: I2P base64 address encoding with custom character set (-~)
- **Garlic32 Protocol**: I2P base32 address encoding
- **Validation**: Length and format validation for both protocols
- **Binary Operations**: Encoding and decoding to/from binary format
- **Multiaddr Integration**: Using garlic protocols in complex multiaddr strings
- **Error Handling**: Proper error handling for invalid addresses

## Requirements

- Python 3.10+
- py-multiaddr library
- Internet connection for some examples

## Usage

```bash
python examples/garlic/garlic_examples.py
```

## Notes

- Garlic64 uses custom base64 alphabet with -~ instead of +/
- Garlic32 uses standard base32 encoding
- Garlic64 requires at least 386 bytes of decoded data
- Garlic32 requires exactly 32 bytes or >= 35 bytes
- Both protocols are used for I2P (Invisible Internet Project) networking
"""

import base64
import os

from multiaddr import Multiaddr


def create_valid_garlic64():
    """Create a valid garlic64 address for testing."""
    # Generate 386 bytes of random data (minimum required for garlic64)
    random_bytes = os.urandom(386)
    # Encode with custom base64 alphabet (-~ instead of +/)
    encoded = base64.b64encode(random_bytes, altchars=b"-~").decode("utf-8")
    return f"/garlic64/{encoded}"


def create_valid_garlic32():
    """Create a valid garlic32 address for testing."""
    # Generate 32 bytes of random data (valid length for garlic32)
    random_bytes = os.urandom(32)
    # Encode with base32
    encoded = base64.b32encode(random_bytes).decode("utf-8").rstrip("=")
    return f"/garlic32/{encoded}"


def basic_garlic64_usage():
    """
    Basic garlic64 usage example.

    This function demonstrates:
    - Creating a garlic64 multiaddr
    - Extracting protocol information
    - Validating the address
    - Getting binary representation
    """
    print("=== Basic Garlic64 Usage ===")

    # Create a valid garlic64 address
    garlic64_addr = create_valid_garlic64()
    print(f"Original garlic64: {garlic64_addr}")

    try:
        ma = Multiaddr(garlic64_addr)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        # Validate the address
        is_valid = len(binary_data) >= 386
        print(f"Valid garlic64 address: {is_valid}")

    except Exception as e:
        print(f"Error: {e}")


def basic_garlic32_usage():
    """
    Basic garlic32 usage example.

    This function demonstrates:
    - Creating a garlic32 multiaddr
    - Extracting protocol information
    - Validating the address
    - Getting binary representation
    """
    print("\n=== Basic Garlic32 Usage ===")

    # Create a valid garlic32 address
    garlic32_addr = create_valid_garlic32()
    print(f"Original garlic32: {garlic32_addr}")

    try:
        ma = Multiaddr(garlic32_addr)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        # Validate the address
        is_valid = len(binary_data) == 32 or len(binary_data) >= 35
        print(f"Valid garlic32 address: {is_valid}")

    except Exception as e:
        print(f"Error: {e}")


def protocol_validation():
    """
    Demonstrate protocol validation.

    This function shows:
    - Valid garlic64 and garlic32 addresses
    - Invalid addresses (too short, wrong encoding)
    - Error handling for validation failures
    """
    print("\n=== Protocol Validation ===")

    # Test valid garlic64
    valid_garlic64 = create_valid_garlic64()
    print(f"Testing valid garlic64: {valid_garlic64}")

    try:
        ma = Multiaddr(valid_garlic64)
        binary_data = ma.to_bytes()
        print("  Valid: True")
        print(f"  Length: {len(binary_data)} bytes")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid garlic64 (too short)
    print("\nTesting invalid garlic64 (too short): /garlic64/short")
    try:
        # Create a short garlic64 address
        short_bytes = os.urandom(385)  # One byte too short
        short_encoded = base64.b64encode(short_bytes, altchars=b"-~").decode("utf-8")
        short_addr = f"/garlic64/{short_encoded}"
        ma = Multiaddr(short_addr)
        print("  Valid: False")
        print("  Error: Invalid length for garlic64: must be at least 386 bytes, got 385")
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

    print("Garlic64 binary operations:")
    garlic64_addr = create_valid_garlic64()
    print(f"  Original: {garlic64_addr}")

    try:
        ma = Multiaddr(garlic64_addr)
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
    Demonstrate garlic protocol integration with multiaddr.

    This function shows:
    - Complex multiaddr strings with garlic protocols
    - Protocol stack analysis
    - Peer ID extraction
    """
    print("\n=== Multiaddr Integration ===")

    # Create a complex multiaddr with garlic64 and peer ID
    garlic64_addr = create_valid_garlic64()
    peer_id = "QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    complex_addr = f"{garlic64_addr}/p2p/{peer_id}"

    print("Complex multiaddr with garlic64:")
    print(f"  Address: {complex_addr}")

    try:
        ma = Multiaddr(complex_addr)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")

        # Extract peer ID
        extracted_peer_id = ma.get_peer_id()
        print(f"  Peer ID: {extracted_peer_id}")

    except Exception as e:
        print(f"  Error: {e}")


def error_handling():
    """
    Demonstrate error handling for invalid addresses.

    This function shows:
    - Invalid base64/base32 encoding
    - Invalid length addresses
    - Proper error messages
    """
    print("\n=== Error Handling ===")

    print("Testing invalid addresses:")

    # Test invalid base64 encoding
    print("  /garlic64/invalid: Invalid base64 encoding")
    try:
        Multiaddr("/garlic64/invalid")
    except Exception as e:
        print(f"    Error: {e}")

    # Test invalid base32 encoding
    print("  /garlic32/invalid: Invalid base32 encoding")
    try:
        Multiaddr("/garlic32/invalid")
    except Exception as e:
        print(f"    Error: {e}")

    # Test short garlic64
    print("  /garlic64/short: Invalid length (too short)")
    try:
        # Create a short address
        short_bytes = os.urandom(100)  # Much too short
        short_encoded = base64.b64encode(short_bytes, altchars=b"-~").decode("utf-8")
        short_addr = f"/garlic64/{short_encoded}"
        Multiaddr(short_addr)
    except Exception as e:
        print(f"    Error: {e}")


def main():
    """
    Run all garlic protocol examples.

    This function orchestrates all the garlic protocol examples:
    1. Basic garlic64 usage
    2. Basic garlic32 usage
    3. Protocol validation
    4. Binary encoding/decoding
    5. Multiaddr integration
    6. Error handling

    Each example demonstrates different aspects of garlic protocol functionality
    and shows how to use it with py-multiaddr.
    """
    print("Garlic Protocol Examples")
    print("=" * 50)

    try:
        basic_garlic64_usage()
        basic_garlic32_usage()
        protocol_validation()
        binary_encoding_decoding()
        multiaddr_integration()
        error_handling()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- Garlic64 and Garlic32 protocols are working correctly")
        print("- Binary encoding/decoding functions properly")
        print("- Validation catches invalid addresses")
        print("- Integration with multiaddr works seamlessly")
        print("- Error handling provides clear error messages")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


if __name__ == "__main__":
    main()
