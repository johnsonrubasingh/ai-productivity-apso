from apso_backend.integrations.bitbucket.normalizer import (
    normalize_diff_evidence,
    normalize_pipeline_step,
    normalize_source_evidence,
    normalize_source_file,
    normalize_test_report,
)


def test_normalize_pipeline_step_and_test_report() -> None:
    step = normalize_pipeline_step(
        {
            "uuid": "{step-1}",
            "name": "Run tests",
            "state": {"name": "COMPLETED", "result": {"name": "SUCCESSFUL"}},
            "started_on": "2026-06-04T10:00:00Z",
            "completed_on": "2026-06-04T10:02:00Z",
        }
    )
    report = normalize_test_report(
        {
            "number_of_test_cases": 12,
            "number_of_successful_test_cases": 10,
            "number_of_failed_test_cases": 1,
            "number_of_skipped_test_cases": 1,
            "duration": 120,
        },
        pipeline_uuid="{pipeline-1}",
        step_uuid=step.uuid,
    )

    assert step.result == "SUCCESSFUL"
    assert report.total_tests == 12
    assert report.passed_tests == 10
    assert report.failed_tests == 1
    assert report.skipped_tests == 1


def test_normalize_source_and_diff_evidence() -> None:
    source_file = normalize_source_file(
        {
            "type": "commit_file",
            "path": "src/app.py",
            "size": 42,
            "commit": {"hash": "abc123"},
            "links": {"html": {"href": "https://bitbucket.example/src/app.py"}},
        }
    )
    assert source_file is not None

    evidence = normalize_source_evidence(source_file, branch="develop", content_excerpt="print('ok')")
    diff = normalize_diff_evidence(reference="pull_request_diff:repo:1", diff_text="+print('ok')")

    assert evidence.evidence_type == "source_file"
    assert evidence.reference == "source:develop:src/app.py"
    assert evidence.commit_sha == "abc123"
    assert diff.evidence_type == "diff"
    assert diff.content_excerpt == "+print('ok')"
