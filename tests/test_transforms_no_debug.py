import logging

from multiaddr.transforms import bytes_to_string, string_to_bytes


def test_transforms_roundtrip_without_debug_noise(caplog):
    addr = "/ip4/127.0.0.1/tcp/4001"
    with caplog.at_level(logging.DEBUG, logger="multiaddr.transforms"):
        raw = string_to_bytes(addr)
        assert bytes_to_string(raw) == addr
    assert caplog.records == []
