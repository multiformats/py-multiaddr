import argparse
import json
import sys
from typing import Any

from . import __version__
from .multiaddr import Multiaddr
from .transforms import bytes_iter


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect multiaddrs")
    parser.add_argument("addr", help="Multiaddr string or hex bytes (0x...)")
    parser.add_argument("-c", "--compact", action="store_true", help="Output compact JSON")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    try:
        if args.addr.startswith("0x"):
            addr_bytes = bytes.fromhex(args.addr[2:])
            addr = Multiaddr(addr_bytes)
        else:
            addr = Multiaddr(args.addr)
    except Exception as e:
        print(f"Error parsing multiaddr: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        components = []
        for _, proto, codec, value_bytes in bytes_iter(addr.to_bytes()):
            component: dict[str, Any] = {
                "protocol": proto.name,
                "code": proto.code,
            }
            if codec.SIZE != 0:
                component["value"] = codec.to_string(proto, value_bytes)
                component["rawValue"] = "0x" + value_bytes.hex()
            else:
                component["value"] = None
                component["rawValue"] = None
            components.append(component)

    except Exception as e:
        print(f"Error decoding multiaddr components: {e}", file=sys.stderr)
        sys.exit(1)

    indent = None if args.compact else 2

    output = {
        "string": str(addr),
        "packed": "0x" + addr.to_bytes().hex(),
        "packedSize": len(addr.to_bytes()),
        "components": components,
    }

    print(json.dumps(output, indent=indent))


if __name__ == "__main__":
    main()
