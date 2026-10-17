import requests
import os
import time
from urllib.parse import urlparse
from exceptions import VSdataError, ControllerLoginError

class AviHttpClient:
    def __init__(self, base_url, user, max_pages, timeout=5, tries = 5, delay =2):
        if tries < 1:
            raise ValueError(f"tries must be at least 1, got {tries}")
        if max_pages < 1:
            raise ValueError(f"max_pages must be at least 1, got {max_pages}")
        self.base_url = base_url
        self.user = user
        self.timeout = timeout
        self.session = requests.Session()
        self.tries = tries
        self.delay = delay
        self.max_pages = max_pages

    def _check_same_host(self, url):
        new_url = urlparse(url).netloc
        new_base_url = urlparse(self.base_url).netloc
        if new_url == new_base_url:
            return None
        else:
            raise VSdataError(f"The host is differs than both host next page-{new_url}, expected-{new_base_url}")

    def _send(self, method, url, **kwargs):
        for attempt in range(1,self.tries + 1):
            try:
                return self.session.request(method, url, timeout=self.timeout, **kwargs)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt == self.tries:
                    raise
                time.sleep(self.delay)
        
    def login(self):

        try:
            url = f"{self.base_url}/login"
            password = os.environ.get("AVI_PASSWORD")
            if password is None or password == "":
                raise VSdataError("AVI_PASSWORD is not set")
            r=self._send("POST",url,json={"username":self.user,"password":password})
            if r.status_code==401:
                raise ControllerLoginError("Login rejected")
            r.raise_for_status()
            token=r.json()["token"]
            self.session.headers.update({"Authorization":f"Bearer {token}"})
        except requests.exceptions.RequestException as e:
            raise VSdataError(f"cannot read {url}: {e}")
        except (ValueError, KeyError) as e:
            raise VSdataError(f"Invalid Error: {e}")


    def list_server(self):
        url = f"{self.base_url}/vs_status.json"
        try:
            r = self._send("GET",url)
            r.raise_for_status()
            data = r.json()
            return data["virtual_services"]
        except requests.exceptions.RequestException as e:
            raise VSdataError(f"cannot read {url}: {e}")
        except (ValueError, KeyError) as e:
            raise VSdataError(f"Invalid Error: {e}")

    def list_all_vs(self):
        url = f"{self.base_url}/vs_pages?page=1"
        items = []
        page = 0
        try:
            while url:
                r = self._send("GET",url)
                r.raise_for_status()
                body = r.json()
                items.extend(body["results"])
                page += 1
                url = body.get("next")
                if url and page >= self.max_pages:
                    raise VSdataError(f"stopped after {page} pages, the server still has a next page")
                if url:
                    self._check_same_host(url)
        except requests.exceptions.RequestException as e:
            raise VSdataError(f"cannot read {url}: {e}")
        except (ValueError, KeyError) as e:
            raise VSdataError(f"Invalid Error: {e}")
        return items