START TRANSACTION;

INSERT INTO items (id, name) VALUES
    (1, 'item-01'), (2, 'item-02'), (3, 'item-03'), (4, 'item-04'), (5, 'item-05'),
    (6, 'item-06'), (7, 'item-07'), (8, 'item-08'), (9, 'item-09'), (10, 'item-10');

INSERT INTO batches (id, label) VALUES
    (1, 'batch-01'), (2, 'batch-02'), (3, 'batch-03'), (4, 'batch-04'), (5, 'batch-05'),
    (6, 'batch-06'), (7, 'batch-07'), (8, 'batch-08'), (9, 'batch-09'), (10, 'batch-10');

INSERT INTO batch_items (id, batch_id, item_id, quantity) VALUES
    (1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3), (4, 4, 4, 4), (5, 5, 5, 5),
    (6, 6, 6, 6), (7, 7, 7, 7), (8, 8, 8, 8), (9, 9, 9, 9), (10, 10, 10, 10);

COMMIT;
