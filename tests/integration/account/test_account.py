from uuid import uuid4

from tests.utils import DbUtils, PayloadGenerator, RequestGenerator, ObjectGenerator
from tests.utils.mock_generator import UniversityMock
from tests.utils.mock_utils import Mock

def extract_keys(response: dict) -> list:
    """As chaves da pagina, na ordem em que a API devolveu."""
    sample_entity_keys = []
    for sample_entity in response["data"]:
        sample_entity_keys.append(sample_entity["sample_entity_key"])
    return sample_entity_keys

class TestAccount:
    def test_creates_account(self):
        
        student_key = ObjectGenerator.create_student()["student_key"]
        status, response = RequestGenerator.POST_account({
            "student_key": student_key
        })

        assert status == 201
        assert "account_key" in response
        assert response["status"] == "ACTIVE"
