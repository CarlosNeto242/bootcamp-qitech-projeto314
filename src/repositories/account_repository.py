from uuid import uuid4

from database import Context
from models.account import Account
from models.student import Student


class AccountRepository:

    def __init__(self, context: Context) -> None:
        self.session = context.db_session

    def create(self, student: Student) -> Account:
        account = Account()

        account.account_key = str(uuid4())
        account.student_id = student.id
        account.type = "STUDENT"
        account.status = "ACTIVE"

        self.session.add(account)

        return account