# Classive JavaScript and TypeScript SDK

Create teaching clips, lessons, written resources, document reviews and courses with the [Classive API](https://classive.app/api). Supports Node.js 20+, ESM, CommonJS and typed request/response autocomplete.

## Install

```sh
npm install @classive/sdk
```

```js
import { Classive } from '@classive/sdk';
const client = new Classive(); // Reads server-side CLASSIVE_API_KEY.
const voices = await client.voices.list();
console.log(voices.data);
```

Create a REST API key in your [dashboard](https://classive.app/app/keys) and keep `CLASSIVE_API_KEY` in your server environment. CommonJS applications use `const { Classive } = require('@classive/sdk')`.

## Create a lesson

Request a quote, check it against your spending policy, then accept it. Calling `create` starts paid generation.

```ts
import { Classive, type CreateLesson } from '@classive/sdk';

const client = new Classive();
const input: CreateLesson = {
  type: 'lesson',
  prompt: 'Teach adding fractions with unlike denominators.',
  audience: { band: 'primary', grade: 'Year 5' },
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

For plain JavaScript, omit the type import and annotation. Use a stable idempotency key when deliberately repeating the same submission.

The SDK covers all 52 public operations, with helpers for material uploads, extraction readiness, cursor pagination, streamed downloads and webhook verification. Mutations never retry automatically. Aborting a local wait does not cancel server work; use `jobs.cancel(id)` explicitly.

See the [workflow examples](https://github.com/classive-hq/sdk/blob/main/docs/workflows.md), [method reference](https://github.com/classive-hq/sdk/blob/main/docs/reference.md), [runnable example](https://github.com/classive-hq/sdk/blob/main/examples/javascript/lesson.mjs) and [API reference](https://classive.app/api).

Looking for Python? See the [Python SDK](https://github.com/classive-hq/sdk/blob/main/python/README.md).
