CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    name VARCHAR(80) NOT NULL
) ENGINE = InnoDB;

CREATE TABLE batches (
    id INTEGER PRIMARY KEY,
    label VARCHAR(40) NOT NULL
) ENGINE = InnoDB;

CREATE TABLE batch_items (
    id INTEGER PRIMARY KEY,
    batch_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    CONSTRAINT fk_batch_items_batch FOREIGN KEY (batch_id) REFERENCES batches(id),
    CONSTRAINT fk_batch_items_item FOREIGN KEY (item_id) REFERENCES items(id),
    CONSTRAINT ck_batch_items_quantity CHECK (quantity > 0),
    UNIQUE (batch_id, item_id)
) ENGINE = InnoDB;
