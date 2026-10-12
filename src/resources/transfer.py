from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import TransferController
from utils.idempotency_key import get_idempotency_key
from utils.schema_handler import SchemaHandler


class TransferResource:
    @SchemaHandler.validate("post_transfer.json")
    def on_post(self, payload: dict, request: Request) -> JSONResponse:
        idempotency_key = get_idempotency_key(request)

        controller = TransferController()
        transfer = controller.create(payload, idempotency_key)

        return JSONResponse(
            content=jsonable_encoder(transfer),
            status_code=http_status.HTTP_201_CREATED,
        )
