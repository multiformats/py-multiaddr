"""
dial_args() demo — convert multiaddrs to socket.connect()-ready pairs.

Usage:
    python examples/dial_args/dial_args_example.py
"""

from multiaddr import Multiaddr, dial_args


def main() -> None:
    print("=== dial_args() ===")
    samples = [
        "/ip4/1.2.3.4/tcp/80",
        "/ip6/::1/tcp/443",
        "/ip4/8.8.8.8/udp/53",
        "/unix/var/run/docker.sock",
    ]
    for addr in samples:
        network, address = dial_args(Multiaddr(addr))
        print(f"{addr}")
        print(f"  -> network={network!r}, address={address!r}")


if __name__ == "__main__":
    main()
