"""
IP Filters example (accept/deny).

Usage:
    python examples/filters/filters_example.py
"""

from multiaddr import Action, Filters, Multiaddr


def main() -> None:
    print("=== Default ACCEPT with private range DENY ===")
    filters = Filters()
    filters.add_filter("10.0.0.0/8", Action.DENY)
    filters.add_filter("192.168.0.0/16", Action.DENY)

    samples = [
        "/ip4/8.8.8.8/tcp/53",
        "/ip4/10.0.0.5/tcp/80",
        "/ip4/192.168.1.10/tcp/443",
        "/unix/var/run/docker.sock",
    ]
    for addr in samples:
        ma = Multiaddr(addr)
        blocked = filters.addr_blocked(ma)
        print(f"{addr} -> blocked={blocked}")


if __name__ == "__main__":
    main()
