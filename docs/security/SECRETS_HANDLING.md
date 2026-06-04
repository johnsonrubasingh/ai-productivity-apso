# APSO Secrets Handling

Live credentials have been provided for Jira, Bitbucket, and Supabase. Treat them as sensitive.

## Rules

- Do not commit real secrets.
- Do not paste secrets into source files, Markdown documents, screenshots, pull requests, issue comments, or logs.
- Use `.env.dev.local` for local development.
- `.env.dev.local` is ignored by `.gitignore`.
- Use production secret storage for `prod` deployments.

## Recommended Immediate Action

Because live credentials were shared in chat, rotate them before exposing the application beyond the local development machine.

Rotate:

- Jira API token
- Bitbucket API token
- Supabase service role key, if possible
- Supabase database password
- JWT secret only with proper Supabase migration planning

## Local Development

Create `.env.dev.local` from `.env.example` and fill values locally.

Never commit `.env.dev.local`.

## Production

Production secrets should be injected through the deployment secret mechanism, not stored in Git.

