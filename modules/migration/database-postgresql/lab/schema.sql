BEGIN;

SET LOCAL search_path = public;

CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name VARCHAR(80) NOT NULL
);

CREATE TABLE batches (
    id INTEGER PRIMARY KEY,
    label VARCHAR(40) NOT NULL
);

CREATE TABLE batch_items (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER NOT NULL REFERENCES batches(id),
    item_id INTEGER NOT NULL REFERENCES items(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (batch_id, item_id)
);

COMMIT;
