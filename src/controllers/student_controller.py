from sqlalchemy.exc import IntegrityError

from connectors.university_connector import UniversityConnector
from controllers.base_controller import BaseController
from dtos.student_dto import StudentDTO
from errors import DuplicatedDocumentNumber, StudentNotVerified, UniversityUnavailable
from repositories.student_repository import StudentRepository

DOCUMENT_NUMBER_CONSTRAINT = "student_document_number_key"


class StudentController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.student_repository = StudentRepository(self.context)
        self.university_connector = UniversityConnector()

    def create(self, student_data: dict) -> dict:
        university_response = self.university_connector.get_by_document_number(student_data["document_number"])

        if university_response.status == 404:
            raise StudentNotVerified()

        if university_response.status != 200:
            raise UniversityUnavailable()

        try:
            student = self.student_repository.create(student_data=student_data)
        except IntegrityError as error:
            if error.orig.diag.constraint_name == DOCUMENT_NUMBER_CONSTRAINT:
                raise DuplicatedDocumentNumber()
            raise

        student_dto = StudentDTO.only_obj_key(student)
        self.session.commit()

        return student_dto
