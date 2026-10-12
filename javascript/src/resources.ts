// Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.
import type * as Models from './types.js';
import type {RequestOptions} from './transport.js';
import {Resource, JobsHelpers, MaterialsHelpers, FilesHelpers, CurriculaHelpers, pathId} from './helpers.js';

export class Voices extends Resource {
  /** Play a voice sample (GET /voices/{id}/preview). */
  preview(id: string, options: RequestOptions = {}): Promise<Uint8Array> {
    return this.transport.request("GET", `/voices/${pathId(id)}/preview`, undefined, undefined, options, "bytes");
  }
  /** List voices (GET /v1/voices). */
  list(options: RequestOptions = {}): Promise<Models.VoiceList> {
    return this.transport.request("GET", `/v1/voices`, undefined, undefined, options, "json");
  }
}

export class Jobs extends JobsHelpers {
  /** Create a job (POST /v1/jobs). */
  create(input: Models.CreateJobRequest, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("POST", `/v1/jobs`, input, undefined, options, "json");
  }
  /** List jobs (GET /v1/jobs). */
  list(query: Models.ListJobsQuery = {}, options: RequestOptions = {}): Promise<Models.JobList> {
    return this.transport.request("GET", `/v1/jobs`, undefined, query, options, "json");
  }
  /** Estimate a job (POST /v1/jobs/estimate). */
  estimate(input: Models.CreateJobRequest, options: RequestOptions = {}): Promise<Models.Estimate> {
    return this.transport.request("POST", `/v1/jobs/estimate`, input, undefined, options, "json");
  }
  /** Get a job (GET /v1/jobs/{id}). */
  get(id: string, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("GET", `/v1/jobs/${pathId(id)}`, undefined, undefined, options, "json");
  }
  /** Get a job’s usage (GET /v1/jobs/{id}/usage). */
  usage(id: string, options: RequestOptions = {}): Promise<Models.Usage> {
    return this.transport.request("GET", `/v1/jobs/${pathId(id)}/usage`, undefined, undefined, options, "json");
  }
  /** Create a revision (POST /v1/jobs/{id}/revisions). */
  revise(id: string, input: Models.CreateRevisionRequest, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("POST", `/v1/jobs/${pathId(id)}/revisions`, input, undefined, options, "json");
  }
  /** Quote a job at fixed scope and prices (POST /v1/jobs/quote). */
  quote(input: Models.CreateJobRequest, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("POST", `/v1/jobs/quote`, input, undefined, options, "json");
  }
  /** Cancel unfinished work and release unused reservations (POST /v1/jobs/{id}/cancel). */
  cancel(id: string, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("POST", `/v1/jobs/${pathId(id)}/cancel`, undefined, undefined, options, "json");
  }
  /** Get the ordered course manifest (GET /v1/jobs/{id}/package). */
  package(id: string, query: Models.GetPackageQuery = {}, options: RequestOptions = {}): Promise<Models.Package> {
    return this.transport.request("GET", `/v1/jobs/${pathId(id)}/package`, undefined, query, options, "json");
  }
  /** Download a course ZIP (GET /v1/jobs/{id}/download). */
  downloadPackage(id: string, query: Models.DownloadPackageQuery = {}, options: RequestOptions = {}): Promise<Uint8Array> {
    return this.transport.request("GET", `/v1/jobs/${pathId(id)}/download`, undefined, query, options, "bytes");
  }
  /** Download a packaged file (GET /v1/jobs/{id}/package/files/{fileId}). */
  packageFile(id: string, fileId: string, query: Models.GetPackageFileQuery = {}, options: RequestOptions = {}): Promise<Uint8Array> {
    return this.transport.request("GET", `/v1/jobs/${pathId(id)}/package/files/${pathId(fileId)}`, undefined, query, options, "bytes");
  }
  /** Quote an individual job revision (POST /v1/jobs/{id}/revisions/quote). */
  quoteRevision(id: string, input: Models.QuoteRevisionInput, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("POST", `/v1/jobs/${pathId(id)}/revisions/quote`, input, undefined, options, "json");
  }
  /** Quote retrying a failed or cancelled individual job (POST /v1/jobs/{id}/retry/quote). */
  quoteRetry(id: string, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("POST", `/v1/jobs/${pathId(id)}/retry/quote`, undefined, undefined, options, "json");
  }
  /** Retry one job while preserving completed siblings (POST /v1/jobs/{id}/retry). */
  retry(id: string, input: Models.RetryJobInput, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("POST", `/v1/jobs/${pathId(id)}/retry`, input, undefined, options, "json");
  }
}

export class Files extends FilesHelpers {
  /** Download a file (GET /v1/files/{id}). */
  download(id: string, options: RequestOptions = {}): Promise<Uint8Array> {
    return this.transport.request("GET", `/v1/files/${pathId(id)}`, undefined, undefined, options, "bytes");
  }
}

export class Materials extends MaterialsHelpers {
  /** Upload a material (POST /v1/materials). */
  create(input: Models.MaterialUpload, options: RequestOptions = {}): Promise<Models.Material> {
    return this.transport.request("POST", `/v1/materials`, input, undefined, options, "json");
  }
  /** List materials (GET /v1/materials). */
  list(query: Models.ListMaterialsQuery = {}, options: RequestOptions = {}): Promise<Models.MaterialList> {
    return this.transport.request("GET", `/v1/materials`, undefined, query, options, "json");
  }
  /** Read extraction coverage and source sections (GET /v1/materials/{id}). */
  get(id: string, options: RequestOptions = {}): Promise<Models.Material> {
    return this.transport.request("GET", `/v1/materials/${pathId(id)}`, undefined, undefined, options, "json");
  }
  /** Delete an unused material and its index (DELETE /v1/materials/{id}). */
  delete(id: string, options: RequestOptions = {}): Promise<Models.DeletedMaterial> {
    return this.transport.request("DELETE", `/v1/materials/${pathId(id)}`, undefined, undefined, options, "json");
  }
  /** Retry a failed extraction (POST /v1/materials/{id}/retry). */
  retry(id: string, options: RequestOptions = {}): Promise<Models.Material> {
    return this.transport.request("POST", `/v1/materials/${pathId(id)}/retry`, undefined, undefined, options, "json");
  }
}

export class Preferences extends Resource {
  /** Preference examples (GET /v1/preferences/examples). */
  examples(options: RequestOptions = {}): Promise<Models.PreferenceExamples> {
    return this.transport.request("GET", `/v1/preferences/examples`, undefined, undefined, options, "json");
  }
}

export class Prices extends Resource {
  /** Current prices (GET /v1/prices). */
  get(options: RequestOptions = {}): Promise<Models.Prices> {
    return this.transport.request("GET", `/v1/prices`, undefined, undefined, options, "json");
  }
}

export class Keys extends Resource {
  /** List API keys (GET /v1/keys). */
  list(options: RequestOptions = {}): Promise<Models.ApiKeyList> {
    return this.transport.request("GET", `/v1/keys`, undefined, undefined, options, "json");
  }
  /** Create an API key (POST /v1/keys). */
  create(input: Models.CreateKeyRequest, options: RequestOptions = {}): Promise<Models.CreatedApiKey> {
    return this.transport.request("POST", `/v1/keys`, input, undefined, options, "json");
  }
  /** Revoke an API key (DELETE /v1/keys/{id}). */
  revoke(id: string, options: RequestOptions = {}): Promise<Models.ApiKey> {
    return this.transport.request("DELETE", `/v1/keys/${pathId(id)}`, undefined, undefined, options, "json");
  }
}

export class Webhooks extends Resource {
  /** List webhook endpoints (GET /v1/webhooks). */
  list(options: RequestOptions = {}): Promise<Models.WebhookList> {
    return this.transport.request("GET", `/v1/webhooks`, undefined, undefined, options, "json");
  }
  /** Add a webhook endpoint (POST /v1/webhooks). */
  create(input: Models.CreateWebhookRequest, options: RequestOptions = {}): Promise<Models.CreatedWebhook> {
    return this.transport.request("POST", `/v1/webhooks`, input, undefined, options, "json");
  }
  /** Remove a webhook endpoint (DELETE /v1/webhooks/{id}). */
  delete(id: string, options: RequestOptions = {}): Promise<Models.Webhook> {
    return this.transport.request("DELETE", `/v1/webhooks/${pathId(id)}`, undefined, undefined, options, "json");
  }
}

export class Billing extends Resource {
  /** Balance and ledger (GET /v1/billing/credits). */
  credits(options: RequestOptions = {}): Promise<Models.Credits> {
    return this.transport.request("GET", `/v1/billing/credits`, undefined, undefined, options, "json");
  }
  /** Credit packs (GET /v1/billing/packs). */
  packs(options: RequestOptions = {}): Promise<Models.Packs> {
    return this.transport.request("GET", `/v1/billing/packs`, undefined, undefined, options, "json");
  }
  /** Start a top-up (POST /v1/billing/topups). */
  createTopup(input: Models.CreateTopupRequest, options: RequestOptions = {}): Promise<Models.CreatedTopup> {
    return this.transport.request("POST", `/v1/billing/topups`, input, undefined, options, "json");
  }
  /** Get a top-up (GET /v1/billing/topups/{id}). */
  getTopup(id: string, options: RequestOptions = {}): Promise<Models.Topup> {
    return this.transport.request("GET", `/v1/billing/topups/${pathId(id)}`, undefined, undefined, options, "json");
  }
  /** Get billing controls (GET /v1/billing/settings). */
  settings(options: RequestOptions = {}): Promise<Models.BillingSettings> {
    return this.transport.request("GET", `/v1/billing/settings`, undefined, undefined, options, "json");
  }
  /** Update billing controls (PATCH /v1/billing/settings). */
  updateSettings(input: Models.BillingSettingsPatch, options: RequestOptions = {}): Promise<Models.BillingSettings> {
    return this.transport.request("PATCH", `/v1/billing/settings`, input, undefined, options, "json");
  }
  /** Save a card (POST /v1/billing/payment-methods/setup). */
  setupPaymentMethod(options: RequestOptions = {}): Promise<Models.CardSetup> {
    return this.transport.request("POST", `/v1/billing/payment-methods/setup`, undefined, undefined, options, "json");
  }
  /** Open the card portal (POST /v1/billing/portal). */
  portal(options: RequestOptions = {}): Promise<Models.BillingPortal> {
    return this.transport.request("POST", `/v1/billing/portal`, undefined, undefined, options, "json");
  }
  /** Stop reusing a saved card (DELETE /v1/billing/payment-methods/{id}). */
  unlinkPaymentMethod(id: string, options: RequestOptions = {}): Promise<Models.UnlinkedPaymentMethod> {
    return this.transport.request("DELETE", `/v1/billing/payment-methods/${pathId(id)}`, undefined, undefined, options, "json");
  }
}

export class Quotes extends Resource {
  /** Read a quote (GET /v1/quotes/{id}). */
  get(id: string, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("GET", `/v1/quotes/${pathId(id)}`, undefined, undefined, options, "json");
  }
}

export class Curricula extends CurriculaHelpers {
  /** List curricula (GET /v1/curricula). */
  list(options: RequestOptions = {}): Promise<Models.CurriculumList> {
    return this.transport.request("GET", `/v1/curricula`, undefined, undefined, options, "json");
  }
  /** Generate a curriculum draft from an accepted planning quote (POST /v1/curricula). */
  create(input: Models.CreateCurriculumInput, options: RequestOptions = {}): Promise<Models.Curriculum> {
    return this.transport.request("POST", `/v1/curricula`, input, undefined, options, "json");
  }
  /** Quote curriculum planning and any uncached source summaries (POST /v1/curricula/quote). */
  quotePlanning(input: Models.CurriculumInput, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("POST", `/v1/curricula/quote`, input, undefined, options, "json");
  }
  /** Recommend editable Classive templates (POST /v1/curricula/recommendations). */
  recommend(input: Models.CurriculumInput, options: RequestOptions = {}): Promise<Models.CurriculumRecommendationList> {
    return this.transport.request("POST", `/v1/curricula/recommendations`, input, undefined, options, "json");
  }
  /** Import a free editable curriculum draft (POST /v1/curricula/import). */
  importPlan(input: Models.ImportCurriculumInput, options: RequestOptions = {}): Promise<Models.Curriculum> {
    return this.transport.request("POST", `/v1/curricula/import`, input, undefined, options, "json");
  }
  /** Read a curriculum version (GET /v1/curricula/{id}). */
  get(id: string, query: Models.GetCurriculumQuery = {}, options: RequestOptions = {}): Promise<Models.Curriculum> {
    return this.transport.request("GET", `/v1/curricula/${pathId(id)}`, undefined, query, options, "json");
  }
  /** Save a new draft version (POST /v1/curricula/{id}/versions). */
  edit(id: string, input: Models.EditCurriculumInput, options: RequestOptions = {}): Promise<Models.Curriculum> {
    return this.transport.request("POST", `/v1/curricula/${pathId(id)}/versions`, input, undefined, options, "json");
  }
  /** Approve the current draft version (POST /v1/curricula/{id}/approve). */
  approve(id: string, input: Models.ApproveCurriculumInput, options: RequestOptions = {}): Promise<Models.Curriculum> {
    return this.transport.request("POST", `/v1/curricula/${pathId(id)}/approve`, input, undefined, options, "json");
  }
  /** Quote selected lessons from an approved version (POST /v1/curricula/{id}/quote). */
  quoteLessons(id: string, input: Models.Selection, options: RequestOptions = {}): Promise<Models.Quote> {
    return this.transport.request("POST", `/v1/curricula/${pathId(id)}/quote`, input, undefined, options, "json");
  }
  /** Generate the selected lessons as separate child jobs (POST /v1/curricula/{id}/generate). */
  generate(id: string, input: Models.GenerateCurriculumLessonsInput, options: RequestOptions = {}): Promise<Models.Job> {
    return this.transport.request("POST", `/v1/curricula/${pathId(id)}/generate`, input, undefined, options, "json");
  }
}

export class Organisation extends Resource {
  /** Read organisation spending and concurrency limits (GET /v1/organisation/limits). */
  limits(options: RequestOptions = {}): Promise<Models.Limits> {
    return this.transport.request("GET", `/v1/organisation/limits`, undefined, undefined, options, "json");
  }
  /** Update organisation spending and concurrency limits (PATCH /v1/organisation/limits). */
  updateLimits(input: Models.Limits, options: RequestOptions = {}): Promise<Models.Limits> {
    return this.transport.request("PATCH", `/v1/organisation/limits`, input, undefined, options, "json");
  }
}
