IF DB_NAME() <> N'workshop'
    THROW 50004, 'Read only the explicitly approved source or target workshop database.', 1;

SELECT s.name AS schema_name, t.name AS table_name
FROM sys.tables AS t
JOIN sys.schemas AS s ON s.schema_id = t.schema_id
WHERE t.is_ms_shipped = 0
ORDER BY s.name, t.name;

SELECT t.name AS table_name, c.column_id, c.name AS column_name,
       ty.name AS type_name, c.max_length, c.precision, c.scale,
       c.is_nullable, c.is_identity, c.collation_name
FROM sys.tables AS t
JOIN sys.columns AS c ON c.object_id = t.object_id
JOIN sys.types AS ty ON ty.user_type_id = c.user_type_id
WHERE t.is_ms_shipped = 0
ORDER BY t.name, c.column_id;

SELECT t.name AS table_name, k.name AS constraint_name, k.type_desc,
       ic.key_ordinal, c.name AS column_name
FROM sys.key_constraints AS k
JOIN sys.tables AS t ON t.object_id = k.parent_object_id
JOIN sys.index_columns AS ic
  ON ic.object_id = t.object_id AND ic.index_id = k.unique_index_id
JOIN sys.columns AS c
  ON c.object_id = t.object_id AND c.column_id = ic.column_id
WHERE t.is_ms_shipped = 0
ORDER BY t.name, k.name, ic.key_ordinal;

SELECT t.name AS table_name, f.name AS constraint_name, c.name AS column_name,
       rt.name AS referenced_table, rc.name AS referenced_column,
       f.delete_referential_action_desc, f.update_referential_action_desc,
       f.is_disabled, f.is_not_trusted
FROM sys.foreign_keys AS f
JOIN sys.tables AS t ON t.object_id = f.parent_object_id
JOIN sys.foreign_key_columns AS fc ON fc.constraint_object_id = f.object_id
JOIN sys.columns AS c
  ON c.object_id = t.object_id AND c.column_id = fc.parent_column_id
JOIN sys.tables AS rt ON rt.object_id = f.referenced_object_id
JOIN sys.columns AS rc
  ON rc.object_id = rt.object_id AND rc.column_id = fc.referenced_column_id
WHERE t.is_ms_shipped = 0
ORDER BY t.name, f.name, fc.constraint_column_id;

SELECT t.name AS table_name, c.name AS constraint_name, c.definition,
       c.is_disabled, c.is_not_trusted
FROM sys.check_constraints AS c
JOIN sys.tables AS t ON t.object_id = c.parent_object_id
WHERE t.is_ms_shipped = 0
ORDER BY t.name, c.name;

SELECT id, name FROM dbo.items ORDER BY id;
SELECT id, label FROM dbo.batches ORDER BY id;
SELECT id, batch_id, item_id, quantity FROM dbo.batch_items ORDER BY id;
