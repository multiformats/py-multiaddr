# Thin Waist Address Validation Examples

This directory contains examples demonstrating how to use the thin waist address validation functionality in the Python multiaddr library.

## What is Thin Waist Address Validation?

Thin waist address validation is a technique used in libp2p to:
- Process multiaddrs and extract thin waist addresses (IP + transport protocol)
- Expand wildcard addresses (like `0.0.0.0` or `::`) to all available network interfaces
- Override ports when needed
- Filter out link-local addresses

## Example File

### `thin_waist_example.py`

A comprehensive example that demonstrates all aspects of thin waist address validation.

**Usage:**
```bash
# Basic examples only
python examples/thin_waist/thin_waist_example.py

# Detailed examples with edge cases and practical scenarios
python examples/thin_waist/thin_waist_example.py --detailed
```

**What it demonstrates:**

**Basic Examples:**
1. Specific IP addresses (no expansion)
2. IPv4 wildcard expansion (`0.0.0.0` → all IPv4 interfaces)
3. IPv6 wildcard expansion (`::` → all IPv6 interfaces)
4. Port override functionality
5. Handling empty input

**Detailed Examples (with `--detailed` flag):**
6. UDP transport support
7. Port override on specific addresses
8. Error handling for invalid multiaddrs
9. Server binding scenarios
10. Dynamic port configuration

## Key Functions

### `get_thin_waist_addresses(ma=None, port=None)`

The main function for thin waist address validation.

**Parameters:**
- `ma`: A Multiaddr object (optional)
- `port`: Port number to override (optional)

**Returns:**
- List of Multiaddr objects representing thin waist addresses

**Examples:**

```python
from multiaddr import Multiaddr
from multiaddr.utils import get_thin_waist_addresses

# Specific address (no expansion)
addr = Multiaddr('/ip4/192.168.1.100/tcp/8080')
result = get_thin_waist_addresses(addr)
# Returns: [<Multiaddr /ip4/192.168.1.100/tcp/8080>]

# Wildcard expansion
addr = Multiaddr('/ip4/0.0.0.0/tcp/8080')
result = get_thin_waist_addresses(addr)
# Returns: [<Multiaddr /ip4/192.168.1.12/tcp/8080>, <Multiaddr /ip4/10.152.168.99/tcp/8080>]

# Port override
addr = Multiaddr('/ip4/0.0.0.0/tcp/8080')
result = get_thin_waist_addresses(addr, port=9000)
# Returns: [<Multiaddr /ip4/192.168.1.12/tcp/9000>, <Multiaddr /ip4/10.152.168.99/tcp/9000>]
```

## Use Cases

1. **Server Configuration**: Expand wildcard addresses to bind to all interfaces
2. **Network Discovery**: Find all available network interfaces
3. **Port Management**: Override ports in multiaddrs
4. **Address Validation**: Ensure multiaddrs represent valid thin waist addresses

## Requirements

- Python 3.9+
- `multiaddr` library with `psutil` dependency
- Network interfaces to demonstrate wildcard expansion

## Running the Example

Make sure you have the virtual environment activated and all dependencies installed:

```bash
# Activate virtual environment
source venv/bin/activate

# Run basic examples
python examples/thin_waist/thin_waist_example.py

# Run detailed examples
python examples/thin_waist/thin_waist_example.py --detailed
```

The output will show your actual network interfaces and demonstrate how wildcard addresses are expanded to specific IP addresses on your system.
