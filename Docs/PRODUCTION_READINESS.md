# Production readiness checklist

The current version is suitable for a local beta or prototype deployment, but it is not yet ready for a multi-user production launch.

## 1. Supabase integration

- Create a Supabase project.
- Apply and test `supabase_schema.sql`.
- Add Supabase client configuration.
- Replace localStorage reads and writes with database operations.
- Implement migrations for existing local data.
- Add connection retries, offline queueing, and conflict handling.

## 2. Authentication and permissions

- Add signup, login, logout, password reset, and optional social login.
- Create profiles automatically after signup.
- Implement notebook invitations.
- Enforce owner, editor, and viewer behavior in the UI and database.
- Review and test RLS policies, especially transaction-share writes and viewer restrictions.

## 3. Backend deployment

- Deploy the Python server behind HTTPS.
- Keep AI parsing and privileged operations behind the deployed backend.
- Store secrets in managed environment variables.
- Add rate limiting, request validation, logging, and error monitoring.
- Configure CORS and allowed origins.

## 4. Frontend deployment

- Serve the app from a production host such as Vercel, Netlify, or Cloudflare Pages.
- Configure the production Supabase URL and public anon key.
- Add a real build and deployment pipeline.
- Configure a custom domain and HTTPS.

## 5. Data migration and backup

- Build a one-time localStorage-to-Supabase migration flow.
- Make migration resumable and idempotent.
- Provide downloadable backups before migration.
- Test duplicate imports and interrupted migrations.

## 6. Testing

Add automated tests for:

- Notebook isolation.
- Existing-ledger migration.
- Expense and transfer balance signs.
- Multiple simultaneous notebooks.
- Reusing the same person name across notebooks.
- Archive, restore, and delete safeguards.
- Import and export.
- RLS access between users.
- Offline edits and reconnect behavior.

## 7. Production operations

- Configure database backups and test restoration.
- Maintain Supabase migration history.
- Add error monitoring.
- Add audit logging for destructive actions.
- Publish privacy and data-retention policies.
- Support account deletion and user data export.
- Performance-test larger notebooks.

## Recommended release order

1. Finish Supabase Auth and database CRUD.
2. Implement local-to-Supabase migration.
3. Deploy the Python AI proxy.
4. Add automated accounting and RLS tests.
5. Deploy the frontend.
6. Run a private beta before public release.

