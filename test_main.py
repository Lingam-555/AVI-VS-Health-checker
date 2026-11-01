from main import parse_args
from main import main
from exceptions import ControllerLoginError
import pytest
import json

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

def test_warning_key_missing(tmp_path,capsys):
    config_data = {
    "critical": 500,
    "url": "http://127.0.0.1:8000",
    "username": "admin",
    "max_pages": 10,
    "output_file": "vs_health.csv"
    }
    config_file = tmp_path/"config.json"

    with open(config_file, "w") as f:
        json.dump(config_data,f,indent=2)
    
    with pytest.raises(SystemExit) as e:
        main(["--config",str(config_file)])
    captured = capsys.readouterr().out
    assert e.value.code == 1
    assert f"Invalid Key:{config_file} is missing the key 'warning'" in captured
    output_lines = captured.strip().splitlines()
    assert len(output_lines) == 1

def test_avi_password_not_set(monkeypatch,tmp_path,capsys):
    monkeypatch.delenv("AVI_PASSWORD", raising=False)
    config_data = {
    "warning": 200,
    "critical": 500,
    "url": "http://127.0.0.1:8000",
    "username": "admin",
    "max_pages": 10,
    "output_file": "vs_health.csv"
    }
    config_file = tmp_path/"config.json"
    with open(config_file, "w") as f:
        json.dump(config_data,f,indent=2)
    with pytest.raises(SystemExit) as e:
        main(["--config",str(config_file)])
    captured = capsys.readouterr().out
    assert e.value.code == 1
    assert "AVI_PASSWORD is not set" in captured
    assert len(captured.strip().splitlines()) == 1

def test_login_rejected(monkeypatch,tmp_path,capsys):
    monkeypatch.setenv("AVI_PASSWORD", "tiger")
    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def login(self):
            raise ControllerLoginError("Login rejected")
    monkeypatch.setattr("main.AviHttpClient", FakeClient)
    config_data = {
        "warning": 200,
        "critical": 500,
        "url": "http://127.0.0.1:8000",
        "username": "admin",
        "max_pages": 10,
        "output_file": "vs_health.csv"
        }
    config_file = tmp_path/"config.json"
    with open(config_file, "w") as f:
        json.dump(config_data,f,indent=2)
    with pytest.raises(SystemExit) as e:
        main(["--config",str(config_file)])
    captured = capsys.readouterr().out
    assert e.value.code == 1
    assert "Login rejected" in captured
    assert len(captured.strip().splitlines()) == 1

def test_normal_run_prints_report(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("AVI_PASSWORD", "tiger")

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def login(self):
            pass

        def list_all_vs(self):
            return []

    monkeypatch.setattr("main.AviHttpClient", FakeClient)

    config_data = {
        "warning": 200,
        "critical": 500,
        "url": "http://127.0.0.1:8000",
        "username": "admin",
        "max_pages": 10,
        "output_file": str(tmp_path / "vs_health.csv"),
    }
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(config_data, f, indent=2)

    main(["--config", str(config_file)])

    captured = capsys.readouterr().out
    assert "Healthy count : 0" in captured
    assert "Down count: 0" in captured
    assert (tmp_path / "vs_health.csv").exists()

