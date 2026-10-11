from os import environ

from tests.utils.requisition import ClientRequisition, BaseConnectorResponse


INTERNAL_TOKEN = environ.get("INTERNAL_TOKEN", "default_token")


class RequestGenerator:
    @staticmethod
    def POST_transfer(
        transfer_payload: dict,
        idempotency_key: str = None,
        internal_token: str = INTERNAL_TOKEN,
    ) -> tuple:
        headers = {}
    def POST_sample_entity(sample_entity_payload: dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST",
            "/sample_entity",
            payload=sample_entity_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json

    @staticmethod
    def POST_student(student_payload : dict) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "POST", 
            "/student",
            payload=student_payload,
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )

        return response.response_status, response.response_json

    @staticmethod
    def GET_sample_entity(sample_entity_key: str) -> BaseConnectorResponse:
        response = ClientRequisition.send(
            "GET",
            f"/sample_entity/{sample_entity_key}",
            headers={"INTERNAL-TOKEN": INTERNAL_TOKEN},
        )
        return response.response_status, response.response_json

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
