
```mermaid
    erDiagram
        Transaction {
            char(36) transaction_key PK "sai o id único da transação"
            float value "informa o valor monetário da transação"
            char(36) origin_account_key FK "vê o id da conta de quem que transferiu"
            char(36) destinantion_account_key FK "vê o id da conta de quem recebeu quem recebeu"
        }

```