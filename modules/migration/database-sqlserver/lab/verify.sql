IF DB_NAME() <> N'workshop'
    THROW 50003, 'Read the explicitly selected workshop database.', 1;

SELECT 'items' AS table_name, COUNT(*) AS row_count FROM dbo.items
UNION ALL
SELECT 'batches', COUNT(*) FROM dbo.batches
UNION ALL
SELECT 'batch_items', COUNT(*) FROM dbo.batch_items
ORDER BY table_name;

SELECT COUNT(*) AS joined_rows, SUM(bi.quantity) AS total_quantity
FROM dbo.batch_items AS bi
JOIN dbo.batches AS b ON b.id = bi.batch_id
JOIN dbo.items AS i ON i.id = bi.item_id;

SELECT bi.id, b.label, i.name, bi.quantity
FROM dbo.batch_items AS bi
JOIN dbo.batches AS b ON b.id = bi.batch_id
JOIN dbo.items AS i ON i.id = bi.item_id
ORDER BY bi.id;
