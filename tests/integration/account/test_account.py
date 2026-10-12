import re
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

from tests.utils import ObjectGenerator, RequestGenerator

UUID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


class TestAccount:
    def test_refuses_malformed_body(self):
        malformed_payloads = [
            ("corpo vazio", {}),
            ("student_key fora do formato UUID", {"student_key": "nao-e-uuid"}),
            ("student_key numerico", {"student_key": 123}),
            ("campo extra", {"student_key": str(uuid4()), "type": "STUDENT"}),
        ]

        for case, payload in malformed_payloads:
            status, response = RequestGenerator.POST_account(payload)

            assert status == 400, f"{case}: status {status}"
            assert response["code"] == "QIT000001", f"{case}: code {response['code']}"

    def test_refuses_nonexistent_student(self):
        status, response = RequestGenerator.POST_account({"student_key": str(uuid4())})

        assert status == 404
        assert response["code"] == "QIT001001"

    def test_creates_account(self):
        student_key = ObjectGenerator.create_student()["student_key"]

        status, response = RequestGenerator.POST_account({"student_key": student_key})

        assert status == 201
        assert UUID_PATTERN.match(response["account_key"])
        assert response["status"] == "ACTIVE"

        status, account = RequestGenerator.GET_account(response["account_key"])
        assert status == 200
        assert account["type"] == "STUDENT"
        assert account["status"] == "ACTIVE"
        assert account["balance"] == 0

    def test_refuses_student_with_existing_account(self):
        student_key = ObjectGenerator.create_student()["student_key"]

        first_status, first_response = RequestGenerator.POST_account({"student_key": student_key})
        second_status, second_response = RequestGenerator.POST_account({"student_key": student_key})

        assert first_status == 201
        assert second_status == 409
        assert second_response["code"] == "QIT001009"
        status, _ = RequestGenerator.GET_account(first_response["account_key"])
        assert status == 200

    def test_simultaneous_accounts_for_same_student_only_one_passes(self):
        student_key = ObjectGenerator.create_student()["student_key"]
        barrier = Barrier(2)

        def send(_):
            barrier.wait()
            return RequestGenerator.POST_account({"student_key": student_key})

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(send, range(2)))

        statuses = sorted(status for status, _ in results)
        codes = [response["code"] for status, response in results if status == 409]

        assert statuses == [201, 409]
        assert codes == ["QIT001009"]
