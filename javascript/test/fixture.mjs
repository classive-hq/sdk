import {createServer} from 'node:http';
export async function fixture(handler) {
  const calls=[];
  const server=createServer(async(req,res)=>{
    const buffers=[];for await(const chunk of req) buffers.push(chunk);
    const bytes=Buffer.concat(buffers),body=bytes.length?JSON.parse(bytes.toString()):undefined;
    const call={method:req.method,url:new URL(req.url,'http://fixture'),headers:req.headers,body};calls.push(call);
    try {await handler(call,res,calls);} catch(e) {res.writeHead(500,{'content-type':'application/json'});res.end(JSON.stringify({error:{code:'fixture_error',message:e.message}}));}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  return {calls,baseUrl:`http://127.0.0.1:${server.address().port}`,close:()=>new Promise(resolve=>{server.closeAllConnections();server.close(resolve);})};
}
export function json(res,data,status=200,headers={}) {res.writeHead(status,{'content-type':'application/json',...headers});res.end(JSON.stringify(data));}
export const input={type:'lesson',prompt:'Teach adding fractions with unlike denominators.',audience:{band:'primary',grade:'Year 5'},outputs:['notes']};
export const job=(status='completed')=>({id:'job_'+'a'.repeat(20),object:'job',type:'lesson',status,input,
  createdAt:'2026-10-12T00:00:00Z',startedAt:null,completedAt:null,estimatedCompletionAt:null,
  credits:{reserved:0,charged:10},results:{lessons:[{order:1,title:'Fractions',notes:{markdown:null,pdf:null,json:{id:'file_'+'a'.repeat(20),url:'https://api.classive.app/v1/files/file_'+'a'.repeat(20),contentType:'application/json',bytes:21}}}]}});
