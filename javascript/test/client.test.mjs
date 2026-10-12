import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,readdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHmac} from 'node:crypto';
import {Classive,AuthenticationError,InsufficientCreditsError,ConflictError,RateLimitError,ServiceError,NetworkError,
  TimeoutError,AbortError,ProtocolError,ValidationError,JobFailedError,JobCancelledError,MaterialFailedError,verifyWebhook} from '../dist/index.js';
import {fixture,json,input,job} from './fixture.mjs';

test('all 52 operations send their contract path, query, body and idempotency header',async()=>{
  const spec=JSON.parse(await readFile(new URL('../../schema/openapi.json',import.meta.url)));
  const ops=JSON.parse(await readFile(new URL('../../schema/operations.json',import.meta.url)));
  const f=await fixture((call,res)=>json(res,{ok:true}));
  try {
    const client=new Classive({apiKey:'ck_live_test',baseUrl:f.baseUrl,maxRetries:0});
    assert.equal(ops.length,52);
    for(const op of ops) {
      const schema=spec.paths[op.path][op.method.toLowerCase()];
      assert.equal(schema.operationId,op.operationId);
      const params=schema.parameters??[],args=[];
      for(const p of params.filter(p=>p.in==='path')) args.push(p.name==='fileId'?'file_test':'id_test');
      const body=schema.requestBody?.content?.['application/json']?{marker:op.operationId}:undefined;
      if(body) args.push(body);
      const query=Object.fromEntries(params.filter(p=>p.in==='query').map(p=>[p.name,p.schema.type==='boolean'?true:p.name==='limit'?2:'value']));
      if(Object.keys(query).length) args.push(query);
      args.push({idempotencyKey:'sdk-test'});
      await client[op.resource][op.javascript](...args);
      const call=f.calls.at(-1);
      assert.equal(call.method,op.method);
      assert.equal(call.url.pathname,op.path.replace(/\{fileId\}/g,'file_test').replace(/\{id\}/g,'id_test'));
      assert.deepEqual(Object.fromEntries(call.url.searchParams),Object.fromEntries(Object.entries(query).map(([k,v])=>[k,String(v)])));
      assert.deepEqual(call.body,body);assert.equal(call.headers.authorization,'Bearer ck_live_test');
      assert.equal(call.headers['idempotency-key'],'sdk-test');
    }
  } finally {await f.close();}
});

test('quote -> create -> wait -> structured result and stream to disk over real HTTP',async()=>{
  let reads=0;
  const f=await fixture((call,res)=>{
    if(call.url.pathname==='/v1/jobs/quote') {assert.deepEqual(call.body,input);return json(res,{id:'quo_test',credits:10});}
    if(call.method==='POST') {assert.equal(call.body.quoteId,'quo_test');assert.equal(call.headers['idempotency-key'],'lesson-1');return json(res,job('queued'),201);}
    if(call.url.pathname.startsWith('/v1/files')) return json(res,{title:'Fractions'});
    json(res,job(reads++===0?'processing':'completed'));
  });
  const dir=await mkdtemp(join(tmpdir(),'classive-js-'));
  try {
    const c=new Classive({apiKey:'ck_live_test',baseUrl:f.baseUrl});
    const quote=await c.jobs.quote(input),accepted=await c.jobs.create({...input,quoteId:quote.id},{idempotencyKey:'lesson-1'});
    const delivered=await c.jobs.wait(accepted.id,{pollIntervalMs:5,waitTimeoutMs:1000});
    assert.equal(delivered.status,'completed');
    assert.deepEqual(await c.files.json(delivered.results.lessons[0].notes.json.id),{title:'Fractions'});
    const destination=join(dir,'notes.json');await c.files.downloadTo('file_test',destination);
    assert.deepEqual(JSON.parse(await readFile(destination)),{title:'Fractions'});
    await assert.rejects(c.files.downloadTo('file_test',destination),{code:'EEXIST'});
    assert.deepEqual(await readdir(dir),['notes.json']);
  } finally {await f.close();await rm(dir,{recursive:true,force:true});}
});

test('read retries honor Retry-After; mutations never retry, even with an idempotency key',async()=>{
  const f=await fixture((call,res,calls)=>calls.length===1?json(res,{error:{code:'busy',message:'Busy'}},429,{'retry-after':'0'}):json(res,{data:[]}));
  try {const c=new Classive({apiKey:'test',baseUrl:f.baseUrl});await c.voices.list();assert.equal(f.calls.length,2);} finally {await f.close();}
  for(const status of [429,500,503]) {
    const g=await fixture((_,res)=>json(res,{error:{code:'rejected',message:'Try later'}},status));
    try {const c=new Classive({apiKey:'test',baseUrl:g.baseUrl,maxRetries:5});await assert.rejects(c.jobs.create(input,{idempotencyKey:'same'}));assert.equal(g.calls.length,1);} finally {await g.close();}
  }
  let calls=0;const fetch=async()=>{calls++;throw new TypeError('network');};
  const c=new Classive({apiKey:'test',fetch,maxRetries:1});
  await assert.rejects(c.jobs.create(input),NetworkError);assert.equal(calls,1);
  calls=0;await assert.rejects(c.voices.list(),NetworkError);assert.equal(calls,2);
});

test('API errors retain status, code, request id and details',async()=>{
  for(const [status,type] of [[401,AuthenticationError],[402,InsufficientCreditsError],[409,ConflictError],[429,RateLimitError],[503,ServiceError]]) {
    const f=await fixture((_,res)=>json(res,{error:{code:'specific',message:'Actionable',details:{field:'prompt'}}},status,{'x-request-id':'request_test'}));
    try {const c=new Classive({apiKey:'test',baseUrl:f.baseUrl,maxRetries:0});await assert.rejects(c.prices.get(),e=>e instanceof type&&e.status===status&&e.code==='specific'&&e.requestId==='request_test'&&e.details.error.details.field==='prompt');} finally {await f.close();}
  }
});

test('wait surfaces failed/cancelled payloads, and timing out sends no server cancellation',async()=>{
  for(const [status,type] of [['failed',JobFailedError],['cancelled',JobCancelledError]]) {
    const f=await fixture((_,res)=>json(res,{...job(status),failure:{code:'generation_failed',message:'Could not deliver'}}));
    try {const c=new Classive({apiKey:'test',baseUrl:f.baseUrl});await assert.rejects(c.jobs.wait('job_test'),e=>e instanceof type&&e.job.status===status);assert.equal(f.calls.length,1);} finally {await f.close();}
  }
  const f=await fixture((_,res)=>json(res,job('processing')));
  try {const c=new Classive({apiKey:'test',baseUrl:f.baseUrl});await assert.rejects(c.jobs.wait('job_test',{waitTimeoutMs:35,pollIntervalMs:5}),TimeoutError);assert.ok(f.calls.every(c=>c.method==='GET'));} finally {await f.close();}
});

test('requests abort and time out, including response bodies',async()=>{
  const f=await fixture((_,res)=>{res.writeHead(200,{'content-type':'application/json'});res.write('{');});
  try {
    const c=new Classive({apiKey:'test',baseUrl:f.baseUrl,maxRetries:0,timeoutMs:40});
    await assert.rejects(c.prices.get(),TimeoutError);
    const controller=new AbortController();setTimeout(()=>controller.abort(),10);
    await assert.rejects(c.prices.get({signal:controller.signal,timeoutMs:1000}),AbortError);
  } finally {await f.close();}
});

test('redirect and arbitrary-url downloads cannot leak credentials; partial files are removed',async()=>{
  let destinationCalls=0;
  const target=await fixture((_,res)=>{destinationCalls++;json(res,{});});
  const f=await fixture((_,res)=>{res.writeHead(302,{location:target.baseUrl+'/stolen'});res.end();});
  const dir=await mkdtemp(join(tmpdir(),'classive-part-'));
  try {
    const c=new Classive({apiKey:'secret',baseUrl:f.baseUrl});
    await assert.rejects(c.files.download('file_test'),ProtocolError);
    await assert.rejects(c.files.downloadTo('file_test',join(dir,'bad')),ProtocolError);
    assert.throws(()=>c.files.download(target.baseUrl),ValidationError);
    assert.throws(()=>c.jobs.get('..'),ValidationError);assert.equal(destinationCalls,0);assert.deepEqual(await readdir(dir),[]);
  } finally {await f.close();await target.close();await rm(dir,{recursive:true,force:true});}
});

test('material upload retains bytes and metadata; helpers wait and paginate without duplicating work',async()=>{
  const f=await fixture((call,res)=>{
    if(call.method==='POST') return json(res,{id:'mat_test',status:'queued'});
    if(call.url.pathname==='/v1/materials') return json(res,{data:[{id:call.url.searchParams.get('starting_after')?'mat_b':'mat_a'}],hasMore:!call.url.searchParams.has('starting_after'),nextCursor:'mat_a'});
    if(call.url.pathname==='/v1/jobs') return json(res,{data:[{id:call.url.searchParams.get('starting_after')?'job_b':'job_a'}],hasMore:!call.url.searchParams.has('starting_after')});
    if(call.url.pathname.startsWith('/v1/curricula')) return json(res,{status:'draft'});
    return json(res,{id:'mat_test',status:'ready'});
  });
  const dir=await mkdtemp(join(tmpdir(),'classive-upload-'));
  try {
    const c=new Classive({apiKey:'test',baseUrl:f.baseUrl});const filename=join(dir,'source.txt');await writeFile(filename,'Fractions ✓');
    await c.materials.upload(filename,{rights:'I have permission to use this content.'});
    assert.equal(Buffer.from(f.calls[0].body.base64,'base64').toString(),'Fractions ✓');assert.equal(f.calls[0].body.contentType,'text/plain');
    assert.equal((await c.materials.wait('mat_test')).status,'ready');
    const materials=[];for await(const m of c.materials.iterate({search:'math'})) materials.push(m.id);assert.deepEqual(materials,['mat_a','mat_b']);
    const jobs=[];for await(const j of c.jobs.iterate()) jobs.push(j.id);assert.deepEqual(jobs,['job_a','job_b']);
    assert.equal((await c.curricula.wait('cur_test')).status,'draft');
  } finally {await f.close();await rm(dir,{recursive:true,force:true});}
});

test('configuration rejects unsafe origins and missing/MCP credentials without printing secrets',()=>{
  for(const apiKey of ['', 'cmcp_live_secret']) assert.throws(()=>new Classive({apiKey}),ValidationError);
  for(const baseUrl of ['http://remote.example','https://user:password@example.com','https://example.com/path','https://example.com?token=private']) assert.throws(()=>new Classive({apiKey:'secret',baseUrl}),ValidationError);
  assert.throws(()=>new Classive({apiKey:'secret',maxRetries:-1}),ValidationError);
});

test('webhook signatures reject changed bodies, old/future timestamps and malformed headers',async()=>{
  const raw='{"event":"é"}',secret='webhook_test',t=1000;
  const signature=createHmac('sha256',secret).update(`${t}.${raw}`).digest('hex'),header=`t=${t},v1=${signature}`;
  assert.equal(await verifyWebhook(raw,header,secret,{now:1000}),true);
  assert.equal(await verifyWebhook(new TextEncoder().encode(raw),header,secret,{now:1000}),true);
  for(const [body,h,now] of [[raw+' ',header,1000],[raw,header,2000],[raw,header,0],[raw,'t=1000,v1=no',1000],[raw,header+',v1='+signature,1000]]) assert.equal(await verifyWebhook(body,h,secret,{now}),false);
});
