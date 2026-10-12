"""Native asynchronous HTTP requests; cancellation propagates to HTTPX."""
from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any
import httpx
from .transport import Configuration, RequestOptions, retry_delay
from .errors import NetworkError, ProtocolError, TimeoutError, api_error

class AsyncTransport(Configuration):
    def __init__(self, api_key: str | None = None, *, http_client: httpx.AsyncClient | None = None, **kwargs: Any):
        super().__init__(api_key, **kwargs)
        self._owned = http_client is None
        self._http = http_client or httpx.AsyncClient(follow_redirects=False)

    async def close(self):
        if self._owned: await self._http.aclose()

    async def _perform(self, method, path, input, query, options, reader):
        url, headers, params, timeout = self.prepare(path, query, options)
        deadline = time.monotonic() + timeout
        try:
            async with asyncio.timeout(timeout):
                for attempt in range(self.max_retries + 1):
                    try:
                        arguments = {"json": input} if input is not None else {}
                        async with self._http.stream(method, url, headers=headers, params=params,
                            timeout=max(.001, deadline-time.monotonic()), follow_redirects=False, **arguments) as response:
                            if 300 <= response.status_code < 400:
                                raise ProtocolError("A redirect was refused to keep your API key on the configured origin.", response.status_code, "redirect_refused")
                            if method == "GET" and attempt < self.max_retries and response.status_code in (429, 500, 502, 503, 504):
                                delay = retry_delay(response, attempt)
                                if delay < deadline - time.monotonic():
                                    await response.aclose()
                                    await asyncio.sleep(delay)
                                    continue
                            if response.is_error:
                                await response.aread()
                                try: body = response.json()
                                except ValueError: body = None
                                raise api_error(response.status_code, body, response.headers.get("x-request-id"))
                            return await reader(response)
                    except httpx.TimeoutException as exc:
                        raise TimeoutError("The Classive request timed out. A mutation may still have been accepted; check its outcome before repeating.", code="timeout") from exc
                    except httpx.HTTPError as exc:
                        if method == "GET" and attempt < self.max_retries:
                            await asyncio.sleep(min(.25 * 2**attempt, 2))
                            continue
                        raise NetworkError("Could not reach Classive. Mutations are not automatically repeated; check their outcome before resubmitting.", code="network_error") from exc
        except asyncio.TimeoutError as exc:
            raise TimeoutError("The Classive request timed out. A mutation may still have been accepted; check its outcome before repeating.", code="timeout") from exc
        raise AssertionError("unreachable")

    async def request(self, method: str, path: str, input: Any = None, query: Any = None,
                      options: RequestOptions | None = None, mode: str = "json") -> Any:
        async def read(response):
            data = await response.aread()
            if mode == "bytes": return data
            if response.status_code == 204: return None
            try: return json.loads(data)
            except (ValueError, UnicodeDecodeError) as exc:
                raise ProtocolError("Classive returned an invalid JSON response.", response.status_code, "invalid_response") from exc
        return await self._perform(method, path, input, query, options, read)

    async def download_to(self, path: str, destination: str | Path, query: Any = None,
                          options: RequestOptions | None = None, overwrite: bool = False):
        destination = Path(destination)
        fd, temporary = tempfile.mkstemp(prefix=".classive-", suffix=".part", dir=destination.parent)
        os.close(fd)
        try:
            async def read(response):
                with open(temporary, "wb") as output:
                    async for chunk in response.aiter_bytes():
                        output.write(chunk)
            await self._perform("GET", path, None, query, options, read)
            if overwrite: os.replace(temporary, destination)
            else: os.link(temporary, destination)
        finally:
            Path(temporary).unlink(missing_ok=True)
