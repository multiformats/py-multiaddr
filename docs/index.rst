.. multiaddr documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to py-multiaddr's documentation!
========================================

What is Multiaddr?
------------------

Multiaddr is a format for encoding addresses from various well-established network protocols.
It is useful for writing applications that future-proof their use of addresses and allow
multiple transport protocols and addresses to coexist.

A multiaddr emphasizes explicitness and self-description through the use of typed components.
This makes it easier to write code that correctly handles addresses from different protocols,
eliminating the need for address family detection and reducing the likelihood of bugs.

Key Features
------------

* **Protocol Agnostic**: Support for IPv4, IPv6, TCP, UDP, DNS, HTTP, HTTPS, and many more protocols
* **Self-Describing**: Each address component includes its protocol type, making addresses explicit and unambiguous
* **Composable**: Addresses can be combined to represent complex network topologies and tunnels
* **Future-Proof**: Easy to add new protocols without breaking existing code
* **DNS Resolution**: Built-in support for DNS, DNS4, DNS6, and DNSADDR resolution
* **Async Support**: Full async/await support with Trio for non-blocking operations
* **Thin Waist Validation**: Network interface discovery and wildcard address expansion

Supported Protocols
-------------------

The library supports a wide range of network protocols:

* **Network Layer**: IPv4, IPv6, DNS, DNS4, DNS6, DNSADDR
* **Transport Layer**: TCP, UDP, SCTP, DCCP, UDT, UTP
* **Application Layer**: HTTP, HTTPS, WebSocket, WebSocket Secure
* **Security**: TLS, Noise
* **P2P**: libp2p peer IDs, circuit addresses
* **Special**: Unix domain sockets, onion addresses

Use Cases
---------

* **Distributed Systems**: Node discovery and addressing in peer-to-peer networks
* **Microservices**: Service addressing and load balancing
* **Network Programming**: Protocol-agnostic network applications
* **DevOps**: Multi-protocol service configuration
* **Research**: Network protocol experimentation and analysis

Getting Started
---------------

* :doc:`readme` - Comprehensive usage guide with code examples
* :doc:`installation` - Installation instructions and requirements
* :doc:`examples` - Detailed examples for specific use cases

Documentation Contents
======================

.. toctree::
   :maxdepth: 2

   readme
   installation
   examples
   contributing
   authors
   history
   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
