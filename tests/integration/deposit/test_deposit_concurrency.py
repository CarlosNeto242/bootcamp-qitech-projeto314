from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from tests.utils import ObjectGenerator, PayloadGenerator, RequestGenerator


def send_simultaneously(requests: list) -> list:
    barrier = Barrier(len(requests))

    def send(request):
        payload, idempotency_key = request
        barrier.wait()
        return RequestGenerator.POST_deposit(payload, idempotency_key=idempotency_key)

    with ThreadPoolExecutor(max_workers=len(requests)) as executor:
        return list(executor.map(send, requests))


class TestDepositConcurrency:
    def test_simultaneous_same_key_with_different_accounts_only_one_passes(self):
        first_account = ObjectGenerator.create_student_account()
        second_account = ObjectGenerator.create_student_account()
        idempotency_key = str(uuid4())

        results = send_simultaneously(
            [
                (PayloadGenerator.create_deposit_payload(account_key=first_account, value=1000), idempotency_key),
                (PayloadGenerator.create_deposit_payload(account_key=second_account, value=1000), idempotency_key),
            ]
        )

        statuses = sorted(status for status, _ in results)
        codes = [response["code"] for status, response in results if status == 409]

        assert statuses == [201, 409]
        assert codes == ["QIT001010"]
        assert ObjectGenerator.get_balance(first_account) + ObjectGenerator.get_balance(second_account) == 1000
