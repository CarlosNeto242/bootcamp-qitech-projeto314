from uuid import uuid4

from tests.utils import RequestGenerator
from tests.utils.mock_generator import UniversityMock
from tests.utils.mock_utils import Mock

def extract_keys(response: dict) -> list:
    student_keys = []
    for student in response["data"]:
        student_keys.append(student["account_key"])
    return student_keys

class TestStudent: 
    def test_creates_student(self):
        Mock().clear()

        name = "Aluno Exemplo"
        document_number = "529.982.247-25"

        UniversityMock.GET_university_student(document_number)
        
        status, response = RequestGenerator.POST_student({"name": name, "document_number" : document_number})

        assert status == 201
        assert "student_key" in response