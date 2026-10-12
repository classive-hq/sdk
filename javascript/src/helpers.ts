import type {Job, Material, MaterialUpload, Curriculum, DownloadPackageQuery, GetPackageFileQuery} from './types.js';
import {JobCancelledError, JobFailedError, MaterialFailedError, TimeoutError, ValidationError} from './errors.js';
import {Transport, sleep, positive, type RequestOptions} from './transport.js';
export function pathId(id: string): string {
  if (typeof id!=='string'||!/^[a-zA-Z0-9_-]+$/.test(id)) throw new ValidationError('Pass an API id, not a URL or path.');
  return encodeURIComponent(id);
}
export class Resource {constructor(protected readonly transport: Transport) {}}
export interface WaitOptions extends RequestOptions {
  /** Overall polling deadline; default 30 minutes. Expiring it never cancels server work. */
  waitTimeoutMs?: number;
  pollIntervalMs?: number;
}
export class JobsHelpers extends Resource {
  /** Wait for delivery. A failed or cancelled job raises an error carrying the complete job. */
  async wait(id: string,options: WaitOptions = {}): Promise<Job> {
    return waitFor(this.transport,`/v1/jobs/${pathId(id)}`,options,job=>{
      if(job.status==='completed') return true;
      if(job.status==='failed') throw new JobFailedError(job);
      if(job.status==='cancelled') throw new JobCancelledError(job);
      return false;
    });
  }
  /** Iterate newest-first through the server's cursor-based job list. */
  async *iterate(query: {limit?: number; starting_after?: string} = {},options: RequestOptions = {}): AsyncGenerator<Job> {
    let cursor=query.starting_after;
    while(true) {
      const page=await this.transport.request<import('./types.js').JobList>('GET','/v1/jobs',undefined,{...query,starting_after:cursor},options);
      for(const job of page.data) yield job;
      if(!page.hasMore) return;
      const next=page.data.at(-1)?.id;
      if(!next||next===cursor) throw new ValidationError('The job list returned an invalid pagination cursor.');
      cursor=next;
    }
  }
  downloadPackageTo(id: string,destination: string,query: DownloadPackageQuery = {},options: RequestOptions = {},overwrite = false): Promise<void> {
    return this.transport.downloadTo(`/v1/jobs/${pathId(id)}/download`,destination,query,options,overwrite);
  }
  packageFileTo(id: string,fileId: string,destination: string,query: GetPackageFileQuery = {},options: RequestOptions = {},overwrite = false): Promise<void> {
    return this.transport.downloadTo(`/v1/jobs/${pathId(id)}/package/files/${pathId(fileId)}`,destination,query,options,overwrite);
  }
}
export class FilesHelpers extends Resource {
  /** Stream a file by id. No bearer credential is ever sent to a URL from generated content. */
  downloadTo(id: string,destination: string,options: RequestOptions = {},overwrite = false): Promise<void> {
    return this.transport.downloadTo(`/v1/files/${pathId(id)}`,destination,undefined,options,overwrite);
  }
  async json<T = unknown>(id: string,options: RequestOptions = {}): Promise<T> {
    return this.transport.request('GET',`/v1/files/${pathId(id)}`,undefined,undefined,options);
  }
}
export type UploadMetadata = Omit<MaterialUpload,'filename'|'contentType'|'base64'>;
export class MaterialsHelpers extends Resource {
  /** Node.js: upload a local file, retaining its filename and MIME type. Maximum 25 MiB. */
  async upload(filePath: string,metadata: UploadMetadata = {},options: RequestOptions = {},contentType?: string): Promise<Material> {
    const fs=await import('node:fs/promises'),path=await import('node:path');
    if ((await fs.stat(filePath)).size>25*1024*1024) throw new ValidationError('Materials must be at most 25 MiB.');
    const data=await fs.readFile(filePath),ext=path.extname(filePath).toLowerCase();
    const mime=contentType??({'.pdf':'application/pdf','.txt':'text/plain','.md':'text/markdown','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document'} as Record<string,string>)[ext];
    if(!mime) throw new ValidationError('Pass contentType for this file extension.');
    return this.transport.request('POST','/v1/materials',{...metadata,filename:path.basename(filePath),contentType:mime,base64:data.toString('base64')},undefined,options);
  }
  /** Browser/server: upload bytes using the public JSON upload contract. */
  uploadBytes(data: Uint8Array,filename: string,contentType: string,metadata: UploadMetadata = {},options: RequestOptions = {}): Promise<Material> {
    if(data.byteLength>25*1024*1024) throw new ValidationError('Materials must be at most 25 MiB.');
    let base64: string;
    if(typeof Buffer!=='undefined') base64=Buffer.from(data).toString('base64');
    else {let text='';for(const byte of data) text+=String.fromCharCode(byte);base64=btoa(text);}
    return this.transport.request('POST','/v1/materials',{...metadata,filename,contentType,base64},undefined,options);
  }
  async wait(id: string,options: WaitOptions = {}): Promise<Material> {
    return waitFor(this.transport,`/v1/materials/${pathId(id)}`,options,material=>{
      if(material.status==='ready') return true;
      if(material.status==='failed'||material.status==='deleted') throw new MaterialFailedError(material);
      return false;
    });
  }
  async *iterate(query: import('./types.js').ListMaterialsQuery = {},options: RequestOptions = {}): AsyncGenerator<Material> {
    let cursor=query.starting_after;
    while(true) {
      const page=await this.transport.request<import('./types.js').MaterialList>('GET','/v1/materials',undefined,{...query,starting_after:cursor},options);
      for(const material of page.data) yield material;
      if(!page.hasMore) return;
      const next=page.nextCursor??page.data.at(-1)?.id;
      if(!next||next===cursor) throw new ValidationError('The material list returned an invalid pagination cursor.');
      cursor=next;
    }
  }
}
export class CurriculaHelpers extends Resource {
  /** Wait for planning, without approving or starting a course. */
  async wait(id: string,options: WaitOptions = {}): Promise<Curriculum> {
    return waitFor(this.transport,`/v1/curricula/${pathId(id)}`,options,curriculum=>{
      if(curriculum.status==='failed') throw new ValidationError('Curriculum planning failed. Inspect curricula.get(id) before retrying.',0,'curriculum_failed',curriculum);
      return curriculum.status==='draft'||curriculum.status==='approved';
    });
  }
}
async function waitFor<T>(transport: Transport,path: string,options: WaitOptions,complete: (value: T)=>boolean): Promise<T> {
  const deadline=Date.now()+positive(options.waitTimeoutMs??30*60_000,'waitTimeoutMs');
  const interval=positive(options.pollIntervalMs??2000,'pollIntervalMs');
  while(true) {
    const remaining=deadline-Date.now();
    if(remaining<=0) throw new TimeoutError('Polling timed out. The work continues on Classive; fetch it later or cancel explicitly.',0,'wait_timeout');
    const value=await transport.request<T>('GET',path,undefined,undefined,{...options,timeoutMs:Math.min(options.timeoutMs??transport.timeoutMs,remaining)});
    if(complete(value)) return value;
    await sleep(Math.min(interval,Math.max(0,deadline-Date.now())),options.signal);
  }
}
