import {writeFile} from 'node:fs/promises';
await writeFile(new URL('../javascript/dist-cjs/package.json',import.meta.url),'{"type":"commonjs"}\n');
