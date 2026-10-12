from sqlalchemy import CHAR, Column, Integer, DateTime, String, UniqueConstraint, func
from models.base import Base


class Student(Base):

    __tablename__ = "student"

    id = Column(Integer, primary_key=True)
    student_key = Column(CHAR(36), nullable=False)
    name = Column(String(255), nullable=False)
    document_number = Column(CHAR(14), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


    __table_args__ = (
        UniqueConstraint("student_key"),
        UniqueConstraint("document_number"),
    )
