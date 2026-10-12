# Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.
from __future__ import annotations
from . import types as models
from .transport import RequestOptions
from .helpers import Resource, JobsHelpers, MaterialsHelpers, FilesHelpers, CurriculaHelpers, path_id

class Voices(Resource):
    def preview(self, id: str, *, options: RequestOptions | None = None) -> bytes:
        """Play a voice sample (GET /voices/{id}/preview)."""
        return self._transport.request("GET", f"/voices/{path_id(id)}/preview", None, None, options, "bytes")

    def list(self, *, options: RequestOptions | None = None) -> models.VoiceList:
        """List voices (GET /v1/voices)."""
        return self._transport.request("GET", f"/v1/voices", None, None, options, "json")

class Jobs(JobsHelpers):
    def create(self, input: models.CreateJobRequest, *, options: RequestOptions | None = None) -> models.Job:
        """Create a job (POST /v1/jobs)."""
        return self._transport.request("POST", f"/v1/jobs", input, None, options, "json")

    def list(self, *, query: models.ListJobsQuery | None = None, options: RequestOptions | None = None) -> models.JobList:
        """List jobs (GET /v1/jobs)."""
        return self._transport.request("GET", f"/v1/jobs", None, query, options, "json")

    def estimate(self, input: models.CreateJobRequest, *, options: RequestOptions | None = None) -> models.Estimate:
        """Estimate a job (POST /v1/jobs/estimate)."""
        return self._transport.request("POST", f"/v1/jobs/estimate", input, None, options, "json")

    def get(self, id: str, *, options: RequestOptions | None = None) -> models.Job:
        """Get a job (GET /v1/jobs/{id})."""
        return self._transport.request("GET", f"/v1/jobs/{path_id(id)}", None, None, options, "json")

    def usage(self, id: str, *, options: RequestOptions | None = None) -> models.Usage:
        """Get a job’s usage (GET /v1/jobs/{id}/usage)."""
        return self._transport.request("GET", f"/v1/jobs/{path_id(id)}/usage", None, None, options, "json")

    def revise(self, id: str, input: models.CreateRevisionRequest, *, options: RequestOptions | None = None) -> models.Job:
        """Create a revision (POST /v1/jobs/{id}/revisions)."""
        return self._transport.request("POST", f"/v1/jobs/{path_id(id)}/revisions", input, None, options, "json")

    def quote(self, input: models.CreateJobRequest, *, options: RequestOptions | None = None) -> models.Quote:
        """Quote a job at fixed scope and prices (POST /v1/jobs/quote)."""
        return self._transport.request("POST", f"/v1/jobs/quote", input, None, options, "json")

    def cancel(self, id: str, *, options: RequestOptions | None = None) -> models.Job:
        """Cancel unfinished work and release unused reservations (POST /v1/jobs/{id}/cancel)."""
        return self._transport.request("POST", f"/v1/jobs/{path_id(id)}/cancel", None, None, options, "json")

    def package(self, id: str, *, query: models.GetPackageQuery | None = None, options: RequestOptions | None = None) -> models.Package:
        """Get the ordered course manifest (GET /v1/jobs/{id}/package)."""
        return self._transport.request("GET", f"/v1/jobs/{path_id(id)}/package", None, query, options, "json")

    def download_package(self, id: str, *, query: models.DownloadPackageQuery | None = None, options: RequestOptions | None = None) -> bytes:
        """Download a course ZIP (GET /v1/jobs/{id}/download)."""
        return self._transport.request("GET", f"/v1/jobs/{path_id(id)}/download", None, query, options, "bytes")

    def package_file(self, id: str, file_id: str, *, query: models.GetPackageFileQuery | None = None, options: RequestOptions | None = None) -> bytes:
        """Download a packaged file (GET /v1/jobs/{id}/package/files/{fileId})."""
        return self._transport.request("GET", f"/v1/jobs/{path_id(id)}/package/files/{path_id(file_id)}", None, query, options, "bytes")

    def quote_revision(self, id: str, input: models.QuoteRevisionInput, *, options: RequestOptions | None = None) -> models.Quote:
        """Quote an individual job revision (POST /v1/jobs/{id}/revisions/quote)."""
        return self._transport.request("POST", f"/v1/jobs/{path_id(id)}/revisions/quote", input, None, options, "json")

    def quote_retry(self, id: str, *, options: RequestOptions | None = None) -> models.Quote:
        """Quote retrying a failed or cancelled individual job (POST /v1/jobs/{id}/retry/quote)."""
        return self._transport.request("POST", f"/v1/jobs/{path_id(id)}/retry/quote", None, None, options, "json")

    def retry(self, id: str, input: models.RetryJobInput, *, options: RequestOptions | None = None) -> models.Job:
        """Retry one job while preserving completed siblings (POST /v1/jobs/{id}/retry)."""
        return self._transport.request("POST", f"/v1/jobs/{path_id(id)}/retry", input, None, options, "json")

class Files(FilesHelpers):
    def download(self, id: str, *, options: RequestOptions | None = None) -> bytes:
        """Download a file (GET /v1/files/{id})."""
        return self._transport.request("GET", f"/v1/files/{path_id(id)}", None, None, options, "bytes")

class Materials(MaterialsHelpers):
    def create(self, input: models.MaterialUpload, *, options: RequestOptions | None = None) -> models.Material:
        """Upload a material (POST /v1/materials)."""
        return self._transport.request("POST", f"/v1/materials", input, None, options, "json")

    def list(self, *, query: models.ListMaterialsQuery | None = None, options: RequestOptions | None = None) -> models.MaterialList:
        """List materials (GET /v1/materials)."""
        return self._transport.request("GET", f"/v1/materials", None, query, options, "json")

    def get(self, id: str, *, options: RequestOptions | None = None) -> models.Material:
        """Read extraction coverage and source sections (GET /v1/materials/{id})."""
        return self._transport.request("GET", f"/v1/materials/{path_id(id)}", None, None, options, "json")

    def delete(self, id: str, *, options: RequestOptions | None = None) -> models.DeletedMaterial:
        """Delete an unused material and its index (DELETE /v1/materials/{id})."""
        return self._transport.request("DELETE", f"/v1/materials/{path_id(id)}", None, None, options, "json")

    def retry(self, id: str, *, options: RequestOptions | None = None) -> models.Material:
        """Retry a failed extraction (POST /v1/materials/{id}/retry)."""
        return self._transport.request("POST", f"/v1/materials/{path_id(id)}/retry", None, None, options, "json")

class Preferences(Resource):
    def examples(self, *, options: RequestOptions | None = None) -> models.PreferenceExamples:
        """Preference examples (GET /v1/preferences/examples)."""
        return self._transport.request("GET", f"/v1/preferences/examples", None, None, options, "json")

class Prices(Resource):
    def get(self, *, options: RequestOptions | None = None) -> models.Prices:
        """Current prices (GET /v1/prices)."""
        return self._transport.request("GET", f"/v1/prices", None, None, options, "json")

class Keys(Resource):
    def list(self, *, options: RequestOptions | None = None) -> models.ApiKeyList:
        """List API keys (GET /v1/keys)."""
        return self._transport.request("GET", f"/v1/keys", None, None, options, "json")

    def create(self, input: models.CreateKeyRequest, *, options: RequestOptions | None = None) -> models.CreatedApiKey:
        """Create an API key (POST /v1/keys)."""
        return self._transport.request("POST", f"/v1/keys", input, None, options, "json")

    def revoke(self, id: str, *, options: RequestOptions | None = None) -> models.ApiKey:
        """Revoke an API key (DELETE /v1/keys/{id})."""
        return self._transport.request("DELETE", f"/v1/keys/{path_id(id)}", None, None, options, "json")

class Webhooks(Resource):
    def list(self, *, options: RequestOptions | None = None) -> models.WebhookList:
        """List webhook endpoints (GET /v1/webhooks)."""
        return self._transport.request("GET", f"/v1/webhooks", None, None, options, "json")

    def create(self, input: models.CreateWebhookRequest, *, options: RequestOptions | None = None) -> models.CreatedWebhook:
        """Add a webhook endpoint (POST /v1/webhooks)."""
        return self._transport.request("POST", f"/v1/webhooks", input, None, options, "json")

    def delete(self, id: str, *, options: RequestOptions | None = None) -> models.Webhook:
        """Remove a webhook endpoint (DELETE /v1/webhooks/{id})."""
        return self._transport.request("DELETE", f"/v1/webhooks/{path_id(id)}", None, None, options, "json")

class Billing(Resource):
    def credits(self, *, options: RequestOptions | None = None) -> models.Credits:
        """Balance and ledger (GET /v1/billing/credits)."""
        return self._transport.request("GET", f"/v1/billing/credits", None, None, options, "json")

    def packs(self, *, options: RequestOptions | None = None) -> models.Packs:
        """Credit packs (GET /v1/billing/packs)."""
        return self._transport.request("GET", f"/v1/billing/packs", None, None, options, "json")

    def create_topup(self, input: models.CreateTopupRequest, *, options: RequestOptions | None = None) -> models.CreatedTopup:
        """Start a top-up (POST /v1/billing/topups)."""
        return self._transport.request("POST", f"/v1/billing/topups", input, None, options, "json")

    def get_topup(self, id: str, *, options: RequestOptions | None = None) -> models.Topup:
        """Get a top-up (GET /v1/billing/topups/{id})."""
        return self._transport.request("GET", f"/v1/billing/topups/{path_id(id)}", None, None, options, "json")

    def settings(self, *, options: RequestOptions | None = None) -> models.BillingSettings:
        """Get billing controls (GET /v1/billing/settings)."""
        return self._transport.request("GET", f"/v1/billing/settings", None, None, options, "json")

    def update_settings(self, input: models.BillingSettingsPatch, *, options: RequestOptions | None = None) -> models.BillingSettings:
        """Update billing controls (PATCH /v1/billing/settings)."""
        return self._transport.request("PATCH", f"/v1/billing/settings", input, None, options, "json")

    def setup_payment_method(self, *, options: RequestOptions | None = None) -> models.CardSetup:
        """Save a card (POST /v1/billing/payment-methods/setup)."""
        return self._transport.request("POST", f"/v1/billing/payment-methods/setup", None, None, options, "json")

    def portal(self, *, options: RequestOptions | None = None) -> models.BillingPortal:
        """Open the card portal (POST /v1/billing/portal)."""
        return self._transport.request("POST", f"/v1/billing/portal", None, None, options, "json")

    def unlink_payment_method(self, id: str, *, options: RequestOptions | None = None) -> models.UnlinkedPaymentMethod:
        """Stop reusing a saved card (DELETE /v1/billing/payment-methods/{id})."""
        return self._transport.request("DELETE", f"/v1/billing/payment-methods/{path_id(id)}", None, None, options, "json")

class Quotes(Resource):
    def get(self, id: str, *, options: RequestOptions | None = None) -> models.Quote:
        """Read a quote (GET /v1/quotes/{id})."""
        return self._transport.request("GET", f"/v1/quotes/{path_id(id)}", None, None, options, "json")

class Curricula(CurriculaHelpers):
    def list(self, *, options: RequestOptions | None = None) -> models.CurriculumList:
        """List curricula (GET /v1/curricula)."""
        return self._transport.request("GET", f"/v1/curricula", None, None, options, "json")

    def create(self, input: models.CreateCurriculumInput, *, options: RequestOptions | None = None) -> models.Curriculum:
        """Generate a curriculum draft from an accepted planning quote (POST /v1/curricula)."""
        return self._transport.request("POST", f"/v1/curricula", input, None, options, "json")

    def quote_planning(self, input: models.CurriculumInput, *, options: RequestOptions | None = None) -> models.Quote:
        """Quote curriculum planning and any uncached source summaries (POST /v1/curricula/quote)."""
        return self._transport.request("POST", f"/v1/curricula/quote", input, None, options, "json")

    def recommend(self, input: models.CurriculumInput, *, options: RequestOptions | None = None) -> models.CurriculumRecommendationList:
        """Recommend editable Classive templates (POST /v1/curricula/recommendations)."""
        return self._transport.request("POST", f"/v1/curricula/recommendations", input, None, options, "json")

    def import_plan(self, input: models.ImportCurriculumInput, *, options: RequestOptions | None = None) -> models.Curriculum:
        """Import a free editable curriculum draft (POST /v1/curricula/import)."""
        return self._transport.request("POST", f"/v1/curricula/import", input, None, options, "json")

    def get(self, id: str, *, query: models.GetCurriculumQuery | None = None, options: RequestOptions | None = None) -> models.Curriculum:
        """Read a curriculum version (GET /v1/curricula/{id})."""
        return self._transport.request("GET", f"/v1/curricula/{path_id(id)}", None, query, options, "json")

    def edit(self, id: str, input: models.EditCurriculumInput, *, options: RequestOptions | None = None) -> models.Curriculum:
        """Save a new draft version (POST /v1/curricula/{id}/versions)."""
        return self._transport.request("POST", f"/v1/curricula/{path_id(id)}/versions", input, None, options, "json")

    def approve(self, id: str, input: models.ApproveCurriculumInput, *, options: RequestOptions | None = None) -> models.Curriculum:
        """Approve the current draft version (POST /v1/curricula/{id}/approve)."""
        return self._transport.request("POST", f"/v1/curricula/{path_id(id)}/approve", input, None, options, "json")

    def quote_lessons(self, id: str, input: models.Selection, *, options: RequestOptions | None = None) -> models.Quote:
        """Quote selected lessons from an approved version (POST /v1/curricula/{id}/quote)."""
        return self._transport.request("POST", f"/v1/curricula/{path_id(id)}/quote", input, None, options, "json")

    def generate(self, id: str, input: models.GenerateCurriculumLessonsInput, *, options: RequestOptions | None = None) -> models.Job:
        """Generate the selected lessons as separate child jobs (POST /v1/curricula/{id}/generate)."""
        return self._transport.request("POST", f"/v1/curricula/{path_id(id)}/generate", input, None, options, "json")

class Organisation(Resource):
    def limits(self, *, options: RequestOptions | None = None) -> models.Limits:
        """Read organisation spending and concurrency limits (GET /v1/organisation/limits)."""
        return self._transport.request("GET", f"/v1/organisation/limits", None, None, options, "json")

    def update_limits(self, input: models.Limits, *, options: RequestOptions | None = None) -> models.Limits:
        """Update organisation spending and concurrency limits (PATCH /v1/organisation/limits)."""
        return self._transport.request("PATCH", f"/v1/organisation/limits", input, None, options, "json")

