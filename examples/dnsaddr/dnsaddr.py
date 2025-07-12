import trio

from multiaddr import Multiaddr
from multiaddr.resolvers import DNSResolver

# Example DNSADDR resolution script
#
# Expected output:
# - Successful resolutions show resolved multiaddrs (e.g., /ip4/139.178.91.71/tcp/4001/p2p/...)
# - Failed resolutions show "(No resolution results)" (empty list returned)
# - This matches the JS implementation and libp2p spec behavior
#
# Sample output:
# Resolving: /dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
#   -> /ip4/139.178.91.71/tcp/4001/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
#   -> /ip4/139.178.91.71/udp/4001/quic-v1/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
#   ...
# Resolving: /dnsaddr/github.com/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN
#   (No resolution results)

ADDRESSES = [
    "/dnsaddr/bootstrap.libp2p.io/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
    "/dnsaddr/bootstrap.libp2p.io/p2p/QmbLHAnMoJPWSCR5Zhtx6BHJX9KiKNN6tpvbUcqanj75Nb",
    "/dnsaddr/bootstrap.libp2p.io/p2p/QmZa1sAxajnQjVM8WjWXoMbmPd7NsWhfKsPkErzpm9wGkp",
    "/dnsaddr/bootstrap.libp2p.io/p2p/QmQCU2EcMqAqQPR2i9bChDtGNJchTbq5TbXJJ16u19uLTa",
    "/dnsaddr/bootstrap.libp2p.io/p2p/QmcZf59bWwK5XFi76CZX8cbJ4BhTzzA3gU1ZjYZcYW3dwt",
    "/dnsaddr/github.com/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
    "/dnsaddr/cloudflare.com/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
    "/dnsaddr/google.com/p2p/QmNnooDu7bfjPFoTZYxMNLWUQJyrVwtbZg5gBMjTezGAJN",
]


async def main():
    resolver = DNSResolver()
    for addr in ADDRESSES:
        print(f"\nResolving: {addr}")
        ma = Multiaddr(addr)
        try:
            resolved = await resolver.resolve(ma)
            if resolved:
                for r in resolved:
                    print(f"  -> {r}")
            else:
                # If DNSADDR resolution fails (no TXT records or no matching entries),
                # the result is an empty list (no resolution results), matching the JS
                # implementation and spec.
                print("  (No resolution results)")
        except Exception as e:
            print(f"  (Error: {e})")


if __name__ == "__main__":
    trio.run(main)
