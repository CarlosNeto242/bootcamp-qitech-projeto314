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
        

class InvalidDocumentNumber(QIException):
    """O CPF tem o formato certo e não existe.

    422, e não 400, de propósito: 400 quer dizer "não consegui ler o seu
    pedido". Aqui a API leu, entendeu, e o valor é que não pode existir —
    os dois últimos dígitos não batem com a conta. A diferença está
    explicada em src/utils/document_number.py.
    """

    code = "QIT001003"

    def __init__(self, document_number) -> None:
        title = "Invalid Document Number"
        http_status = 422
        description = f"The document number {document_number} is not a valid CPF."
        translation = "O CPF informado não é válido."
        super().__init__(title, self.code, http_status, description, translation)


class DuplicatedDocumentNumber(QIException):
    """Já existe um cadastro com este CPF.

    409 Conflict: o pedido está correto em si, e o que impede é o que já
    está no banco. É a mesma família do SampleEntityFinalStatus aqui em
    cima — conflito com o que já existe, não erro de quem pediu.
    """

    code = "QIT001004"

    def __init__(self, document_number) -> None:
        title = "Document Number already registered"
        http_status = 409
        description = f"There is already an entity with the document number {document_number}."
        translation = "Já existe um cadastro com este CPF."
        super().__init__(title, self.code, http_status, description, translation)

class UniversityUnavailable(QIException):

    code = "QIT001014"

    def __init__(self, birthdate) -> None:
        title = "Service Unavailable"
        http_status = 503
        description = "University verification could not be completed"
        translation = "Não foi possível concluir a verificação junto à universidade"
        super().__init__(title, self.code, http_status, description, translation)

class StudentNotVerified(QIException):
    
    code = "QIT001015"

    def __init__(self, birthdate) -> None:
        title = "Unprocessable Entity"
        http_status = 422
        description = "Student could not be verified by the university"
        translation = "O estudante não foi reconhecido pela universidade"
        super().__init__(title, self.code, http_status, description, translation)