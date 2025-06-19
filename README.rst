py-multiaddr
==========================

.. image:: https://img.shields.io/pypi/v/multiaddr.svg
        :target: https://pypi.python.org/pypi/multiaddr

.. image:: https://api.travis-ci.com/multiformats/py-multiaddr.svg?branch=master
        :target: https://travis-ci.com/multiformats/py-multiaddr

.. image:: https://codecov.io/github/multiformats/py-multiaddr/coverage.svg?branch=master
        :target: https://codecov.io/github/multiformats/py-multiaddr?branch=master

.. image:: https://readthedocs.org/projects/multiaddr/badge/?version=latest
        :target: https://readthedocs.org/projects/multiaddr/?badge=latest
        :alt: Documentation Status
..

    multiaddr_ implementation in Python

.. _multiaddr: https://github.com/multiformats/multiaddr

..


.. contents:: :local:

Usage
=====

Simple
------

.. code-block:: python

    from multiaddr import Multiaddr

    # construct from a string
    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")

    # construct from bytes
    #m2 = Multiaddr(bytes_addr=m1.to_bytes()) # deprecated
    m2 = Multiaddr(m1.to_bytes())

    assert str(m1) == "/ip4/127.0.0.1/udp/1234"
    assert str(m1) == str(m2)
    assert m1.to_bytes() == m2.to_bytes()
    assert m1 == m2
    assert m2 == m1
    assert not (m1 != m2)
    assert not (m2 != m1)


Protocols
---------

.. code-block:: python

    from multiaddr import Multiaddr

    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")

    # get the multiaddr protocol description objects
    m1.protocols()
    # [Protocol(code=4, name='ip4', size=32), Protocol(code=17, name='udp', size=16)]


En/decapsulate
--------------

.. code-block:: python

    from multiaddr import Multiaddr

    m1 = Multiaddr("/ip4/127.0.0.1/udp/1234")
    m1.encapsulate(Multiaddr("/sctp/5678"))
    # <Multiaddr /ip4/127.0.0.1/udp/1234/sctp/5678>
    m1.decapsulate(Multiaddr("/udp"))
    # <Multiaddr /ip4/127.0.0.1>


Tunneling
---------

Multiaddr allows expressing tunnels very nicely.


.. code-block:: python

    printer = Multiaddr("/ip4/192.168.0.13/tcp/80")
    proxy = Multiaddr("/ip4/10.20.30.40/tcp/443")
    printerOverProxy = proxy.encapsulate(printer)
    print(printerOverProxy)
    # /ip4/10.20.30.40/tcp/443/ip4/192.168.0.13/tcp/80

    proxyAgain = printerOverProxy.decapsulate(printer)
    print(proxyAgain)
    # /ip4/10.20.30.40/tcp/443

DNS Resolution
-------------

Multiaddr supports DNS-based address resolution using the DNSADDR protocol.


.. code-block:: python

    from multiaddr import Multiaddr

    # Create a DNSADDR multiaddr
    ma = Multiaddr("/dnsaddr/example.com")
    
    # Resolve to actual IP addresses
    resolved = await ma.resolve()
    print(resolved)
    # [Multiaddr("/ip4/93.184.216.34"), Multiaddr("/ip6/2606:2800:220:1:248:1893:25c8:1946")]

    # DNSADDR with peer ID
    ma_with_peer = Multiaddr("/dnsaddr/example.com/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")
    resolved_with_peer = await ma_with_peer.resolve()
    print(resolved_with_peer)
    # [Multiaddr("/ip4/93.184.216.34/p2p/QmYyQSo1c1Ym7orWxLYvCrM2EmxFTANf8wXmmE7wjh53Qk")]

    # Using the DNS resolver directly
    from multiaddr.resolvers import DNSResolver
    resolver = DNSResolver()
    resolved = await resolver.resolve(ma)
    print(resolved)
    # [Multiaddr("/ip4/93.184.216.34"), Multiaddr("/ip6/2606:2800:220:1:248:1893:25c8:1946")]

Maintainers
===========

Original author: `@sbuss`_.

Contribute
==========

Contributions welcome. Please check out `the issues`_.

Check out our `contributing document`_ for more information on how we work, and about contributing in general.
Please be aware that all interactions related to multiformats are subject to the IPFS `Code of Conduct`_.

License
=======

Dual-licensed:

-  `MIT`_ © 2014 Steven Buss
-  `Apache 2`_ © 2014 Steven Buss

.. _the issues: https://github.com/multiformats/py-multiaddr/issues
.. _contributing document: https://github.com/multiformats/multiformats/blob/master/contributing.md
.. _Code of Conduct: https://github.com/ipfs/community/blob/master/code-of-conduct.md
.. _standard-readme: https://github.com/RichardLitt/standard-readme
.. _MIT: LICENSE-MIT
.. _Apache 2: LICENSE-APACHE2
.. _`@sbuss`: https://github.com/sbuss
