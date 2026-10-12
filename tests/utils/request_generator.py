from os import environ

from tests.utils.requisition import ClientRequisition, BaseConnectorResponse


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
