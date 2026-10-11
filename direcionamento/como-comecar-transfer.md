# Como começar a rota `POST /transfer`

Roteiro de trabalho para a rota `POST /transfer`, baseado no padrão do `base-service` (a `sample_entity` em `src/`) e nas decisões do projeto.

**Legenda das marcações:**
- **(1)** explícito no `base-service` ou nos materiais da QI Tech;
- **(2)** consequência lógica das decisões já tomadas;
- **(3)** sugestão, ainda a confirmar.

---

## 1. Como o `base-service` divide uma rota

O caminho de uma requisição está descrito em `docs/como-o-projeto-e-organizado.md` **(1)**:

```text
schemas → resources → controllers → repositories → models → banco
                                         ↓
                                       dtos → resposta
```

Cada passo do fluxo do `/transfer` cai em uma camada:

| Passo do fluxo | Camada | Arquivo |
|---|---|---|
| 1. Validar o corpo (`400`) | `schemas/` | `post_transfer.json` |
| 1. Validar o header `Idempotency-Key` | ainda não existe no `base-service` (ver ponto B, seção 3) | — |
| 2 a 8. Regras: `QIT001013`, `404`, `QIT001012`, idempotência, `CLOSED`, saldo e `commit` | `controllers/` | `transfer_controller.py` |
| `SELECT` simples, `FOR UPDATE`, busca da chave, saldo, `INSERT` da `TRANSFER` e da `FEE` | `repositories/` | `account_repository.py`, `transaction_repository.py` |
| As tabelas em Python | `models/` | `account.py`, `transaction.py` |
| Resposta `201` com a `transaction_key` | `dtos/` e `resources/` | `transaction_dto.py`, `transfer.py` e o registro da rota em `app.py` |
| Os códigos `QIT00100x` | `errors/` | `custom_errors.py` |

**Commit e rollback (1):** o `commit` fica no controller, como última linha antes de responder. O `session_manager` faz `rollback` quando a requisição termina em exceção e nunca faz `commit`. Por isso o `ROLLBACK` dos fluxos já vem pronto: basta lançar a exceção.

---

## 2. Ordem de trabalho

A ordem segue o processo da QI Tech: modelar → endpoints e contratos → fluxos → RFC → **testes → implementação → refatoração**.

### Fase 0: banco (`database/database.sql`)

Criar as 3 tabelas (`student`, `account`, `transaction`), os ENUMs, os índices `transaction(origin_account_id)` e `transaction(destination_account_id)` e o seed das contas institucionais, incluindo a conta de tarifas.

Essa fase vem primeiro porque os testes de integração usam o `DbUtils.rollback()`, que recria o banco a partir desse arquivo **(1)**. Sem as tabelas, nenhum teste roda **(2)**.

### Fase 1: testes (`tests/integration/transfer/`)

- Helpers: `POST_transfer` em `tests/utils/request_generator.py` e o payload em `tests/utils/payload_generator.py`, seguindo o modelo dos helpers da `sample_entity` **(1)**.
- Testes da seção 13 do CLAUDE.md: caminho feliz, cada erro da tabela de endpoints, bordas de validação, tarifa e idempotência. A concorrência vem depois.
- No começo, todos os testes vão falhar, e isso é o esperado.

### Fase 2: implementação, de baixo para cima

1. `errors/`: as classes dos códigos de erro.
2. `models/`: `Account` e `Transaction`.
3. `repositories/`: as consultas, incluindo o `FOR UPDATE` em ordem crescente de `id` e o cálculo de saldo.
4. `controllers/`: os passos 2 a 11 do fluxo, na ordem exata da seção 10 do CLAUDE.md.
5. `dtos/`, depois `schemas/`, depois `resources/` e a linha da rota em `app.py`.

A ordem é de baixo para cima porque cada camada importa a de baixo, e assim cada uma pode ser testada assim que fica pronta **(3)**.

### Fase 3: verde e refatoração

Rodar a suíte até tudo passar e só então refatorar.

---

## 3. Pontos de atenção encontrados no código

### A. Conflito de códigos de erro

A `sample_entity` já usa `QIT001001` a `QIT001007` com outros significados. O `error_verification()` em `src/errors/base_error.py` **impede a API de subir** se o mesmo código aparecer em duas classes **(1)**. Os erros da `sample_entity` terão que ser removidos ou substituídos pelos do projeto.

### B. `Idempotency-Key` em header

O `SchemaHandler` (`src/utils/schema_handler.py`) valida só o corpo e a query string. O `base-service` não tem validação de header. Falta decidir como validar a `Idempotency-Key` (presente e no formato UUID) sem fugir do padrão.

### C. `INTERNAL-TOKEN`

Todas as rotas, exceto `/` e `/health_check`, exigem o header `INTERNAL-TOKEN` por middleware (`src/middlewares/internal_token.py`) **(1)**. **Decidido: o token fica, por enquanto.** O contrato e a RFC precisam citar o header e o `403 QIT000002`, e os testes do `/transfer` mandam o header pelo `RequestGenerator`, como os da `sample_entity`.

### D. Dados para os testes do `/transfer`

Para testar uma transferência é preciso ter estudante, conta e saldo. Há dois caminhos:

| Opção | Como funciona | Consequência |
|---|---|---|
| Inserir direto no banco | Um helper ao lado do `DbUtils` insere estudante, conta e um `DEPOSIT` | Permite trabalhar no `/transfer` sem depender das outras rotas nem do mock do servidor da universidade. Foge um pouco do estilo da `sample_entity`, que cria tudo pela API **(3)** |
| Usar as rotas da API | O teste chama `/student`, `/account` e `/deposit` | Exige implementar essas rotas antes e criar um mock do servidor externo usado pelo `/student` |

**Decidido: inserir direto no banco, por enquanto.** Um helper ao lado do `DbUtils` (em `tests/utils/`) cria estudante, conta e o `DEPOSIT` que dá saldo.

---

## 4. Próximo passo

Os pontos C e D já foram decididos. O próximo passo é a Fase 0 (`database/database.sql`). Os pontos A e B serão tratados um de cada vez, conforme o trabalho chegar neles.
