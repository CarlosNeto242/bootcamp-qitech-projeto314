from sqlalchemy.exc import IntegrityError

from controllers.base_controller import BaseController
from dtos import TransactionDTO
from errors import (
    ClosedAccount,
    DeniedDeposit,
    DuplicatedIdempotencyKey,
    StudentOrAccountDoesNotExist,
)
from models import Account, Transaction
from repositories import AccountRepository, TransactionRepository

IDEMPOTENCY_KEY_CONSTRAINT = "uq_transaction_idempotency_key"


class DepositController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transaction_repository = TransactionRepository(self.context)

    def create(self, payload: dict, idempotency_key: str) -> dict:
        account_key = payload["account_key"].lower()
        value = payload["value"]
        idempotency_key = idempotency_key.lower()

        self.session.connection(execution_options={"isolation_level": "READ COMMITTED"})

        account = self.account_repository.get_by_key(account_key)

        if account is None:
            raise StudentOrAccountDoesNotExist()

        if account.type == Account.INSTITUTIONAL:
            raise DeniedDeposit()

        self.account_repository.lock_by_ids([account.id])

        duplicated_or_retry = self.transaction_repository.get_by_idempotency_key(idempotency_key)
        if duplicated_or_retry is not None:
            is_retry = (
                duplicated_or_retry.transaction_type == Transaction.DEPOSIT
                and duplicated_or_retry.value == value
                and duplicated_or_retry.destination_account_id == account.id
            )
            if not is_retry:
                raise DuplicatedIdempotencyKey()
            transaction_dto = TransactionDTO.only_obj_key(duplicated_or_retry)
            self.session.commit()
            return transaction_dto

        if account.status == Account.CLOSED:
            raise ClosedAccount()

        try:
            deposit = self.transaction_repository.create(
                Transaction.DEPOSIT,
                value,
                account.id,
                idempotency_key=idempotency_key,
            )
        except IntegrityError as error:
            if error.orig.diag.constraint_name == IDEMPOTENCY_KEY_CONSTRAINT:
                raise DuplicatedIdempotencyKey()
            raise

        transaction_dto = TransactionDTO.only_obj_key(deposit)
        self.session.commit()

        return transaction_dto
