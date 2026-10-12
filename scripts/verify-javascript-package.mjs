// Test the actual packed artifact in a clean consumer, not source-relative imports.
import {execFileSync} from 'node:child_process';
import {mkdtemp,readFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {fixture,json,job} from '../javascript/test/fixture.mjs';
const root=resolve(fileURLToPath(new URL('..',import.meta.url)));
const dir=await mkdtemp(join(tmpdir(),'classive-consumer-'));
try {
  const packed=JSON.parse(execFileSync('npm',['pack','--json','--pack-destination',dir],{cwd:root,encoding:'utf8'}))[0];
  const tar=join(dir,packed.filename);
  await writeFile(join(dir,'package.json'),JSON.stringify({type:'module',private:true}));
  execFileSync('npm',['install','--no-audit','--no-fund',tar],{cwd:dir,stdio:'pipe'});
  const files=packed.files.map(f=>f.path);
  if(files.some(f=>f.includes('node_modules')||f.endsWith('.env'))) throw new Error('Unexpected packaged file');
  await writeFile(join(dir,'esm.mjs'),`import {Classive,ValidationError} from '@classive/sdk';\nconst c=new Classive({apiKey:'test',fetch:async()=>new Response(JSON.stringify({data:[{id:'adam'}]}),{status:200})});\nif((await c.voices.list()).data[0].id!=='adam') throw new Error('ESM consumer failed');\n`);
  await writeFile(join(dir,'cjs.cjs'),`const {Classive}=require('@classive/sdk');\nconst c=new Classive({apiKey:'test',fetch:async()=>new Response(JSON.stringify({data:[]}),{status:200})});\nc.voices.list().then(v=>{if(v.data.length) throw new Error('CommonJS consumer failed')}).catch(e=>{console.error(e);process.exitCode=1});\n`);
  execFileSync(process.execPath,['esm.mjs'],{cwd:dir,stdio:'inherit'});
  execFileSync(process.execPath,['cjs.cjs'],{cwd:dir,stdio:'inherit'});
  await writeFile(join(dir,'typed.ts'),await readFile(join(root,'examples/javascript/typed.ts')));
  execFileSync(join(root,'node_modules/.bin/tsc'),['--noEmit','--strict','--skipLibCheck','--module','NodeNext','--moduleResolution','NodeNext','--target','ES2022',join(dir,'typed.ts')],{cwd:dir,stdio:'inherit'});
  // Run the shipped documentation example against a local HTTP fixture.
  await writeFile(join(dir,'lesson.mjs'),await readFile(join(root,'examples/javascript/lesson.mjs')));
  const f=await fixture((call,res)=>{
    if(call.url.pathname==='/v1/jobs/quote') return json(res,{id:'quo_example',credits:10});
    if(call.method==='POST') return json(res,job('queued'),201);
    return json(res,job());
  });
  try {
    const {spawn}=await import('node:child_process');
    const run=submit=>new Promise((resolve,reject)=>{
      const child=spawn(process.execPath,['lesson.mjs',...(submit?['--submit']:[])],{cwd:dir,env:{...process.env,CLASSIVE_API_KEY:'ck_live_test',CLASSIVE_BASE_URL:f.baseUrl},stdio:'inherit'});
      child.once('error',reject);child.once('exit',code=>code===0?resolve():reject(new Error('Example exited '+code)));
    });
    await run(false);
    if(f.calls.length!==1||f.calls[0].url.pathname!=='/v1/jobs/quote') throw new Error('Quote-only example submitted work.');
    f.calls.length=0;await run(true);
    if(f.calls.filter(c=>c.method==='POST'&&c.url.pathname==='/v1/jobs').length!==1) throw new Error('Example did not submit exactly once.');
  } finally {await f.close();}
  console.log('Packaged ESM, CommonJS and TypeScript consumers passed.');
} finally {await rm(dir,{recursive:true,force:true});}
