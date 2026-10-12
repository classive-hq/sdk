import {Classive,type CreateLesson,type Job,type ListMaterialsQuery} from '@classive/sdk';
const client=new Classive({apiKey:'ck_live_example'});
const input: CreateLesson={type:'lesson',prompt:'Teach fractions.',audience:{band:'primary'},outputs:['notes']};
async function lesson(): Promise<Job> {
  const quote=await client.jobs.quote(input);
  const job=await client.jobs.create({...input,quoteId:quote.id},{idempotencyKey:'my-request-1'});
  return client.jobs.wait(job.id);
}
const query: ListMaterialsQuery={search:'algebra',status:'ready',limit:25};
void query;void lesson;
// @ts-expect-error Invalid audience bands must be caught in the consumer's IDE.
const invalid: CreateLesson={type:'lesson',prompt:'Teach fractions.',audience:{band:'college'}};
void invalid;
