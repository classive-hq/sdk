// Generate the typed facade from the public OpenAPI snapshot. No service internals.
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const source = await readFile(new URL('../schema/openapi.json', import.meta.url), 'utf8');
const spec = JSON.parse(source), schemas = {...spec.components.schemas};
const naming = {
  voicePreview:['voices','preview'], createJob:['jobs','create'], listJobs:['jobs','list'], estimateJob:['jobs','estimate'],
  quoteJob:['jobs','quote'], getJob:['jobs','get'], getJobUsage:['jobs','usage'], createRevision:['jobs','revise'],
  quoteRevision:['jobs','quoteRevision'], quoteRetry:['jobs','quoteRetry'], retryJob:['jobs','retry'], cancelJob:['jobs','cancel'],
  getPackage:['jobs','package'], downloadPackage:['jobs','downloadPackage'], getPackageFile:['jobs','packageFile'], getFile:['files','download'],
  uploadMaterial:['materials','create'], listMaterials:['materials','list'], getMaterial:['materials','get'], deleteMaterial:['materials','delete'], retryMaterial:['materials','retry'],
  listVoices:['voices','list'], getPreferenceExamples:['preferences','examples'], getPrices:['prices','get'],
  listKeys:['keys','list'], createKey:['keys','create'], revokeKey:['keys','revoke'],
  listWebhooks:['webhooks','list'], createWebhook:['webhooks','create'], deleteWebhook:['webhooks','delete'],
  getCredits:['billing','credits'], listPacks:['billing','packs'], createTopup:['billing','createTopup'], getTopup:['billing','getTopup'],
  getBillingSettings:['billing','settings'], updateBillingSettings:['billing','updateSettings'], setupPaymentMethod:['billing','setupPaymentMethod'],
  createBillingPortal:['billing','portal'], unlinkPaymentMethod:['billing','unlinkPaymentMethod'],
  getQuote:['quotes','get'], listCurricula:['curricula','list'], createCurriculum:['curricula','create'],
  quoteCurriculumPlanning:['curricula','quotePlanning'], recommendCurricula:['curricula','recommend'], importCurriculum:['curricula','importPlan'],
  getCurriculum:['curricula','get'], editCurriculum:['curricula','edit'], approveCurriculum:['curricula','approve'],
  quoteCurriculumLessons:['curricula','quoteLessons'], generateCurriculumLessons:['curricula','generate'],
  getLimits:['organisation','limits'], updateLimits:['organisation','updateLimits']
};
const pascal = s => s[0].toUpperCase()+s.slice(1);
const snake = s => s.replace(/[A-Z]/g,c=>'_'+c.toLowerCase());
const operations = [];
for (const [path, methods] of Object.entries(spec.paths)) for (const [method, o] of Object.entries(methods)) {
  if (!o.operationId) continue;
  if (!naming[o.operationId]) throw new Error('Unmapped operation '+o.operationId);
  const [group, name] = naming[o.operationId];
  const parameters = o.parameters ?? [];
  const paths = parameters.filter(p=>p.in==='path');
  const queries = parameters.filter(p=>p.in==='query');
  const body = o.requestBody?.content?.['application/json']?.schema;
  const success = Object.entries(o.responses).find(([code])=>code.startsWith('2'))?.[1];
  const content = success?.content ?? {};
  // File delivery depends on the file's media type; do not assume JSON notes.
  const binary = o.operationId==='getFile' || Object.keys(content).some(t=>t!=='application/json');
  const response = content['application/json']?.schema;
  const model = (schema, suffix) => {
    if (!schema) return undefined;
    if (schema.$ref) return schema.$ref.split('/').at(-1);
    const key = pascal(o.operationId)+suffix; schemas[key] = schema; return key;
  };
  const bodyType = model(body,'Input');
  const queryType = queries.length ? model({type:'object',properties:Object.fromEntries(queries.map(p=>[p.name,p.schema]))},'Query') : undefined;
  operations.push({id:o.operationId, group, name, path, method:method.toUpperCase(), paths, bodyType, queryType,
    responseType: binary ? undefined : model(response,'Response'), binary, summary:o.summary ?? o.operationId,
    idempotency:parameters.some(p=>p.name==='Idempotency-Key')});
}
const literal = v => JSON.stringify(v);
function ts(s) {
  if (s.$ref) return s.$ref.split('/').at(-1);
  if ('const' in s) return literal(s.const);
  if (s.enum) return s.enum.map(literal).join(' | ');
  if (s.oneOf || s.anyOf) return (s.oneOf??s.anyOf).map(ts).join(' | ');
  if (s.allOf) return s.allOf.map(ts).join(' & ');
  if (Array.isArray(s.type)) return s.type.map(type=>ts({...s,type})).join(' | ');
  if (s.type==='array') return `Array<${ts(s.items??{})}>`;
  if (s.type==='object' || s.properties) {
    const fields = Object.entries(s.properties??{}).map(([k,v])=>{
      const doc = v.description ? `/** ${v.description.replaceAll('*/','* /').replaceAll('\n',' ')} */ ` : '';
      return `${doc}${literal(k)}${s.required?.includes(k)?'':'?'}: ${ts(v)};`;
    });
    if (s.additionalProperties && typeof s.additionalProperties==='object') fields.push(`[key: string]: ${ts(s.additionalProperties)}${Object.keys(s.properties??{}).some(k=>!s.required?.includes(k))?' | undefined':''};`);
    return fields.length ? `{ ${fields.join(' ')} }` : 'Record<string, unknown>';
  }
  return ({string:'string',integer:'number',number:'number',boolean:'boolean',null:'null'})[s.type]??'unknown';
}
const generated = '// Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.\n';
let tsTypes = generated+Object.entries(schemas).map(([k,s])=>`${s.description?`/** ${s.description.replaceAll('*/','* /').replaceAll('\n',' ')} */\n`:''}export type ${k} = ${ts(s)};`).join('\n')+'\n';
let tsResources = generated+`import type * as Models from './types.js';\nimport type {RequestOptions} from './transport.js';\nimport {Resource, JobsHelpers, MaterialsHelpers, FilesHelpers, CurriculaHelpers, pathId} from './helpers.js';\n`;
const groups = [...new Set(operations.map(o=>o.group))];
for (const group of groups) {
  const parent = ['jobs','materials','files','curricula'].includes(group) ? pascal(group)+'Helpers' : 'Resource';
  tsResources += `\nexport class ${pascal(group)} extends ${parent} {\n`;
  for (const o of operations.filter(o=>o.group===group)) {
    const args = o.paths.map(p=>`${p.name}: string`);
    if (o.bodyType) args.push(`input: Models.${o.bodyType}`);
    if (o.queryType) args.push(`query: Models.${o.queryType} = {}`);
    args.push('options: RequestOptions = {}');
    let path = o.path.replace(/\{(\w+)\}/g, (_,p)=>'${pathId('+p+')}');
    tsResources += `  /** ${o.summary.replaceAll('*/','* /')} (${o.method} ${o.path}). */\n  ${o.name}(${args.join(', ')}): Promise<${o.binary?'Uint8Array':o.responseType?'Models.'+o.responseType:'unknown'}> {\n    return this.transport.request(${literal(o.method)}, \`${path}\`, ${o.bodyType?'input':'undefined'}, ${o.queryType?'query':'undefined'}, options, ${literal(o.binary?'bytes':'json')});\n  }\n`;
  }
  tsResources+='}\n';
}
// Python TypedDicts preserve JSON property names. Methods/options use snake_case.
let pyNested = new Map();
const pyLiteral = v => v===null?'None':v===true?'True':v===false?'False':JSON.stringify(v);
function py(s, hint) {
  if (s.$ref) return `"${s.$ref.split('/').at(-1)}"`;
  if ('const' in s) return `Literal[${pyLiteral(s.const)}]`;
  if (s.enum) return `Literal[${s.enum.map(pyLiteral).join(', ')}]`;
  if (s.oneOf || s.anyOf) return `Union[${(s.oneOf??s.anyOf).map((v,i)=>py(v,hint+i)).join(', ')}]`;
  if (s.allOf?.length===1) return py(s.allOf[0],hint);
  if (s.allOf) throw new Error('Python intersection needs explicit handling: '+hint);
  if (Array.isArray(s.type)) return `Union[${s.type.map(type=>py({...s,type},hint)).join(', ')}]`;
  if (s.type==='array') return `list[${py(s.items??{},hint+'Item')}]`;
  if (s.type==='object' || s.properties) {
    if (s.properties) { if (!pyNested.has(hint)) pyNested.set(hint,s); return `"${hint}"`; }
    return `dict[str, ${typeof s.additionalProperties==='object'?py(s.additionalProperties,hint+'Value'):'Any'}]`;
  }
  return ({string:'str',integer:'int',number:'float',boolean:'bool',null:'None'})[s.type]??'Any';
}
let pyTypes = '# Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.\nfrom typing import Any, Literal, NotRequired, TypedDict, Union, TypeAlias\n\n';
function pyClass(k,s) {
  const fields = Object.entries(s.properties??{}).map(([name,v])=>`    ${name}: ${s.required?.includes(name)?py(v,k+pascal(name)):'NotRequired['+py(v,k+pascal(name))+']'}`);
  return `class ${k}(TypedDict):\n${fields.join('\n')||'    pass'}\n\n`;
}
for (const [k,s] of Object.entries(schemas)) pyTypes += (s.type==='object'||s.properties) && s.properties ? pyClass(k,s) : `${k}: TypeAlias = ${py(s,k)}\n\n`;
for (const [k,s] of pyNested) pyTypes += pyClass(k,s);
function pyResources(async) {
  let out = '# Generated from schema/openapi.json by scripts/generate.mjs. Do not edit.\nfrom __future__ import annotations\nfrom . import types as models\nfrom .transport import RequestOptions\nfrom .'+(async?'async_helpers':'helpers')+' import Resource, JobsHelpers, MaterialsHelpers, FilesHelpers, CurriculaHelpers, path_id\n\n';
  for (const group of groups) {
    const parent = ['jobs','materials','files','curricula'].includes(group) ? pascal(group)+'Helpers':'Resource';
    out+=`class ${pascal(group)}(${parent}):\n`;
    for (const o of operations.filter(o=>o.group===group)) {
      const args = ['self',...o.paths.map(p=>`${snake(p.name)}: str`)];
      if (o.bodyType) args.push(`input: models.${o.bodyType}`);
      args.push('*');
      if (o.queryType) args.push(`query: models.${o.queryType} | None = None`);
      args.push('options: RequestOptions | None = None');
      const path = o.path.replace(/\{(\w+)\}/g, (_,p)=>'{path_id('+snake(p)+')}');
      out+=`    ${async?'async ':''}def ${snake(o.name)}(${args.join(', ')}) -> ${o.binary?'bytes':o.responseType?'models.'+o.responseType:'object'}:\n        """${o.summary.replaceAll('"','')} (${o.method} ${o.path})."""\n        return ${async?'await ':''}self._transport.request(${literal(o.method)}, f${literal(path)}, ${o.bodyType?'input':'None'}, ${o.queryType?'query':'None'}, options, ${literal(o.binary?'bytes':'json')})\n\n`;
    }
  }
  return out;
}
const files = {'javascript/src/types.ts':tsTypes,'javascript/src/resources.ts':tsResources,'python/src/classive/types.py':pyTypes,
  'python/src/classive/resources.py':pyResources(false),'python/src/classive/async_resources.py':pyResources(true),
  'schema/operations.json':JSON.stringify(operations.map(({id,group,name,method,path,idempotency})=>({operationId:id,resource:group,javascript:name,python:snake(name),method,path,idempotency})),null,2)+'\n',
  'schema/source.json':JSON.stringify({url:'https://classive.app/openapi.json',sha256:createHash('sha256').update(source).digest('hex'),operations:operations.length},null,2)+'\n'};
let reference = '# SDK method reference\n\nGenerated from the public OpenAPI snapshot. Request and response types are exported by `@classive/sdk` and `classive.types`. JSON bodies keep their wire field names; Python methods and SDK options use snake_case.\n\nFor workflows, pagination, polling and downloads, see [workflow examples](workflows.md) and the [SDK guide](../README.md). Query-bearing methods take a query object in JavaScript and `query={...}` in Python; request controls go in the final options object / `options={...}`.\n';
for(const group of groups) {
  reference += `\n## ${pascal(group)}\n\n| JavaScript | Python | REST reference | Request body | Response |\n| --- | --- | --- | --- | --- |\n`;
  for(const o of operations.filter(o=>o.group===group)) {
    const tag=spec.paths[o.path][o.method.toLowerCase()].tags?.[0]?.toLowerCase();
    const link=`https://classive.app/api#tag/${tag}/${o.id}`;
    reference += `| \`client.${group}.${o.name}\` | \`client.${group}.${snake(o.name)}\` | [${o.method} ${o.path}](${link}) | ${o.bodyType?'`'+o.bodyType+'`':'—'} | ${o.binary?'bytes':'`'+o.responseType+'`'} |\n`;
  }
}
files['docs/reference.md']=reference;
for (const [path, content] of Object.entries(files)) {
  const url = new URL('../'+path,import.meta.url);
  if (process.argv.includes('--check')) { if (await readFile(url,'utf8')!==content) throw new Error('Generated contract drift: '+path); }
  else await writeFile(url,content);
}
console.log(`${process.argv.includes('--check')?'Checked':'Generated'} ${operations.length} operations for both SDKs.`);
