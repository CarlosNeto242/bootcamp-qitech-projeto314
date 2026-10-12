from uuid import uuid4

from tests.utils import RequestGenerator, ObjectGenerator


def extract_keys(response: dict) -> list:

    account_keys = []
    for account in response["data"]:
        account_keys.append(account["account_key"])
    return account_keys

class TestAccount:
    def test_creates_account(self):
        
        student_key = ObjectGenerator.create_student()["student_key"]
        status, response = RequestGenerator.POST_account({
            "student_key": student_key
        })

        assert status == 201
        assert "account_key" in response
        assert response["status"] == "ACTIVE"
