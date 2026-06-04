from typing import Any

from apso_backend.schemas.bitbucket import (
    BitbucketCommitSummary,
    BitbucketPipelineSummary,
    BitbucketPullRequestSummary,
    BitbucketRepositorySummary,
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
