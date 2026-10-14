SET XACT_ABORT ON;

IF DB_NAME() <> N'workshop'
    THROW 50001, 'Select the approved synthetic source database workshop.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    CREATE TABLE dbo.items (
        id INT NOT NULL CONSTRAINT pk_items PRIMARY KEY,
        name VARCHAR(80) NOT NULL
    );

    CREATE TABLE dbo.batches (
        id INT NOT NULL CONSTRAINT pk_batches PRIMARY KEY,
        label VARCHAR(40) NOT NULL
    );

    CREATE TABLE dbo.batch_items (
        id INT NOT NULL CONSTRAINT pk_batch_items PRIMARY KEY,
        batch_id INT NOT NULL,
        item_id INT NOT NULL,
        quantity INT NOT NULL,
        CONSTRAINT fk_batch_items_batch FOREIGN KEY (batch_id) REFERENCES dbo.batches(id),
        CONSTRAINT fk_batch_items_item FOREIGN KEY (item_id) REFERENCES dbo.items(id),
        CONSTRAINT ck_batch_items_quantity CHECK (quantity > 0),
        CONSTRAINT uq_batch_items UNIQUE (batch_id, item_id)
    );

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;
    THROW;
END CATCH;
