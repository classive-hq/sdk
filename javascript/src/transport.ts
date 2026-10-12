import {AbortError, NetworkError, ProtocolError, TimeoutError, ValidationError, apiError} from './errors.js';

export interface RequestOptions {
  /** Use a stable key for an explicitly repeated job submission. Mutations are never automatically retried. */
  idempotencyKey?: string;
  /** A byte range for file requests, for example bytes=0-1023. */
  range?: string;
  timeoutMs?: number;
  signal?: AbortSignal;
}
export interface ClientOptions {
  /** Defaults to CLASSIVE_API_KEY in Node.js. Keep it on your server. */
  apiKey?: string;
  baseUrl?: string;
  /** Total time per request, including read retries and response body consumption. Default 30 seconds. */
  timeoutMs?: number;
  /** Additional attempts for GET only. Default 2; set 0 to disable. */
  maxRetries?: number;
  fetch?: typeof globalThis.fetch;
}
export function positive(value: number, label: string): number {
  if (!Number.isFinite(value) || value <= 0) throw new ValidationError(`${label} must be a positive finite number.`);
  return value;
}
export function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve,reject)=>{
    if (signal?.aborted) return reject(new AbortError('The request was aborted.',0,'aborted'));
    const abort = () => {clearTimeout(timer); reject(new AbortError('The request was aborted.',0,'aborted'));};
    const timer = setTimeout(()=>{signal?.removeEventListener('abort',abort);resolve();},ms);
    signal?.addEventListener('abort',abort,{once:true});
  });
}
export class Transport {
  readonly baseUrl: string;
  private readonly key: string;
  private readonly fetcher: typeof globalThis.fetch;
  readonly timeoutMs: number;
  readonly maxRetries: number;
  constructor(options: ClientOptions = {}) {
    const key = options.apiKey ?? (typeof process==='undefined' ? undefined : process.env.CLASSIVE_API_KEY);
    if (!key?.trim()) throw new ValidationError('Set CLASSIVE_API_KEY or pass apiKey from your Classive dashboard.');
    if (key.startsWith('cmcp_')) throw new ValidationError('Use a REST API key (ck_live_…), not an MCP key.');
    if (/[\r\n]/.test(key)) throw new ValidationError('The API key contains an invalid newline.');
    const url = new URL(options.baseUrl ?? 'https://api.classive.app');
    if (url.username || url.password || url.search || url.hash || url.pathname!=='/' ||
      !(url.protocol==='https:' || (url.protocol==='http:' && ['localhost','127.0.0.1','[::1]'].includes(url.hostname))))
      throw new ValidationError('baseUrl must be an HTTPS origin, or localhost HTTP for testing.');
    this.baseUrl=url.origin;this.key=key.trim();this.fetcher=options.fetch ?? globalThis.fetch;
    this.timeoutMs=positive(options.timeoutMs??30_000,'timeoutMs');this.maxRetries=options.maxRetries??2;
    if (!Number.isInteger(this.maxRetries)||this.maxRetries<0||this.maxRetries>10) throw new ValidationError('maxRetries must be an integer from 0 to 10.');
  }
  request<T>(method: string, path: string, input?: unknown, query?: object, options: RequestOptions = {}, mode: 'json'|'bytes' = 'json'): Promise<T> {
    return this.perform(method,path,input,query,options,async response=>{
      if (mode==='bytes') return new Uint8Array(await response.arrayBuffer()) as T;
      if (response.status===204) return undefined as T;
      try { return await response.json() as T; } catch {throw new ProtocolError('Classive returned an invalid JSON response.',response.status,'invalid_response');}
    });
  }
  /** Stream to a temporary file and publish the complete file only after a successful download. Node.js only. */
  async downloadTo(path: string, destination: string, query?: object, options: RequestOptions = {}, overwrite = false): Promise<void> {
    const fs=await import('node:fs/promises'),p=await import('node:path'),crypto=await import('node:crypto');
    const temporary=p.join(p.dirname(destination),`.classive-${crypto.randomUUID()}.part`);
    try {
      await this.perform('GET',path,undefined,query,options,async response=>{
        const file=await fs.open(temporary,'wx');
        try {
          if (!response.body) throw new ProtocolError('The download response has no body.',response.status,'invalid_response');
          const reader=response.body.getReader();
          try {while(true) {const chunk=await reader.read();if(chunk.done) break;await file.writeFile(chunk.value);}} finally {reader.releaseLock();}
        } finally {await file.close();}
      });
      if (overwrite) await fs.rename(temporary,destination);
      else {await fs.link(temporary,destination);await fs.unlink(temporary);}
    } finally {await fs.unlink(temporary).catch(()=>{});}
  }
  private async perform<T>(method: string,path: string,input: unknown,query: object|undefined,options: RequestOptions,read: (response: Response)=>Promise<T>): Promise<T> {
    if (!path.startsWith('/')||path.startsWith('//')||path.split('/').some(s=>s==='.'||s==='..')) throw new ValidationError('Use an SDK resource method with an API id. Arbitrary download URLs are not accepted.');
    const url=new URL(path,this.baseUrl);
    for (const [k,v] of Object.entries(query??{})) if(v!==undefined&&v!==null) url.searchParams.set(k,String(v));
    const timeout=positive(options.timeoutMs??this.timeoutMs,'timeoutMs'),deadline=Date.now()+timeout;
    const controller=new AbortController();const abort=()=>controller.abort();
    if (options.signal?.aborted) throw new AbortError('The request was aborted.',0,'aborted');
    const headers: Record<string,string>={Authorization:`Bearer ${this.key}`,Accept:'application/json, */*','X-Classive-SDK':'javascript/0.1.1'};
    if(input!==undefined) headers['Content-Type']='application/json';
    if (options.idempotencyKey!==undefined) {
      if (!options.idempotencyKey.trim()||options.idempotencyKey.length>200||/[\r\n]/.test(options.idempotencyKey)) throw new ValidationError('idempotencyKey must contain 1–200 characters without newlines.');
      headers['Idempotency-Key']=options.idempotencyKey;
    }
    if(options.range) headers.Range=options.range;
    options.signal?.addEventListener('abort',abort,{once:true});
    const timer=setTimeout(abort,timeout);
    try {
      for(let attempt=0;;attempt++) {
        let response: Response;
        try {response=await this.fetcher(url,{method,headers,body:input===undefined?undefined:JSON.stringify(input),signal:controller.signal,redirect:'manual'});}
        catch {
          if(controller.signal.aborted) throw options.signal?.aborted ? new AbortError('The request was aborted.',0,'aborted') : new TimeoutError('The Classive request timed out. A mutation may still have been accepted; check its quote/job before repeating.',0,'timeout');
          if (method==='GET'&&attempt<this.maxRetries) {await sleep(Math.min(250*2**attempt,2000),controller.signal);continue;}
          throw new NetworkError('Could not reach Classive. Mutations are not automatically repeated; check their outcome before resubmitting.',0,'network_error');
        }
        if(response.status>=300&&response.status<400) {await response.body?.cancel();throw new ProtocolError('Classive returned a redirect. It was refused to keep your API key on the configured origin.',response.status,'redirect_refused');}
        if (method==='GET'&&attempt<this.maxRetries&&[429,500,502,503,504].includes(response.status)) {
          const retry=response.headers.get('retry-after'),seconds=retry===null?NaN:Number(retry);
          const delay=retry===null?Math.min(250*2**attempt,2000):Number.isFinite(seconds)?Math.max(0,seconds*1000):Math.max(0,Date.parse(retry)-Date.now());
          if(Number.isFinite(delay)&&delay<deadline-Date.now()) {
            await response.body?.cancel();await sleep(delay,controller.signal);continue;
          }
        }
        if(!response.ok) {let body: unknown;try {body=await response.json();} catch {body=undefined;}throw apiError(response.status,body,response.headers.get('x-request-id')??undefined);}
        return await read(response);
      }
    } catch (e) {
      if(controller.signal.aborted) throw options.signal?.aborted?new AbortError('The request was aborted.',0,'aborted'):new TimeoutError('The Classive request timed out. A mutation may still have been accepted; check its outcome before repeating.',0,'timeout');
      throw e;
    } finally {clearTimeout(timer);options.signal?.removeEventListener('abort',abort);}
  }
}
