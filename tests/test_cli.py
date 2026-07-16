import json
import sys
from unittest.mock import patch

import pytest

from multiaddr import cli


def test_cli_string(capsys):
    with patch.object(sys, "argv", ["multiaddr", "/ip4/1.2.3.4/tcp/80"]):
        cli.main()
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert data["string"] == "/ip4/1.2.3.4/tcp/80"
    assert data["packed"] == "0x0401020304060050"
    assert data["packedSize"] == 8
    assert len(data["components"]) == 2
    
    assert data["components"][0]["protocol"] == "ip4"
    assert data["components"][0]["value"] == "1.2.3.4"
    assert data["components"][0]["rawValue"] == "0x01020304"
    
    assert data["components"][1]["protocol"] == "tcp"
    assert data["components"][1]["value"] == "80"
    assert data["components"][1]["rawValue"] == "0x0050"


def test_cli_hex(capsys):
    with patch.object(sys, "argv", ["multiaddr", "0x0401020304060050"]):
        cli.main()
    
    out, _ = capsys.readouterr()
    data = json.loads(out)
    
    assert data["string"] == "/ip4/1.2.3.4/tcp/80"
    assert data["packed"] == "0x0401020304060050"


def test_cli_compact(capsys):
    with patch.object(sys, "argv", ["multiaddr", "-c", "/ip4/1.2.3.4"]):
        cli.main()
    
    out, _ = capsys.readouterr()
    assert "\n" not in out.strip()
    data = json.loads(out)
    assert data["string"] == "/ip4/1.2.3.4"


def test_cli_invalid_input(capsys):
    with patch.object(sys, "argv", ["multiaddr", "/invalid/input"]):
        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 1
    
    _, err = capsys.readouterr()
    assert "Error parsing multiaddr:" in err
