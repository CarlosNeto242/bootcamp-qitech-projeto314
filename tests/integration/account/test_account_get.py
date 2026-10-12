from datetime import datetime
from uuid import uuid4

from tests.utils import (
    CANTEEN_ACCOUNT_KEY,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
)

ACCOUNT_FIELDS = {"account_key", "type", "status", "balance", "created_at"}


class TestAccountGet:
    def test_refuses_malformed_account_key(self):
        malformed_keys = [
            "nao-e-uuid",
            "123",
            "26ccf53d7a9141bfacc209a93743f423",
            "26ccf53d-7a91-41bf-acc2-09a93743f42",
        ]

        for account_key in malformed_keys:
            status, response = RequestGenerator.GET_account(account_key)

            assert status == 400, f"{account_key}: status {status}"
            assert response["code"] == "QIT000001", f"{account_key}: code {response['code']}"

    def test_refuses_nonexistent_account(self):
        status, response = RequestGenerator.GET_account(str(uuid4()))

        assert status == 404
        assert response["code"] == "QIT001001"

    def test_returns_account(self):
        account_key = ObjectGenerator.create_student_account(balance=1500)

        status, response = RequestGenerator.GET_account(account_key)

        assert status == 200
        assert set(response.keys()) == ACCOUNT_FIELDS
        assert response["account_key"] == account_key
        assert response["type"] == "STUDENT"
        assert response["status"] == "ACTIVE"
        assert response["balance"] == 1500
        assert response["created_at"].endswith("+00:00")
        datetime.fromisoformat(response["created_at"])

    def test_accepts_account_key_in_uppercase(self):
        account_key = ObjectGenerator.create_student_account(balance=700)

        status, response = RequestGenerator.GET_account(account_key.upper())

        assert status == 200
        assert response["account_key"] == account_key
        assert response["balance"] == 700

    def test_returns_zero_balance_for_account_without_transactions(self):
        account_key = ObjectGenerator.create_student_account()

        status, response = RequestGenerator.GET_account(account_key)

        assert status == 200
        assert response["balance"] == 0

    def test_balance_reflects_transfer_and_fee(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))
        assert status == 201

        _, origin_response = RequestGenerator.GET_account(origin)
        _, destination_response = RequestGenerator.GET_account(destination)

        assert origin_response["balance"] == 3800
        assert destination_response["balance"] == 1000

    def test_refuses_closed_account(self):
        account_key = ObjectGenerator.create_student_account(balance=500)
        ObjectGenerator.close_account(account_key)

        status, response = RequestGenerator.GET_account(account_key)

        assert status == 409
        assert response["code"] == "QIT001002"
        assert "balance" not in response

    def test_returns_institutional_account(self):
        status, response = RequestGenerator.GET_account(CANTEEN_ACCOUNT_KEY)

        assert status == 200
        assert response["type"] == "INSTITUTIONAL"
        assert response["status"] == "ACTIVE"
        assert response["balance"] == ObjectGenerator.get_balance(CANTEEN_ACCOUNT_KEY)
