from main import parse_args
import pytest

def test_defaults(argv=None):
    arg = parse_args([])
    assert arg.log_level == "INFO"
    assert arg.config.endswith("project4/config.json")

def test_log_level_is_read():
    arg = parse_args(["--log-level", "DEBUG"])
    assert arg.log_level == "DEBUG"

def test_bad_log_level_exits_with_2():
    with pytest.raises(SystemExit) as e:
        parse_args(["--log-level", "LOUD"])
    assert e.value.code == 2