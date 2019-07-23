from __future__ import absolute_import

import base58
import six

from . import LENGTH_PREFIXED_VAR_SIZE


SIZE = LENGTH_PREFIXED_VAR_SIZE
IS_PATH = False


def to_bytes(proto, string):
    # the address is a base58-encoded string
    if six.PY2 and isinstance(string, unicode):  # pragma: no cover (PY2)  # noqa: F821
        string = string.encode('ascii')

    if not 25 <= len(string) <= 35:
        raise ValueError('ZeroNet site address must have 25-35 chars')

    mm = base58.b58decode(string)
    return mm


def to_string(proto, buf):
    return base58.b58encode(buf).decode('ascii')
