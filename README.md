# Classive SDKs

JavaScript/TypeScript and Python clients for the [Classive Results API](https://classive.app/api). Create teaching clips, lessons, written packs, document reviews and courses from approved curricula.

Both clients cover all 52 public API operations. JavaScript supports ESM and CommonJS on Node.js 20+. Python supports synchronous and native asynchronous clients on Python 3.11+.

Language guides: [JavaScript and TypeScript](https://github.com/classive-hq/sdk/blob/main/javascript/README.md) · [Python](https://github.com/classive-hq/sdk/blob/main/python/README.md).

## Install

Install JavaScript/TypeScript from npm:

```sh
npm install @classive/sdk
```

Install Python:

```sh
python -m pip install https://github.com/classive-hq/sdk/releases/download/v0.1.1/classive_sdk-0.1.1-py3-none-any.whl
```

Create a REST API key in your [dashboard](https://classive.app/app/keys) and set `CLASSIVE_API_KEY` in your server environment. MCP keys are different and cannot authenticate this SDK. Keep the key out of browser code and source control.

## JavaScript / TypeScript

The following starts paid generation after accepting a quote. In an application, compare the quote with your own spending policy before calling `create`.

```ts
import { Classive, type CreateLesson } from '@classive/sdk';

const client = new Classive(); // CLASSIVE_API_KEY
const input: CreateLesson = {
  type: 'lesson',
  prompt: 'Teach adding fractions with unlike denominators.',
  audience: { band: 'primary', grade: 'Year 5' },
  goals: ['Add two fractions by finding a common denominator.'],
  outputs: ['notes', 'quiz'],
};

const quote = await client.jobs.quote(input);
console.log('Quoted credits:', quote.credits);
const job = await client.jobs.create(
  { ...input, quoteId: quote.id },
  { idempotencyKey: 'fractions-lesson-1' },
);
const finished = await client.jobs.wait(job.id);
console.log(finished.results);
```

For plain JavaScript, omit the type import and annotation. CommonJS:

```js
const { Classive } = require('@classive/sdk');
const client = new Classive({ apiKey: process.env.CLASSIVE_API_KEY });
```

Use a new idempotency key for a new submission; reuse the same key and exact input only when deliberately repeating that submission. The SDK never automatically repeats a mutation.

## Python

Request and response dictionaries retain the API's JSON field names. Methods and SDK options use Python's `snake_case`.

```python
from classive import Classive
from classive.types import CreateLesson

input: CreateLesson = {
    "type": "lesson",
    "prompt": "Teach adding fractions with unlike denominators.",
    "audience": {"band": "primary", "grade": "Year 5"},
    "goals": ["Add two fractions by finding a common denominator."],
    "outputs": ["notes", "quiz"],
}

with Classive() as client:  # CLASSIVE_API_KEY
    quote = client.jobs.quote(input)
    print("Quoted credits:", quote["credits"])
    job = client.jobs.create(
        {**input, "quoteId": quote["id"]},
        options={"idempotency_key": "fractions-lesson-1"},
    )
    finished = client.jobs.wait(job["id"])
    print(finished.get("results"))
```

Asynchronous applications use the same resource methods with `await`:

```python
import asyncio
from classive import AsyncClassive

async def main():
    async with AsyncClassive() as client:
        voices = await client.voices.list()
        print(voices["data"])

asyncio.run(main())
```

## Common workflows

| Task | JavaScript | Python |
| --- | --- | --- |
| Upload and wait for extraction | `materials.upload(path)`, `materials.wait(id)` | `materials.upload(path)`, `materials.wait(id)` |
| Search materials | `materials.list({search: 'algebra'})` | `materials.list(query={"search": "algebra"})` |
| List jobs across pages | `for await (const job of client.jobs.iterate())` | `for job in client.jobs.iterate()` |
| Get a price and start a job | `jobs.quote(input)`, `jobs.create(input)` | `jobs.quote(input)`, `jobs.create(input)` |
| Wait for delivery | `jobs.wait(id)` | `jobs.wait(id)` |
| Download a file to disk | `files.downloadTo(fileId, path)` | `files.download_to(file_id, path)` |
| Read structured notes/assessment JSON | `files.json(fileId)` | `files.json(file_id)` |
| Download a course ZIP | `jobs.downloadPackageTo(jobId, path)` | `jobs.download_package_to(job_id, path)` |
| Plan a curriculum | `curricula.quotePlanning(input)`, `curricula.create(input)`, `curricula.wait(id)` | `curricula.quote_planning(input)`, `curricula.create(input)`, `curricula.wait(id)` |
| Approve and generate a course | `curricula.approve(id, {version})`, `quoteLessons`, `generate` | `curricula.approve(id, {"version": version})`, `quote_lessons`, `generate` |
| Revise or retry a job | `jobs.quoteRevision`, `jobs.revise`, `jobs.quoteRetry`, `jobs.retry` | `jobs.quote_revision`, `jobs.revise`, `jobs.quote_retry`, `jobs.retry` |
| Cancel server work | `jobs.cancel(id)` | `jobs.cancel(id)` |
| Manage billing, keys and webhooks | `billing`, `keys`, `webhooks` | `billing`, `keys`, `webhooks` |

See [workflow examples](https://github.com/classive-hq/sdk/blob/main/docs/workflows.md), the [complete method reference](https://github.com/classive-hq/sdk/blob/main/docs/reference.md), and [runnable examples](https://github.com/classive-hq/sdk/tree/main/examples). Upload only material you have the right to use. Extraction readiness is separate from a lesson's selected/covered source sections.

## Errors, retries and timeouts

Errors carry `status`, `code`, `details` and `requestId` (Python: `request_id`). Catch `AuthenticationError`, `InsufficientCreditsError`, `ValidationError`, `ConflictError`, `RateLimitError`, `ServiceError`, `NetworkError` or `TimeoutError` to choose the appropriate response. `JobFailedError` and `JobCancelledError` retain the full job in `error.job`, including any retained course outputs and charges.

GET requests retry transient connection errors and HTTP 429/500/502/503/504 twice by default, respecting `Retry-After` within the request budget. Set `maxRetries: 0` / `max_retries=0` to disable. POST, PATCH and DELETE requests never retry automatically, including when you supplied an idempotency key. A network error or timeout after submitting work is an ambiguous outcome: inspect the quote/job, or deliberately resubmit the exact input with its original idempotency key where the endpoint supports it.

JavaScript's `timeoutMs` defaults to 30,000 and covers the request, retries and body consumption. Python's `timeout` is in seconds: HTTPX applies network phase timeouts; the SDK also checks the response/retry budget, and the async client enforces a wall-clock deadline. Disk operations and a blocking synchronous network read can outlast the synchronous response budget. Polling defaults to two-second intervals with a 30-minute overall wait budget.

```js
await client.jobs.wait(job.id, {
  pollIntervalMs: 2000,
  waitTimeoutMs: 20 * 60_000,
  signal: abortController.signal,
});
```

```python
client.jobs.wait(job["id"], options={"poll_interval": 2, "wait_timeout": 1200})
```

Aborting or timing out a wait stops the local caller; it does not cancel work on Classive. Cancel the job explicitly when needed. Download helpers use file ids, refuse redirects and stream to temporary files; they preserve existing destination files unless you explicitly opt into overwriting.

## Verify webhooks

Use the raw request body and the `Classive-Signature` header before parsing JSON:

```js
import { verifyWebhook } from '@classive/sdk';
const valid = await verifyWebhook(rawBody, signatureHeader, signingSecret);
```

```python
from classive import verify_webhook
valid = verify_webhook(raw_body, signature_header, signing_secret)
```

Verification checks the HMAC-SHA256 signature and a five-minute timestamp window. Record processed event ids in your application, because deliveries can repeat. See the [webhook guide](https://classive.app/docs/webhooks).

## Development and contract updates

```sh
npm ci
npm test
node scripts/verify-javascript-package.mjs
python -m pip install ./python build mypy
python -m unittest discover -s python/tests -v
mypy python/src/classive examples/python
python -m build python
```

`schema/openapi.json` is a snapshot of the live public contract, with its source hash in `schema/source.json`. `npm run generate` regenerates the method facades and types for both languages; `npm run check:generated` catches drift. Update the snapshot deliberately, review additions and changes, map new operation names in `scripts/generate.mjs`, regenerate and run both suites before releasing.

API reference: [classive.app/api](https://classive.app/api). Current documentation: [classive.app/docs](https://classive.app/docs), [machine-readable index](https://classive.app/llms.txt). This SDK is an initial 0.1 release; pin your version. It does not certify the teaching pipeline's quality or reliability.
