import {Transport,type ClientOptions} from './transport.js';
import {Jobs,Materials,Files,Voices,Preferences,Prices,Keys,Webhooks,Billing,Quotes,Curricula,Organisation} from './resources.js';
/** Classive Results API client. Keep REST API keys in your application's server environment. */
export class Classive {
  readonly jobs: Jobs; readonly materials: Materials; readonly files: Files;
  readonly voices: Voices; readonly preferences: Preferences; readonly prices: Prices;
  readonly keys: Keys; readonly webhooks: Webhooks; readonly billing: Billing;
  readonly quotes: Quotes; readonly curricula: Curricula; readonly organisation: Organisation;
  constructor(options: ClientOptions = {}) {
    const transport=new Transport(options);
    this.jobs=new Jobs(transport);this.materials=new Materials(transport);this.files=new Files(transport);
    this.voices=new Voices(transport);this.preferences=new Preferences(transport);this.prices=new Prices(transport);
    this.keys=new Keys(transport);this.webhooks=new Webhooks(transport);this.billing=new Billing(transport);
    this.quotes=new Quotes(transport);this.curricula=new Curricula(transport);this.organisation=new Organisation(transport);
  }
}
export default Classive;
export * from './errors.js';
export * from './webhooks.js';
export type {ClientOptions,RequestOptions} from './transport.js';
export type {WaitOptions,UploadMetadata} from './helpers.js';
export type * from './types.js';
