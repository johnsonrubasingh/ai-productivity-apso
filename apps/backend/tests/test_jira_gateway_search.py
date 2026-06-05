from apso_backend.core.config import JiraSettings
from apso_backend.integrations.jira.normalizer import normalize_search_response


def test_jira_search_jql_response_without_total_is_stable() -> None:
    settings = JiraSettings(
        mode="live_read_only",
        base_url="https://example.atlassian.net",
        username_env="JIRA_USERNAME",
        token_env="JIRA_API_TOKEN",
    )
    total, max_results, issues = normalize_search_response(
        {
            "issues": [
                {
                    "id": "10001",
                    "key": "APSO-1",
                    "fields": {
                        "issuetype": {"name": "Story"},
                        "status": {"name": "To Do"},
                        "summary": "Validate Jira gateway search",
                    },
                }
            ]
        },
        settings,
    )

    assert total == 1
    assert max_results == 1
    assert issues[0].issue_key == "APSO-1"
