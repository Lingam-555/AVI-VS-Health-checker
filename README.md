# AVI VS Health Checker

A practice project that fetches virtual services (VS) from an AVI-style API, classifies each one as healthy, warning, critical, down or unknown, and prints a summary. It runs against a local fake server, and no real controller is involved.

## What it does
1. Reads settings from `config.json` (server URL, user name, thresholds, page limit).
2. Logs in with a password taken from the `AVI_PASSWORD` environment variable.
3. Fetches every page of VS data, following the `next` link.
4. Classifies each VS by latency and status, then prints counts and the names of the VS that are not healthy.

## Health rules
| Condition | Label |
|-----------|-------|
| status `OPER_DOWN` | DOWN |
| unrecognised status, or a latency that is not a number | UNKNOWN |
| latency >= critical threshold | CRITICAL |
| latency >= warning threshold | WARNING |
| anything else | HEALTHY |

## Files
| File | Job |
|------|-----|
| `main.py` | entry point: flags, config, login, fetch, report |
| `client.py` | `AviHttpClient`: login, retries, pagination, same-host check |
| `classifier.py` | `classify_vs`: one VS in, one health result out |
| `summary.py` | `summarise`: counts and the non-healthy list |
| `models.py` | `VirtualService` dataclass and the function that builds it from a dict |
| `labels.py` | the five health labels, defined once |
| `exceptions.py` | `VSdataError` and `ControllerLoginError` |
| `config.py`, `config.json` | loading and holding the settings |
| `loader.py` | reads a VS data file |
| `fake_server.py` | practice server (login, paged VS list) |
| `test_*.py` | pytest tests |

## Configuration
`config.json` (example values):
```json
{
  "url": "http://127.0.0.1:8000",
  "username": "admin",
  "warning": 200,
  "critical": 500,
  "max_pages": 10
}
```
The password is never stored in a file. It comes from the `AVI_PASSWORD` environment variable only.

## Run it
Needs Python 3 with `requests` and `pytest` installed.

Terminal 1, the practice server:
```bash
read -s FAKE_PASSWORD
export FAKE_PASSWORD
python3 fake_server.py
```

Terminal 2, the checker. Type the same password you gave the server:
```bash
read -s AVI_PASSWORD
export AVI_PASSWORD
python3 main.py
python3 main.py --log-level DEBUG
python3 main.py --config /path/to/other_config.json
python3 main.py --help
```

Exit codes: `0` success, `1` a handled error (server down, rejected login, bad config), `2` wrong command-line usage.

## Run the tests
```bash
python3 -m pytest -v
```
The client tests use a fake session, so no server is needed.

## Design choices
- **Retry only when there is no reply** (connection error or timeout). A reply with a bad status, such as a rejected login, is never retried, because repeated wrong passwords can lock an account.
- **Page limit:** pagination stops with an error if the server keeps sending a `next` link beyond `max_pages`.
- **Same-host check:** the `next` URL comes from the server, so the client refuses a URL on a different host. The session sends its token with every request, so a foreign host must never receive it.
- **One error type for the caller:** every client problem becomes `VSdataError`, so `main.py` prints one clean line and exits with `1`.
- **Secrets:** the password and the token are never logged, printed or put in a URL.
- **Typos fail loudly:** labels are constants and VS records are dataclass objects, so a misspelled name raises an error instead of giving a silent wrong result.

## Limits
- It has been tested only against `fake_server.py`. A real controller's API paths, reply fields and login method may differ, and the project would need adapting.
- `fake_server.py` and its token are for practice only.
