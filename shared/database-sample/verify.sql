SELECT 'items' AS table_name, COUNT(*) AS row_count FROM items
UNION ALL
SELECT 'batches', COUNT(*) FROM batches
UNION ALL
SELECT 'batch_items', COUNT(*) FROM batch_items
ORDER BY table_name;

SELECT COUNT(*) AS joined_rows, SUM(bi.quantity) AS total_quantity
FROM batch_items AS bi
JOIN batches AS b ON b.id = bi.batch_id
JOIN items AS i ON i.id = bi.item_id;

SELECT bi.id, b.label, i.name, bi.quantity
FROM batch_items AS bi
JOIN batches AS b ON b.id = bi.batch_id
JOIN items AS i ON i.id = bi.item_id
ORDER BY bi.id;
