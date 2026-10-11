from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator


def send_simultaneously(requests: list) -> list:
    barrier = Barrier(len(requests))

    def send(request):
        payload, idempotency_key = request
        barrier.wait()
        return RequestGenerator.POST_transfer(payload, idempotency_key=idempotency_key)

    with ThreadPoolExecutor(max_workers=len(requests)) as executor:
        return list(executor.map(send, requests))


class TestTransferConcurrency:
    def test_simultaneous_transfers_exceeding_balance_only_one_passes(self):
        origin = ObjectGenerator.create_student_account(balance=1200)
        first_destination = ObjectGenerator.create_student_account()
        second_destination = ObjectGenerator.create_student_account()

        results = send_simultaneously(
            [
                (
                    PayloadGenerator.create_transfer_payload(
                        origin_account_key=origin,
                        destination_account_key=first_destination,
                        value=1000,
                    ),
                    str(uuid4()),
                ),
                (
                    PayloadGenerator.create_transfer_payload(
                        origin_account_key=origin,
                        destination_account_key=second_destination,
                        value=1000,
                    ),
                    str(uuid4()),
                ),
            ]
        )

        statuses = sorted(status for status, _ in results)
        codes = [response["code"] for status, response in results if status == 409]

        assert statuses == [201, 409]
        assert codes == ["QIT001008"]
        assert ObjectGenerator.get_balance(origin) == 0
        assert ObjectGenerator.get_balance(first_destination) + ObjectGenerator.get_balance(second_destination) == 1000

    def test_simultaneous_same_key_with_different_accounts_only_one_passes(self):
        first_origin = ObjectGenerator.create_student_account(balance=5000)
        second_origin = ObjectGenerator.create_student_account(balance=5000)
        destination = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        results = send_simultaneously(
            [
                (
                    PayloadGenerator.create_transfer_payload(
                        origin_account_key=first_origin,
                        destination_account_key=destination,
                        value=1000,
                    ),
                    idempotency_key,
                ),
                (
                    PayloadGenerator.create_transfer_payload(
                        origin_account_key=second_origin,
                        destination_account_key=destination,
                        value=1000,
                    ),
                    idempotency_key,
                ),
            ]
        )

        statuses = sorted(status for status, _ in results)
        codes = [response["code"] for status, response in results if status == 409]

        assert statuses == [201, 409]
        assert codes == ["QIT001010"]
        assert ObjectGenerator.get_balance(destination) == 1000
        assert ObjectGenerator.get_balance(first_origin) + ObjectGenerator.get_balance(second_origin) == 8800
