from sqlalchemy.exc import IntegrityError

from constants import FEE_ACCOUNT_KEY
from controllers.base_controller import BaseController
from dtos import TransactionDTO
from errors import (
    ClosedAccount,
    DeniedDestinationAccount,
    DeniedOriginAccount,
    DuplicatedIdempotencyKey,
    InternalError,
    NotEnoughMoney,
    SelfTransfer,
    StudentOrAccountDoesNotExist,
)
from models import Account, Transaction
from repositories import AccountRepository, TransactionRepository

FEE_VALUE = 200
IDEMPOTENCY_KEY_CONSTRAINT = "transaction_idempotency_key_key"


class TransferController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.transaction_repository = TransactionRepository(self.context)

    def create(self, payload: dict, idempotency_key: str) -> dict:
        origin_key = payload["origin_account_key"].lower()
        destination_key = payload["destination_account_key"].lower()
        value = payload["value"]
        idempotency_key = idempotency_key.lower()

        if origin_key == destination_key:
            raise SelfTransfer()

        if destination_key == FEE_ACCOUNT_KEY:
            raise DeniedDestinationAccount()

        self.session.connection(execution_options={"isolation_level": "READ COMMITTED"})

        account_keys = [origin_key, destination_key, FEE_ACCOUNT_KEY]
        accounts = {}
        for account in self.account_repository.get_by_keys(account_keys):
            accounts[account.account_key] = account

        origin = accounts.get(origin_key)
        destination = accounts.get(destination_key)
        fee_account = accounts.get(FEE_ACCOUNT_KEY)

        if origin is None or destination is None:
            raise StudentOrAccountDoesNotExist()

        if fee_account is None:
            raise InternalError()

        if origin.type == Account.INSTITUTIONAL:
            raise DeniedOriginAccount()

        student_ids = [a.id for a in (origin, destination) if a.type == Account.STUDENT]
        self.account_repository.lock_by_ids(student_ids)

        duplicated_or_retry = self.transaction_repository.get_by_idempotency_key(idempotency_key)
        if duplicated_or_retry is not None:
            is_retry = (
                duplicated_or_retry.transaction_type == Transaction.TRANSFER
                and duplicated_or_retry.value == value
                and duplicated_or_retry.origin_account_id == origin.id
                and duplicated_or_retry.destination_account_id == destination.id
            )
            if not is_retry:
                raise DuplicatedIdempotencyKey()
            transaction_dto = TransactionDTO.only_obj_key(duplicated_or_retry)
            self.session.commit()
            return transaction_dto

        if origin.status == Account.CLOSED or destination.status == Account.CLOSED:
            raise ClosedAccount()

        if self.account_repository.get_balance(origin.id) < value + FEE_VALUE:
            raise NotEnoughMoney()

        try:
            transfer = self.transaction_repository.create(
                Transaction.TRANSFER,
                value,
                destination.id,
                origin_account_id=origin.id,
                idempotency_key=idempotency_key,
            )
        except IntegrityError as error:
            if error.orig.diag.constraint_name == IDEMPOTENCY_KEY_CONSTRAINT:
                raise DuplicatedIdempotencyKey()
            raise

        self.transaction_repository.create(
            Transaction.FEE,
            FEE_VALUE,
            fee_account.id,
            origin_account_id=origin.id,
            related_transaction_id=transfer.id,
        )

        transaction_dto = TransactionDTO.only_obj_key(transfer)
        self.session.commit()

        return transaction_dto
