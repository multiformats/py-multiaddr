from multiaddr.protocols import Protocol


def test_protocol_size_and_path_use_cached_codec():
    proto = Protocol(6, "tcp", "uint16be")
    assert proto._codec_obj is None
    assert proto.size == 16
    assert proto._codec_obj is not None
    cached = proto._codec_obj
    assert proto.path is False
    assert proto._codec_obj is cached


def test_path_protocol_cached_path_flag():
    proto = Protocol(0x0190, "unix", "fspath")
    assert proto._codec_obj is None
    assert proto.path is True
    assert proto._codec_obj is not None
