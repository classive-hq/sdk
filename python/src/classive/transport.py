"""Shared configuration and the synchronous HTTP transport."""
from __future__ import annotations
import email.utils
import json
import math
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Callable, TypedDict
from urllib.parse import urlsplit
import httpx
from .errors import NetworkError, ProtocolError, TimeoutError, ValidationError, api_error

class RequestOptions(TypedDict, total=False):
    idempotency_key: str
    range: str
    timeout: float

def positive(value: float, label: str) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValidationError(f"{label} must be a positive finite number.")
    return value

class Configuration:
    def __init__(self, api_key: str | None = None, *, base_url: str = "https://api.classive.app", timeout: float = 30, max_retries: int = 2):
        key = api_key if api_key is not None else os.getenv("CLASSIVE_API_KEY")
        if not key or not key.strip():
            raise ValidationError("Set CLASSIVE_API_KEY or pass api_key from your Classive dashboard.")
        if key.startswith("cmcp_"):
            raise ValidationError("Use a REST API key (ck_live_…), not an MCP key.")
        if "\r" in key or "\n" in key:
            raise ValidationError("The API key contains an invalid newline.")
        url = urlsplit(base_url)
        if url.username or url.password or url.query or url.fragment or url.path not in ("", "/") or not (
            url.scheme == "https" or (url.scheme == "http" and url.hostname in ("localhost", "127.0.0.1", "::1"))):
            raise ValidationError("base_url must be an HTTPS origin, or localhost HTTP for testing.")
        self.base_url = base_url.rstrip("/")
        self.timeout = positive(timeout, "timeout")
        if not isinstance(max_retries, int) or not 0 <= max_retries <= 10:
            raise ValidationError("max_retries must be an integer from 0 to 10.")
        self.max_retries = max_retries
        self._headers = {"Authorization": f"Bearer {key.strip()}", "Accept": "application/json, */*", "X-Classive-SDK": "python/0.1.0"}

    def prepare(self, path: str, query: dict[str, Any] | None, options: RequestOptions | None):
        if not path.startswith("/") or path.startswith("//") or any(p in (".", "..") for p in path.split("/")):
            raise ValidationError("Use an SDK resource method with an API id. Arbitrary URLs are not accepted.")
        options = options or {}
        headers = dict(self._headers)
        key = options.get("idempotency_key")
        if key is not None:
            if not key.strip() or len(key) > 200 or "\r" in key or "\n" in key:
                raise ValidationError("idempotency_key must contain 1–200 characters without newlines.")
            headers["Idempotency-Key"] = key
        if options.get("range"):
            headers["Range"] = options["range"]
        params = {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in (query or {}).items() if v is not None}
        return self.base_url + path, headers, params, positive(options.get("timeout", self.timeout), "timeout")

def retry_delay(response: httpx.Response, attempt: int) -> float:
    raw = response.headers.get("retry-after")
    if raw is None:
        return min(.25 * 2**attempt, 2)
    try:
        return max(0, float(raw))
    except ValueError:
        try:
            return max(0, email.utils.parsedate_to_datetime(raw).timestamp() - time.time())
        except (ValueError, TypeError, OverflowError):
            return math.inf

class Transport(Configuration):
    def __init__(self, api_key: str | None = None, *, http_client: httpx.Client | None = None, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self._owned = http_client is None
        self._http = http_client or httpx.Client(follow_redirects=False)

    def close(self):
        if self._owned:
            self._http.close()

    def _perform(self, method: str, path: str, input: Any, query: Any, options: RequestOptions | None,
                 reader: Callable[[httpx.Response, float], Any]) -> Any:
        url, headers, params, timeout = self.prepare(path, query, options)
        deadline = time.monotonic() + timeout
        for attempt in range(self.max_retries + 1):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("The Classive request timed out. Check a mutation's outcome before repeating it.", code="timeout")
            try:
                arguments = {"json": input} if input is not None else {}
                with self._http.stream(method, url, headers=headers, params=params, timeout=remaining,
                                       follow_redirects=False, **arguments) as response:
                    if 300 <= response.status_code < 400:
                        raise ProtocolError("A redirect was refused to keep your API key on the configured origin.", response.status_code, "redirect_refused")
                    if method == "GET" and attempt < self.max_retries and response.status_code in (429, 500, 502, 503, 504):
                        delay = retry_delay(response, attempt)
                        if delay < deadline - time.monotonic():
                            # Close the response before waiting; no connection is held during backoff.
                            response.close()
                            time.sleep(delay)
                            continue
                    if response.is_error:
                        response.read()
                        try: body = response.json()
                        except ValueError: body = None
                        raise api_error(response.status_code, body, response.headers.get("x-request-id"))
                    return reader(response, deadline)
            except httpx.TimeoutException as exc:
                raise TimeoutError("The Classive request timed out. A mutation may still have been accepted; check its quote/job before repeating.", code="timeout") from exc
            except httpx.HTTPError as exc:
                if method == "GET" and attempt < self.max_retries:
                    delay = min(.25 * 2**attempt, 2)
                    if delay < deadline - time.monotonic():
                        time.sleep(delay)
                        continue
                raise NetworkError("Could not reach Classive. Mutations are not automatically repeated; check their outcome before resubmitting.", code="network_error") from exc
        raise AssertionError("unreachable")

    def request(self, method: str, path: str, input: Any = None, query: Any = None,
                options: RequestOptions | None = None, mode: str = "json") -> Any:
        def read(response, deadline):
            chunks = []
            for chunk in response.iter_bytes():
                if time.monotonic() >= deadline:
                    raise TimeoutError("The Classive response exceeded the request deadline.", code="timeout")
                chunks.append(chunk)
            data = b"".join(chunks)
            if mode == "bytes": return data
            if response.status_code == 204: return None
            try: return json.loads(data)
            except (ValueError, UnicodeDecodeError) as exc:
                raise ProtocolError("Classive returned an invalid JSON response.", response.status_code, "invalid_response") from exc
        return self._perform(method, path, input, query, options, read)

    def download_to(self, path: str, destination: str | Path, query: Any = None,
                    options: RequestOptions | None = None, overwrite: bool = False):
        destination = Path(destination)
        fd, temporary = tempfile.mkstemp(prefix=".classive-", suffix=".part", dir=destination.parent)
        os.close(fd)
        try:
            def read(response, deadline):
                with open(temporary, "wb") as output:
                    for chunk in response.iter_bytes():
                        if time.monotonic() >= deadline:
                            raise TimeoutError("The Classive download exceeded the request deadline.", code="timeout")
                        output.write(chunk)
            self._perform("GET", path, None, query, options, read)
            if overwrite: os.replace(temporary, destination)
            else: os.link(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)
