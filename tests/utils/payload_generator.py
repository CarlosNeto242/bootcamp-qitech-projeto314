from tests.utils.constants import CANTEEN_ACCOUNT_KEY

from tests.utils.random_generator import RandomGenerator


class PayloadGenerator:
    @staticmethod
    def create_transfer_payload(
        origin_account_key: str = None,
        destination_account_key: str = None,
        value: int = None,
    ) -> dict:
        if destination_account_key is None:
            destination_account_key = CANTEEN_ACCOUNT_KEY

        if value is None:
            value = 1000

        payload = {
            "origin_account_key": origin_account_key,
            "destination_account_key": destination_account_key,
            "value": value,
        }
        return payload

    @staticmethod
    def create_student_payload(
        name: str = None,
        document_number: str = None,
    ) -> dict:

        if name is None:
            name = "Maria da Silva"

        if document_number is None:
            document_number = RandomGenerator.generate_cpf()

        payload = {
            "name": name,
            "document_number": document_number,
        }
        return payload
     
    @staticmethod
    def create_deposit_payload(
        account_key: str = None,
        value: int = None,
    ) -> dict:
        if value is None:
            value = 1000

        payload = {
            "account_key": account_key,
            "value": value,
        }
        return payload
