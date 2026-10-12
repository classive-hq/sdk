# Classive JavaScript and TypeScript SDK

Build teaching clips, lessons, written resources, document reviews and courses with the [Classive API](https://classive.app/api). The client supports Node.js 20+, ESM, CommonJS and typed request/response autocomplete.

```sh
npm install @classive/sdk
```

```js
import { Classive } from '@classive/sdk';
const client = new Classive(); // Server-side CLASSIVE_API_KEY.
const voices = await client.voices.list();
console.log(voices.data);
```

For TypeScript, request and response types are exported from the same package. CommonJS applications use `const { Classive } = require('@classive/sdk')`.

Use `jobs.quote`, explicitly accept the quote with `jobs.create`, then `jobs.wait` or receive webhooks. Helpers support material extraction readiness, cursor pagination and streamed downloads. Mutations never retry automatically, and local cancellation never cancels server work.

See the [quickstart](../README.md#javascript--typescript), [workflow examples](../docs/workflows.md), [complete method reference](../docs/reference.md) and [runnable lesson example](../examples/javascript/lesson.mjs). All 52 operations in the public contract are supported. Keep the API key in your server environment; an SDK is not a way to safely expose a secret in learner browsers.
