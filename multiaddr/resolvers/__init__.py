"""DNS resolution support for multiaddr."""

from typing import TYPE_CHECKING
from typing import Protocol as TypeProtocol

from .dns import DNSResolver

__all__ = ["DNSResolver", "Resolver"]

if TYPE_CHECKING:
    from ..multiaddr import Multiaddr


class Resolver(TypeProtocol):
    """Base protocol for multiaddr resolvers."""

    async def resolve(self, ma: "Multiaddr") -> list["Multiaddr"]:
        """Resolve a multiaddr that contains a resolvable protocol.

        Args:
            ma: The multiaddr to resolve

        Returns:
            A list of resolved multiaddrs
        """
        ...
