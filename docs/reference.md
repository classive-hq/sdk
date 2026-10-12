# SDK method reference

Generated from the public OpenAPI snapshot. Request and response types are exported by `@classive/sdk` and `classive.types`. JSON bodies keep their wire field names; Python methods and SDK options use snake_case.

For workflows, pagination, polling and downloads, see [workflow examples](workflows.md) and the [SDK guide](../README.md). Query-bearing methods take a query object in JavaScript and `query={...}` in Python; request controls go in the final options object / `options={...}`.

## Voices

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.voices.preview` | `client.voices.preview` | [GET /voices/{id}/preview](https://classive.app/api#tag/catalogue/voicePreview) | — | bytes |
| `client.voices.list` | `client.voices.list` | [GET /v1/voices](https://classive.app/api#tag/catalogue/listVoices) | — | `VoiceList` |

## Jobs

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.jobs.create` | `client.jobs.create` | [POST /v1/jobs](https://classive.app/api#tag/jobs/createJob) | `CreateJobRequest` | `Job` |
| `client.jobs.list` | `client.jobs.list` | [GET /v1/jobs](https://classive.app/api#tag/jobs/listJobs) | — | `JobList` |
| `client.jobs.estimate` | `client.jobs.estimate` | [POST /v1/jobs/estimate](https://classive.app/api#tag/jobs/estimateJob) | `CreateJobRequest` | `Estimate` |
| `client.jobs.get` | `client.jobs.get` | [GET /v1/jobs/{id}](https://classive.app/api#tag/jobs/getJob) | — | `Job` |
| `client.jobs.usage` | `client.jobs.usage` | [GET /v1/jobs/{id}/usage](https://classive.app/api#tag/jobs/getJobUsage) | — | `Usage` |
| `client.jobs.revise` | `client.jobs.revise` | [POST /v1/jobs/{id}/revisions](https://classive.app/api#tag/jobs/createRevision) | `CreateRevisionRequest` | `Job` |
| `client.jobs.quote` | `client.jobs.quote` | [POST /v1/jobs/quote](https://classive.app/api#tag/jobs/quoteJob) | `CreateJobRequest` | `Quote` |
| `client.jobs.cancel` | `client.jobs.cancel` | [POST /v1/jobs/{id}/cancel](https://classive.app/api#tag/jobs/cancelJob) | — | `Job` |
| `client.jobs.package` | `client.jobs.package` | [GET /v1/jobs/{id}/package](https://classive.app/api#tag/files/getPackage) | — | `Package` |
| `client.jobs.downloadPackage` | `client.jobs.download_package` | [GET /v1/jobs/{id}/download](https://classive.app/api#tag/files/downloadPackage) | — | bytes |
| `client.jobs.packageFile` | `client.jobs.package_file` | [GET /v1/jobs/{id}/package/files/{fileId}](https://classive.app/api#tag/files/getPackageFile) | — | bytes |
| `client.jobs.quoteRevision` | `client.jobs.quote_revision` | [POST /v1/jobs/{id}/revisions/quote](https://classive.app/api#tag/jobs/quoteRevision) | `QuoteRevisionInput` | `Quote` |
| `client.jobs.quoteRetry` | `client.jobs.quote_retry` | [POST /v1/jobs/{id}/retry/quote](https://classive.app/api#tag/jobs/quoteRetry) | — | `Quote` |
| `client.jobs.retry` | `client.jobs.retry` | [POST /v1/jobs/{id}/retry](https://classive.app/api#tag/jobs/retryJob) | `RetryJobInput` | `Job` |

## Files

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.files.download` | `client.files.download` | [GET /v1/files/{id}](https://classive.app/api#tag/files/getFile) | — | bytes |

## Materials

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.materials.create` | `client.materials.create` | [POST /v1/materials](https://classive.app/api#tag/materials/uploadMaterial) | `MaterialUpload` | `Material` |
| `client.materials.list` | `client.materials.list` | [GET /v1/materials](https://classive.app/api#tag/materials/listMaterials) | — | `MaterialList` |
| `client.materials.get` | `client.materials.get` | [GET /v1/materials/{id}](https://classive.app/api#tag/materials/getMaterial) | — | `Material` |
| `client.materials.delete` | `client.materials.delete` | [DELETE /v1/materials/{id}](https://classive.app/api#tag/materials/deleteMaterial) | — | `DeletedMaterial` |
| `client.materials.retry` | `client.materials.retry` | [POST /v1/materials/{id}/retry](https://classive.app/api#tag/materials/retryMaterial) | — | `Material` |

## Preferences

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.preferences.examples` | `client.preferences.examples` | [GET /v1/preferences/examples](https://classive.app/api#tag/catalogue/getPreferenceExamples) | — | `PreferenceExamples` |

## Prices

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.prices.get` | `client.prices.get` | [GET /v1/prices](https://classive.app/api#tag/catalogue/getPrices) | — | `Prices` |

## Keys

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.keys.list` | `client.keys.list` | [GET /v1/keys](https://classive.app/api#tag/keys/listKeys) | — | `ApiKeyList` |
| `client.keys.create` | `client.keys.create` | [POST /v1/keys](https://classive.app/api#tag/keys/createKey) | `CreateKeyRequest` | `CreatedApiKey` |
| `client.keys.revoke` | `client.keys.revoke` | [DELETE /v1/keys/{id}](https://classive.app/api#tag/keys/revokeKey) | — | `ApiKey` |

## Webhooks

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.webhooks.list` | `client.webhooks.list` | [GET /v1/webhooks](https://classive.app/api#tag/webhooks/listWebhooks) | — | `WebhookList` |
| `client.webhooks.create` | `client.webhooks.create` | [POST /v1/webhooks](https://classive.app/api#tag/webhooks/createWebhook) | `CreateWebhookRequest` | `CreatedWebhook` |
| `client.webhooks.delete` | `client.webhooks.delete` | [DELETE /v1/webhooks/{id}](https://classive.app/api#tag/webhooks/deleteWebhook) | — | `Webhook` |

## Billing

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.billing.credits` | `client.billing.credits` | [GET /v1/billing/credits](https://classive.app/api#tag/billing/getCredits) | — | `Credits` |
| `client.billing.packs` | `client.billing.packs` | [GET /v1/billing/packs](https://classive.app/api#tag/billing/listPacks) | — | `Packs` |
| `client.billing.createTopup` | `client.billing.create_topup` | [POST /v1/billing/topups](https://classive.app/api#tag/billing/createTopup) | `CreateTopupRequest` | `CreatedTopup` |
| `client.billing.getTopup` | `client.billing.get_topup` | [GET /v1/billing/topups/{id}](https://classive.app/api#tag/billing/getTopup) | — | `Topup` |
| `client.billing.settings` | `client.billing.settings` | [GET /v1/billing/settings](https://classive.app/api#tag/billing/getBillingSettings) | — | `BillingSettings` |
| `client.billing.updateSettings` | `client.billing.update_settings` | [PATCH /v1/billing/settings](https://classive.app/api#tag/billing/updateBillingSettings) | `BillingSettingsPatch` | `BillingSettings` |
| `client.billing.setupPaymentMethod` | `client.billing.setup_payment_method` | [POST /v1/billing/payment-methods/setup](https://classive.app/api#tag/billing/setupPaymentMethod) | — | `CardSetup` |
| `client.billing.portal` | `client.billing.portal` | [POST /v1/billing/portal](https://classive.app/api#tag/billing/createBillingPortal) | — | `BillingPortal` |
| `client.billing.unlinkPaymentMethod` | `client.billing.unlink_payment_method` | [DELETE /v1/billing/payment-methods/{id}](https://classive.app/api#tag/billing/unlinkPaymentMethod) | — | `UnlinkedPaymentMethod` |

## Quotes

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.quotes.get` | `client.quotes.get` | [GET /v1/quotes/{id}](https://classive.app/api#tag/curricula/getQuote) | — | `Quote` |

## Curricula

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.curricula.list` | `client.curricula.list` | [GET /v1/curricula](https://classive.app/api#tag/curricula/listCurricula) | — | `CurriculumList` |
| `client.curricula.create` | `client.curricula.create` | [POST /v1/curricula](https://classive.app/api#tag/curricula/createCurriculum) | `CreateCurriculumInput` | `Curriculum` |
| `client.curricula.quotePlanning` | `client.curricula.quote_planning` | [POST /v1/curricula/quote](https://classive.app/api#tag/curricula/quoteCurriculumPlanning) | `CurriculumInput` | `Quote` |
| `client.curricula.recommend` | `client.curricula.recommend` | [POST /v1/curricula/recommendations](https://classive.app/api#tag/curricula/recommendCurricula) | `CurriculumInput` | `CurriculumRecommendationList` |
| `client.curricula.importPlan` | `client.curricula.import_plan` | [POST /v1/curricula/import](https://classive.app/api#tag/curricula/importCurriculum) | `ImportCurriculumInput` | `Curriculum` |
| `client.curricula.get` | `client.curricula.get` | [GET /v1/curricula/{id}](https://classive.app/api#tag/curricula/getCurriculum) | — | `Curriculum` |
| `client.curricula.edit` | `client.curricula.edit` | [POST /v1/curricula/{id}/versions](https://classive.app/api#tag/curricula/editCurriculum) | `EditCurriculumInput` | `Curriculum` |
| `client.curricula.approve` | `client.curricula.approve` | [POST /v1/curricula/{id}/approve](https://classive.app/api#tag/curricula/approveCurriculum) | `ApproveCurriculumInput` | `Curriculum` |
| `client.curricula.quoteLessons` | `client.curricula.quote_lessons` | [POST /v1/curricula/{id}/quote](https://classive.app/api#tag/curricula/quoteCurriculumLessons) | `Selection` | `Quote` |
| `client.curricula.generate` | `client.curricula.generate` | [POST /v1/curricula/{id}/generate](https://classive.app/api#tag/curricula/generateCurriculumLessons) | `GenerateCurriculumLessonsInput` | `Job` |

## Organisation

| JavaScript | Python | REST reference | Request body | Response |
| --- | --- | --- | --- | --- |
| `client.organisation.limits` | `client.organisation.limits` | [GET /v1/organisation/limits](https://classive.app/api#tag/keys/getLimits) | — | `Limits` |
| `client.organisation.updateLimits` | `client.organisation.update_limits` | [PATCH /v1/organisation/limits](https://classive.app/api#tag/keys/updateLimits) | `Limits` | `Limits` |
