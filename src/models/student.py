from sqlalchemy import CHAR, Column, Integer, String, UniqueConstraint

from models.base import Base


class Student(Base):
    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    student_key = Column(CHAR(36), nullable=False)
    name = Column(String(255), nullable=False)
    document_number = Column(CHAR(14), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_key"),
        UniqueConstraint("document_number"),
    )
