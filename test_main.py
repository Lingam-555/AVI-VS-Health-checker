from main import parse_args
from main import main
import pytest

def test_defaults():
    arg = parse_args([])
    assert arg.log_level == "INFO"
    assert arg.config.endswith("config.json")

def test_log_level_is_read():
    arg = parse_args(["--log-level", "DEBUG"])
    assert arg.log_level == "DEBUG"

def test_bad_log_level_exits_with_2():
    with pytest.raises(SystemExit) as e:
        parse_args(["--log-level", "LOUD"])
    assert e.value.code == 2

def test_config_file_missing(tmp_path,capsys):
    config_file = tmp_path/"missing.json"
    with pytest.raises(SystemExit) as e:
        main(["--config",str(config_file)])
    captured = capsys.readouterr().out
    assert e.value.code == 1
    assert "Data File doesn't exist" in captured
    output_lines = captured.strip().splitlines()
    assert len(output_lines) == 1
    assert "Traceback" not in captured
