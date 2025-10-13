Examples
========

This section provides practical examples of how to use the multiaddr library for various use cases.

DNS Resolution Examples
-----------------------

The `examples/dns/` directory contains comprehensive examples demonstrating DNS-based address resolution.

This example shows:
- Standard DNS resolution for both IPv4 and IPv6
- Protocol-specific DNS resolution (dns4/dns6)
- Peer ID preservation during resolution
- Bootstrap node resolution using real libp2p nodes
- Error handling and timeout management

.. literalinclude:: ../examples/dns/dns_examples.py
   :language: python
   :caption: examples/dns/dns_examples.py

DNSADDR Examples
----------------

The `examples/dnsaddr/` directory shows how to work with DNSADDR records for libp2p bootstrap nodes.

This example demonstrates:
- DNSADDR record parsing and resolution
- Peer ID extraction and preservation
- Bootstrap node discovery
- TXT record processing

.. literalinclude:: ../examples/dnsaddr/dnsaddr.py
   :language: python
   :caption: examples/dnsaddr/dnsaddr.py

QUIC Protocol Examples
----------------------

The `examples/quic/` directory demonstrates how to work with QUIC and QUIC-v1 protocols in multiaddr addresses.

This example shows:
- Basic QUIC and QUIC-v1 protocol usage
- QUIC with peer IDs for P2P networking
- Protocol stack analysis and manipulation
- Address encapsulation and decapsulation
- Binary representation and validation
- IPv4 and IPv6 support with QUIC
- Validation of valid and invalid QUIC address combinations

.. literalinclude:: ../examples/quic/simple_quic_usage.py
   :language: python
   :caption: examples/quic/simple_quic_usage.py

Thin Waist Address Examples
---------------------------

The `examples/thin_waist/` directory demonstrates thin waist address validation and network interface discovery.

This example shows:
- Network interface discovery
- Wildcard address expansion
- IPv4 and IPv6 support
- Port management
- Server binding scenarios

.. literalinclude:: ../examples/thin_waist/thin_waist_example.py
   :language: python
   :caption: examples/thin_waist/thin_waist_example.py

Decapsulate Code Examples
-------------------------

The `examples/decapsulate/` directory demonstrates how to use the `decapsulate_code` method for protocol layer manipulation.

This example demonstrates:
- Protocol code-based layer removal
- Protocol stack analysis
- Address transformation
- Error handling for edge cases
- Practical network configuration scenarios

.. literalinclude:: ../examples/decapsulate/decapsulate_example.py
   :language: python
   :caption: examples/decapsulate/decapsulate_example.py

Garlic Protocol Examples
------------------------

The `examples/garlic/` directory demonstrates how to work with garlic32 and garlic64 protocols for I2P (Invisible Internet Project) addresses.

This example shows:
- Basic garlic64 and garlic32 protocol usage
- Protocol validation and error handling
- Binary encoding and decoding operations
- Multiaddr integration with peer IDs
- I2P address format validation
- Custom base64 alphabet handling (-~ instead of +/)

.. literalinclude:: ../examples/garlic/garlic_examples.py
   :language: python
   :caption: examples/garlic/garlic_examples.py

Running the Examples
--------------------

All examples can be run directly with Python:

.. code-block:: bash

    # DNS examples
    python examples/dns/dns_examples.py

    # DNSADDR examples
    python examples/dnsaddr/dnsaddr.py

    # QUIC examples
    python examples/quic/simple_quic_usage.py

    # Thin waist examples
    python examples/thin_waist/thin_waist_example.py

    # Decapsulate examples
    python examples/decapsulate/decapsulate_example.py

    # Garlic protocol examples
    python examples/garlic/garlic_examples.py

Note: Some examples require network connectivity and may take a few seconds to complete due to DNS resolution.
