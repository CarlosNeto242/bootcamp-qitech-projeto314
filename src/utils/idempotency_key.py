from fastapi import Request

from utils.uuid_validator import validate_uuid

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"


def get_idempotency_key(request: Request) -> str:
    return validate_uuid(request.headers.get(IDEMPOTENCY_KEY_HEADER), f"{IDEMPOTENCY_KEY_HEADER} header")
