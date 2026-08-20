# Implementation progress

## Current status

- [x] Read `PROJECT_REPORT.md` and identified the existing localStorage model and entry points.
- [x] Add notebook-scoped local model and safe migration from the single ledger.
- [x] Add notebook switching and notebook management UI.
- [x] Scope people, transactions, filtering, summaries, exports, and AI input to the active notebook.
- [x] Add JSON backup/import and Supabase schema/RLS foundation in `supabase_schema.sql`.
- [x] Run `node --check app.js` and `python -m py_compile server.py`.
- [x] Inspect browser smoke harness; installed `jsdom` did not complete within the timeout, so no automated DOM assertion is claimed.

## Notes for collaborating agents

- The legacy storage key is `splitwise-local-ledger-v1`.
- Existing accounting rules and transfer signs are documented in `PROJECT_REPORT.md` and must remain unchanged.
- Keep `.env` private; never expose or log its contents.

## Implementation notes

- Existing `splitwise-local-ledger-v1` data is migrated on startup into a single `Home` notebook.
- Notebook members use stable local IDs; `person`/`payer` name snapshots remain on transactions for historical readability.
- The Supabase SQL is a production schema/RLS foundation; Auth, hosted migration execution, and sync transport still require Supabase project credentials and deployment configuration.
- Production deployment requirements are tracked in `PRODUCTION_READINESS.md`.
- Vercel frontend and Render backend selected.
- [x] Added Render service definition, health endpoint, CORS allowlist, request-size limit, and safer production error responses.
- [x] Updated the Python server to bind to Render's public `0.0.0.0` interface while retaining the configurable local port.
- [x] Added Vercel security headers and frontend runtime configuration template.
- [x] Added Vercel build-time generation of `config.js` from public environment variables.
- [ ] Wire Supabase Auth and hosted database sync using the created project's URL and public anon key.
- [ ] Deploy and run private-beta checks.
