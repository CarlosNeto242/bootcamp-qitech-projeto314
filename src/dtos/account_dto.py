from datetime import timezone

from models.account import Account


class AccountDTO:
    @staticmethod
    def only_obj_key(account: Account) -> dict:
        return {
            "account_key": account.account_key,
            "status": account.status,
        }

    @staticmethod
    def obj_to_dict(account: Account, balance: int) -> dict:
        return {
            "account_key": account.account_key,
            "type": account.type,
            "status": account.status,
            "balance": balance,
            "created_at": account.created_at.replace(tzinfo=timezone.utc).isoformat(),
        }
