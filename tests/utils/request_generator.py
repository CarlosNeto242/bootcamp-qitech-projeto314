from os import environ

from tests.utils.requisition import ClientRequisition


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")


class RequestGenerator:
    @staticmethod
    def POST_transfer(
        transfer_payload: dict,
        idempotency_key: str = None,
        internal_token: str = INTERNAL_TOKEN,
    ) -> tuple:
        headers = {}

        if internal_token is not None:
            headers["INTERNAL-TOKEN"] = internal_token

        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key

        response = ClientRequisition.send(
            "POST",
            "/transfer",
            payload=transfer_payload,
            headers=headers,
        )
        return response.response_status, response.response_json
