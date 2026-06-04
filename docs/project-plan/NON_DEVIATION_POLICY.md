# APSO Non-Deviation Policy

This document is mandatory for APSO development.

## Locked Scope

APSO development must follow the staged project plan and locked freeware stack. The MVP scope is read-only extraction, analysis, evidence generation, dashboards, and reports.

## Environment Lock

Only two environments are allowed:

- `dev`
- `prod`

No `stage`, `uat`, `qa`, `local`, or alternate runtime environment should be added unless this policy is formally revised.

## Integration Lock

Jira, Bitbucket, and AWS integrations must be configuration-driven.

For MVP:

- Jira is read-only.
- Bitbucket is read-only.
- AWS is mocked until AWS credentials are supplied later.
- No write-back to Jira or Bitbucket is allowed.
- No live AWS write or deployment operation is allowed.

## AI Lock

All AI calls must go through the APSO AI Gateway.

Development defaults:

- LLM: `qwen2.5-coder:14b`
- Embeddings: `qwen3-embedding:4b`
- Runtime: Ollama

No product module may call Ollama, OpenAI, Claude, Gemini, Bedrock, or any provider directly.

## Tooling Lock

No alternate framework, paid SaaS, paid AI API, paid database, managed vector database, managed object store, alternate workflow engine, or alternate observability platform may be introduced without an approved document update.

## Secret Handling

Secrets must never be committed to source control.

Do not commit:

- Jira tokens
- Bitbucket tokens
- Supabase service role keys
- Supabase database passwords
- JWT secrets
- AWS access keys
- API tokens
- connection strings containing passwords

Use ignored local `.env.*` files or the approved encrypted local secret store only.

## Change Control

Any deviation requires:

1. Written reason.
2. Impact assessment.
3. Approval.
4. Update to the staged project plan.
5. Update to config templates if applicable.

