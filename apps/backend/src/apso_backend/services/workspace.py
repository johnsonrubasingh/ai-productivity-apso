from pathlib import Path

from apso_backend.core.config import get_settings


class WorkspaceService:
    def __init__(self):
        settings = get_settings()
        self.repository_root = Path(settings.workspace.repository_root).resolve()
        self.artifact_root = Path(settings.workspace.artifact_root).resolve()

    def ensure_roots(self) -> None:
        self.repository_root.mkdir(parents=True, exist_ok=True)
        self.artifact_root.mkdir(parents=True, exist_ok=True)

    def repository_path(self, provider: str, workspace: str, slug: str) -> Path:
        safe_provider = self._safe_segment(provider)
        safe_workspace = self._safe_segment(workspace)
        safe_slug = self._safe_segment(slug)
        path = (self.repository_root / safe_provider / safe_workspace / safe_slug).resolve()
        self._assert_inside(path, self.repository_root)
        return path

    def artifact_path(self, tenant_id: str, category: str) -> Path:
        path = (self.artifact_root / self._safe_segment(tenant_id) / self._safe_segment(category)).resolve()
        self._assert_inside(path, self.artifact_root)
        return path

    @staticmethod
    def _safe_segment(value: str) -> str:
        cleaned = "".join(ch for ch in value if ch.isalnum() or ch in {"-", "_", "."}).strip(".")
        if not cleaned:
            raise ValueError("Path segment cannot be empty")
        return cleaned

    @staticmethod
    def _assert_inside(path: Path, root: Path) -> None:
        path.relative_to(root)
