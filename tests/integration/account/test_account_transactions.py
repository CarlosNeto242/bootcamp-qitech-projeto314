from datetime import datetime
from uuid import uuid4

from tests.utils import (
    CANTEEN_ACCOUNT_KEY,
    UNIVERSITY_ACCOUNT_KEY,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
)

PAGE_FIELDS = {"data", "limit", "page", "is_last_page"}
LINE_FIELDS = {
    "transaction_key",
    "transaction_type",
    "amount",
    "counterparty_type",
    "counterparty_name",
    "counterparty_account_key",
    "created_at",
}


def create_account_with_deposits(values: list) -> str:
    account_key = ObjectGenerator.create_student_account(balance=values[0])
    for value in values[1:]:
        ObjectGenerator.deposit(account_key, value)
    return account_key


def amounts(response: dict) -> list:
    return [line["amount"] for line in response["data"]]


class TestAccountTransactions:
    def test_refuses_malformed_request(self):
        account_key = ObjectGenerator.create_student_account(balance=1000)

        cases = [
            ("account_key fora do formato UUID", "nao-e-uuid", None),
            ("page negativa", account_key, {"page": -1}),
            ("page nao inteira", account_key, {"page": "abc"}),
            ("limit zero", account_key, {"limit": 0}),
            ("limit acima de 100", account_key, {"limit": 101}),
            ("limit nao inteiro", account_key, {"limit": "abc"}),
            ("parametro desconhecido", account_key, {"pagina": 0}),
        ]

        for case, key, params in cases:
            status, response = RequestGenerator.GET_account_transactions(key, params)

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

    def test_refuses_nonexistent_account(self):
        status, response = RequestGenerator.GET_account_transactions(str(uuid4()))

        assert status == 404
        assert response["code"] == "QIT001001"

    def test_refuses_closed_account(self):
        account_key = ObjectGenerator.create_student_account()
        ObjectGenerator.close_account(account_key)

        status, response = RequestGenerator.GET_account_transactions(account_key)

        assert status == 409
        assert response["code"] == "QIT001002"

    def test_last_page(self):
        account_key = create_account_with_deposits([100, 200, 300])

        status, response = RequestGenerator.GET_account_transactions(account_key, {"page": 1, "limit": 2})

        assert status == 200
        assert set(response.keys()) == PAGE_FIELDS
        assert response["page"] == 1
        assert response["limit"] == 2
        assert response["is_last_page"] is True
        assert amounts(response) == [100]

    def test_last_page_when_total_is_exact_multiple_of_limit(self):
        account_key = create_account_with_deposits([100, 200, 300, 400])

        status, response = RequestGenerator.GET_account_transactions(account_key, {"page": 1, "limit": 2})

        assert status == 200
        assert response["is_last_page"] is True
        assert amounts(response) == [200, 100]

    def test_not_last_page(self):
        account_key = create_account_with_deposits([100, 200, 300])

        status, response = RequestGenerator.GET_account_transactions(account_key, {"page": 0, "limit": 2})

        assert status == 200
        assert response["page"] == 0
        assert response["limit"] == 2
        assert response["is_last_page"] is False
        assert amounts(response) == [300, 200]

    def test_page_beyond_last_returns_empty(self):
        account_key = create_account_with_deposits([100, 200])

        status, response = RequestGenerator.GET_account_transactions(account_key, {"page": 5, "limit": 2})

        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_account_without_transactions_returns_empty(self):
        account_key = ObjectGenerator.create_student_account()

        status, response = RequestGenerator.GET_account_transactions(account_key)

        assert status == 200
        assert response["data"] == []
        assert response["is_last_page"] is True

    def test_default_page_and_limit(self):
        account_key = create_account_with_deposits(list(range(1, 13)))

        status, response = RequestGenerator.GET_account_transactions(account_key)

        assert status == 200
        assert response["page"] == 0
        assert response["limit"] == 10
        assert response["is_last_page"] is False
        assert amounts(response) == list(range(12, 2, -1))

    def test_deposit_line(self):
        account_key = ObjectGenerator.create_student_account(balance=1500)

        _, response = RequestGenerator.GET_account_transactions(account_key)
        deposit = response["data"][0]

        assert set(deposit.keys()) == LINE_FIELDS
        assert deposit["transaction_type"] == "DEPOSIT"
        assert deposit["amount"] == 1500
        assert deposit["counterparty_type"] is None
        assert deposit["counterparty_name"] is None
        assert deposit["counterparty_account_key"] is None
        assert deposit["created_at"].endswith("+00:00")
        datetime.fromisoformat(deposit["created_at"])

    def test_transfer_between_students_seen_by_both_sides(self):
        origin = ObjectGenerator.create_student_account(balance=5000, name="Ana Origem")
        destination = ObjectGenerator.create_student_account(name="Bruno Destino")
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, transfer_response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))
        assert status == 201

        _, origin_response = RequestGenerator.GET_account_transactions(origin)
        fee, transfer, deposit = origin_response["data"]

        assert fee["transaction_type"] == "FEE"
        assert fee["amount"] == -200
        assert fee["counterparty_type"] == "INSTITUTIONAL"
        assert fee["counterparty_name"] is None
        assert fee["counterparty_account_key"] == UNIVERSITY_ACCOUNT_KEY

        assert transfer["transaction_type"] == "TRANSFER"
        assert transfer["transaction_key"] == transfer_response["transaction_key"]
        assert transfer["amount"] == -1000
        assert transfer["counterparty_type"] == "STUDENT"
        assert transfer["counterparty_name"] == "Bruno Destino"
        assert transfer["counterparty_account_key"] is None

        assert deposit["transaction_type"] == "DEPOSIT"
        assert deposit["amount"] == 5000

        _, destination_response = RequestGenerator.GET_account_transactions(destination)
        received = destination_response["data"]

        assert len(received) == 1
        assert received[0]["transaction_key"] == transfer_response["transaction_key"]
        assert received[0]["amount"] == 1000
        assert received[0]["counterparty_type"] == "STUDENT"
        assert received[0]["counterparty_name"] == "Ana Origem"
        assert received[0]["counterparty_account_key"] is None

    def test_transfer_to_institution_shows_institution_key(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=CANTEEN_ACCOUNT_KEY,
            value=1000,
        )

        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))
        assert status == 201

        _, response = RequestGenerator.GET_account_transactions(origin)
        transfer = response["data"][1]

        assert transfer["transaction_type"] == "TRANSFER"
        assert transfer["amount"] == -1000
        assert transfer["counterparty_type"] == "INSTITUTIONAL"
        assert transfer["counterparty_name"] is None
        assert transfer["counterparty_account_key"] == CANTEEN_ACCOUNT_KEY
