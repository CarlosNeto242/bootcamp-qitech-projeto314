from uuid import uuid4

from tests.utils.constants import CANTEEN_ACCOUNT_KEY
from tests.utils.mock_generator import UniversityMock
from tests.utils.payload_generator import PayloadGenerator
from tests.utils.request_generator import RequestGenerator

MAXIMUM_VALUE = 200000000
FEE_VALUE = 200
STATEMENT_LIMIT = 100


class ObjectGenerator:
    @staticmethod
    def create_student(name: str = None) -> dict:
        student_payload = PayloadGenerator.create_student_payload(name=name)

        UniversityMock.GET_university_student(student_payload["document_number"])

        status, response = RequestGenerator.POST_student(student_payload)
        assert status == 201

        return response

    @staticmethod
    def create_student_account(balance: int = 0, name: str = "Maria da Silva") -> str:
        student_key = ObjectGenerator.create_student(name=name)["student_key"]

        status, response = RequestGenerator.POST_account({"student_key": student_key})
        assert status == 201

        account_key = response["account_key"]

        remaining = balance
        while remaining > 0:
            value = min(remaining, MAXIMUM_VALUE)
            ObjectGenerator.deposit(account_key, value)
            remaining = remaining - value

        return account_key

    @staticmethod
    def deposit(account_key: str, value: int, idempotency_key: str = None) -> str:
        payload = PayloadGenerator.create_deposit_payload(account_key=account_key, value=value)

        status, response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key or str(uuid4()))
        assert status == 201

        return response["transaction_key"]

    @staticmethod
    def get_balance(account_key: str) -> int:
        status, response = RequestGenerator.GET_account(account_key)
        assert status == 200

        return response["balance"]

    @staticmethod
    def empty_account(account_key: str) -> None:
        balance = ObjectGenerator.get_balance(account_key)

        if balance == 0:
            return

        assert balance > FEE_VALUE, "a tarifa impede esvaziar uma conta com saldo de ate 200"

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=account_key,
            destination_account_key=CANTEEN_ACCOUNT_KEY,
            value=balance - FEE_VALUE,
        )
        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))
        assert status == 201

    @staticmethod
    def close_account(account_key: str) -> None:
        ObjectGenerator.empty_account(account_key)

        status, _ = RequestGenerator.POST_account_close(account_key)
        assert status == 200

    @staticmethod
    def list_transactions(account_key: str) -> list:
        status, response = RequestGenerator.GET_account_transactions(account_key, {"limit": STATEMENT_LIMIT})
        assert status == 200

        return response["data"]
