from errors import QIException


class NotFoundSampleEntity(QIException):
    code = "QIT001001"

    def __init__(self, sample_entity_key) -> None:
        title = "Entity not Found"
        http_status = 404
        description = f"Entity with key {sample_entity_key} was not found."
        translation = f"A entidade com chave {sample_entity_key} não foi encontrada."
        super().__init__(title, self.code, http_status, description, translation)


class SampleEntityFinalStatus(QIException):
    code = "QIT001002"

    def __init__(self, old_status, new_status) -> None:
        title = "Entity cannot change status"
        http_status = 409
        description = f"Entity with status {old_status} cannot update to {new_status}."
        translation = "Essa entidade não pode ser atualizada."
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


class DuplicatedEmail(QIException):
    code = "QIT001005"

    def __init__(self, email) -> None:
        title = "Email already registered"
        http_status = 409
        description = f"There is already an entity with the email {email}."
        translation = "Já existe um cadastro com este e-mail."
        super().__init__(title, self.code, http_status, description, translation)


class UnderageSampleEntity(QIException):
    code = "QIT001006"

    def __init__(self, age, minimum_age) -> None:
        title = "Entity is underage"
        http_status = 422
        description = f"The entity is {age} years old, and the minimum is {minimum_age}."
        translation = f"É preciso ter pelo menos {minimum_age} anos."
        super().__init__(title, self.code, http_status, description, translation)


class InvalidBirthdate(QIException):
    """A data tem o formato certo e não existe no calendário.

    Existe porque o `pattern` do schema sabe contar dígitos, não dias:
    "2025-02-30" e "9999-99-99" passam pelo regex e morrem no
    `date.fromisoformat`. Sem esta classe, esse ValueError virava 500 —
    a API culpando a si mesma por um erro de quem chamou.
    """

    code = "QIT001007"

    def __init__(self, birthdate) -> None:
        title = "Invalid Birthdate"
        http_status = 422
        description = f"The birthdate {birthdate} is not a real date."
        translation = "A data de nascimento informada não existe."
        super().__init__(title, self.code, http_status, description, translation)

class NotEnoughMoney(QIException):

    code = "QT001008"

    def __init__(self, balance, transaction_money):
        title = "Not Enough Money"
        http_status = 422 
        description = f"The balance of {balance}R$ is not enough to pay the {transaction_money}RS$ transaction"
        translation = "O saldo é insuficiente para completar a transferência"
        super().__init__(title, self.code, http_status, description, translation)

class DuplicatedAccount(QIException):

    code = "QT001009"

    def __init__(self, student_key):
        title = "Duplicated Account"
        http_status = 409 
        description = f"The student with key {student_key} already has an account created"
        translation = "O estudante já possui uma conta criada"
        super().__init__(title, self.code, http_status, description, translation)

class DuplicatedIdempotencyKey(QIException):

    code = "QT001010"

    def __init__(self, idempotency_key):
        title = "Duplicated Idempotency Key"
        http_status = 409 
        description = f"The idempotency key {idempotency_key} already has been used"
        translation = "O chave de idempotência está duplicada para diferentes transações"
        super().__init__(title, self.code, http_status, description, translation)

class DeniedDeposit(QIException):

    code = "QT001011"

    def __init__(self, account_key):
        title = "Denied Deposit"
        http_status = 409 
        description = f"The account {account_key} aimed for the deposit can't recieve it"
        translation = "A conta que deseja-se receber o depósito não pode recebê-lo"
        super().__init__(title, self.code, http_status, description, translation)

class DeniedOriginAccount(QIException):

    code = "QT001012"

    def __init__(self, account_key):
        title = "Denied Origin Account"
        http_status = 409 
        description = f"The account {account_key} can't transfer"
        translation = "A conta não pode transferir"
        super().__init__(title, self.code, http_status, description, translation)

class SelfTransfer(QIException):

    code = "QT001013"

    def __init__(self, account_key):
        title = "Self Transfer"
        http_status = 409 
        description = f"The account {account_key} can't trasnfer to itself"
        translation = "A conta não pode se auto-transferir"
        super().__init__(title, self.code, http_status, description, translation)

