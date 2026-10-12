from uuid import uuid4

from tests.utils import (
    CANTEEN_ACCOUNT_KEY,
    UNIVERSITY_ACCOUNT_KEY,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
)


class TestDepositCreate:
    def test_refuses_malformed_body(self):
        account = ObjectGenerator.create_student_account()
        valid_payload = PayloadGenerator.create_deposit_payload(account_key=account)

        malformed_payloads = [
            ("corpo vazio", {}),
            ("sem value", {"account_key": account}),
            ("sem account_key", {"value": 1000}),
            ("campo extra", {**valid_payload, "campo_extra": 1}),
            ("value zero", {**valid_payload, "value": 0}),
            ("value negativo", {**valid_payload, "value": -100}),
            ("value decimal", {**valid_payload, "value": 10.5}),
            ("value texto", {**valid_payload, "value": "1000"}),
            ("value acima do teto", {**valid_payload, "value": 200000001}),
            ("account_key fora do formato UUID", {**valid_payload, "account_key": "nao-e-uuid"}),
        ]

        for case, payload in malformed_payloads:
            status, response = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(account) == 0

    def test_refuses_nonexistent_account(self):
        payload = PayloadGenerator.create_deposit_payload(account_key=str(uuid4()))

        status, response = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

        assert status == 404
        assert response["code"] == "QIT001001"

    def test_refuses_institutional_account(self):
        for account in [CANTEEN_ACCOUNT_KEY, UNIVERSITY_ACCOUNT_KEY]:
            balance_before = ObjectGenerator.get_balance(account)
            payload = PayloadGenerator.create_deposit_payload(account_key=account)

            status, response = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

            assert status == 409, f"{account}: status {status}"
            assert response["code"] == "QIT001011", f"{account}: code {response['code']}"
            assert ObjectGenerator.get_balance(account) == balance_before

    def test_refuses_closed_account(self):
        account = ObjectGenerator.create_student_account(balance=500)
        ObjectGenerator.close_account(account)
        payload = PayloadGenerator.create_deposit_payload(account_key=account)

        status, response = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001002"
        assert ObjectGenerator.get_balance(account) == 500

    def test_deposit_credits_account_without_fee(self):
        account = ObjectGenerator.create_student_account()
        university_balance_before = ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY)
        idempotency_key = str(uuid4())
        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=1500)

        status, response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

        assert status == 201
        assert ObjectGenerator.get_balance(account) == 1500
        assert ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY) == university_balance_before

        transactions = ObjectGenerator.list_transactions(account)
        assert len(transactions) == 1

        deposit = transactions[0]
        assert deposit["transaction_type"] == "DEPOSIT"
        assert deposit["transaction_key"] == response["transaction_key"]
        assert deposit["value"] == 1500
        assert deposit["origin_account_key"] is None
        assert deposit["destination_account_key"] == account
        assert deposit["idempotency_key"] == idempotency_key

    def test_retry_with_same_data_returns_original(self):
        account = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())
        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=1000)

        first_status, first_response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)
        second_status, second_response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

        assert first_status == 201
        assert second_status == 201
        assert second_response["transaction_key"] == first_response["transaction_key"]
        assert ObjectGenerator.get_balance(account) == 1000
        assert len(ObjectGenerator.list_transactions(account)) == 1

    def test_same_idempotency_key_with_different_deposit_is_refused(self):
        account = ObjectGenerator.create_student_account()
        other_account = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())
        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=1000)

        status, _ = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)
        assert status == 201

        different_payloads = [
            ("value diferente", {**payload, "value": 2000}),
            ("conta diferente", {**payload, "account_key": other_account}),
        ]

        for case, different_payload in different_payloads:
            status, response = RequestGenerator.POST_deposit(different_payload, idempotency_key=idempotency_key)

            assert status == 409, f"{case}: status {status}"
            assert response["code"] == "QIT001010", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(account) == 1000
        assert ObjectGenerator.get_balance(other_account) == 0

    def test_refuses_missing_or_malformed_idempotency_key(self):
        account = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_deposit_payload(account_key=account)

        cases = [
            ("Idempotency-Key ausente", None),
            ("Idempotency-Key fora do formato UUID", "nao-e-uuid"),
        ]

        for case, idempotency_key in cases:
            status, response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(account) == 0

    def test_retry_after_account_closed_returns_original(self):
        account = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())
        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=1000)

        first_status, first_response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)
        assert first_status == 201

        ObjectGenerator.close_account(account)

        second_status, second_response = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

        assert second_status == 201
        assert second_response["transaction_key"] == first_response["transaction_key"]
        assert ObjectGenerator.get_balance(account) == 1000

    def test_failed_request_does_not_consume_idempotency_key(self):
        account = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        institutional_payload = PayloadGenerator.create_deposit_payload(account_key=CANTEEN_ACCOUNT_KEY)
        status, response = RequestGenerator.POST_deposit(institutional_payload, idempotency_key=idempotency_key)
        assert status == 409
        assert response["code"] == "QIT001011"

        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=1000)
        status, _ = RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

        assert status == 201
        assert ObjectGenerator.get_balance(account) == 1000

    def test_deposit_of_maximum_value_passes(self):
        account = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_deposit_payload(account_key=account, value=200000000)

        status, _ = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

        assert status == 201
        assert ObjectGenerator.get_balance(account) == 200000000
