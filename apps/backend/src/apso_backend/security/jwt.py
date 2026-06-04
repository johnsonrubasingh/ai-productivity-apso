import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, status


@dataclass(frozen=True)
class VerifiedJwt:
    subject: str
    role: str | None
    email: str | None
    claims: dict[str, Any]


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _json_decode(value: str) -> dict[str, Any]:
    return json.loads(_b64url_decode(value))


def verify_supabase_jwt(token: str, secret: str) -> VerifiedJwt:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT format")

    header_b64, payload_b64, signature_b64 = parts
    header = _json_decode(header_b64)
    payload = _json_decode(payload_b64)

    if header.get("alg") != "HS256":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported JWT algorithm")

    signed = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).digest()
    received = _b64url_decode(signature_b64)
    if not hmac.compare_digest(expected, received):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT signature")

    exp = payload.get("exp")
    if exp is not None and int(exp) < int(time.time()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT has expired")

    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT missing subject")

    return VerifiedJwt(
        subject=str(subject),
        role=payload.get("role"),
        email=payload.get("email"),
        claims=payload,
    )

