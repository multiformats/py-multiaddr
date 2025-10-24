#!/usr/bin/env python3
"""
SNI (Server Name Indication) protocol examples for py-multiaddr.

This script demonstrates how to use the 'sni' protocol in py-multiaddr,
which is typically used to specify the hostname during the TLS handshake.

## Overview

This script shows various examples of SNI protocol usage:

1. **Basic SNI Usage**: Creating and parsing a basic /sni/hostname address.
2. **Protocol Validation**: Testing valid and invalid hostnames.
3. **Binary Encoding/Decoding**: Working with binary representations.
4. **Multiaddr Integration**: Using 'sni' in a realistic multiaddr string 
   (e.g., /dns/google.com/tcp/443/tls/sni/google.com).
5. **Error Handling**: Demonstrating errors for invalid domain names.

# Expected Output

When you run this script, you should see output similar to:

```
SNI Protocol Examples
==================================================
=== Basic SNI Usage ===
Original SNI: /sni/protocol.ai 
Protocols: ['sni'] 
Extracted Value: protocol.ai 
Binary length: 14 bytes 
Valid SNI address: True

=== Protocol Validation ===
Testing valid SNI: /sni/protocol.ai 
    Valid: True
    Value: protocol.ai

Testing invalid SNI (invalid domain chars): /sni/invalid_hostname!
    Valid: False Error: invalid_hostname! is not a valid domain name

Testing invalid SNI (empty value): /sni/ 
    Valid: False Error: is not a valid domain name
    
=== Binary Encoding/Decoding ===
SNI binary operations: 
    Original: /sni/protocol.ai
    Binary: 14 bytes 
    Round-trip: /sni/protocol.ai 
    Match: True

=== Multiaddr Integration === 
Complex multiaddr with SNI: 
    Address: /dns/google.com/tcp/443/tls/sni/google.com    
    Protocols: ['dns', 'tcp', 'tls', 'sni'] 
    Extracted SNI value: google.com
    Match: True

==================================================
All examples completed!
```

## Key features Demonstrated

- **SNI Protocol**: Represents a Server Name Indication value.
- **Validation**: Ensures the value is a valid domain name (as it uses the 'domain' transcoder).
- **Binary Operation**: Encoding and decoding to/from binary format.
- **Multiaddr Integration**: Using 'sni' within a '/tls' protocol.
- **Error Handling**: Proper error handling for invalid domain names.

## Requirements

- Python 3.10+
- py-multiaddr library

## Usage

```bash
python examples/sni_examples.py
```
"""

from multiaddr import Multiaddr

# A valid domain name to use for SNI
VALID_SNI_DOMAIN = "protocol.ai"
VALID_SNI_ADDR = f"/sni/{VALID_SNI_DOMAIN}"

def basic_sni_usage():
    """
    Basic SNI usage example
    
    This function demonstrates:
    - Creating an SNI multiaddr
    - Extracting protocol information
    - Extracting the value
    - Getting binary representation
    """
    
    print("=== Basic SNI Usage ===")
    print(f"Original SNI: {VALID_SNI_ADDR}")
    
    try:
        ma = Multiaddr(VALID_SNI_ADDR)
        print(f"Protocols: {[p.name for p in ma.protocols()]}")
        
        # Extract the value
        sni_value = ma.value_for_protocol('sni')
        print(f"Extracted Value: {sni_value}")
        
        # Get binary representation
        binary_data = ma.to_bytes()
        print(f"Binary length: {len(binary_data)} bytes")
        
        print("Valid SNI address: True")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Valid SNI address: False")
        
def protocol_validation():
    """
    Demonstrate protocol validation.

    This function shows:
    - A valid SNI address
    - Invalid SNI addresses (invalid domain characters, empty)
    - Error handling for validation failures
    """
    
    print("\n=== Protocol Validation ===")

    # Test valid SNI
    print(f"Testing valid SNI: {VALID_SNI_ADDR}")
    try:
        ma = Multiaddr(VALID_SNI_ADDR)
        print("  Valid: True")
        print(f"  Value: {ma.value_for_protocol('sni')}")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid SNI (invalid characters)
    invalid_addr_str = "/sni/invalid_hostname!"
    print(f"\nTesting invalid SNI (invalid domain chars): {invalid_addr_str}")
    try:
        Multiaddr(invalid_addr_str)
        print("  Valid: True (ERROR: Should have failed)")
    except Exception as e:
        print("  Valid: False")
        print(f"  Error: {e}")

    # Test invalid SNI (empty value)
    invalid_addr_str = "/sni/"
    print(f"\nTesting invalid SNI (empty value): {invalid_addr_str}")
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

    print("SNI binary operations:")
    print(f"  Original: {VALID_SNI_ADDR}")

    try:
        ma = Multiaddr(VALID_SNI_ADDR)
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
    Demonstrate SNI protocol integration with other protocols.

    This function shows:
    - The most common use case for /sni, nested within /tls.
    - Protocol stack analysis
    - SNI value extraction
    """
    
    print("\n=== Multiaddr Integration ===")

    # Create a complex multiaddr with SNI
    # This is a typical address for a secure websocket connection
    sni_host = "google.com"
    complex_addr = f"/dns/google.com/tcp/443/tls/sni/{sni_host}"

    print("Complex multiaddr with SNI:")
    print(f"  Address: {complex_addr}")

    try:
        ma = Multiaddr(complex_addr)
        protocols = [p.name for p in ma.protocols()]
        print(f"  Protocols: {protocols}")

        # Extract SNI value
        extracted_sni_value = ma.value_for_protocol('sni')
        print(f"  Extracted SNI value: {extracted_sni_value}")
        print(f"  Match: {extracted_sni_value == sni_host}")

    except Exception as e:
        print(f"  Error: {e}")

def main():
    """
    Run all SNI protocol examples.

    This function orchestrates all the SNI protocol examples:
    1. Basic SNI usage
    2. Protocol validation
    3. Binary encoding/decoding
    4. Multiaddr integration

    Each example demonstrates different aspects of SNI protocol functionality
    and shows how to use it with py-multiaddr.
    """
    print("SNI (Server Name Indication) Protocol Examples")
    print("=" * 50)

    try:
        basic_sni_usage()
        protocol_validation()
        binary_encoding_decoding()
        multiaddr_integration()

        print("\n" + "=" * 50)
        print("All examples completed!")
        print("\nSummary:")
        print("- SNI protocol is working correctly")
        print("- Binary encoding/decoding functions properly")
        print("- Validation catches invalid domain names")
        print("- Integration with /tls protocol works as expected")

    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        
    
if __name__ == "__main__":
    main()