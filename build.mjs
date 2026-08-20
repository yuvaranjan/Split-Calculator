import { writeFile } from 'node:fs/promises';

const config = `window.APP_CONFIG = ${JSON.stringify({
  apiBaseUrl: process.env.PUBLIC_API_BASE_URL || '',
  supabaseUrl: process.env.SUPABASE_URL || '',
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY || ''
}, null, 2)};\n`;
await writeFile('config.js', config, 'utf8');
console.log('Generated frontend runtime configuration.');
