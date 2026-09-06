"""
WireGuard multiaddr codec example.

Demonstrates valid roundtrips and clearer errors for pasted wg(8) keys.

Usage:
    python examples/wg/wg_examples.py
"""

from multiaddr import Multiaddr
from multiaddr.codecs import wg


def main() -> None:
    print("=== Valid WireGuard multiaddr ===")
    # 32 zero bytes as multibase base64url
    key = "uAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    ma = Multiaddr(f"/ip4/1.2.3.4/udp/51820/wg/{key}")
    print(f"Input:  {ma}")
    print(f"Value:  {ma.value_for_protocol('wg')}")
    print(f"Bytes:  {ma.to_bytes().hex()}")
    print()

    print("=== Pasted std-base64 (wg(8) style) is rejected with a conversion hint ===")
    codec = wg.Codec()
    bad = "uAAAA+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    try:
        codec.to_bytes(None, bad)
    except ValueError as exc:
        print(f"Input:  {bad}")
        print(f"Error:  {exc}")


if __name__ == "__main__":
    main()
