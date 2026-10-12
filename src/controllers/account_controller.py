from sqlalchemy.exc import IntegrityError

from controllers.base_controller import BaseController
from dtos.account_dto import AccountDTO
from errors import DuplicatedAccount, StudentOrAccountDoesNotExist
from repositories.account_repository import AccountRepository
from repositories.student_repository import StudentRepository

STUDENT_ID_CONSTRAINT = "account_student_id_key"


class AccountController(BaseController):
    def __init__(self) -> None:
        super().__init__(__name__)
        self.account_repository = AccountRepository(self.context)
        self.student_repository = StudentRepository(self.context)

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
