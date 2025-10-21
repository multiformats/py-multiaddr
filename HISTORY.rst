History
=======

.. towncrier release notes start

py-multiaddr v0.0.12 (2025-10-21)
---------------------------------

Features
~~~~~~~~

- Added the http-path protocol in reference with go-multiaddr. (`#94 <https://github.com/multiformats/py-multiaddr/issues/94>`__)
- Added ipcidr protocol support to py-multiaddr

  - Implements protocol code 43 (0x2B) for CIDR notation support
  - Full compatibility with Go multiaddr implementation
  - Comprehensive test coverage including edge cases (`#95 <https://github.com/multiformats/py-multiaddr/issues/95>`__)
- Added garlic32 and garlic64 protocol support to py-multiaddr

  - Implements protocol code 446 and 447.
  - Full compatibility with Go multiaddr implementation
  - Comprehensive test coverage including edge cases
  - Complete documentation and examples in examples/garlic/garlic_examples.py
  - Integration with multiaddr documentation system (`#96 <https://github.com/multiformats/py-multiaddr/issues/96>`__)


py-multiaddr v0.0.11 (2025-09-15)
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
- Integrated the memory protocol, in reference with go-libp2p (`#92 <https://github.com/multiformats/py-multiaddr/issues/92>`__)


Internal Changes - for py-multiaddr Contributors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Enhanced type safety with comprehensive type hints, improved validation, and expanded test coverage for better code reliability and maintainability. (`#65 <https://github.com/multiformats/py-multiaddr/issues/65>`__)
- Added full tests and doc. All typecheck passes (`#80 <https://github.com/multiformats/py-multiaddr/issues/80>`__)
- Drop python3.9 and run py-upgrade, set up CI, add readthedocs config, updates to Makefile (`#85 <https://github.com/multiformats/py-multiaddr/issues/85>`__)


0.0.10 (2025-6-18)
------------------

* Fix Type Issues and add strict type checks using Ruff & Pyright
* Spec updates, Python 3.4- unsupport & custom registries by @ntninja in #59
* add quic-v1 protocol by @justheuristic in #63
* Fix/typecheck by @acul71 in #65
* chore: rm local pyrightconfig.json by @arcinston in #70

0.0.9 (2019-12-23)
------------------

* Add Multiaddr.__hash__ method for hashable multiaddrs
* Add onion3 address support
* Fix broken reST and links in documentation
* Remove emoji from README.rst

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
