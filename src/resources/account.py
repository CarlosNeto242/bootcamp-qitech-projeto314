from fastapi import Request
from fastapi import status as http_status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from controllers.account_controller import AccountController
from utils.schema_handler import SchemaHandler
from utils.uuid_validator import validate_uuid

DEFAULT_LIMIT = 10
DEFAULT_PAGE = 0


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

    @SchemaHandler.validate_query_params("get_account_transactions.json")
    def on_get_transactions(self, account_key: str, request: Request) -> JSONResponse:
        validate_uuid(account_key, "account_key")

        limit = int(request.query_params.get("limit", DEFAULT_LIMIT))
        page = int(request.query_params.get("page", DEFAULT_PAGE))

        controller = AccountController()
        transactions_page = controller.get_transactions(account_key, limit, page * limit)

        page_envelope = {
            "data": transactions_page["statement_lines_dto"],
            "limit": limit,
            "page": page,
            "is_last_page": transactions_page["is_last_page"],
        }

        return JSONResponse(
            content=jsonable_encoder(page_envelope),
            status_code=http_status.HTTP_200_OK,
        )
