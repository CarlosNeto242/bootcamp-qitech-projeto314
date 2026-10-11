from tests.utils.mock_utils import BaseExpectation, Mock

class UniversityMock:

    @staticmethod
    def GET_university_student(document_number: str):

        mock = Mock()

        mock.add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/student/{document_number}",
                status_code=200,
                response_json={
                    "name": "Aluno Exemplo",
                    "document_number": document_number,
                },
            )
        )