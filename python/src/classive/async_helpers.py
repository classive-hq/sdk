"""Asynchronous workflow helpers, including interruptible polling."""
from __future__ import annotations
import asyncio
from pathlib import Path
import time
from typing import Any, AsyncIterator
from . import types as models
from .async_transport import AsyncTransport
from .transport import RequestOptions, positive
from .helpers import WaitOptions, UploadMetadata, path_id, upload_input, read_upload, job_done, material_done, curriculum_done
from .errors import TimeoutError, ValidationError

async def wait_for(transport, path, options, done):
    options = options or {}
    timeout = positive(options.get("wait_timeout", 1800), "wait_timeout")
    deadline = time.monotonic() + timeout
    interval = positive(options.get("poll_interval", 2), "poll_interval")
    try:
        async with asyncio.timeout(timeout):
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0: raise asyncio.TimeoutError()
                value = await transport.request("GET", path, options={**options, "timeout": min(options.get("timeout", transport.timeout), remaining)})
                if done(value): return value
                await asyncio.sleep(min(interval, max(0, deadline-time.monotonic())))
    except asyncio.TimeoutError as exc:
        raise TimeoutError("Polling timed out. The work continues on Classive; fetch it later or cancel explicitly.", code="wait_timeout") from exc

class Resource:
    def __init__(self, transport: AsyncTransport): self._transport = transport

class JobsHelpers(Resource):
    async def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Job:
        """Wait for delivery, raising terminal errors carrying the complete job."""
        return await wait_for(self._transport, f"/v1/jobs/{path_id(id)}", options, job_done)

    async def iterate(self, *, query: models.ListJobsQuery | None = None, options: RequestOptions | None = None) -> AsyncIterator[models.Job]:
        params: dict[str, Any] = dict(query or {})
        while True:
            page = await self._transport.request("GET", "/v1/jobs", query=params, options=options)
            for job in page["data"]: yield job
            if not page["hasMore"]: return
            next_cursor = page["data"][-1]["id"] if page["data"] else None
            if not next_cursor or next_cursor == params.get("starting_after"):
                raise ValidationError("The job list returned an invalid pagination cursor.")
            params["starting_after"] = next_cursor

    async def download_package_to(self, id: str, destination: str | Path, *, query: models.DownloadPackageQuery | None = None,
                                  options: RequestOptions | None = None, overwrite: bool = False) -> None:
        await self._transport.download_to(f"/v1/jobs/{path_id(id)}/download", destination, query, options, overwrite)

    async def package_file_to(self, id: str, file_id: str, destination: str | Path, *, query: models.GetPackageFileQuery | None = None,
                              options: RequestOptions | None = None, overwrite: bool = False) -> None:
        await self._transport.download_to(f"/v1/jobs/{path_id(id)}/package/files/{path_id(file_id)}", destination, query, options, overwrite)

class FilesHelpers(Resource):
    async def download_to(self, id: str, destination: str | Path, *, options: RequestOptions | None = None, overwrite: bool = False) -> None:
        await self._transport.download_to(f"/v1/files/{path_id(id)}", destination, options=options, overwrite=overwrite)

    async def json(self, id: str, *, options: RequestOptions | None = None) -> Any:
        return await self._transport.request("GET", f"/v1/files/{path_id(id)}", options=options)

class MaterialsHelpers(Resource):
    async def upload(self, file_path: str | Path, *, metadata: UploadMetadata | None = None,
                     content_type: str | None = None, options: RequestOptions | None = None) -> models.Material:
        data, name, mime = await asyncio.to_thread(read_upload, file_path, content_type)
        return await self.upload_bytes(data, name, mime, metadata=metadata, options=options)

    async def upload_bytes(self, data: bytes, filename: str, content_type: str, *, metadata: UploadMetadata | None = None,
                           options: RequestOptions | None = None) -> models.Material:
        return await self._transport.request("POST", "/v1/materials", upload_input(data, filename, content_type, metadata), options=options)

    async def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Material:
        return await wait_for(self._transport, f"/v1/materials/{path_id(id)}", options, material_done)

    async def iterate(self, *, query: models.ListMaterialsQuery | None = None, options: RequestOptions | None = None) -> AsyncIterator[models.Material]:
        params: dict[str, Any] = dict(query or {})
        while True:
            page = await self._transport.request("GET", "/v1/materials", query=params, options=options)
            for material in page["data"]: yield material
            if not page.get("hasMore"): return
            next_cursor = page.get("nextCursor") or (page["data"][-1]["id"] if page["data"] else None)
            if not next_cursor or next_cursor == params.get("starting_after"):
                raise ValidationError("The material list returned an invalid pagination cursor.")
            params["starting_after"] = next_cursor

class CurriculaHelpers(Resource):
    async def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Curriculum:
        return await wait_for(self._transport, f"/v1/curricula/{path_id(id)}", options, curriculum_done)
