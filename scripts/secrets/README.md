# Local Secret Helpers

Use `save-dev-secrets.ps1` if you want a local encrypted secret file instead of a plain `.env.dev.local`.

Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\secrets\save-dev-secrets.ps1
```

The generated `.secrets/apso.dev.secrets.json.dpapi` file is ignored by Git.

This is for local development only. Production deployments should use the deployment platform's secret injection mechanism.

To generate `.env.dev.local` from the encrypted local store:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\secrets\materialize-dev-env.ps1
```

Then run backend connector checks:

```powershell
$env:APSO_ENV = "dev"
$env:PYTHONPATH = "apps/backend/src"
python apps/backend/scripts/check_connectors.py
python apps/backend/scripts/check_database.py
```
