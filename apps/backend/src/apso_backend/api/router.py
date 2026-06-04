from fastapi import APIRouter

from apso_backend.api.routes import ai, auth, config, core, dashboard, engines, findings, health, integrations, jobs, ops, quality, reports

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(engines.router, prefix="/engines", tags=["engines"])
api_router.include_router(core.router, prefix="/core", tags=["core"])
api_router.include_router(findings.router, prefix="/findings", tags=["findings"])
api_router.include_router(quality.router, prefix="/quality", tags=["quality"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(ops.router, prefix="/ops", tags=["ops"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
