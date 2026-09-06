from unittest.mock import patch

from multiaddr import Multiaddr, interface_multiaddrs


def test_interface_multiaddrs_builds_multiaddrs():
    with patch("multiaddr.utils.get_network_addrs") as mock_addrs:
        mock_addrs.side_effect = lambda family: (["192.0.2.10"] if family == 4 else ["2001:db8::1"])
        addrs = interface_multiaddrs()
    assert addrs == [
        Multiaddr("/ip4/192.0.2.10"),
        Multiaddr("/ip6/2001:db8::1"),
    ]


def test_interface_multiaddrs_empty_when_no_interfaces():
    with patch("multiaddr.utils.get_network_addrs", return_value=[]):
        assert interface_multiaddrs() == []
