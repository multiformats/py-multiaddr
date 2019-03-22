# -*- encoding: utf-8 -*-
import pytest

from multiaddr.codec import find_codec_by_name
from multiaddr.codec import bytes_iter
from multiaddr.codec import bytes_to_string
from multiaddr.codec import size_for_addr
from multiaddr.codec import string_to_bytes

import multiaddr.protocols
from multiaddr.protocols import _codes_to_protocols
from multiaddr.protocols import _names_to_protocols
from multiaddr.protocols import protocol_with_code
from multiaddr.protocols import Protocol

# These test values were generated by running them
# through the go implementation of multiaddr.
# https://github.com/jbenet/multiaddr
ADDR_BYTES_MAP_STR_TEST_DATA = [
    (_names_to_protocols['ip4'], b'\x0a\x0b\x0c\x0d', '10.11.12.13'),
    (_names_to_protocols['ip6'],
     b'\x1a\xa1\x2b\xb2\x3c\xc3\x4d\xd4\x5e\xe5\x6f\xf6\x7a\xb7\x8a\xc8',
     '1aa1:2bb2:3cc3:4dd4:5ee5:6ff6:7ab7:8ac8'),
    (_names_to_protocols['tcp'], b'\xab\xcd', '43981'),
    (_names_to_protocols['onion'],
     b'\x9a\x18\x08\x73\x06\x36\x90\x43\x09\x1f\x04\xd2',
     'timaq4ygg2iegci7:1234'),
    (_names_to_protocols['p2p'],
     b'\x12\x20\xd5\x2e\xbb\x89\xd8\x5b\x02\xa2\x84\x94\x82\x03\xa6\x2f\xf2'
     b'\x83\x89\xc5\x7c\x9f\x42\xbe\xec\x4e\xc2\x0d\xb7\x6a\x68\x91\x1c\x0b',
     'QmcgpsyWgH8Y8ajJz1Cu72KnS5uo2Aa2LpzU7kinSupNKC'),

# Additional test data
    (_names_to_protocols['dns4'],
     b'xn--4gbrim.xn----ymcbaaajlc6dj7bxne2c.xn--wgbh1c',
     u'موقع.وزارة-الاتصالات.مصر'),  # Explicietly mark this as unicode to force the text to be LTR in editors
    (_names_to_protocols['dns4'],
     b'xn--fuball-cta.example',
     u'fußball.example'),  # This will fail if IDNA-2003/NamePrep is used
]

BYTES_MAP_STR_TEST_DATA = [
    ("/ip4/127.0.0.1/udp/1234", b'\x04\x7f\x00\x00\x01\x91\x02\x04\xd2'),
    ("/ip4/127.0.0.1/tcp/4321", b'\x04\x7f\x00\x00\x01\x06\x10\xe1'),
    ("/ip4/127.0.0.1/udp/1234/ip4/127.0.0.1/tcp/4321",
     b'\x04\x7f\x00\x00\x01\x91\x02\x04\xd2\x04\x7f\x00\x00\x01\x06\x10\xe1')
]


@pytest.mark.parametrize("codec_name, buf, expected", [
    (None, b'\x01\x02\x03', (0, 0)),
    ('ip4', b'\x01\x02\x03', (4, 0)),
    ('p2p', b'\x40\x50\x60\x51', (64, 1)),
])
def test_size_for_addr(codec_name, buf, expected):
    assert size_for_addr(find_codec_by_name(codec_name), buf) == expected


@pytest.mark.parametrize("buf, expected", [
    # "/ip4/127.0.0.1/udp/1234/ip4/127.0.0.1/tcp/4321"
    (b'\x04\x7f\x00\x00\x01\x91\x02\x04\xd2\x04\x7f\x00\x00\x01\x06\x10\xe1',
     [(_names_to_protocols["ip4"], b'\x7f\x00\x00\x01'),
      (_names_to_protocols["udp"], b'\x04\xd2'),
      (_names_to_protocols["ip4"], b'\x7f\x00\x00\x01'),
      (_names_to_protocols["tcp"], b'\x10\xe1')]),
])
def test_bytes_iter(buf, expected):
    assert list((proto, val) for proto, _, val in bytes_iter(buf)) == expected


@pytest.mark.parametrize("proto, buf, expected", ADDR_BYTES_MAP_STR_TEST_DATA)
def test_codec_to_string(proto, buf, expected):
    assert find_codec_by_name(proto.codec).to_string(proto, buf) == expected


@pytest.mark.parametrize("proto, expected, string",
                         ADDR_BYTES_MAP_STR_TEST_DATA)
def test_codec_to_bytes(proto, string, expected):
    assert find_codec_by_name(proto.codec).to_bytes(proto, string) == expected


@pytest.mark.parametrize("string, buf", BYTES_MAP_STR_TEST_DATA)
def test_string_to_bytes(string, buf):
    assert string_to_bytes(string) == buf


@pytest.mark.parametrize("string, buf", BYTES_MAP_STR_TEST_DATA)
def test_bytes_to_string(string, buf):
    assert bytes_to_string(buf) == string


class DummyProtocol(Protocol):
    def __init__(self, code, name, codec=None):
        self.code = code
        self.name = name
        self.codec = codec


class UnparsableProtocol(DummyProtocol):
	def __init__(self):
		super(UnparsableProtocol, self).__init__(333, "unparsable", "?")


@pytest.fixture
def protocol_extension(monkeypatch):
	# “Add” additional non-parsable protocol to protocols from code list
	names_to_protocols = _names_to_protocols.copy()
	codes_to_protocols = _codes_to_protocols.copy()
	names_to_protocols["unparsable"] = codes_to_protocols[333] = UnparsableProtocol()
	monkeypatch.setattr(multiaddr.protocols, "_names_to_protocols", names_to_protocols)
	monkeypatch.setattr(multiaddr.protocols, "_codes_to_protocols", codes_to_protocols)


@pytest.mark.parametrize("string", [
	'test',
	'/ip4/',
	'/unparsable/5'
])
def test_string_to_bytes_value_error(protocol_extension, string):
	with pytest.raises(ValueError):
		string_to_bytes(string)


@pytest.mark.parametrize("bytes", [
	b'\xcd\x02\x0c\x0d'
])
def test_bytes_to_string_value_error(protocol_extension, bytes):
	with pytest.raises(ValueError):
		bytes_to_string(bytes)


@pytest.mark.parametrize("proto, address", [
    (_names_to_protocols['ip4'], '1124.2.3'),
    (_names_to_protocols['ip6'], '123.123.123.123'),
    (_names_to_protocols['tcp'], 'a'),
    (_names_to_protocols['tcp'], '100000'),
    (_names_to_protocols['onion'], '100000'),
    (_names_to_protocols['onion'], '1234567890123456:0'),
    (_names_to_protocols['onion'], 'timaq4ygg2iegci7:a'),
    (_names_to_protocols['onion'], 'timaq4ygg2iegci7:0'),
    (_names_to_protocols['onion'], 'timaq4ygg2iegci7:71234'),
    (_names_to_protocols['p2p'], '15230d52ebb89d85b02a284948203a'),
])
def test_codec_to_bytes_value_error(proto, address):
    with pytest.raises(ValueError):
        find_codec_by_name(proto.codec).to_bytes(proto, address)


@pytest.mark.parametrize("proto, buf", [
    (_names_to_protocols['tcp'], b'\xff\xff\xff\xff')
])
def test_codec_to_string_value_error(proto, buf):
    with pytest.raises(ValueError):
        find_codec_by_name(proto.codec).to_string(proto, buf)
