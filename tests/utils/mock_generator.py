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

    @staticmethod
    def GET_university_student_not_found(document_number: str):
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/student/{document_number}",
                status_code=404,
                response_json={},
            )
        )

    @staticmethod
    def GET_university_student_server_error(document_number: str):
        Mock().add_expectations(
            BaseExpectation.generate_expectation(
                "GET",
                f"/student/{document_number}",
                status_code=500,
                response_json={},
            )
        )

    @staticmethod
    def GET_university_student_timeout(document_number: str, delay_seconds: int = 7):
        expectation = BaseExpectation.generate_expectation(
            "GET",
            f"/student/{document_number}",
            status_code=200,
            response_json={"name": "Aluno Exemplo", "document_number": document_number},
        )
        expectation["httpResponse"]["delay"] = {"timeUnit": "SECONDS", "value": delay_seconds}
        Mock().add_expectations(expectation)

    @staticmethod
    def GET_university_student_connection_dropped(document_number: str):
        Mock().add_expectations(
            BaseExpectation.generate_error(
                "GET",
                f"/student/{document_number}",
                error_json={"dropConnection": True},
            )
        )
