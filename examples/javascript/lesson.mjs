import {Classive} from '@classive/sdk';
import {pathToFileURL} from 'node:url';

/** Run the quote-only preview by default. `--submit` explicitly starts paid generation. */
export async function runLesson(client,submit=false) {
  const input={type:'lesson',prompt:'Teach adding fractions with unlike denominators.',audience:{band:'primary',grade:'Year 5'},outputs:['notes','quiz']};
  const quote=await client.jobs.quote(input);
  console.log('Quoted credits:',quote.credits);
  if(!submit) return quote;
  const job=await client.jobs.create({...input,quoteId:quote.id},{idempotencyKey:`fractions-${quote.id}`});
  const completed=await client.jobs.wait(job.id);
  console.log('Delivered job:',completed.id);
  return completed;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  const client=new Classive({baseUrl:process.env.CLASSIVE_BASE_URL});
  await runLesson(client,process.argv.includes('--submit'));
}
