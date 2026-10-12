from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from tests.utils import (
    CANTEEN_ACCOUNT_KEY,
    UNIVERSITY_ACCOUNT_KEY,
    ObjectGenerator,
    PayloadGenerator,
    RequestGenerator,
)


class TestAccountClose:
    def test_refuses_malformed_account_key(self):
        for account_key in ["nao-e-uuid", "123", "26ccf53d7a9141bfacc209a93743f423"]:
            status, response = RequestGenerator.POST_account_close(account_key)

            assert status == 400, f"{account_key}: status {status}"
            assert response["code"] == "QIT000001", f"{account_key}: code {response['code']}"

    def test_refuses_nonexistent_account(self):
        status, response = RequestGenerator.POST_account_close(str(uuid4()))

        assert status == 404
        assert response["code"] == "QIT001001"

    def test_refuses_institutional_account(self):
        for account_key in [CANTEEN_ACCOUNT_KEY, UNIVERSITY_ACCOUNT_KEY]:
            status, response = RequestGenerator.POST_account_close(account_key)

            assert status == 409, f"{account_key}: status {status}"
            assert response["code"] == "QIT001017", f"{account_key}: code {response['code']}"

            status, account = RequestGenerator.GET_account(account_key)
            assert status == 200
            assert account["status"] == "ACTIVE"

    def test_refuses_account_with_balance(self):
        account_key = ObjectGenerator.create_student_account(balance=1)

        status, response = RequestGenerator.POST_account_close(account_key)

        assert status == 409
        assert response["code"] == "QIT001016"

        status, account = RequestGenerator.GET_account(account_key)
        assert status == 200
        assert account["status"] == "ACTIVE"
        assert account["balance"] == 1

    def test_closes_account_with_zero_balance(self):
        account_key = ObjectGenerator.create_student_account()

        status, response = RequestGenerator.POST_account_close(account_key)

        assert status == 200
        assert response == {"account_key": account_key, "status": "CLOSED"}

        status, response = RequestGenerator.GET_account(account_key)
        assert status == 409
        assert response["code"] == "QIT001002"

    def test_closed_account_refuses_deposit(self):
        account_key = ObjectGenerator.create_student_account()
        RequestGenerator.POST_account_close(account_key)

        payload = PayloadGenerator.create_deposit_payload(account_key=account_key)
        status, response = RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

        assert status == 409
        assert response["code"] == "QIT001002"

    def test_refuses_already_closed_account(self):
        account_key = ObjectGenerator.create_student_account()

        first_status, _ = RequestGenerator.POST_account_close(account_key)
        second_status, second_response = RequestGenerator.POST_account_close(account_key)

        assert first_status == 200
        assert second_status == 409
        assert second_response["code"] == "QIT001002"

    def test_closes_account_emptied_by_transfer(self):
        origin = ObjectGenerator.create_student_account(balance=1200)
        destination = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_transfer_payload(
            origin_account_key=origin,
            destination_account_key=destination,
            value=1000,
        )

        status, _ = RequestGenerator.POST_transfer(payload, idempotency_key=str(uuid4()))
        assert status == 201

        status, response = RequestGenerator.POST_account_close(origin)

        assert status == 200
        assert response["status"] == "CLOSED"
        assert ObjectGenerator.get_balance(destination) == 1000

    def test_accepts_account_key_in_uppercase(self):
        account_key = ObjectGenerator.create_student_account()

        status, response = RequestGenerator.POST_account_close(account_key.upper())

        assert status == 200
        assert response["account_key"] == account_key

    def test_simultaneous_deposit_and_close_never_leave_balance_in_closed_account(self):
        account_key = ObjectGenerator.create_student_account()
        payload = PayloadGenerator.create_deposit_payload(account_key=account_key, value=1000)
        barrier = Barrier(2)

        def close(_):
            barrier.wait()
            return RequestGenerator.POST_account_close(account_key)

        def deposit(_):
            barrier.wait()
            return RequestGenerator.POST_deposit(payload, idempotency_key=str(uuid4()))

        with ThreadPoolExecutor(max_workers=2) as executor:
            close_future = executor.submit(close, None)
            deposit_future = executor.submit(deposit, None)
            close_status, close_response = close_future.result()
            deposit_status, deposit_response = deposit_future.result()

        if close_status == 200:
            assert deposit_status == 409
            assert deposit_response["code"] == "QIT001002"
        else:
            assert close_status == 409
            assert close_response["code"] == "QIT001016"
            assert deposit_status == 201
            assert ObjectGenerator.get_balance(account_key) == 1000
