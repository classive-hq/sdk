/** Verify the Classive-Signature header against the untouched request body. */
export async function verifyWebhook(rawBody: string | Uint8Array,header: string | null | undefined,secret: string,
  options: {toleranceSeconds?: number; now?: number} = {}): Promise<boolean> {
  if(!secret||!header) return false;
  const match=/^t=(\d+),v1=([0-9a-f]{64})$/.exec(header.trim());
  if(!match) return false;
  const timestamp=Number(match[1]),now=options.now??Date.now()/1000,tolerance=options.toleranceSeconds??300;
  if(!Number.isSafeInteger(timestamp)||!Number.isFinite(now)||!Number.isFinite(tolerance)||tolerance<0||Math.abs(now-timestamp)>tolerance) return false;
  const bytes=typeof rawBody==='string'?new TextEncoder().encode(rawBody):rawBody;
  const prefix=new TextEncoder().encode(`${timestamp}.`),signed=new Uint8Array(prefix.length+bytes.length);
  signed.set(prefix);signed.set(bytes,prefix.length);
  const key=await globalThis.crypto.subtle.importKey('raw',new TextEncoder().encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);
  const mac=new Uint8Array(await globalThis.crypto.subtle.sign('HMAC',key,signed));
  const expected=match[2]!;let difference=0;
  for(let i=0;i<mac.length;i++) difference|=mac[i]!^parseInt(expected.slice(i*2,i*2+2),16);
  return difference===0;
}
