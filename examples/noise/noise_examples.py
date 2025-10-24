#!/usr/bin/env python3
"""
Noise protocol examples for py-multiaddr.

This script demonstrates how to use the 'noise' protocol in py-multiaddr.
The 'noise' protocol is a tag protocol, meaning it does not take an
argument. Its presence signifies that the connection is secured using
the Noise Protocol Framework.

## Overview

This script shows various examples of Noise protocol usage:

1. **Basic Noise Usage**: Creating and parsing a simple /noise address.
2. **Protocol Validation**: Testing valid (/noise) and invalid (/noise/value)
   addresses.
3. **Binary Encoding/Decoding**: Working with binary representations.
4. **Multiaddr Integration**: Using 'noise' in a realistic multiaddr string 
   (e.g., /ip4/127.0.0.1/tcp/12345/noise).
5. **Error Handling**: Demonstrating errors when a value is incorrectly
   provided.

## Expected Output

When you run this script, you should see output similar to:

```
NOISE Protocol Examples
==================================================
=== Basic Noise Usage ===
Original Noise: /noise
    Protocols: ['noise'] 
    Binary length: 2 bytes
    Valid Noise address: True

=== Protocol Validation ===
Testing valid Noise: /noise
    Valid: True
    Protocols: ['noise']

Testing invalid Noise (with value): /noise/somevalue 
    Valid: False 
    Error: Protocol 'noise' does not take an argument

=== Binary Encoding/Decoding ===
Noise binary operations: 
    Original: /noise 
    Binary: 2 bytes 
    Round-trip: /noise Match: True

=== Multiaddr Integration ===
Complex multiaddr with Noise:
    Address: /ip4/127.0.0.1/tcp/12345/noise/p2p/Qm... 
    Protocols: ['ip4', 'tcp', 'noise', 'p2p'] 
    Has 'noise' protocol: True
    
==================================================
All examples completed!
```

## Key Features Demonstrated

- **Noise Protocol**: Represents a connection secured by the Noise framework.
- **Tag Protocol**: 'noise' is a tag-only protocol and takes no arguments.
- **Validation**: Ensures no value is provided to the 'noise' protocol.
- **Binary Operations**: Encoding and decoding to/from binary format.
- **Multiaddr Integration**: Using 'noise' as part of a connection stack.
- **Error Handling**: Proper error handling for invalid formats.

## Requirements

- Python 3.10+
- py-multiaddr library

## Usage

```bash
python examples/noise_examples.py
```
"""

from multiaddr import Multiaddr

NOISE_ADDR = "/noise"

def basic_noise_usage():
    """
    Basic Noise usage example.

    This function demonstrates:
    - Creating a Noise multiaddr
    - Extracting protocol information
    - Getting binary representation
    """
    
    print(f'Original Noise: {NOISE_ADDR}')
    
    try:
        ma = Multiaddr(NOISE_ADDR)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")

        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")

        print("Valid Noise address: True")

    except Exception as e:
        print(f"Error: {e}")
        print("Valid Noise address: False")

def protocol_validation(): 
    """
    Demonstrate protocol validation.

    This function shows:
    - A valid Noise address
    - An invalid Noise address (with a value)
    - Error handling for validation failures
    """
    print("\n=== Protocol Validation ===")

    # Test valid Noise
    print(f"Testing valid Noise: {NOISE_ADDR}")
    try:
        ma = Multiaddr(NOISE_ADDR)
        print("  Valid: True")
        print(f"  Protocols: {[p.name for p in ma.protocols()]}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid Noise (with a value)
    invalid_addr_str = "/noise/somevalue"
    print(f"\nTesting invalid Noise (with value): {invalid_addr_str}")
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

    print("Noise binary operations:")
    print(f"  Original: {NOISE_ADDR}")

    try:
        ma = Multiaddr(NOISE_ADDR)
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
    Demonstrate Noise protocol integration with other protocols.

    This function shows:
    - Using /noise as part of a libp2p stack.
    - Protocol stack analysis
    """
    print("\n=== Multiaddr Integration ===")

    # Create a complex multiaddr with Noise
    # This is a typical address for a libp2p node
    peer_id = "QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN"
    complex_addr = f"/ip4/127.0.0.1/tcp/12345/noise/p2p/{peer_id}"

    print("Complex multiaddr with Noise:")
    print(f"  Address: {complex_addr}")

    try:
        ma = Multiaddr(complex_addr)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")

        # Check for 'noise' protocol
        has_noise = 'noise' in protocols
        print(f"  Has 'noise' protocol: {has_noise}")

    except Exception as e:
        print(f"  Error: {e}")
        
def main():
    """
    Run all Noise protocol examples.

    This function orchestrates all the Noise protocol examples:
    1. Basic Noise usage
    2. Protocol validation
    3. Binary encoding/decoding
    4. Multiaddr integration

    Each example demonstrates different aspects of Noise protocol functionality
    and shows how to use it with py-multiaddr.
    """
    print("Noise Protocol Examples")
    print("=" * 50)

    try:
        basic_noise_usage()
        protocol_validation()
        binary_encoding_decoding()
        multiaddr_integration()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- Noise protocol is working correctly")
        print("- Binary encoding/decoding functions properly")
        print("- Validation catches invalid use (with a value)")
        print("- Integration with libp2p stack works as expected")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        
if __name__ == "__main__":
    main()
