from sqlalchemy import CHAR, CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint, func

from models.base import Base


class Transaction(Base):
    __tablename__ = "transaction"

    DEPOSIT = "DEPOSIT"
    TRANSFER = "TRANSFER"
    FEE = "FEE"

    id = Column(Integer, primary_key=True)
    transaction_key = Column(CHAR(36), nullable=False)
    transaction_type = Column(Enum(DEPOSIT, TRANSFER, FEE, name="transaction_type", create_type=False), nullable=False)
    value = Column(Integer, nullable=False)
    origin_account_id = Column(Integer, ForeignKey("account.id"))
    destination_account_id = Column(Integer, ForeignKey("account.id"), nullable=False)
    related_transaction_id = Column(Integer, ForeignKey("transaction.id"))
    idempotency_key = Column(CHAR(36), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("transaction_key"),
        UniqueConstraint("idempotency_key"),
        CheckConstraint("value > 0"),
    )
