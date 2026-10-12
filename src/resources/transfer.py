import re

from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import TransferController
from errors import InvalidSchema
from utils.schema_handler import SchemaHandler

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
UUID_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


class TransferResource:
    @SchemaHandler.validate("post_transfer.json")
    def on_post(self, payload: dict, request: Request) -> JSONResponse:
        idempotency_key = request.headers.get(IDEMPOTENCY_KEY_HEADER)

        if idempotency_key is None or not UUID_PATTERN.match(idempotency_key):
            raise InvalidSchema(f"{IDEMPOTENCY_KEY_HEADER} header must be a valid UUID")

        controller = TransferController()
        transfer = controller.create(payload, idempotency_key)

        return JSONResponse(
            content=jsonable_encoder(transfer),
            status_code=http_status.HTTP_201_CREATED,
        )
