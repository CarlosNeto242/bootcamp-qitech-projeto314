from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers.account_controller import AccountController
from utils.schema_handler import SchemaHandler
from utils.uuid_validator import validate_uuid


class AccountResource:
    @SchemaHandler.validate("post_account.json")
    def on_post(self, payload: dict) -> JSONResponse:
        controller = AccountController()
        account = controller.create(payload)

        return JSONResponse(
            content=jsonable_encoder(account),
            status_code=http_status.HTTP_201_CREATED,
        )

    def on_get_by_key(self, account_key: str) -> JSONResponse:
        validate_uuid(account_key, "account_key")

        controller = AccountController()
        account = controller.get_by_key(account_key)

        return JSONResponse(
            content=jsonable_encoder(account),
            status_code=http_status.HTTP_200_OK,
        )
