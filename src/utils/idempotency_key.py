import re

from fastapi import Request

from errors import InvalidSchema

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def get_idempotency_key(request: Request) -> str:
    idempotency_key = request.headers.get(IDEMPOTENCY_KEY_HEADER)

    if idempotency_key is None or not UUID_PATTERN.match(idempotency_key):
        raise InvalidSchema(f"{IDEMPOTENCY_KEY_HEADER} header must be a valid UUID")

    return idempotency_key
