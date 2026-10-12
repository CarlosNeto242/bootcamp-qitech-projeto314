from models.account import Account


class AccountDTO:

    @staticmethod
    def only_obj_key(account: Account) -> dict:
        return {
            "account_key": account.account_key,
            "status": account.status,
        }