from typing import Any

from apso_backend.schemas.bitbucket import (
    BitbucketCodeEvidenceSummary,
    BitbucketCommitSummary,
    BitbucketPipelineSummary,
    BitbucketPipelineStepSummary,
    BitbucketPullRequestSummary,
    BitbucketRepositorySummary,
    BitbucketSourceFileSummary,
    BitbucketTestRunSummary,
)


def normalize_repository(repo: dict[str, Any]) -> BitbucketRepositorySummary:
    links = repo.get("links", {})
    html = links.get("html", {})
    main_branch = repo.get("mainbranch") or {}
    return BitbucketRepositorySummary(
        uuid=repo.get("uuid"),
        slug=str(repo.get("slug", "")),
        name=str(repo.get("name", repo.get("slug", ""))),
        full_name=str(repo.get("full_name", "")),
        main_branch=main_branch.get("name"),
        is_private=repo.get("is_private"),
        source_url=html.get("href"),
    )


def normalize_pull_request(pr: dict[str, Any]) -> BitbucketPullRequestSummary:
    links = pr.get("links", {})
    html = links.get("html", {})
    author = pr.get("author") or {}
    source = pr.get("source") or {}
    destination = pr.get("destination") or {}
    source_branch = (source.get("branch") or {}).get("name")
    target_branch = (destination.get("branch") or {}).get("name")
    return BitbucketPullRequestSummary(
        id=int(pr.get("id", 0)),
        title=str(pr.get("title", "")),
        state=str(pr.get("state", "")),
        author=author.get("display_name") or author.get("nickname") or author.get("account_id"),
        source_branch=source_branch,
        target_branch=target_branch,
        source_url=html.get("href"),
    )


def normalize_commit(commit: dict[str, Any], branch: str | None = None) -> BitbucketCommitSummary:
    links = commit.get("links", {})
    html = links.get("html", {})
    author = commit.get("author") or {}
    user = author.get("user") or {}
    return BitbucketCommitSummary(
        hash=str(commit.get("hash", "")),
        message=commit.get("message"),
        author=user.get("display_name") or author.get("raw"),
        branch=branch,
        committed_at=commit.get("date"),
        source_url=html.get("href"),
    )


def normalize_pipeline(pipeline: dict[str, Any]) -> BitbucketPipelineSummary:
    links = pipeline.get("links", {})
    html = links.get("html", {})
    state = pipeline.get("state") or {}
    target = pipeline.get("target") or {}
    commit = target.get("commit") or {}
    selector = target.get("selector") or {}
    return BitbucketPipelineSummary(
        uuid=str(pipeline.get("uuid", "")),
        state=str(state.get("name", "")),
        result=(state.get("result") or {}).get("name"),
        branch=selector.get("pattern") or target.get("ref_name"),
        commit_sha=commit.get("hash"),
        source_url=html.get("href"),
    )


def normalize_pipeline_step(step: dict[str, Any]) -> BitbucketPipelineStepSummary:
    state = step.get("state") or {}
    return BitbucketPipelineStepSummary(
        uuid=str(step.get("uuid", "")),
        name=step.get("name"),
        state=state.get("name"),
        result=(state.get("result") or {}).get("name"),
        started_on=step.get("started_on"),
        completed_on=step.get("completed_on"),
    )


def normalize_test_report(
    report: dict[str, Any],
    *,
    pipeline_uuid: str,
    step_uuid: str,
    source_url: str | None = None,
) -> BitbucketTestRunSummary:
    total = int(report.get("number_of_test_cases") or report.get("total") or 0)
    failed = int(report.get("number_of_failed_test_cases") or report.get("failed") or 0)
    skipped = int(report.get("number_of_skipped_test_cases") or report.get("skipped") or 0)
    successful = int(report.get("number_of_successful_test_cases") or report.get("successful") or 0)
    passed = successful if successful > 0 else max(0, total - failed - skipped)
    duration = report.get("duration") or report.get("duration_seconds")
    return BitbucketTestRunSummary(
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
        total_tests=total,
        passed_tests=passed,
        failed_tests=failed,
        skipped_tests=skipped,
        duration_seconds=int(duration) if duration is not None else None,
        source_url=source_url,
    )


def normalize_source_file(node: dict[str, Any]) -> BitbucketSourceFileSummary | None:
    if node.get("type") != "commit_file":
        return None
    links = node.get("links", {})
    html = links.get("html", {})
    commit = node.get("commit") or {}
    return BitbucketSourceFileSummary(
        path=str(node.get("path", "")),
        commit_sha=commit.get("hash"),
        size=node.get("size"),
        source_url=html.get("href"),
    )


def normalize_source_evidence(
    source_file: BitbucketSourceFileSummary,
    *,
    branch: str,
    content_excerpt: str | None = None,
) -> BitbucketCodeEvidenceSummary:
    reference = f"source:{branch}:{source_file.path}"
    return BitbucketCodeEvidenceSummary(
        evidence_type="source_file",
        reference=reference,
        file_path=source_file.path,
        commit_sha=source_file.commit_sha,
        content_excerpt=content_excerpt,
        source_url=source_file.source_url,
    )


def normalize_diff_evidence(
    *,
    reference: str,
    diff_text: str,
    source_url: str | None = None,
) -> BitbucketCodeEvidenceSummary:
    return BitbucketCodeEvidenceSummary(
        evidence_type="diff",
        reference=reference,
        file_path=None,
        commit_sha=None,
        content_excerpt=diff_text[:8000],
        source_url=source_url,
    )
