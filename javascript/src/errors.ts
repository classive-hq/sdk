/** A rejected API request. The structured response is available in `details`. */
export class ClassiveError extends Error {
  constructor(message: string, public readonly status = 0, public readonly code = 'sdk_error',
    public readonly details: unknown = undefined, public readonly requestId?: string) {
    super(message); this.name = new.target.name;
  }
}
export class AuthenticationError extends ClassiveError {}
export class PermissionError extends ClassiveError {}
export class ValidationError extends ClassiveError {}
export class InsufficientCreditsError extends ClassiveError {}
export class NotFoundError extends ClassiveError {}
export class ConflictError extends ClassiveError {}
export class RateLimitError extends ClassiveError {}
export class ServiceError extends ClassiveError {}
export class NetworkError extends ClassiveError {}
export class TimeoutError extends ClassiveError {}
export class AbortError extends ClassiveError {}
export class ProtocolError extends ClassiveError {}
export class JobFailedError extends ClassiveError {
  constructor(public readonly job: import('./types.js').Job) {
    super(job.failure?.message ?? 'The job failed. Inspect error.job for details and completed outputs.', 0, job.failure?.code ?? 'job_failed');
  }
}
export class JobCancelledError extends ClassiveError {
  constructor(public readonly job: import('./types.js').Job) {
    super('The job was cancelled. Inspect error.job for retained outputs and charges.', 0, 'job_cancelled');
  }
}
export class MaterialFailedError extends ClassiveError {
  constructor(public readonly material: import('./types.js').Material) {
    super(material.error ?? 'Material extraction failed. Inspect error.material before retrying.', 0, 'material_failed');
  }
}
export function apiError(status: number, body: unknown, requestId?: string): ClassiveError {
  const e = (body as {error?: {message?: string; code?: string}} | null)?.error;
  const ctor = ({400:ValidationError,401:AuthenticationError,402:InsufficientCreditsError,403:PermissionError,
    404:NotFoundError,409:ConflictError,422:ValidationError,429:RateLimitError} as Record<number, typeof ClassiveError>)[status] ?? ServiceError;
  return new ctor(e?.message ?? `Classive returned HTTP ${status}. See status, details and requestId.`, status, e?.code ?? 'http_error', body, requestId);
}
