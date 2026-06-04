from sqlalchemy import select
from sqlalchemy.orm import Session

from apso_backend.db.models import AiFinding, AiRun
from apso_backend.schemas.findings import FindingCreate


class AiRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        tenant_id: str,
        task_name: str,
        provider: str,
        model_name: str,
        prompt_version: str,
        status: str,
        latency_ms: int | None = None,
        validation_result: dict | None = None,
    ) -> AiRun:
        run = AiRun(
            tenant_id=tenant_id,
            task_name=task_name,
            provider=provider,
            model_name=model_name,
            prompt_version=prompt_version,
            status=status,
            latency_ms=latency_ms,
            validation_result=validation_result or {},
        )
        self.session.add(run)
        self.session.flush()
        return run


class FindingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, tenant_id: str, payload: FindingCreate) -> AiFinding:
        finding = AiFinding(
            tenant_id=tenant_id,
            ai_run_id=payload.ai_run_id,
            project_id=payload.project_id,
            finding_type=payload.finding_type,
            severity=payload.severity,
            status="open",
            title=payload.title,
            description=payload.description,
            evidence=payload.evidence,
            confidence=payload.confidence,
        )
        self.session.add(finding)
        self.session.commit()
        self.session.refresh(finding)
        return finding

    def bulk_create(self, *, tenant_id: str, payloads: list[FindingCreate]) -> list[AiFinding]:
        findings = [
            AiFinding(
                tenant_id=tenant_id,
                ai_run_id=payload.ai_run_id,
                project_id=payload.project_id,
                finding_type=payload.finding_type,
                severity=payload.severity,
                status="open",
                title=payload.title,
                description=payload.description,
                evidence=payload.evidence,
                confidence=payload.confidence,
            )
            for payload in payloads
        ]
        self.session.add_all(findings)
        self.session.commit()
        for finding in findings:
            self.session.refresh(finding)
        return findings

    def list_for_tenant(self, tenant_id: str, status: str | None = None, limit: int = 100) -> list[AiFinding]:
        query = select(AiFinding).where(AiFinding.tenant_id == tenant_id)
        if status:
            query = query.where(AiFinding.status == status)
        return list(self.session.scalars(query.order_by(AiFinding.created_at.desc()).limit(limit)))

    def update_status(self, *, tenant_id: str, finding_id: str, status: str) -> AiFinding | None:
        finding = self.session.scalar(
            select(AiFinding).where(AiFinding.tenant_id == tenant_id, AiFinding.id == finding_id)
        )
        if finding is None:
            return None
        finding.status = status
        self.session.commit()
        self.session.refresh(finding)
        return finding

