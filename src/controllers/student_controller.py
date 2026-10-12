from connectors.university_connector import UniversityConnector
from controllers.base_controller import BaseController
from dtos.student_dto import StudentDTO
from errors import (
    InvalidDocumentNumber,
    DuplicatedDocumentNumber,
    StudentNotVerified,
    UniversityUnavailable,
)
from repositories.student_repository import StudentRepository
from utils.document_number import is_valid_cpf


class StudentController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)

        self.student_repository = StudentRepository(self.context)
        self.university_connector = UniversityConnector()

    def create(self, student_data: dict) -> dict:
 
        self.logger.debug("Criando uma novo estudante")

        document_number = student_data["document_number"]
        name = student_data["name"]

        university_response = self.university_connector.get_by_document_number(document_number)

        if university_response.status != 200:
            raise StudentNotVerified(document_number)

        if not is_valid_cpf(document_number):
            raise InvalidDocumentNumber(document_number)

        if self.student_repository.get_by_document_number(document_number) is not None:
            raise DuplicatedDocumentNumber(document_number)

        student = self.student_repository.create(student_data=student_data)

        student_dto = StudentDTO.only_obj_key(student)
        self.session.commit()

        return student_dto
