"""Utility functions for multiaddr resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import RecursionLimitError
from ..multiaddr import Multiaddr
from ..protocols import P_DNS, P_DNS4, P_DNS6, P_DNSADDR

if TYPE_CHECKING:
    from .base import Resolver

__all__ = ["addr_len", "fqdn", "is_fqdn", "matches", "offset_addr", "resolve_all"]

_DNS_PROTOCOLS = frozenset({P_DNS, P_DNS4, P_DNS6, P_DNSADDR})


def is_fqdn(s: str) -> bool:
    """Check if string is a fully qualified domain name (ends with unescaped dot).

    Args:
        s: The domain name string to check.

    Returns:
        ``True`` if *s* ends with an unescaped ``'.'``, ``False`` otherwise.
    """
    if not s:
        return False
    # Count trailing backslashes before the final character
    if s[-1] != ".":
        return False
    # Check if the trailing dot is escaped
    num_backslashes = 0
    for i in range(len(s) - 2, -1, -1):
        if s[i] == "\\":
            num_backslashes += 1
        else:
            break
    # Odd number of backslashes means the dot is escaped
    return num_backslashes % 2 == 0


def fqdn(s: str) -> str:
    """Append a trailing dot to *s* if it is not already a FQDN.

    Args:
        s: The domain name string.

    Returns:
        The domain name with a trailing ``'.'`` appended if needed.

    Example::

        >>> fqdn("example.com")
        'example.com.'
        >>> fqdn("example.com.")
        'example.com.'
    """
    if is_fqdn(s):
        return s
    return s + "."


def addr_len(maddr: Multiaddr) -> int:
    """Count the number of protocol components in a multiaddr.

    Args:
        maddr: The multiaddr to measure.

    Returns:
        The number of protocol components.
    """
    return len(list(maddr.protocols()))


def offset_addr(maddr: Multiaddr, n: int) -> Multiaddr:
    """Return a new multiaddr with the first *n* protocol components removed.

    Args:
        maddr: The source multiaddr.
        n: Number of leading components to skip.  Must be >= 0.

    Returns:
        A new :class:`~multiaddr.Multiaddr` without the first *n* components,
        or ``Multiaddr("/")`` if *n* >= the total number of components.

    Raises:
        ValueError: If *n* is negative.
    """
    if n < 0:
        raise ValueError(f"offset must be non-negative, got {n}")
    parts = maddr.split(n)
    if len(parts) <= n:
        return Multiaddr("/")
    return parts[n]


def matches(maddr: Multiaddr) -> bool:
    """Check if a multiaddr contains any DNS protocol component.

    Args:
        maddr: The multiaddr to inspect.

    Returns:
        ``True`` if *maddr* contains a ``dns``, ``dns4``, ``dns6``, or
        ``dnsaddr`` component.

    Example::

        >>> matches(Multiaddr("/dns4/example.com/tcp/80"))
        True
        >>> matches(Multiaddr("/ip4/127.0.0.1/tcp/80"))
        False
    """
    return any(p.code in _DNS_PROTOCOLS for p in maddr.protocols())


async def resolve_all(
    resolver: Resolver,
    maddr: Multiaddr,
    *,
    max_iterations: int = 32,
) -> list[Multiaddr]:
    """Resolve all DNS components in a multiaddr iteratively.

    Calls ``resolver.resolve()`` in a loop until every returned address is
    free of DNS components.

    Args:
        resolver: A resolver instance implementing an async ``resolve()`` method.
        maddr: The multiaddr to resolve.
        max_iterations: Safety limit on resolution rounds to prevent infinite
        loops (default ``32``).

    Returns:
        A list of fully-resolved :class:`~multiaddr.Multiaddr` instances.

    Raises:
        RecursionLimitError: If DNS components remain after *max_iterations*
        rounds.

    Example::

        >>> import trio
        >>> result = trio.run(resolve_all, my_resolver, Multiaddr("/dns4/example.com/tcp/80"))
    """
    queue = [maddr]
    resolved: list[Multiaddr] = []

    for _ in range(max_iterations):
        if not queue:
            break
        next_queue: list[Multiaddr] = []
        for addr in queue:
            if not matches(addr):
                resolved.append(addr)
                continue
            results = await resolver.resolve(addr)
            for r in results:
                if matches(r):
                    next_queue.append(r)
                else:
                    resolved.append(r)
        queue = next_queue

    if queue:
        raise RecursionLimitError(
            f"resolve_all exceeded {max_iterations} iterations; "
            f"{len(queue)} addresses still contain DNS components"
        )

    return resolved
