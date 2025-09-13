History
=======

.. towncrier release notes start

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
