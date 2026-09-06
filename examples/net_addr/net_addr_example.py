"""
from_net_addr / to_net_addr demo.

Usage:
    python examples/net_addr/net_addr_example.py
"""

from multiaddr import from_net_addr, to_net_addr


def main() -> None:
    print("=== from_net_addr() ===")
    samples = [
        (("1.2.3.4", 80), "tcp"),
        (("::1", 443), "tcp"),
        (("8.8.8.8", 53), "udp"),
    ]
    for addr, transport in samples:
        ma = from_net_addr(addr, transport=transport)
        print(f"{addr} transport={transport} -> {ma}")

    print()
    print("=== to_net_addr() ===")
    for ma in (
        from_net_addr(("1.2.3.4", 80)),
        from_net_addr(("::1", 443)),
    ):
        print(f"{ma} -> {to_net_addr(ma)}")


if __name__ == "__main__":
    main()
