import requests

from connectors.rest_connector import BaseConnectorResponse, RestConnector
from constants import UNIVERSITY_API_INTERNAL_TOKEN, UNIVERSITY_API_TIMEOUT, UNIVERSITY_API_URL
from errors import UniversityUnavailable


class UniversityConnector(RestConnector):
    def __init__(self) -> None:
        super().__init__(
            class_name=__name__,
            base_url=UNIVERSITY_API_URL,
            timeout=UNIVERSITY_API_TIMEOUT,
            internal_token=UNIVERSITY_API_INTERNAL_TOKEN,
        )

    def get_by_document_number(self, document_number: str) -> BaseConnectorResponse:
        try:
            return self.send(endpoint=f"/student/{document_number}", method="GET")
        except requests.exceptions.RequestException:
            raise UniversityUnavailable()
