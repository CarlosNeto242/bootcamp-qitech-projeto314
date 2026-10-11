
CREATE TYPE account_type AS ENUM ('STUDENT','INSTITUTIONAL');
CREATE TYPE account_status AS ENUM('ACTIVE','CLOSED');
CREATE TYPE transaction_type AS ENUM('DEPOSIT', 'TRANSFER' , 'FEE');

CREATE TABLE student(
    id                              SERIAL PRIMARY KEY,
    student_key                     CHAR(36) NOT NULL,
    name                            VARCHAR(255) NOT NULL,
    document_number                 CHAR(14) NOT NULL,
    UNIQUE(student_key),
    UNIQUE(document_number)
);

CREATE TABLE account(
    id                              SERIAL PRIMARY KEY,
    account_key                     CHAR(36) NOT NULL,
    student_id                      INTEGER REFERENCES student(id),
    type                            account_type NOT NULL,
    status                          account_status NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(account_key),
    UNIQUE(student_id),
    CHECK(
        (type = 'STUDENT'       AND student_id IS NOT NULL) OR
        (type = 'INSTITUTIONAL' AND student_id IS NULL)
    )
);

INSERT INTO account (account_key, student_id, type, status) VALUES
('26ccf53d-7a91-41bf-acc2-09a93743f423', NULL, 'INSTITUTIONAL', 'ACTIVE'), --universidade
('06d8b86d-6d68-402d-9c8a-e089230f16ce', NULL, 'INSTITUTIONAL', 'ACTIVE'), --cantina
('e2f33a85-efb7-4bc5-afde-4ffe5229f7f3', NULL, 'INSTITUTIONAL', 'ACTIVE'); --estacionamento

CREATE TABLE transaction(
    id                              SERIAL PRIMARY KEY,
    transaction_key                 CHAR(36) NOT NULL,
    transaction_type                transaction_type NOT NULL,
    value                           INTEGER NOT NULL,
    origin_account_id               INTEGER REFERENCES account(id),
    destination_account_id          INTEGER REFERENCES account(id) NOT NULL,
    related_transaction_id          INTEGER REFERENCES transaction(id),
    idempotency_key                 CHAR(36) NOT NULL,
    created_at                      TIMESTAMP NOT NULL DEFAULT(NOW()),
    UNIQUE(transaction_key),
    UNIQUE(idempotency_key),
    CHECK (value > 0)
);

CREATE INDEX idx_transaction_origin_id ON transaction (origin_account_id);
CREATE INDEX idx_transaction_destination_id ON transaction (destination_account_id);

