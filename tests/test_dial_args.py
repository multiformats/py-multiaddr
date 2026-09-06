import pytest

from multiaddr import Multiaddr, dial_args


def test_dial_args_tcp4():
    assert dial_args(Multiaddr("/ip4/1.2.3.4/tcp/80")) == ("tcp4", "1.2.3.4:80")


def test_dial_args_tcp6():
    assert dial_args(Multiaddr("/ip6/::1/tcp/80")) == ("tcp6", "[::1]:80")


def test_dial_args_udp4():
    assert dial_args(Multiaddr("/ip4/1.2.3.4/udp/53")) == ("udp4", "1.2.3.4:53")


def test_dial_args_unix():
    assert dial_args(Multiaddr("/unix/var/run/docker.sock")) == (
        "unix",
        "/var/run/docker.sock",
    )


def test_dial_args_rejects_non_thin_waist():
    with pytest.raises(ValueError, match="thin waist"):
        dial_args(Multiaddr("/dns4/example.com/tcp/80"))
