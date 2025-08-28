History
=======

.. towncrier release notes start

py-multiaddr v0.0.10 (2025-08-28)
---------------------------------

Improved Documentation
~~~~~~~~~~~~~~~~~~~~~~

- Adds example of DNS address resolution. (`#75 <https://github.com/multiformats/py-multiaddr/issues/75>`__)


Features
~~~~~~~~

- Added support for CIDv1 format and improved sequence protocol handling with enhanced indexing and slicing operations. (`#65 <https://github.com/multiformats/py-multiaddr/issues/65>`__)
- Add quic tests. new quic example (`#66 <https://github.com/multiformats/py-multiaddr/issues/66>`__)
- Adds DNSADDR protocol support. (`#68 <https://github.com/multiformats/py-multiaddr/issues/68>`__)
- Add thin waist address validation (`#72 <https://github.com/multiformats/py-multiaddr/issues/72>`__)
- Adds support for p2p-circuit addresses. (`#74 <https://github.com/multiformats/py-multiaddr/issues/74>`__)
- Added full support for dnsaddr protocol and dns4 and dns6 as well (`#80 <https://github.com/multiformats/py-multiaddr/issues/80>`__)


Internal Changes - for py-multiaddr Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Enhanced type safety with comprehensive type hints, improved validation, and expanded test coverage for better code reliability and maintainability. (`#65 <https://github.com/multiformats/py-multiaddr/issues/65>`__)
- Added full tests and doc. All typecheck passes (`#80 <https://github.com/multiformats/py-multiaddr/issues/80>`__)
- Drop python3.9 and run py-upgrade, set up CI, add readthedocs config, updates to Makefile (`#85 <https://github.com/multiformats/py-multiaddr/issues/85>`__)


0.0.7 (2019-5-8)
----------------

* include subpackage
* refactor util and codec

0.0.5 (2019-5-7)
----------------

* unhexilified bytes
* new exceptions
* miscellaneous improvements [via alexander255_ `#42`_]

.. _alexander255: https://github.com/alexander255
.. _`#42`: https://github.com/multiformats/py-multiaddr/pull/42

0.0.2 (2016-5-4)
----------------

* Fix a bug in decapsulate that threw an IndexError instead of a copy of the
  Multiaddr when the original multiaddr does not contain the multiaddr to
  decapsulate. [via fredthomsen_ `#9`_]
* Increase test coverage [via fredthomsen_ `#9`_]

.. _fredthomsen: https://github.com/fredthomsen
.. _`#9`: https://github.com/multiformats/py-multiaddr/pull/9

0.0.1 (2016-1-22)
------------------

* First release on PyPI.
