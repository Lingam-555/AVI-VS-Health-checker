from csv_report import csv_report
from labels import WARNING, DOWN, UNKNOWN
import pytest

def test_csv_normal_data(tmp_path):
    out = tmp_path/"out.csv"
    expected = "name,health\napi-vs,WARNING\nlogin-vs,DOWN\npayment-vs,UNKNOWN\n"
    Non_healthy_vs = (["api-vs",WARNING],["login-vs",DOWN],["payment-vs",UNKNOWN])
    csv_report(out,Non_healthy_vs)
    assert out.read_text() == expected

def test_csv_healthy_data(tmp_path):
    out = tmp_path/"out.csv"
    Non_healthy_vs = ([])
    expected = "name,health\n"
    csv_report(out,Non_healthy_vs)
    assert out.read_text() == expected

def test_csv_path(tmp_path):
    out = tmp_path/"missing"/"out.csv"
    Non_healthy_vs = ([])
    with pytest.raises(OSError):
        csv_report(out,Non_healthy_vs)
