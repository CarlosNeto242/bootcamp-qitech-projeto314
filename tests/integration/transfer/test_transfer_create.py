from uuid import uuid4

from tests.utils import (
    CANTEEN_ACCOUNT_KEY,
    UNIVERSITY_ACCOUNT_KEY,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
)


class TestTransferCreate:
    def test_refuses_malformed_body(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        valid_payload = PayloadGenerator.create_transfer_payload(origin_account_key=origin)

        malformed_payloads = [
            ("corpo vazio", {}),
            ("sem value", {k: v for k, v in valid_payload.items() if k != "value"}),
            ("campo extra", {**valid_payload, "campo_extra": 1}),
            ("value zero", {**valid_payload, "value": 0}),
            ("value negativo", {**valid_payload, "value": -100}),
            ("value decimal", {**valid_payload, "value": 10.5}),
            ("value texto", {**valid_payload, "value": "1000"}),
            ("origin_account_key fora do formato UUID", {**valid_payload, "origin_account_key": "nao-e-uuid"}),
        ]

        for case, payload in malformed_payloads:
            status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(origin) == 5000

    def test_refuses_missing_or_malformed_idempotency_key(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        payload = PayloadGenerator.create_transfer_payload(origin_account_key=origin)

        cases = [
            ("Idempotency-Key ausente", None),
            ("Idempotency-Key fora do formato UUID", "nao-e-uuid"),
        ]

        for case, idempotency_key in cases:
            status, response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(origin) == 5000

    def test_refuses_same_origin_and_destination(self):
        account = ObjectGenerator.create_student_account(balance=5000)
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=account,
            destination_account_key=account,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001013"
        assert ObjectGenerator.get_balance(account) == 5000

    def test_refuses_university_as_destination(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        university_balance_before = ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY)

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=UNIVERSITY_ACCOUNT_KEY,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001015"
        assert ObjectGenerator.get_balance(origin) == 5000
        assert ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY) == university_balance_before

    def test_refuses_nonexistent_account(self):
        existing = ObjectGenerator.create_student_account(balance=5000)
        nonexistent = str(uuid4())

        cases = [
            ("origem inexistente", nonexistent, existing),
            ("destino inexistente", existing, nonexistent),
        ]

        for case, origin, destination in cases:
            payload = PayloadGenerator.create_transfer_payload(
                origin_account_key=origin,
                destination_account_key=destination,
            )

            status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

            assert status == 404, f"{case}: status {status}"
            assert response["code"] == "QIT001001", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(existing) == 5000

    def test_refuses_institutional_origin(self):
        destination = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=CANTEEN_ACCOUNT_KEY,
            destination_account_key=destination,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001012"
        assert ObjectGenerator.get_balance(destination) == 0

    def test_refuses_closed_origin(self):
        origin = ObjectGenerator.create_student_account()
        destination = ObjectGenerator.create_student_account()
        ObjectGenerator.close_account(origin)

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001002"
        assert ObjectGenerator.get_balance(destination) == 0

    def test_refuses_closed_destination(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        ObjectGenerator.close_account(destination)

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001002"
        assert ObjectGenerator.get_balance(origin) == 5000

    def test_refuses_insufficient_balance(self):
        origin = ObjectGenerator.create_student_account(balance=1199)
        destination = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001008"
        assert ObjectGenerator.get_balance(origin) == 1199
        assert ObjectGenerator.get_balance(destination) == 0

    def test_exact_balance_for_value_plus_fee_passes(self):
        origin = ObjectGenerator.create_student_account(balance=1200)
        destination = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 201
        assert ObjectGenerator.get_balance(origin) == 0
        assert ObjectGenerator.get_balance(destination) == 1000

    def test_refuses_idempotency_key_used_by_deposit(self):
        origin = ObjectGenerator.create_student_account()
        destination = ObjectGenerator.create_student_account()
        deposit_idempotency_key = str(uuid4())
        ObjectGenerator.deposit(origin, 5000, idempotency_key=deposit_idempotency_key)

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=deposit_idempotency_key)

        assert status == 409
        assert response["code"] == "QIT001010"
        assert ObjectGenerator.get_balance(origin) == 5000
        assert ObjectGenerator.get_balance(destination) == 0

    def test_transfer_between_students_charges_fee(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        university_balance_before = ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY)

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))

        assert status == 201
        assert ObjectGenerator.get_balance(origin) == 3800
        assert ObjectGenerator.get_balance(destination) == 1000
        assert ObjectGenerator.get_balance(UNIVERSITY_ACCOUNT_KEY) == university_balance_before + 200

        fee, transfer, deposit = ObjectGenerator.list_transactions(origin)

        assert fee["transaction_type"] == "FEE"
        assert fee["amount"] == -200
        assert fee["counterparty_account_key"] == UNIVERSITY_ACCOUNT_KEY
        assert fee["created_at"] == transfer["created_at"]

        assert transfer["transaction_type"] == "TRANSFER"
        assert transfer["transaction_key"] == response["transaction_key"]
        assert transfer["amount"] == -1000
        assert transfer["counterparty_type"] == "STUDENT"

        assert deposit["transaction_type"] == "DEPOSIT"
        assert deposit["amount"] == 5000

    def test_retry_with_same_data_returns_original(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        first_status, first_response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)
        second_status, second_response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)

        assert first_status == 201
        assert second_status == 201
        assert second_response["transaction_key"] == first_response["transaction_key"]
        assert ObjectGenerator.get_balance(origin) == 3800
        assert ObjectGenerator.get_balance(destination) == 1000

        transaction_types = [line["transaction_type"] for line in ObjectGenerator.list_transactions(origin)]
        assert transaction_types == ["FEE", "TRANSFER", "DEPOSIT"]

    def test_retry_with_different_data_is_refused(self):
        origin = ObjectGenerator.create_student_account(balance=10000)
        destination = ObjectGenerator.create_student_account()
        other_destination = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)
        assert status == 201

        different_payloads = [
            ("value diferente", {**payload, "value": 2000}),
            ("destino diferente", {**payload, "destination_account_key": other_destination}),
        ]

        for case, different_payload in different_payloads:
            status, response = RequestGenerator.POST_transfer(different_payload, idempotency_key=idempotency_key)

            assert status == 409, f"{case}: status {status}"
            assert response["code"] == "QIT001010", f"{case}: code {response['code']}"

        assert ObjectGenerator.get_balance(origin) == 8800
        assert ObjectGenerator.get_balance(destination) == 1000
        assert ObjectGenerator.get_balance(other_destination) == 0

    def test_retry_after_origin_closed_returns_original(self):
        origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        first_status, first_response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)
        assert first_status == 201

        ObjectGenerator.close_account(origin)

        second_status, second_response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)

        assert second_status == 201
        assert second_response["transaction_key"] == first_response["transaction_key"]
        assert ObjectGenerator.get_balance(destination) == 1000

    def test_failed_request_does_not_consume_idempotency_key(self):
        origin = ObjectGenerator.create_student_account(balance=500)
        destination = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)
        assert status == 409
        assert response["code"] == "QIT001008"

        ObjectGenerator.deposit(origin, 700)

        status, response = RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)

        assert status == 201
        assert ObjectGenerator.get_balance(origin) == 0
        assert ObjectGenerator.get_balance(destination) == 1000
