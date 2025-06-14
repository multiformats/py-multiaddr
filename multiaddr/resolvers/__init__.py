"""DNS resolution support for multiaddr."""

from typing import TYPE_CHECKING, List
from typing import Protocol as TypeProtocol

if TYPE_CHECKING:
    from ..multiaddr import Multiaddr


class Resolver(TypeProtocol):
    """Base protocol for multiaddr resolvers."""

    async def resolve(self, ma: 'Multiaddr') -> List['Multiaddr']:
        """Resolve a multiaddr that contains a resolvable protocol.

        Args:
            ma: The multiaddr to resolve

        Returns:
            A list of resolved multiaddrs
        """
        ...


from .dns import DNSResolver

__all__ = ["Resolver", "DNSResolver"]
