"""Typed errors with the original API details and request id."""
from __future__ import annotations
from typing import Any

class ClassiveError(Exception):
    def __init__(self, message: str, status: int = 0, code: str = "sdk_error", details: Any = None, request_id: str | None = None):
        super().__init__(message)
        self.status, self.code, self.details, self.request_id = status, code, details, request_id

class AuthenticationError(ClassiveError): pass
class PermissionError(ClassiveError): pass
class ValidationError(ClassiveError): pass
class InsufficientCreditsError(ClassiveError): pass
class NotFoundError(ClassiveError): pass
class ConflictError(ClassiveError): pass
class RateLimitError(ClassiveError): pass
class ServiceError(ClassiveError): pass
class NetworkError(ClassiveError): pass
class TimeoutError(ClassiveError): pass
class ProtocolError(ClassiveError): pass

class JobFailedError(ClassiveError):
    def __init__(self, job: Any):
        self.job = job
        failure = job.get("failure") or {}
        super().__init__(failure.get("message", "The job failed. Inspect error.job for details and completed outputs."), code=failure.get("code", "job_failed"))

class JobCancelledError(ClassiveError):
    def __init__(self, job: Any):
        self.job = job
        super().__init__("The job was cancelled. Inspect error.job for retained outputs and charges.", code="job_cancelled")

class MaterialFailedError(ClassiveError):
    def __init__(self, material: Any):
        self.material = material
        super().__init__(material.get("error") or "Material extraction failed. Inspect error.material before retrying.", code="material_failed")

def api_error(status: int, body: Any, request_id: str | None) -> ClassiveError:
    error = body.get("error", {}) if isinstance(body, dict) else {}
    cls = {400: ValidationError, 401: AuthenticationError, 402: InsufficientCreditsError,
           403: PermissionError, 404: NotFoundError, 409: ConflictError, 422: ValidationError,
           429: RateLimitError}.get(status, ServiceError)
    return cls(error.get("message", f"Classive returned HTTP {status}. See status, details and request_id."),
               status, error.get("code", "http_error"), body, request_id)
