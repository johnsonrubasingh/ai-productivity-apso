from typing import Any

from apso_backend.core.config import JiraSettings
from apso_backend.schemas.jira import JiraIssueSummary


def _display_name(value: dict[str, Any] | None) -> str | None:
    if not value:
        return None
    return value.get("displayName") or value.get("emailAddress") or value.get("accountId")


def _adf_to_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    parts: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            text = node.get("text")
            if text:
                parts.append(str(text))
            for child in node.get("content", []):
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    result = " ".join(part.strip() for part in parts if part and part.strip())
    return result or None


def normalize_issue(issue: dict[str, Any], settings: JiraSettings) -> JiraIssueSummary:
    fields = issue.get("fields", {})
    issue_type = fields.get("issuetype") or {}
    status = fields.get("status") or {}
    priority = fields.get("priority") or {}

    issue_key = str(issue.get("key", ""))
    return JiraIssueSummary(
        external_id=str(issue.get("id", issue_key)),
        issue_key=issue_key,
        issue_type=str(issue_type.get("name", "Unknown")),
        status=str(status.get("name", "Unknown")),
        summary=str(fields.get("summary", "")),
        description_text=_adf_to_text(fields.get("description")),
        priority=priority.get("name"),
        assignee=_display_name(fields.get("assignee")),
        reporter=_display_name(fields.get("reporter")),
        updated=fields.get("updated"),
        source_url=f"{settings.base_url.rstrip('/')}/browse/{issue_key}",
    )


def normalize_search_response(payload: dict[str, Any], settings: JiraSettings) -> tuple[int, int, list[JiraIssueSummary]]:
    raw_issues = payload.get("issues", [])
    total = int(payload.get("total", len(raw_issues)))
    max_results = int(payload.get("maxResults", len(raw_issues)))
    issues = [normalize_issue(issue, settings) for issue in raw_issues]
    return total, max_results, issues
