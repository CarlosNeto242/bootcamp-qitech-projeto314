from uuid import uuid4

from sqlalchemy import text

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

    def list_page_by_account(self, account_id: int, limit: int, offset: int) -> list:
        return self.session.execute(
            text(
                "SELECT t.transaction_key, t.transaction_type, t.created_at, "
                "       CASE WHEN t.destination_account_id = :account_id THEN t.value ELSE -t.value END AS amount, "
                "       counterparty.type AS counterparty_type, "
                "       counterparty.account_key AS counterparty_account_key, "
                "       counterparty_student.name AS counterparty_name "
                "FROM transaction t "
                "LEFT JOIN account counterparty ON counterparty.id = CASE "
                "    WHEN t.destination_account_id = :account_id THEN t.origin_account_id "
                "    ELSE t.destination_account_id END "
                "LEFT JOIN student counterparty_student ON counterparty_student.id = counterparty.student_id "
                "WHERE t.destination_account_id = :account_id OR t.origin_account_id = :account_id "
                "ORDER BY t.created_at DESC, t.id DESC "
                "LIMIT :limit OFFSET :offset"
            ),
            {"account_id": account_id, "limit": limit, "offset": offset},
        ).mappings().all()
