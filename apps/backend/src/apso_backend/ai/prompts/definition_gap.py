from apso_backend.ai.schemas import RequirementGapInput


PROMPT_VERSION = "definition_gap.v0.1.0"


def build_definition_gap_prompt(payload: RequirementGapInput) -> str:
    comments = "\n".join(f"- {comment}" for comment in payload.comments[:10]) or "None"
    acceptance = payload.acceptance_criteria or "Not provided"
    description = payload.description or "Not provided"
    return f"""
You are APSO's Definition Gap Engine. Review the Jira story below.

Rules:
- Use only the provided story text and comments.
- Do not invent business facts.
- Do not invent productivity metrics.
- Return strict JSON only.
- Every finding must include at least one evidence item.
- metric_label must be "ai_inferred" unless the input explicitly contains actual measured data.

Required JSON shape:
{{
  "issue_key": "{payload.issue_key}",
  "quality_score": 0,
  "findings": [
    {{
      "finding_type": "definition_gap",
      "severity": "low|medium|high|critical",
      "title": "short finding title",
      "description": "clear explanation",
      "recommendation": "specific action",
      "confidence": 0,
      "metric_label": "ai_inferred",
      "evidence": [
        {{
          "source": "jira",
          "artifact_type": "story",
          "artifact_id": "{payload.issue_key}",
          "url": null,
          "summary": "what text supports this finding"
        }}
      ]
    }}
  ]
}}

Story:
Issue: {payload.issue_key}
Summary: {payload.summary}
Description: {description}
Acceptance Criteria: {acceptance}
Comments:
{comments}
""".strip()

