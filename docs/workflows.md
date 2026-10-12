# SDK workflows

These examples complement the [quickstart](../README.md). The full [method reference](reference.md) links every SDK method to its REST endpoint. Python examples work with `AsyncClassive` by adding `await` to calls and using `async for` for iterators.

## Materials

Upload only content you have the right to use. Wait for asynchronous extraction before quoting work that uses the material. Check its extraction coverage and errors; `ready` does not mean every page was successfully extracted or every section will be used by a lesson.

```js
const material = await client.materials.upload('./chapter.pdf', {
  role: 'reference', rights: 'Licensed for this educational use.',
});
const ready = await client.materials.wait(material.id);
console.log(ready.coverage, ready.sections);
for await (const match of client.materials.iterate({ search: 'chapter', status: 'ready' })) {
  console.log(match.id, match.filename);
}
```

```python
material = client.materials.upload("./chapter.pdf", metadata={
    "role": "reference", "rights": "Licensed for this educational use.",
})
ready = client.materials.wait(material["id"])
print(ready["coverage"], ready["sections"])
for match in client.materials.iterate(query={"search": "chapter", "status": "ready"}):
    print(match["id"], match["filename"])
```

Use the material id in a job's `materials` array. Re-upload a changed document with `previousVersionId`; quote the intended material versions again. The service's current upload limits and retention rules are in the [materials guide](https://classive.app/docs/materials).

## Video, written outputs and reviews

The same `jobs.quote`, `jobs.create` and `jobs.wait` sequence supports:

| Request | Fields |
| --- | --- |
| Short video | `type: "clip"`, `outputs: ["video"]`, `lengthMinutes` within the clip range |
| Complete teaching lesson | `type: "lesson"`, selected video/notes/quiz/flashcards outputs |
| Written pack | `type: "lesson"`, `outputs: ["notes", "quiz", "flashcards"]` |
| Material review | `type: "review"`, `materials: [materialId]`, `audience` and optional review prompt |

Select a voice from `voices.list()`. `voices.preview(id)` returns audio bytes. Video delivery includes captions; adding outputs changes the quote. Follow the [current limits](https://classive.app/api#tag/jobs/createJob), rather than relying on a prose copy of those limits here.

## Approved curricula and full courses

A course starts from an approved curriculum version; it is not a direct `jobs.create({type: "course"})` request. Planning and lesson generation are separately quoted chargeable operations. Recommendation and imported-plan methods are also available.

```js
const input = {
  prompt: 'A five-lesson introduction to fractions.',
  audience: { band: 'primary', grade: 'Year 5' }, lessons: 5,
};
const planningQuote = await client.curricula.quotePlanning(input);
// Apply your spending policy before accepting each quote.
const pending = await client.curricula.create({ ...input, quoteId: planningQuote.id });
const draft = await client.curricula.wait(pending.id);
console.log(draft.plan); // Review/edit objectives, sequence, prerequisites and coverage.
const approved = await client.curricula.approve(draft.id, { version: draft.version });
const quote = await client.curricula.quoteLessons(approved.id, { version: approved.version });
const course = await client.curricula.generate(
  approved.id, { quoteId: quote.id }, { idempotencyKey: 'fractions-course-1' },
);
const delivered = await client.jobs.wait(course.id);
await client.jobs.downloadPackageTo(delivered.id, './fractions-course.zip');
```

```python
from classive.types import CurriculumInput

input: CurriculumInput = {
    "prompt": "A five-lesson introduction to fractions.",
    "audience": {"band": "primary", "grade": "Year 5"}, "lessons": 5,
}
planning_quote = client.curricula.quote_planning(input)
pending = client.curricula.create({**input, "quoteId": planning_quote["id"]})
draft = client.curricula.wait(pending["id"])
print(draft["plan"])  # Review/edit before approval.
approved = client.curricula.approve(draft["id"], {"version": draft["version"]})
quote = client.curricula.quote_lessons(approved["id"], {"version": approved["version"]})
course = client.curricula.generate(
    approved["id"], {"quoteId": quote["id"]},
    options={"idempotency_key": "fractions-course-1"},
)
delivered = client.jobs.wait(course["id"])
client.jobs.download_package_to(delivered["id"], "./fractions-course.zip")
```

Approval above is an explicit application action; the SDK does not inspect or approve the plan on your behalf. `quoteLessons` / `quote_lessons` accepts a selected set of `lessonIds` for generating individual lessons. Import a reviewed plan with `curricula.importPlan` / `import_plan`, or edit a version using `curricula.edit`. See [curriculum workflows](https://classive.app/docs/api/curricula).

## Downloads and answer keys

Use a result's file id, not its generated URL. `files.download` returns bytes; `files.downloadTo` / `download_to` streams to disk. Existing destination files are preserved by default. Use the explicit overwrite argument only when replacement is intended.

Course packages default to the learner audience. Instructor downloads use `audience: "instructor"`; a packaged assessment can use `answers: true` when requesting the instructor file. Keep instructor files and answer keys out of learner-facing responses.

```js
await client.jobs.downloadPackageTo(jobId, './instructor.zip', { audience: 'instructor' });
await client.jobs.packageFileTo(jobId, fileId, './answer-key.json', {
  audience: 'instructor', answers: true,
});
```

```python
client.jobs.download_package_to(job_id, "./instructor.zip", query={"audience": "instructor"})
client.jobs.package_file_to(job_id, file_id, "./answer-key.json", query={
    "audience": "instructor", "answers": True,
})
```

## Revisions, retries and cancellation

Request a new quote before a paid revision or retry. They create a new job; the SDK never loops through critics or retries a failed generation for you.

```js
const change = { prompt: 'Use a number-line example in the recap.' };
const quote = await client.jobs.quoteRevision(jobId, change);
const revision = await client.jobs.revise(jobId, { ...change, quoteId: quote.id }, {
  idempotencyKey: 'revision-1',
});
const retryQuote = await client.jobs.quoteRetry(failedJobId);
const retry = await client.jobs.retry(failedJobId, { quoteId: retryQuote.id }, {
  idempotencyKey: 'retry-1',
});
// This explicitly requests server cancellation.
await client.jobs.cancel(retry.id);
```

```python
change = {"prompt": "Use a number-line example in the recap."}
quote = client.jobs.quote_revision(job_id, change)
revision = client.jobs.revise(job_id, {**change, "quoteId": quote["id"]},
                              options={"idempotency_key": "revision-1"})
retry_quote = client.jobs.quote_retry(failed_job_id)
retry = client.jobs.retry(failed_job_id, {"quoteId": retry_quote["id"]},
                         options={"idempotency_key": "retry-1"})
client.jobs.cancel(retry["id"])
```

Cancellation preserves delivered outputs and settles according to the [billing policy](https://classive.app/docs/billing); a cancelled job is not necessarily free. Inspect the returned `credits` and retained outputs. A local timeout or cancelled Python task is not a server cancellation.

## Webhooks and sensitive operations

For production apps, register a webhook with `webhooks.create`, store its returned signing secret securely, verify the raw body and deduplicate event ids. Webhooks can replace long-lived polling. Refetch the job before acting on its latest state.

Key management, webhooks, billing controls and organisation limits require the appropriate API-key scopes. Saving cards, opening checkout, enabling automatic top-ups and changing spending limits are explicit operations; the SDK never enables them as part of generation. See [API keys](https://classive.app/docs/api/keys), [webhooks](https://classive.app/docs/webhooks) and [credits and billing](https://classive.app/docs/billing).
