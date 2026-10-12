from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers import DepositController
from utils.idempotency_key import get_idempotency_key
from utils.schema_handler import SchemaHandler


class DepositResource:
    @SchemaHandler.validate("post_deposit.json")
    def on_post(self, payload: dict, request: Request) -> JSONResponse:
        idempotency_key = get_idempotency_key(request)

        controller = DepositController()
        deposit = controller.create(payload, idempotency_key)

        return JSONResponse(
            content=jsonable_encoder(deposit),
            status_code=http_status.HTTP_201_CREATED,
        )
