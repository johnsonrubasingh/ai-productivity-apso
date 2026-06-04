# APSO Project Plan Folder

This folder contains the controlling project plan and scope lock for APSO development.

Developers must follow these files:

- `APSO_Locked_Freeware_Implementation_Plan.docx`
- `APSO_Technical_Architecture_and_Tech_Stack_Guide.docx`
- `APSO_Business_Functionality_and_Value_Guide.docx`
- `APSO_PROJECT_BASELINE.md`
- `NON_DEVIATION_POLICY.md`
- `../../config/environments.dev.yaml`
- `../../config/environments.prod.yaml`
- `../../docs/security/SECRETS_HANDLING.md`

## Document Usage

- Use `APSO_Technical_Architecture_and_Tech_Stack_Guide.docx` for developers, tech leads, architects, DevOps, and security reviewers.
- Use `APSO_Business_Functionality_and_Value_Guide.docx` for business stakeholders, sponsors, delivery leaders, and customer-facing discussions.
- Use `APSO_Locked_Freeware_Implementation_Plan.docx` as the scope lock and delivery control document.

## Mandatory Rules

- Only `dev` and `prod` environments are allowed.
- Jira and Bitbucket are read-only for MVP.
- AWS remains mocked until AWS credentials are supplied.
- All secrets stay outside source control.
- All AI calls go through APSO AI Gateway.
- Development uses Ollama with Qwen models.
- No paid SaaS or paid AI dependency may be added to MVP.
