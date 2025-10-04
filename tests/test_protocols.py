import base64
import os

import pytest
import varint

from multiaddr import Multiaddr, exceptions, protocols
from multiaddr.codecs import garlic32, garlic64, http_path, ipcidr, memory
from multiaddr.exceptions import BinaryParseError, StringParseError


def test_code_to_varint():
    vi = varint.encode(5)
    assert vi == b"\x05"
    vi = varint.encode(150)
    assert vi == b"\x96\x01"


def test_varint_to_code():
    cc = varint.decode_bytes(b"\x05")
    assert cc == 5
    cc = varint.decode_bytes(b"\x96\x01")
    assert cc == 150


@pytest.fixture
def valid_params():
    return {"code": protocols.P_IP4, "name": "ipb4", "codec": "ipb"}


def test_valid(valid_params):
    proto = protocols.Protocol(**valid_params)
    for key in valid_params:
        assert getattr(proto, key) == valid_params[key]


@pytest.mark.parametrize("invalid_code", ["abc"])
def test_invalid_code(valid_params, invalid_code):
    valid_params["code"] = invalid_code
    with pytest.raises(TypeError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("invalid_name", [123, 1.0])
def test_invalid_name(valid_params, invalid_name):
    valid_params["name"] = invalid_name
    with pytest.raises(TypeError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("invalid_codec", [b"ip4", 123, 0.123])
def test_invalid_codec(valid_params, invalid_codec):
    valid_params["codec"] = invalid_codec
    with pytest.raises(TypeError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("name", ["foo-str", "foo-u"])
def test_valid_names(valid_params, name):
    valid_params["name"] = name
    test_valid(valid_params)


@pytest.mark.parametrize("codec", ["ip4", "ip6"])
def test_valid_codecs(valid_params, codec):
    valid_params["codec"] = codec
    test_valid(valid_params)


def test_protocol_with_name():
    proto = protocols.protocol_with_name("ip4")
    assert proto.name == "ip4"
    assert proto.code == protocols.P_IP4
    assert proto.size == 32
    assert proto.vcode == varint.encode(protocols.P_IP4)
    assert protocols.protocol_with_any("ip4") == proto
    assert protocols.protocol_with_any(proto) == proto

    with pytest.raises(exceptions.ProtocolNotFoundError):
        proto = protocols.protocol_with_name("foo")


def test_protocol_with_code():
    proto = protocols.protocol_with_code(protocols.P_IP4)
    assert proto.name == "ip4"
    assert proto.code == protocols.P_IP4
    assert proto.size == 32
    assert proto.vcode == varint.encode(protocols.P_IP4)
    assert protocols.protocol_with_any(protocols.P_IP4) == proto
    assert protocols.protocol_with_any(proto) == proto

    with pytest.raises(exceptions.ProtocolNotFoundError):
        proto = protocols.protocol_with_code(1234)


def test_protocol_equality():
    proto1 = protocols.protocol_with_name("ip4")
    proto2 = protocols.protocol_with_code(protocols.P_IP4)
    proto3 = protocols.protocol_with_name("onion")
    proto4 = protocols.protocol_with_name("onion3")

    assert proto1 == proto2
    assert proto1 != proto3
    assert proto3 != proto4
    assert proto1 is not None
    assert proto2 != str(proto2)


@pytest.mark.parametrize("names", [["ip4"], ["ip4", "tcp"], ["ip4", "tcp", "udp"]])
def test_protocols_with_string(names):
    expected = [protocols.protocol_with_name(name) for name in names]
    ins = "/".join(names)
    assert protocols.protocols_with_string(ins) == expected
    assert protocols.protocols_with_string("/" + ins) == expected
    assert protocols.protocols_with_string("/" + ins + "/") == expected


@pytest.mark.parametrize("invalid_name", ["", "/", "//"])
def test_protocols_with_string_invalid(invalid_name):
    assert protocols.protocols_with_string(invalid_name) == []


def test_protocols_with_string_mixed():
    names = ["ip4"]
    ins = "/".join(names)
    test_protocols_with_string(names)
    with pytest.raises(exceptions.StringParseError):
        names.append("foo")
        ins = "/".join(names)
        protocols.protocols_with_string(ins)


def test_add_protocol(valid_params):
    registry = protocols.ProtocolRegistry()
    proto = protocols.Protocol(**valid_params)
    registry.add(proto)
    assert proto.name in registry._names_to_protocols
    assert proto.code in registry._codes_to_protocols
    assert registry.find(proto.name) is registry.find(proto.code) is proto


def test_add_protocol_twice(valid_params):
    registry = protocols.ProtocolRegistry()
    proto = registry.add(protocols.Protocol(**valid_params))

    with pytest.raises(exceptions.ProtocolExistsError):
        registry.add(proto)
    del registry._names_to_protocols[proto.name]
    with pytest.raises(exceptions.ProtocolExistsError):
        registry.add(proto)
    del registry._codes_to_protocols[proto.code]
    registry.add(proto)


def test_add_protocol_alias():
    registry = protocols.REGISTRY.copy(unlock=True)
    tcp_proto = protocols.protocol_with_name("tcp")
    registry.add_alias_name("tcp", "abcd")
    registry.add_alias_code(tcp_proto, 123456)

    with pytest.raises(exceptions.ProtocolExistsError):
        registry.add_alias_name("tcp", "abcd")
    with pytest.raises(exceptions.ProtocolExistsError):
        registry.add_alias_code(tcp_proto, 123456)

    assert registry.find("tcp") is registry.find("abcd")
    assert registry.find("tcp") is registry.find(123456)


def test_add_protocol_lock(valid_params):
    registry = protocols.REGISTRY.copy(unlock=True)
    assert not registry.locked
    registry.lock()
    assert registry.locked

    with pytest.raises(exceptions.ProtocolRegistryLocked):
        registry.add(protocols.Protocol(**valid_params))
    with pytest.raises(exceptions.ProtocolRegistryLocked):
        registry.add_alias_name("tcp", "abcdef")
    with pytest.raises(exceptions.ProtocolRegistryLocked):
        tcp_proto = protocols.protocol_with_name("tcp")
        registry.add_alias_code(tcp_proto, 123456)


def test_protocol_repr():
    proto = protocols.protocol_with_name("ip4")
    assert "Protocol(code=4, name='ip4', codec='ip4')" == repr(proto)


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


def test_memory_integration_edge_values():
    # Minimum (0)
    ma0 = Multiaddr("/memory/0")
    assert str(ma0) == "/memory/0"
    assert ma0.value_for_protocol(777) == "0"

    # Maximum (2**64 - 1)
    max_val = str(2**64 - 1)
    mamax = Multiaddr(f"/memory/{max_val}")
    assert str(mamax) == f"/memory/{max_val}"
    assert mamax.value_for_protocol(777) == max_val


def test_memory_integration_invalid_values():
    # Negative number
    with pytest.raises(ValueError):
        Multiaddr("/memory/-1")

    # Too large (overflow > uint64)
    with pytest.raises(ValueError):
        Multiaddr(f"/memory/{2**64}")


def test_http_path_bytes_string_roundtrip():
    codec = http_path.Codec()

    # some valid HTTP path strings (URL-encoded input as expected by multiaddr system)
    from urllib.parse import quote

    for s in ["/foo", "/foo/bar", "/a b", "/こんにちは", "/path/with/special!@#"]:
        encoded_s = quote(s, safe="")  # Use same encoding as codec
        b = codec.to_bytes(None, encoded_s)
        assert isinstance(b, bytes)
        out = codec.to_string(None, b)
        # Should return the same URL-encoded string
        assert out == encoded_s


def test_http_path_empty_string_raises():
    codec = http_path.Codec()
    with pytest.raises(ValueError):
        codec.to_bytes(None, "")


def test_http_path_empty_bytes_raises():
    codec = http_path.Codec()
    with pytest.raises(BinaryParseError):
        codec.to_string(None, b"")


def test_http_path_special_characters():
    codec = http_path.Codec()
    path = "/foo bar/あいうえお"
    from urllib.parse import quote

    encoded_path = quote(path, safe="")  # Use same encoding as codec
    b = codec.to_bytes(None, encoded_path)

    assert codec.to_string(None, b) == encoded_path


def test_http_path_validate_function():
    codec = http_path.Codec()

    # valid path
    codec.validate(b"/valid/path")  # should not raise

    # empty path
    with pytest.raises(ValueError):
        codec.validate(b"")


# --- Garlic64 Test Data ---
INVALID_BYTES_385 = os.urandom(385)
SHORT_GARLIC64_STRING = base64.b64encode(INVALID_BYTES_385, altchars=b"-~").decode("utf-8")

VALID_BYTES_386 = os.urandom(386)
VALID_GARLIC64_STRING_386 = base64.b64encode(VALID_BYTES_386, altchars=b"-~").decode("utf-8")


def test_garlic64_valid_roundtrip():
    codec = garlic64.Codec()

    # Convert the valid string to bytes
    b = codec.to_bytes(None, VALID_GARLIC64_STRING_386)
    assert isinstance(b, bytes)
    assert b == VALID_BYTES_386

    # Convert the bytes back to a string
    s_out = codec.to_string(None, b)
    assert s_out == VALID_GARLIC64_STRING_386


def test_garlic64_custom_alphabet():
    codec = garlic64.Codec()

    special_bytes = b"\xff" * 386

    # Standard base64 would have '+' and '/'
    standard_b64 = base64.b64encode(special_bytes).decode("utf-8")
    assert "+" in standard_b64 or "/" in standard_b64

    # Our codec should produce a string with '-' and '~' instead
    garlic_str = codec.to_string(None, special_bytes)
    assert "+" not in garlic_str
    assert "/" not in garlic_str
    assert "-" in garlic_str or "~" in garlic_str


def test_garlic64_string_decodes_to_short_bytes_raises():
    """
    Tests that calling to_bytes() with a string that decodes to less than
    386 bytes raises a ValueError, as the validation should fail.
    """
    codec = garlic64.Codec()
    with pytest.raises(ValueError):
        codec.to_bytes(None, SHORT_GARLIC64_STRING)


def test_garlic64_bytes_too_short_raises():
    """
    Tests that calling to_string() with a byte array shorter than
    386 bytes raises a ValueError.
    """
    codec = garlic64.Codec()
    with pytest.raises(ValueError):
        codec.to_string(None, INVALID_BYTES_385)


def test_garlic64_invalid_b64_string_raises():
    """
    Tests that passing a string with invalid Base64 characters to
    to_bytes() raises a ValueError.
    """
    codec = garlic64.Codec()
    invalid_string = "this-is-not-valid-base64-!@#$%"
    with pytest.raises(ValueError):
        codec.to_bytes(None, invalid_string)


def test_garlic64_memory_validate_function():
    """
    Directly tests the memory_validate method to ensure it correctly
    validates byte length.
    """
    codec = garlic64.Codec()

    # A valid byte array should not raise an error
    codec.validate(VALID_BYTES_386)

    # An invalid (too short) byte array should raise a ValueError
    with pytest.raises(ValueError):
        codec.validate(INVALID_BYTES_385)


def create_garlic32_string(b: bytes) -> str:
    """Helper to create a valid garlic32 string from bytes."""
    return base64.b32encode(b).decode("utf-8").lower().rstrip("=")


# --- Garlic32 Test Data ---
# Valid length: 32 bytes
VALID_BYTES_32 = os.urandom(32)
VALID_GARLIC32_STRING_32 = create_garlic32_string(VALID_BYTES_32)

# Valid length: 35 bytes
VALID_BYTES_35 = os.urandom(35)
VALID_GARLIC32_STRING_35 = create_garlic32_string(VALID_BYTES_35)

# Valid length: 40 bytes
VALID_BYTES_40 = os.urandom(40)
VALID_GARLIC32_STRING_40 = create_garlic32_string(VALID_BYTES_40)

# Invalid length: 34 bytes
INVALID_BYTES_34 = os.urandom(34)
INVALID_GARLIC32_STRING_34 = create_garlic32_string(INVALID_BYTES_34)


@pytest.mark.parametrize(
    "valid_bytes, valid_string",
    [
        (VALID_BYTES_32, VALID_GARLIC32_STRING_32),
        (VALID_BYTES_35, VALID_GARLIC32_STRING_35),
        (VALID_BYTES_40, VALID_GARLIC32_STRING_40),
    ],
)
def test_garlic32_valid_roundtrip(valid_bytes, valid_string):
    """
    Tests that valid garlic32 strings of different lengths can be
    converted to bytes and back without modification.
    """
    codec = garlic32.Codec()

    # Convert the valid string to bytes
    b = codec.to_bytes(None, valid_string)
    assert isinstance(b, bytes)
    assert b == valid_bytes

    # Convert the bytes back to a string
    s_out = codec.to_string(None, b)
    assert s_out == valid_string


def test_garlic32_padding_and_case_handling():
    """
    Tests that the codec correctly handles stripped padding and is case-insensitive
    on input, while producing lowercase, unpadded output.
    """
    codec = garlic32.Codec()
    # String is lowercase and has no padding
    assert codec.to_string(None, VALID_BYTES_32) == VALID_GARLIC32_STRING_32

    # Decoder should handle uppercase input
    assert codec.to_bytes(None, VALID_GARLIC32_STRING_32.upper()) == VALID_BYTES_32


def test_garlic32_bytes_invalid_length_raises():
    """
    Tests that to_string() raises an error if the byte array has an
    invalid length.
    """
    codec = garlic32.Codec()
    with pytest.raises(ValueError):
        codec.to_string(None, INVALID_BYTES_34)  # 34 bytes is invalid
    with pytest.raises(ValueError):
        codec.to_string(None, os.urandom(31))  # 31 bytes is invalid


def test_garlic32_invalid_b32_string_raises():
    """
    Tests that passing a string with invalid Base32 characters
    (like '1' or '8') raises a ValueError.
    """
    codec = garlic32.Codec()
    # Add padding to make it a valid length for b32decode to attempt parsing
    invalid_string = "thisisnotvalidbase32string1890===="
    with pytest.raises(ValueError):
        codec.to_bytes(None, invalid_string)


def test_garlic32_memory_validate_function():
    """
    Directly tests the memory_validate method.
    """
    codec = garlic32.Codec()

    # Valid lengths
    codec.validate(VALID_BYTES_32)
    codec.validate(VALID_BYTES_35)
    codec.validate(VALID_BYTES_40)

    # Invalid lengths
    with pytest.raises(ValueError):
        codec.validate(INVALID_BYTES_34)
    with pytest.raises(ValueError):
        codec.validate(os.urandom(0))
    with pytest.raises(ValueError):
        codec.validate(os.urandom(33))


# --- IPCIDR Tests ---
def test_ipcidr_valid_roundtrip():
    codec = ipcidr.Codec()

    for val in ["0", "8", "16", "24", "32", "128", "255"]:
        b = codec.to_bytes(None, val)
        s = codec.to_string(None, b)

        # back and forth conversion should match
        assert s == val
        assert codec.to_bytes(None, s) == b


def test_ipcidr_bytes_to_string():
    codec = ipcidr.Codec()

    assert codec.to_string(None, bytes([0])) == "0"
    assert codec.to_string(None, bytes([24])) == "24"
    assert codec.to_string(None, bytes([255])) == "255"


def test_ipcidr_invalid_string_inputs():
    codec = ipcidr.Codec()

    with pytest.raises(StringParseError):
        codec.to_bytes(None, "-1")  # negative

    with pytest.raises(StringParseError):
        codec.to_bytes(None, "256")  # too large

    with pytest.raises(StringParseError):
        codec.to_bytes(None, "abc")  # not a number


def test_ipcidr_invalid_bytes_inputs():
    codec = ipcidr.Codec()

    with pytest.raises(BinaryParseError):
        codec.to_string(None, b"")  # empty

    with pytest.raises(BinaryParseError):
        codec.to_string(None, b"\x01\x02")  # too long

    with pytest.raises(ValueError):
        codec.validate(b"")  # validate should fail empty

    with pytest.raises(ValueError):
        codec.validate(b"\x01\x02")
