from uuid import uuid4

from database import Context
from models import Transaction


class TransactionRepository:
    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def get_by_idempotency_key(self, idempotency_key: str) -> Transaction:
        return self.session.query(Transaction).filter(Transaction.idempotency_key == idempotency_key).first()

    def create(
        self,
        transaction_type: str,
        value: int,
        destination_account_id: int,
        origin_account_id: int = None,
        related_transaction_id: int = None,
        idempotency_key: str = None,
    ) -> Transaction:
        transaction = Transaction()

        transaction.transaction_key = str(uuid4())
        transaction.transaction_type = transaction_type
        transaction.value = value
        transaction.origin_account_id = origin_account_id
        transaction.destination_account_id = destination_account_id
        transaction.related_transaction_id = related_transaction_id
        transaction.idempotency_key = idempotency_key or transaction.transaction_key

        self.session.add(transaction)
        self.session.flush()

        return transaction
