from datetime import timezone

from models import Account
from models.transaction import Transaction


class TransactionDTO:
    @staticmethod
    def only_obj_key(transaction: Transaction) -> dict:
        return {
            "transaction_key": transaction.transaction_key,
        }

    @staticmethod
    def statement_line(row) -> dict:
        counterparty_type = row["counterparty_type"]

        counterparty_name = None
        if counterparty_type == Account.STUDENT:
            counterparty_name = row["counterparty_name"]

        counterparty_account_key = None
        if counterparty_type == Account.INSTITUTIONAL:
            counterparty_account_key = row["counterparty_account_key"]

        return {
            "transaction_key": row["transaction_key"],
            "transaction_type": row["transaction_type"],
            "amount": row["amount"],
            "counterparty_type": counterparty_type,
            "counterparty_name": counterparty_name,
            "counterparty_account_key": counterparty_account_key,
            "created_at": row["created_at"].replace(tzinfo=timezone.utc).isoformat(),
        }

    @staticmethod
    def list_statement_lines(rows: list) -> list:
        return [TransactionDTO.statement_line(row) for row in rows]
