from client import AviHttpClient
import pytest
from exceptions import VSdataError, ControllerLoginError
import requests
import logging

class FakeResponse:
    def __init__(self, body, status_code=200):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body

    def raise_for_status(self):
        pass

class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append(url)
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

def test_two_pages_are_joined():
    client=AviHttpClient("http://127.0.0.1:8000","admin",max_pages=10)
    client.session = FakeSession([
        FakeResponse({"results": ["a"] , "next": "http://127.0.0.1:8000/vs_pages?page=2"}),
        FakeResponse({"results": ["b"]})
    ])
    assert client.list_all_vs() == ['a','b']
    assert client.session.calls == ["http://127.0.0.1:8000/vs_pages?page=1", "http://127.0.0.1:8000/vs_pages?page=2"]

def test_next_page_on_other_host_is_refused():
    client=AviHttpClient("http://127.0.0.1:8000", "admin", max_pages=10)
    client.session = FakeSession([
        FakeResponse({"results": ["a"] , "next": "http://localhost:8000/vs_pages?page=2"}),
        FakeResponse({"results": ["b"]})
    ])
    with pytest.raises(VSdataError):
        client.list_all_vs()
    assert client.session.calls == ["http://127.0.0.1:8000/vs_pages?page=1"]

def test_failed_with_retry_request():
    client = AviHttpClient("http://127.0.0.1:8000", "admin",max_pages=10, tries=3, delay =0)
    client.session = FakeSession([
        requests.exceptions.ConnectionError("no reply"),
        requests.exceptions.ConnectionError("no reply"),
        FakeResponse({"results": ["a"]})
    ])
    assert client.list_all_vs() == ["a"]
    assert client.session.calls == ["http://127.0.0.1:8000/vs_pages?page=1"] * 3

def test_rejected_login_is_not_retried(monkeypatch):
    monkeypatch.setenv("AVI_PASSWORD", "tiger")
    client = AviHttpClient("http://127.0.0.1:8000", "admin",max_pages=10, tries=3, delay=0)
    client.session = FakeSession([
        FakeResponse({}, status_code=401)
    ])
    with pytest.raises(ControllerLoginError):
        client.login()
    assert client.session.calls == ["http://127.0.0.1:8000/login"]

def test_connection_failures_exhaust_retries():
    client = AviHttpClient("http://127.0.0.1:8000", "admin",max_pages=10, tries=2, delay=0)
    client.session = FakeSession([
        requests.exceptions.ConnectionError("no reply"),
        requests.exceptions.ConnectionError("no reply")
       ])
    with pytest.raises(VSdataError):
        client.list_all_vs()
    assert client.session.calls == ["http://127.0.0.1:8000/vs_pages?page=1"] * 2


def test_each_failed_attempt_is_logged(caplog):
    client = AviHttpClient("http://127.0.0.1:8000", "admin", max_pages=10, tries=3, delay=0)
    client.session = FakeSession([
        requests.exceptions.ConnectionError("no reply"),
        requests.exceptions.ConnectionError("no reply"),
        FakeResponse({"results": ["a"]})
    ])
    with caplog.at_level(logging.WARNING):
        client.list_all_vs()
    assert len(caplog.records) == 2
    assert "no reply on attempt 2 of 3 from http://127.0.0.1:8000" in caplog.text

def test_checks_password_never_reaches_a_log(monkeypatch, caplog):
    secret = "tiger-secret"
    monkeypatch.setenv("AVI_PASSWORD", secret)
    client = AviHttpClient("http://127.0.0.1:8000", "admin", max_pages=10, tries=2, delay=0)
    client.session = FakeSession([
        requests.exceptions.ConnectionError("no reply"),
        requests.exceptions.ConnectionError("no reply")
    ])
    with caplog.at_level(logging.DEBUG), pytest.raises(VSdataError):
        client.login()
    assert "no reply on attempt" in caplog.text
    assert secret not in caplog.text
