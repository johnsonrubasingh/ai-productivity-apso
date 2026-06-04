from datetime import UTC, datetime

from sqlalchemy.orm import Session

from apso_backend.core.request_id import get_request_id
from apso_backend.db.models import AuditEvent
from apso_backend.security.context import RequestContext


class AuditService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        *,
        context: RequestContext,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        metadata: dict | None = None,
        commit: bool = False,
    ) -> AuditEvent:
        event = AuditEvent(
            tenant_id=context.tenant_id,
            actor_user_id=context.user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            created_at=datetime.now(UTC),
            metadata_json={
                **(metadata or {}),
                "role": context.role,
                "request_id": get_request_id(),
            },
        )
        self.session.add(event)
        if commit:
            self.session.commit()
            self.session.refresh(event)
        return event

