from models.transaction import Transaction

class TransactionDTO:

    @staticmethod
    def only_obj_key(transaction: Transaction) -> dict:
        return{
            "transaction_key": transaction.transaction_key,
        }