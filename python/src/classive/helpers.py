"""Workflow helpers that do not approve, repeat or cancel server work implicitly."""
from __future__ import annotations
import base64
import mimetypes
from pathlib import Path
import re
import time
from typing import Any, Iterator, TypedDict
from . import types as models
from .transport import Transport, RequestOptions, positive
from .errors import JobFailedError, JobCancelledError, MaterialFailedError, TimeoutError, ValidationError

class WaitOptions(RequestOptions, total=False):
    wait_timeout: float
    poll_interval: float

class UploadMetadata(TypedDict, total=False):
    previousVersionId: str
    role: str
    sourceUrl: str
    rights: str
    retentionDays: int

def path_id(id: str) -> str:
    if not isinstance(id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", id):
        raise ValidationError("Pass an API id, not a URL or path.")
    return id

def upload_input(data: bytes, filename: str, content_type: str, metadata: UploadMetadata | None):
    if len(data) > 25 * 1024 * 1024:
        raise ValidationError("Materials must be at most 25 MiB.")
    return {**(metadata or {}), "filename": filename, "contentType": content_type,
            "base64": base64.b64encode(data).decode("ascii")}

def read_upload(file_path: str | Path, content_type: str | None):
    path = Path(file_path)
    if path.stat().st_size > 25 * 1024 * 1024:
        raise ValidationError("Materials must be at most 25 MiB.")
    mime = content_type or mimetypes.guess_type(str(path))[0]
    if not mime: raise ValidationError("Pass content_type for this file extension.")
    return path.read_bytes(), path.name, mime

def job_done(job: models.Job) -> bool:
    if job["status"] == "failed": raise JobFailedError(job)
    if job["status"] == "cancelled": raise JobCancelledError(job)
    return job["status"] == "completed"

def material_done(material: models.Material) -> bool:
    if material["status"] in ("failed", "deleted"): raise MaterialFailedError(material)
    return material["status"] == "ready"

def curriculum_done(curriculum: models.Curriculum) -> bool:
    if curriculum["status"] == "failed":
        raise ValidationError("Curriculum planning failed. Inspect curricula.get(id) before retrying.", code="curriculum_failed", details=curriculum)
    return curriculum["status"] in ("draft", "approved")

def wait_for(transport, path, options, done):
    options = options or {}
    deadline = time.monotonic() + positive(options.get("wait_timeout", 1800), "wait_timeout")
    interval = positive(options.get("poll_interval", 2), "poll_interval")
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Polling timed out. The work continues on Classive; fetch it later or cancel explicitly.", code="wait_timeout")
        value = transport.request("GET", path, options={**options, "timeout": min(options.get("timeout", transport.timeout), remaining)})
        if done(value): return value
        time.sleep(min(interval, max(0, deadline-time.monotonic())))

class Resource:
    def __init__(self, transport: Transport): self._transport = transport

class JobsHelpers(Resource):
    def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Job:
        """Wait for delivery. Terminal failure errors carry the complete job; no server cancellation occurs."""
        return wait_for(self._transport, f"/v1/jobs/{path_id(id)}", options, job_done)

    def iterate(self, *, query: models.ListJobsQuery | None = None, options: RequestOptions | None = None) -> Iterator[models.Job]:
        """Iterate newest-first through the server's cursor-based job list."""
        params: dict[str, Any] = dict(query or {})
        while True:
            page = self._transport.request("GET", "/v1/jobs", query=params, options=options)
            yield from page["data"]
            if not page["hasMore"]: return
            next_cursor = page["data"][-1]["id"] if page["data"] else None
            if not next_cursor or next_cursor == params.get("starting_after"):
                raise ValidationError("The job list returned an invalid pagination cursor.")
            params["starting_after"] = next_cursor

    def download_package_to(self, id: str, destination: str | Path, *, query: models.DownloadPackageQuery | None = None,
                            options: RequestOptions | None = None, overwrite: bool = False) -> None:
        """Stream a course ZIP to disk. Existing files are preserved unless overwrite=True."""
        self._transport.download_to(f"/v1/jobs/{path_id(id)}/download", destination, query, options, overwrite)

    def package_file_to(self, id: str, file_id: str, destination: str | Path, *, query: models.GetPackageFileQuery | None = None,
                        options: RequestOptions | None = None, overwrite: bool = False) -> None:
        self._transport.download_to(f"/v1/jobs/{path_id(id)}/package/files/{path_id(file_id)}", destination, query, options, overwrite)

class FilesHelpers(Resource):
    def download_to(self, id: str, destination: str | Path, *, options: RequestOptions | None = None, overwrite: bool = False) -> None:
        """Stream by file id, never an arbitrary URL. Only complete files become visible at the destination."""
        self._transport.download_to(f"/v1/files/{path_id(id)}", destination, options=options, overwrite=overwrite)

    def json(self, id: str, *, options: RequestOptions | None = None) -> Any:
        """Read a structured notes, quiz, flashcards or review file as JSON."""
        return self._transport.request("GET", f"/v1/files/{path_id(id)}", options=options)

class MaterialsHelpers(Resource):
    def upload(self, file_path: str | Path, *, metadata: UploadMetadata | None = None,
               content_type: str | None = None, options: RequestOptions | None = None) -> models.Material:
        """Upload a local file up to 25 MiB, using the public JSON upload contract."""
        data, name, mime = read_upload(file_path, content_type)
        return self.upload_bytes(data, name, mime, metadata=metadata, options=options)

    def upload_bytes(self, data: bytes, filename: str, content_type: str, *, metadata: UploadMetadata | None = None,
                     options: RequestOptions | None = None) -> models.Material:
        return self._transport.request("POST", "/v1/materials", upload_input(data, filename, content_type, metadata), options=options)

    def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Material:
        """Wait for extraction readiness, not a promise that every section is used in subsequent jobs."""
        return wait_for(self._transport, f"/v1/materials/{path_id(id)}", options, material_done)

    def iterate(self, *, query: models.ListMaterialsQuery | None = None, options: RequestOptions | None = None) -> Iterator[models.Material]:
        params: dict[str, Any] = dict(query or {})
        while True:
            page = self._transport.request("GET", "/v1/materials", query=params, options=options)
            yield from page["data"]
            if not page.get("hasMore"): return
            next_cursor = page.get("nextCursor") or (page["data"][-1]["id"] if page["data"] else None)
            if not next_cursor or next_cursor == params.get("starting_after"):
                raise ValidationError("The material list returned an invalid pagination cursor.")
            params["starting_after"] = next_cursor

class CurriculaHelpers(Resource):
    def wait(self, id: str, *, options: WaitOptions | None = None) -> models.Curriculum:
        """Wait for planning, without approving the plan or starting a course."""
        return wait_for(self._transport, f"/v1/curricula/{path_id(id)}", options, curriculum_done)
