from client import AviHttpClient
import pytest
from exceptions import VSdataError
import requests

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
