
```mermaid
    erDiagram
        Transaction {
            char(36) transaction_key PK "sai o id único da transação"
            float value "informa o valor monetário da transação"
            char(36) origin_account_CPF FK "vê o id da conta de quem que transferiu"
            char(36) destinantion_account_CPF FK "vê o id da conta de quem recebeu quem recebeu"
        }
```

| Método | Caminho | O que faz | Entrada (campos que importam) | Saídas (status e quando) |
|---|---|---|---|---|
|`POST`|`transaction/`|Efetua uma transação de valor `value`|`value`, `origin_account_CPF`, `destination_account_CPF`|`201` com o `transaction_key`, `400` `QIT000001` corpo fora do formato,`422` `QIT001001` cpf do destinatário não está vinculado a uma conta cadastrada, `422` `QIT001008` valor de saldo insuficiente |
