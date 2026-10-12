from os import environ

from tests.utils.requisition import ClientRequisition


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")


class RequestGenerator:
    @staticmethod
    def POST_transfer(
        transfer_payload: dict,
        idempotency_key: str = None,
    ) -> tuple:
        headers = {"INTERNAL-TOKEN": INTERNAL_TOKEN}

        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key

        response = ClientRequisition.send(
            "POST",
            "/transfer",
            payload=transfer_payload,
            headers=headers,
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_deposit(
        deposit_payload: dict,
        idempotency_key: str = None,
    ) -> tuple:
        headers = {"INTERNAL-TOKEN": INTERNAL_TOKEN}

        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key

        response = ClientRequisition.send(
            "POST",
            "/deposit",
            payload=deposit_payload,
            headers=headers,
        )
        return response.response_status, response.response_json

    @staticmethod
    def POST_student(student_payload: dict) -> tuple:
        response = ClientRequisition.send(
            "POST",
            "/student",
            payload=student_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json

    @staticmethod
    def POST_account(account_payload: dict) -> tuple:
        response = ClientRequisition.send(
            "POST",
            "/account",
            payload=account_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json

    @staticmethod
    def GET_account(account_key: str) -> tuple:
        response = ClientRequisition.send(
            "GET",
            f"/account/{account_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json

    @staticmethod
    def GET_account_transactions(account_key: str, params: dict = None) -> tuple:
        response = ClientRequisition.send(
            "GET",
            f"/account/{account_key}/transactions",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
            query_params=params,
        )

        return response.response_status, response.response_json

    @staticmethod
    def POST_account_close(account_key: str) -> tuple:
        response = ClientRequisition.send(
            "POST",
            f"/account/{account_key}/close",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json
