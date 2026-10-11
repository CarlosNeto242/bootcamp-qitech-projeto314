from uuid import uuid4

from sqlalchemy import create_engine, text

from tests.utils.db_utils import DbUtils
from tests.utils.random_generator import RandomGenerator

UNIVERSITY_ACCOUNT_KEY = "26ccf53d-7a91-41bf-acc2-09a93743f423"
CANTEEN_ACCOUNT_KEY = "06d8b86d-6d68-402d-9c8a-e089230f16ce"
PARKING_ACCOUNT_KEY = "e2f33a85-efb7-4bc5-afde-4ffe5229f7f3"


class ObjectGenerator:
    @staticmethod
    def _execute(query: str, params: dict = None):
        engine = create_engine(DbUtils.database_url())

        try:
            with engine.begin() as connection:
                result = connection.execute(text(query), params or {})

                if not result.returns_rows:
                    return []

                return result.fetchall()
        finally:
            engine.dispose()

    @staticmethod
    def create_student_account(balance: int = 0, name: str = "Maria da Silva") -> str:
        account_key = str(uuid4())
        engine = create_engine(DbUtils.database_url())

        try:
            with engine.begin() as connection:
                student_id = connection.execute(
                    text(
                        "INSERT INTO student (student_key, name, document_number) "
                        "VALUES (:student_key, :name, :document_number) RETURNING id"
                    ),
                    {
                        "student_key": str(uuid4()),
                        "name": name,
                        "document_number": RandomGenerator.generate_cpf(),
                    },
                ).scalar()

                account_id = connection.execute(
                    text(
                        "INSERT INTO account (account_key, student_id, type, status) "
                        "VALUES (:account_key, :student_id, 'STUDENT', 'ACTIVE') RETURNING id"
                    ),
                    {"account_key": account_key, "student_id": student_id},
                ).scalar()

                if balance > 0:
                    connection.execute(
                        text(
                            "INSERT INTO transaction "
                            "(transaction_key, transaction_type, value, destination_account_id, idempotency_key) "
                            "VALUES (:transaction_key, 'DEPOSIT', :value, :account_id, :idempotency_key)"
                        ),
                        {
                            "transaction_key": str(uuid4()),
                            "value": balance,
                            "account_id": account_id,
                            "idempotency_key": str(uuid4()),
                        },
                    )
        finally:
            engine.dispose()

        return account_key

    @staticmethod
    def get_balance(account_key: str) -> int:
        rows = ObjectGenerator._execute(
            "SELECT COALESCE(SUM(CASE WHEN t.destination_account_id = a.id THEN t.value END), 0) "
            "     - COALESCE(SUM(CASE WHEN t.origin_account_id = a.id THEN t.value END), 0) "
            "FROM account a "
            "LEFT JOIN transaction t ON t.destination_account_id = a.id OR t.origin_account_id = a.id "
            "WHERE a.account_key = :account_key",
            {"account_key": account_key},
        )
        return rows[0][0]

    @staticmethod
    def deposit(account_key: str, value: int) -> None:
        ObjectGenerator._execute(
            "INSERT INTO transaction "
            "(transaction_key, transaction_type, value, destination_account_id, idempotency_key) "
            "VALUES (:transaction_key, 'DEPOSIT', :value, "
            "(SELECT id FROM account WHERE account_key = :account_key), :idempotency_key)",
            {
                "transaction_key": str(uuid4()),
                "value": value,
                "account_key": account_key,
                "idempotency_key": str(uuid4()),
            },
        )

    @staticmethod
    def close_account(account_key: str) -> None:
        ObjectGenerator._execute(
            "UPDATE account SET status = 'CLOSED' WHERE account_key = :account_key",
            {"account_key": account_key},
        )

    @staticmethod
    def list_transactions(account_key: str) -> list:
        rows = ObjectGenerator._execute(
            "SELECT t.transaction_key, t.transaction_type, t.value, "
            "       origin.account_key, destination.account_key, related.transaction_key, t.idempotency_key "
            "FROM transaction t "
            "LEFT JOIN account origin ON origin.id = t.origin_account_id "
            "JOIN account destination ON destination.id = t.destination_account_id "
            "LEFT JOIN transaction related ON related.id = t.related_transaction_id "
            "WHERE origin.account_key = :account_key OR destination.account_key = :account_key "
            "ORDER BY t.id",
            {"account_key": account_key},
        )

        return [
            {
                "transaction_key": row[0],
                "transaction_type": row[1],
                "value": row[2],
                "origin_account_key": row[3],
                "destination_account_key": row[4],
                "related_transaction_key": row[5],
                "idempotency_key": row[6],
            }
            for row in rows
        ]
