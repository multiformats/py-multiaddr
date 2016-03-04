# -*- coding: utf-8 -*-
from abc import ABCMeta
from abc import abstractmethod


class MultiaddrInterface(object):
    """Multiaddr is a representation of multiple nested
    Multiaddr is a cross-protocol, cross-platform format for representing
    internet addresses. It emphasizes explicitness and self-description.

    Learn more here: https://github.com/jbenet/multiaddr

    Multiaddrs have both a binary and string representation.

        >>> from multiaddr import Multiaddr
        >>> addr = Multiaddr("/ip4/1.2.3.4/tcp/80")

    Multiaddr objects are immutable, so `encapsulate` and `decapsulate`
    return new objects rather than modify internal state.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, string=None):
        """Instantiate a new Multiaddr.

        Args:
            string (optional): A string-encoded Multiaddr
        """

    @abstractmethod
    def __eq__(self, other):
        """Checks if two Multiaddr objects are exactly equal."""

    @abstractmethod
    def __str__(self):
        """Return the string representation of this Multiaddr.

        May raise an exception if the internal state of the Multiaddr is
        corrupted."""

    @abstractmethod
    def __bytes__(self):
        """Returns the byte array representation of this Multiaddr."""

    @abstractmethod
    def protocols(self):
        """Returns a list of Protocols this Multiaddr includes."""

    @abstractmethod
    def encapsulate(self, other):
        """Wrap this Multiaddr around another.

        For example:
            /ip4/1.2.3.4 encapsulate /tcp/80 = /ip4/1.2.3.4/tcp/80
        """

    @abstractmethod
    def decapsulate(self, other):
        """Remove a Multiaddr wrapping.

        For example:
            /ip4/1.2.3.4/tcp/80 decapsulate /ip4/1.2.3.4 = /tcp/80
        """

    @abstractmethod
    def value_for_protocol(self, protocol):
        """Return the value (if any) following the specified protocol."""
