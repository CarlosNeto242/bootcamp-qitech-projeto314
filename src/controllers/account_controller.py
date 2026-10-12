from controllers.base_controller import BaseController
from dtos.account_dto import AccountDTO
from errors import StudentOrAccountDoesNotExist
from repositories.account_repository import AccountRepository
from repositories.student_repository import StudentRepository


class AccountController(BaseController):

    def __init__(self) -> None:
        super().__init__(__name__)

        self.account_repository = AccountRepository(self.context)
        self.student_repository = StudentRepository(self.context)

    def create(self, account_data: dict) -> dict:

        self.logger.debug("Criando uma nova conta")

        student_key = account_data["student_key"]

        student = self.student_repository.get_by_key(student_key)

        if student is None:
            raise StudentOrAccountDoesNotExist(student_key)

        account = self.account_repository.create(student=student)

        account_dto = AccountDTO.only_obj_key(account)
        self.session.commit()

        return account_dto