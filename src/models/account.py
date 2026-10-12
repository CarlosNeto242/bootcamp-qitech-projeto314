from sqlalchemy import CHAR, CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func

from models.base import Base


class Account(Base):
    __tablename__ = "account"

    STUDENT = "STUDENT"
    INSTITUTIONAL = "INSTITUTIONAL"

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

    id = Column(Integer, primary_key=True)
    account_key = Column(CHAR(36), nullable=False)
    student_id = Column(Integer, ForeignKey("student.id"))
    type = Column(Enum(STUDENT, INSTITUTIONAL, name="account_type", create_type=False), nullable=False)
    status = Column(Enum(ACTIVE, CLOSED, name="account_status", create_type=False), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("account_key"),
        UniqueConstraint("student_id"),
        CheckConstraint(
            "(type = 'STUDENT' AND student_id IS NOT NULL) OR "
            "(type = 'INSTITUTIONAL' AND student_id IS NULL)"
        ),
    )
