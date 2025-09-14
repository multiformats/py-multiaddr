import pytest

from multiaddr.codecs import memory
from multiaddr.exceptions import BinaryParseError


def test_to_bytes_and_to_string_roundtrip():
    codec = memory.Codec()

    # some valid values
    for val in [0, 1, 42, 2**32, 2**64 - 1]:
        s = str(val)
        b = codec.to_bytes(None, s)
        # must be exactly 8 bytes
        assert isinstance(b, bytes)
        assert len(b) == 8
        # roundtrip back to string
        out = codec.to_string(None, b)
        assert out == s


def test_invalid_string_to_bytes():
    codec = memory.Codec()

    # not a number
    with pytest.raises(ValueError):
        codec.to_bytes(None, "abc")

    # negative number
    with pytest.raises(ValueError):
        codec.to_bytes(None, "-1")

    # too large
    with pytest.raises(ValueError):
        codec.to_bytes(None, str(2**64))


def test_invalid_bytes_to_string():
    codec = memory.Codec()

    # too short
    with pytest.raises(BinaryParseError):
        codec.to_string(None, b"\x00\x01")

    # too long
    with pytest.raises(BinaryParseError):
        codec.to_string(None, b"\x00" * 9)


def test_specific_encoding():
    codec = memory.Codec()

    # 42 encoded in big-endian
    expected_bytes = b"\x00\x00\x00\x00\x00\x00\x00*"
    assert codec.to_bytes(None, "42") == expected_bytes
    assert codec.to_string(None, expected_bytes) == "42"


def test_memory_validate_function():
    # Directly test the helper
    codec = memory.Codec()

    # Valid case
    codec.memory_validate(b"\x00" * 8)  # should not raise

    # Invalid length
    with pytest.raises(ValueError):
        codec.memory_validate(b"\x00" * 7)
