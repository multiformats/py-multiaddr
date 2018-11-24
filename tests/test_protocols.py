from multiaddr import protocols
import pytest


def test_code_to_varint():
    vi = protocols.code_to_varint(5)
    assert vi == b'05'
    vi = protocols.code_to_varint(150)
    assert vi == b'9601'


def test_varint_to_code():
    cc = protocols.varint_to_code(b'05')
    assert cc == 5
    cc = protocols.varint_to_code(b'9601')
    assert cc == 150


@pytest.fixture
def valid_params():
    return {'code': protocols.P_IP4,
            'size': 32,
            'name': 'ipb4',
            'vcode': protocols.code_to_varint(protocols.P_IP4)}


def test_valid(valid_params):
    proto = protocols.Protocol(**valid_params)
    for key in valid_params:
        assert getattr(proto, key) == valid_params[key]


@pytest.mark.parametrize("invalid_code", [0.5, 'abc'])
def test_invalid_code(valid_params, invalid_code):
    assert invalid_code not in protocols._CODES
    valid_params['code'] = invalid_code
    with pytest.raises(ValueError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("invalid_size", [-2, 512, 1.3])
def test_invalid_size(valid_params, invalid_size):
    valid_params['size'] = invalid_size
    with pytest.raises(ValueError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("invalid_name", [123, 1.0])
def test_invalid_name(valid_params, invalid_name):
    valid_params['name'] = invalid_name
    with pytest.raises(ValueError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("invalid_vcode", [3, u'a3'])
def test_invalid_vcode(valid_params, invalid_vcode):
    valid_params['vcode'] = invalid_vcode
    with pytest.raises(ValueError):
        protocols.Protocol(**valid_params)


@pytest.mark.parametrize("name", ["foo-str", u"foo-u"])
def test_valid_names(valid_params, name):
    valid_params['name'] = name
    test_valid(valid_params)


def test_protocol_with_name():
    proto = protocols.protocol_with_name('ip4')
    assert proto.name == 'ip4'
    assert proto.code == protocols.P_IP4

    with pytest.raises(ValueError):
        proto = protocols.protocol_with_name('foo')


def test_protocol_with_code():
    proto = protocols.protocol_with_code(protocols.P_IP4)
    assert proto.name == 'ip4'
    assert proto.code == protocols.P_IP4

    with pytest.raises(ValueError):
        proto = protocols.protocol_with_code(1234)


def test_protocol_equality():
    proto1 = protocols.protocol_with_name('ip4')
    proto2 = protocols.protocol_with_code(protocols.P_IP4)
    proto3 = protocols.protocol_with_name('onion')

    assert proto1 == proto2
    assert proto1 != proto3


@pytest.mark.parametrize("names", [['ip4'],
                                   ['ip4', 'tcp'],
                                   ['ip4', 'tcp', 'udp']])
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
    names = ['ip4']
    ins = "/".join(names)
    test_protocols_with_string(names)
    with pytest.raises(ValueError):
        names.append("foo")
        ins = "/".join(names)
        protocols.protocols_with_string(ins)


# add_protocol is stateful, so we need to mock out
# multiaddr.protocols.PROTOCOLS
@pytest.fixture()
def patch_protocols(monkeypatch):
    monkeypatch.setattr(protocols, 'PROTOCOLS', [])
    monkeypatch.setattr(protocols, '_names_to_protocols', {})
    monkeypatch.setattr(protocols, '_codes_to_protocols', {})


def test_add_protocol(patch_protocols, valid_params):
    proto = protocols.Protocol(**valid_params)
    protocols.add_protocol(proto)
    assert protocols.PROTOCOLS == [proto]
    assert proto.name in protocols._names_to_protocols
    assert proto.code in protocols._codes_to_protocols
    proto = protocols.Protocol(
        protocols.P_TCP, 16, "tcp", protocols.code_to_varint(protocols.P_TCP))


def test_add_protocol_twice(patch_protocols, valid_params):
    proto = protocols.Protocol(**valid_params)
    protocols.add_protocol(proto)
    with pytest.raises(ValueError):
        protocols.add_protocol(proto)
    del protocols._names_to_protocols[proto.name]
    with pytest.raises(ValueError):
        protocols.add_protocol(proto)
    del protocols._codes_to_protocols[proto.code]
    protocols.add_protocol(proto)
    assert protocols.PROTOCOLS == [proto, proto]


def test_protocol_repr():
    proto = protocols.protocol_with_name('ip4')
    assert "Protocol(code=4, name='ip4', size=32)" == repr(proto)


@pytest.mark.parametrize("buf", [
    b'\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x01',
    b'\x90\x91\x92\x93\x94\x95\x96\x97\x98\x02'])
def test_overflowing_varint(buf):
    with pytest.raises(ValueError):
        protocols.read_varint_code(buf)


def test_nonterminated_varint():
    assert protocols.read_varint_code(b'\x80\x80') == (0, 0)
