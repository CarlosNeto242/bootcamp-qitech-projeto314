from sqlalchemy.exc import IntegrityError

from controllers.base_controller import BaseController
from dtos import TransactionDTO
from dtos.account_dto import AccountDTO
from errors import (
    AccountWithBalance,
    ClosedAccount,
    DeniedAccountClosing,
    DuplicatedAccount,
    StudentOrAccountDoesNotExist,
)
from models import Account
from repositories.account_repository import AccountRepository
from repositories.student_repository import StudentRepository
from repositories.transaction_repository import TransactionRepository

STUDENT_ID_CONSTRAINT = "account_student_id_key"


class AccountController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.student_repository = StudentRepository(self.context)
        self.transaction_repository = TransactionRepository(self.context)

    def create(self, account_data: dict) -> dict:
        student = self.student_repository.get_by_key(account_data["student_key"])

        if student is None:
            raise StudentOrAccountDoesNotExist()

        try:
            account = self.account_repository.create(student=student)
        except IntegrityError as error:
            if error.orig.diag.constraint_name == STUDENT_ID_CONSTRAINT:
                raise DuplicatedAccount()
            raise

        account_dto = AccountDTO.only_obj_key(account)
        self.session.commit()

        return account_dto

    def get_by_key(self, account_key: str) -> dict:
        account = self._get_open_account(account_key)
        balance = self.account_repository.get_balance(account.id)

        return AccountDTO.obj_to_dict(account, balance)

    def get_transactions(self, account_key: str, limit: int, offset: int) -> dict:
        account = self._get_open_account(account_key)

        rows = self.transaction_repository.list_page_by_account(account.id, limit + 1, offset)

        is_last_page = True
        if len(rows) > limit:
            is_last_page = False
            rows = rows[:-1]

        return {
            "statement_lines_dto": TransactionDTO.list_statement_lines(rows),
            "is_last_page": is_last_page,
        }

    def close(self, account_key: str) -> dict:
        self.session.connection(execution_options={"isolation_level": "READ COMMITTED"})

        account = self.account_repository.get_by_key(account_key.lower())

        if account is None:
            raise StudentOrAccountDoesNotExist()

        if account.type == Account.INSTITUTIONAL:
            raise DeniedAccountClosing()

        self.account_repository.lock_by_ids([account.id])

        if account.status == Account.CLOSED:
            raise ClosedAccount()

        if self.account_repository.get_balance(account.id) != 0:
            raise AccountWithBalance()

        self.account_repository.close(account)

        account_dto = AccountDTO.only_obj_key(account)
        self.session.commit()

        return account_dto

    def _get_open_account(self, account_key: str) -> Account:
        account = self.account_repository.get_by_key(account_key.lower())

        if account is None:
            raise StudentOrAccountDoesNotExist()

        if account.status == Account.CLOSED:
            raise ClosedAccount()

        return account
