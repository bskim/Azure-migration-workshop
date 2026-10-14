# Shared synthetic database inputs

English | [한국어](./README-ko.md)

PostgreSQL and MySQL reuse these SQL inputs and small comparison criteria. They are not a migration/CDC/copy implementation, a second business app or an app DB adapter. SQL Server uses separate T-SQL files for the same logical data.

## Use sequence and boundaries

Create only an approved fresh synthetic source DB workshop. Run the selected engine's schema, then this seed.sql once on source only. Stop on existing objects/data; do not DROP/TRUNCATE/IF NOT EXISTS to hide a mismatch. Run the same read-only verify.sql on source and the migrated target. Choose the explicit DB/session and error-stop policy; PostgreSQL uses public, MySQL workshop. Credentials/users/grants/DB provisioning belong to approved inputs, not SQL assets.

**Resources for this step**

- [Source-only synthetic seed](./seed.sql)
- [Read-only verification queries](./verify.sql)

## Expected observable results

Verify three workload tables, ten rows in each and thirty total. The representative join returns ten ordered rows and quantity sum 55. Compare actual columns, types, nullability, PK/FK/CHECK/unique constraints and all small ordered results, not only counts or sums. Seed the source once; do not seed the migration target. The shared memory API has no DB adapter, so SQL client success is not application DB connectivity. First representative ordered row: 1, batch-01, item-01, 1; last: 10, batch-10, item-10, 10. Compare table names/counts by identity, not collation-dependent alphabetical display order. Explicit numeric ID order makes the join comparable.

## Engine-specific behavior

PostgreSQL DDL is transactional and needs error-stop plus commit/rollback verification. MySQL schema explicitly uses InnoDB; DDL implicit commit can leave partial tables, so diagnose instead of automatically deleting/reseeding. Check CHECK enforcement in the actual version (candidate 8.0.16+). Data inserts use a transaction; never ignore an error and commit/retry. SQL Server uses dbo-specific T-SQL with XACT_ABORT/transaction/error handling rather than this START TRANSACTION dialect.

## Choose one engine module

Select only PostgreSQL's dedicated migration service, MySQL DMS or SQL Server's separate module. The chosen module owns source protection/permissions/tool/cleanup; the shared app does not automatically consume these DB tables. SQL Server's SqlPackage path imports a source-only BACPAC to an empty target, not seeded data or DMS evidence. A MySQL DMS target may have one explicitly inspected empty dms_persistent_objects artifact; mapped workload comparisons must record it separately and fail on unexplained extras.

**Resources for this step**

- [Database postgresql](../../modules/migration/database-postgresql/README.md)
- [Database mysql](../../modules/migration/database-mysql/README.md)
- [Database sqlserver](../../modules/migration/database-sqlserver/README.md)
- [Complete SQL schema and row comparison](../../modules/migration/database-sqlserver/verify/compare.sql)
