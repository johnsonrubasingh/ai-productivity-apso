SENSITIVE_MARKERS = (
    "token",
    "secret",
    "password",
    "service_role",
    "jwt",
    "key",
    "db_url",
    "connection",
)


def should_redact(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in SENSITIVE_MARKERS)


def redact_mapping(value):
    if isinstance(value, dict):
        return {
            key: "***REDACTED***" if should_redact(str(key)) else redact_mapping(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_mapping(item) for item in value]
    return value

