from uuid import uuid4

from tests.utils import DbUtils, PayloadGenerator, RequestGenerator
from tests.utils.mock_generator import UniversityMock
from tests.utils.mock_utils import Mock

def extract_keys(response: dict) -> list:
    """As chaves da pagina, na ordem em que a API devolveu."""
    sample_entity_keys = []
    for sample_entity in response["data"]:
        sample_entity_keys.append(sample_entity["sample_entity_key"])
    return sample_entity_keys

class TestStudent: 
    def test_creates_student(self):
        Mock().clear()

        name = "Aluno Exemplo"
        document_number = "123.456.789-10"

        UniversityMock.GET_university_student(document_number)
        
        status, response = RequestGenerator.POST_student({"name": name, "document_number" : document_number})

        print(response)

        assert status == 201
        assert "student_key" in response