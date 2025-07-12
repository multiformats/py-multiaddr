# Decapsulate Code Examples

This directory contains examples demonstrating the `decapsulate_code` functionality of the multiaddr library.

## Overview

The `decapsulate_code` method allows you to remove specific protocol layers from multiaddrs by their protocol codes. This is different from the standard `decapsulate` method which removes by multiaddr string.

## Key Features

- **Protocol Code Removal**: Remove layers by protocol code (e.g., TCP=6, UDP=17)
- **Stack Analysis**: Analyze protocol stacks layer by layer
- **Address Transformation**: Convert between different address formats
- **Error Handling**: Proper handling of edge cases and errors

## Examples Included

### 1. Basic Decapsulate Examples
Demonstrates fundamental usage of `decapsulate_code`:
- Removing TCP layers
- Removing UDP layers
- Removing IP layers

### 2. Protocol Stack Analysis
Shows how to analyze complex multiaddr structures:
- Layer-by-layer breakdown
- Protocol identification
- Stack visualization

### 3. Address Transformation
Practical scenarios for address manipulation:
- Secure to insecure conversion
- Transport layer extraction
- IP version conversion simulation

### 4. Error Handling
Demonstrates proper error handling:
- Non-existent protocol removal
- Empty multiaddr handling
- Edge case management

### 5. Practical Use Cases
Real-world applications:
- Network configuration analysis
- Protocol compatibility checking
- Server/client address classification

## Running the Examples

```bash
python examples/decapsulate/decapsulate_example.py
```

## Expected Output

The examples will show:
- Original multiaddr structures
- Protocol information (names and codes)
- Results after decapsulation
- Error handling demonstrations
- Practical use case analysis

## Protocol Codes Reference

Common protocol codes used in examples:
- `P_IP4` (4): IPv4 addresses
- `P_IP6` (41): IPv6 addresses
- `P_TCP` (6): TCP transport
- `P_UDP` (17): UDP transport
- `P_TLS` (448): TLS security layer
- `P_P2P` (421): P2P peer ID

## Use Cases

The `decapsulate_code` method is particularly useful for:
- Network protocol analysis and debugging
- Address format conversion
- Protocol stack manipulation
- Network configuration management
- Compatibility checking between different protocols
