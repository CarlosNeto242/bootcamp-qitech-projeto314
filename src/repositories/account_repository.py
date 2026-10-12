from sqlalchemy import text

from database import Context
from models import Account


class AccountRepository:
    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def get_by_key(self, account_key: str) -> Account:
        return self.session.query(Account).filter(Account.account_key == account_key).first()

    def get_by_keys(self, account_keys: list) -> list:
        return self.session.query(Account).filter(Account.account_key.in_(account_keys)).all()

    def lock_by_ids(self, account_ids: list) -> list:
        return (
            self.session.query(Account)
            .filter(Account.id.in_(account_ids))
            .order_by(Account.id)
            .with_for_update()
            .populate_existing()
            .all()
        )

    def get_balance(self, account_id: int) -> int:
        return self.session.execute(
            text(
                "SELECT COALESCE(SUM(CASE WHEN destination_account_id = :account_id THEN value END), 0) "
                "     - COALESCE(SUM(CASE WHEN origin_account_id = :account_id THEN value END), 0) "
                "FROM transaction "
                "WHERE destination_account_id = :account_id OR origin_account_id = :account_id"
            ),
            {"account_id": account_id},
        ).scalar()
