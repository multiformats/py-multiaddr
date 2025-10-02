Added ipcidr protocol support to py-multiaddr

- Implements protocol code 43 (0x2B) for CIDR notation support
- Supports IPv4 and IPv6 CIDR ranges (0-255)
- Full compatibility with Go multiaddr implementation
- Comprehensive test coverage including edge cases
- Enables network address representation with subnet masks
