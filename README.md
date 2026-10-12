# Banco universitário: API

API REST de um serviço bancário universitário, feita no Bootcamp da QI Tech a partir do `base-service` (Python, FastAPI, SQLAlchemy e PostgreSQL, em Docker). O estudante se cadastra, cria uma conta, deposita, transfere (com tarifa de R$ 2,00), consulta saldo e extrato e encerra a conta.

Do clone aos testes verdes:

```
git clone  →  docker compose up  →  pytest  →  verde
```

---

## 1. O que você precisa ter instalado

| Programa | Para quê | Como conferir |
|---|---|---|
| **Docker** (Docker Desktop no Windows e no Mac) | Roda a API, o banco e o mock da universidade | `docker compose version` |
| **Git** | Baixar o projeto | `git --version` |
| **Python 3.11 ou mais novo** | Rodar os testes | `python --version` |

Os testes rodam **na sua máquina**, contra a API que está de pé no Docker.

No Windows, o Docker Desktop precisa do WSL2 e do recurso "Plataforma de Máquina Virtual". Se ele pedir para ativar, ative e reinicie o computador.

---

## 2. Subir a API

```bash
git clone https://github.com/CarlosNeto242/bootcamp-qitech-projeto314
cd bootcamp-qitech-projeto314
docker compose up
```

Espere os serviços aparecerem como `(healthy)`. Os serviços são:

| Serviço | Endereço na sua máquina | O que é |
|---|---|---|
| `api` | `http://localhost:3000` | A API |
| `db` | `localhost:5432` (usuário, senha e banco: `bootcamp`) | PostgreSQL 16 |
| `mock` | `http://localhost:1080` | Mockserver que simula o servidor da universidade |

Para conferir: `curl -i http://localhost:3000/health_check` deve responder `204`.

Para desligar: `Ctrl+C` e depois `docker compose down`. Para desligar **e apagar o banco**: `docker compose down -v`.

> **Mudou o `database/database.sql`?** O banco só lê esse arquivo quando é criado. Recrie com `docker compose down -v` e depois `docker compose up --build`.

---

## 3. Rodar os testes

Os testes precisam de três bibliotecas que não vêm com o Python: `pytest`, `requests` e `python-dotenv`. Se o seu Python já tem as três, pule direto para o `pytest`. Senão, instale **uma vez só**, na raiz do projeto, por um dos dois caminhos:

**Opção A: direto no Python da máquina (mais simples)**

```bash
pip install -r requirements-dev.txt
```

**Opção B: num ambiente virtual (isola as bibliotecas deste projeto)**

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux ou Mac
pip install -r requirements-dev.txt
```

Na opção B, ative o ambiente sempre que abrir um terminal novo para rodar os testes.

**Toda vez, com a API de pé, em outro terminal:**

```bash
pytest
```

Todos os testes devem passar. Para rodar só uma parte:

```bash
pytest tests/integration/transfer -v      # só uma rota
pytest -k simultaneous -v                 # só os de concorrência
pytest -x                                 # para no primeiro erro
```

**Como os testes funcionam:**
- São testes de integração: cada um chama a API **por HTTP**, como um cliente faria. Nenhum teste lê ou escreve direto no banco.
- Cada teste cria as próprias contas pelas rotas (`tests/utils/object_generator.py`), então eles não dependem de banco limpo e podem ser rodados várias vezes seguidas.
- O servidor da universidade é o mockserver. Os testes registram nele a resposta que querem (aluno, não aluno, fora do ar, lento).
- O teste de timeout da universidade demora cerca de 5 segundos de propósito.

Para acompanhar o que a API está fazendo durante os testes: `docker compose logs -f api`.

---

## 4. Usar a API manualmente

Toda rota, exceto `/` e `/health_check`, exige o header `INTERNAL-TOKEN: default_token`. Sem ele, a resposta é `403`. Valores são em **centavos**.

| Método | Rota | O que faz |
|---|---|---|
| `POST` | `/student` | Cadastra um estudante (`name`, `document_number` no formato `000.000.000-00`) |
| `POST` | `/account` | Cria a conta do estudante (`student_key`) |
| `POST` | `/deposit` | Deposita (`account_key`, `value`) |
| `POST` | `/transfer` | Transfere com tarifa de 200 (`origin_account_key`, `destination_account_key`, `value`) |
| `GET` | `/account/{account_key}` | Conta e saldo |
| `GET` | `/account/{account_key}/transactions?page=0&limit=10` | Extrato paginado |
| `POST` | `/account/{account_key}/close` | Encerra a conta (só com saldo zero) |

`/deposit` e `/transfer` exigem também o header `Idempotency-Key` com um UUID novo a cada operação. Repetir a mesma chave com os mesmos dados devolve a transação original, sem mover o dinheiro de novo.

**Exemplo completo (Git Bash, Linux ou Mac):**

```bash
# 1. Dizer ao mock da universidade que este CPF é de um aluno
curl -X PUT http://localhost:1080/mockserver/expectation \
  -d '{"httpRequest": {"method": "GET", "path": "/student/529.982.247-25"},
       "httpResponse": {"statusCode": 200, "body": {"name": "Maria da Silva"}}}'

# 2. Cadastrar o estudante (devolve student_key)
curl -X POST http://localhost:3000/student \
  -H "INTERNAL-TOKEN: default_token" -H "Content-Type: application/json" \
  -d '{"name": "Maria da Silva", "document_number": "529.982.247-25"}'

# 3. Criar a conta (devolve account_key)
curl -X POST http://localhost:3000/account \
  -H "INTERNAL-TOKEN: default_token" -H "Content-Type: application/json" \
  -d '{"student_key": "<student_key>"}'

# 4. Depositar R$ 50,00
curl -X POST http://localhost:3000/deposit \
  -H "INTERNAL-TOKEN: default_token" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(python -c 'import uuid; print(uuid.uuid4())')" \
  -d '{"account_key": "<account_key>", "value": 5000}'

# 5. Pagar R$ 10,00 na cantina (mais R$ 2,00 de tarifa)
curl -X POST http://localhost:3000/transfer \
  -H "INTERNAL-TOKEN: default_token" -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(python -c 'import uuid; print(uuid.uuid4())')" \
  -d '{"origin_account_key": "<account_key>", "destination_account_key": "06d8b86d-6d68-402d-9c8a-e089230f16ce", "value": 1000}'

# 6. Ver o saldo e o extrato
curl http://localhost:3000/account/<account_key> -H "INTERNAL-TOKEN: default_token"
curl "http://localhost:3000/account/<account_key>/transactions" -H "INTERNAL-TOKEN: default_token"
```

As contas institucionais já vêm no banco:

| Conta | `account_key` |
|---|---|
| Universidade (recebe só as tarifas) | `26ccf53d-7a91-41bf-acc2-09a93743f423` |
| Cantina | `06d8b86d-6d68-402d-9c8a-e089230f16ce` |
| Estacionamento | `e2f33a85-efb7-4bc5-afde-4ffe5229f7f3` |

No Windows, use o **Git Bash** para esses comandos. No PowerShell, `curl` é outro programa, com outra sintaxe.

---

## 5. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `Não consegui falar com a API` | A API não está de pé, ou ainda não está `healthy`. Rode `docker compose up` e espere |
| `docker` não é reconhecido | O Docker Desktop não está aberto, ou o terminal foi aberto antes da instalação |
| `port is already allocated` | Outra coisa usa a porta. Crie um `.env` com `API_PORT=3001` (ou `DB_PORT`, `MOCK_PORT`) |
| `pytest` não é reconhecido, ou `No module named 'requests'` | As bibliotecas de teste não estão instaladas: rode `pip install -r requirements-dev.txt`. Se você usou o ambiente virtual (opção B), ele não está ativado |
| Testes de concorrência falham com `500` | O banco foi criado com um `database.sql` antigo. Recrie com `docker compose down -v` e `docker compose up --build` |

---

## 6. Onde está cada coisa

```
database/database.sql    esquema do banco e contas institucionais
src/app.py               lista de rotas
src/schemas/             validação dos corpos e da query string (JSON Schema)
src/resources/           entrada HTTP de cada rota
src/controllers/         regras de negócio
src/repositories/        consultas ao banco
src/models/ e src/dtos/  tabelas e formato das respostas
tests/integration/       testes, uma pasta por rota
tests/utils/             helpers dos testes (requisições, payloads, mock)
direcionamento/          documentos de apoio, incluindo o material da RFC
```

A organização das camadas segue o `base-service` e está explicada em `docs/como-o-projeto-e-organizado.md`.
