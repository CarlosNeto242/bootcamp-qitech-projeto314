from errors import QIException


class StudentOrAccountDoesNotExist(QIException):
    code = "QIT001001"

    def __init__(self) -> None:
        title = "Student Or Account Does Not Exist"
        http_status = 404
        description = "The referenced student or account does not exist."
        translation = "O estudante ou a conta informada não existe."
        super().__init__(title, self.code, http_status, description, translation)


class ClosedAccount(QIException):
    code = "QIT001002"

    def __init__(self) -> None:
        title = "Closed Account"
        http_status = 409
        description = "The account is closed and cannot be moved."
        translation = "A conta está encerrada e não pode ser movimentada."
        super().__init__(title, self.code, http_status, description, translation)


class NotEnoughMoney(QIException):
    code = "QIT001008"

    def __init__(self) -> None:
        title = "Not Enough Money"
        http_status = 409
        description = "The origin account balance is not enough for the value plus the fee."
        translation = "O saldo da conta de origem não é suficiente para o valor mais a tarifa."
        super().__init__(title, self.code, http_status, description, translation)


class DuplicatedAccount(QIException):
    code = "QIT001009"

    def __init__(self) -> None:
        title = "Duplicated Account"
        http_status = 409
        description = "The student already has an account."
        translation = "O estudante já possui uma conta."
        super().__init__(title, self.code, http_status, description, translation)


class DuplicatedIdempotencyKey(QIException):
    code = "QIT001010"

    def __init__(self) -> None:
        title = "Duplicated Idempotency Key"
        http_status = 409
        description = "The idempotency key has already been used in another operation."
        translation = "A chave de idempotência já foi usada em outra operação."
        super().__init__(title, self.code, http_status, description, translation)


class DeniedDeposit(QIException):
    code = "QIT001011"

    def __init__(self) -> None:
        title = "Denied Deposit"
        http_status = 409
        description = "The account cannot receive deposits."
        translation = "A conta não pode receber depósitos."
        super().__init__(title, self.code, http_status, description, translation)


class DeniedOriginAccount(QIException):
    code = "QIT001012"

    def __init__(self) -> None:
        title = "Denied Origin Account"
        http_status = 409
        description = "The origin account cannot transfer."
        translation = "A conta de origem não pode transferir."
        super().__init__(title, self.code, http_status, description, translation)


class SelfTransfer(QIException):
    code = "QIT001013"

    def __init__(self) -> None:
        title = "Self Transfer"
        http_status = 409
        description = "The account cannot transfer to itself."
        translation = "A conta não pode transferir para si mesma."
        super().__init__(title, self.code, http_status, description, translation)


class DeniedDestinationAccount(QIException):
    code = "QIT001015"

    def __init__(self) -> None:
        title = "Denied Destination Account"
        http_status = 409
        description = "The destination account cannot receive transfers."
        translation = "A conta de destino não pode receber transferências."
        super().__init__(title, self.code, http_status, description, translation)
