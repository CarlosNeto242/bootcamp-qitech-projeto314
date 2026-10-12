from uuid import uuid4

from database import Context 
from models.student import Student 

class StudentRepository:
    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, student_data: dict) -> Student:
        student = Student()

        student.student_key = str(uuid4())
        student.name = student_data["name"]
        student.document_number = student_data["document_number"]

        self.session.add(student)
        self.session.flush()

        return student

    def get_by_key(self, student_key: str) -> Student:
        return self.session.query(Student).filter(Student.student_key == student_key).first()

    def get_by_document_number(self, document_number: str) -> Student:
        return self.session.query(Student).filter(Student.document_number == document_number).first()

    def list_page(self, limit: int, offset: int) -> list:
        query = self.session.query(Student).order_by(Student.created_at.desc(), Student.id.desc())

        return query.limit(limit + 1).offset(offset).all()