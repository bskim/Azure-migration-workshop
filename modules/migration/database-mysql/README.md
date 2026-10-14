# MySQL — read current DMS tasks and independent data results

English | [한국어](./README-ko.md)

Select the current MySQL DMS experience and supported source/target before running a native offline schema/data activity. SQL Server DMS and PostgreSQL's dedicated migration service are different experiences.

## 1. Learning objectives and module boundaries

For RDS/Aurora/general MySQL users. Choose A: concepts/SQL reading (30 minutes), B: approved private reachable synthetic source, empty Flexible Server and DMS (45–60 minutes setup plus 45–60 minutes lab), or C: a separately approved utility comparison. Skip other engines/compute/Terraform/app. This workshop uses illustrative AWS source and synthetic Azure samples; it does not create an AWS environment. A running local Docker source does not mean the Azure service can reach it.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

### 2.1. Introduce DMS and compare engine selection in the Portal

Search Services for Azure Database Migration Services and open Get started. Compare managed migration, Arc-enabled SQL and Migrate responsibilities, then select MySQL in Start a new migration. The illustrated experience recommends Azure Database for MySQL with Database Migration Service (classic). Use broad UI tables for orientation, then confirm the current version/target/mode support. Follow current support and Premium/private prerequisites; selection is not deployment or a migration result.

![Portal dms introduction](./images/portal-dms-introduction.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

![Portal dms mysql classic](./images/portal-dms-mysql-classic.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

**Resources for this step**

- [Dms overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Resource scenario status](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status)
- [Tutorial mysql azure mysql offline portal](https://learn.microsoft.com/en-us/azure/dms/tutorial-mysql-azure-mysql-offline-portal)
- [Overview](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/overview)
- [Virtual networks overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)

## 3. Prerequisites, permissions and cost

Use Portal/native DMS plus an approved MySQL client. Confirm supported engine versions/patches, InnoDB, charset/collation/SQL mode and enforced CHECK (8.0.16+ for the candidate source). The current offline tutorial requires Premium DMS: confirm the selected tier supports the required capability. Separate Azure management/subnet join from source/target engine privileges; additional views/triggers/routines/events may require more. Protect native connection JSON and secure input, never output full task input. Prepare private DNS/TLS/3306 and required runtime outbound/endpoints; do not globally expose DBs or disable TLS. MySQL connection properties differ from SQL trustServerCertificate flags. Approve source/target/runtime/storage/backup/network costs and leave HA/large datasets out. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Connection.example.json](./lab/connection.example.json)
- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Read the MySQL source requirements

Use mysql-sample and the common three-table/thirty-row dataset with the same logical meaning as PostgreSQL, without requiring both engines. Separate known/unknown version, engine, charset/collation/SQL mode, active writers, privilege and reachability. A supported synthetic general MySQL source is not an observed RDS/Aurora source.

**Resources for this step**

- [Planning](../planning/README.md)
- [Database sample](../../../shared/database-sample/README.md)

### 4.2. Prepare only the new synthetic source

Confirm workshop on the approved source server/session/owner. Run MySQL schema once, common seed once on source only, then save verify.sql baseline. Use the exact database, approved TLS/CA/password-prompt or owner-private option file and stop on errors; never use --force. MySQL DDL implicitly commits and can leave partial tables, so investigate partial failure without auto-DROP/TRUNCATE/reseed. Verify three workload tables, ten rows in each and thirty total. The representative join returns ten ordered rows and quantity sum 55. Compare actual columns, types, nullability, PK/FK/CHECK/unique constraints and all small ordered results, not only counts or sums. Seed the source once; do not seed the migration target. The shared memory API has no DB adapter, so SQL client success is not application DB connectivity.

**Resources for this step**

- [Source schema](./lab/schema.sql)
- [Source-only synthetic seed](../../../shared/database-sample/seed.sql)
- [Read-only verification queries](../../../shared/database-sample/verify.sql)
- [Database sample](../../../shared/database-sample/README.md)

### 4.3. Prepare a new target and current MySQL DMS project

Approve fresh rg-amw-mysql-<lab-id>, a supported small Flexible Server target, engine versions/patches/TLS/network/storage/backup and native DMS tier. Create a unique project for MySQL → Azure Database for MySQL, not a renamed SQL Server experience. Distinguish Create project only from starting an activity. Stop when support/price or the current UI/API cannot be confirmed; project preparation is not data copy.

### 4.4. Review connections, DB/table mapping and risky options

Test approved source/target credentials/TLS and map workshop only. Inspect whether the selected experience migrates schema; if data-only, separately approve empty schema-only preparation, never target seed. Select only the three workload tables and confirm target emptiness, FK/constraints and actual actions. Make Source Server Read Only can affect every DB on that server and is not the default. Existing target table selection may truncate data; populated targets are outside this basic lab, so stop rather than click through. Read native precheck/validation errors before copy approval.

### 4.5. Run the separately approved offline activity

Confirm source writer control, baseline/backups/recovery, empty target, table/mode/impact and costs in Summary. Only then approve Start migration. Observe initializing/running/completed or failures at server/DB/table levels, row progress and actual errors. Preserve source and independently compare results after native completion. Online/binlog/replication/privilege/PK/retention/lag/source-impact changes need separate current support and approval; no zero-downtime promise or automatic global-parameter changes.

To inspect an activity that already exists, open **Azure Database Migration Service (classic) → the approved owned service/project → the selected Offline activity → Database results → workshop**. Read the database status, table-completion progress, displayed size and activity time without starting another migration.

![Native MySQL offline database result for workshop: Completed, three of three tables](./images/portal-native-offline-result.png)

*This small result shows Completed, 3 of 3 tables, 0.08 MB and 00:00:07. Displayed size/time are service-progress summaries, not an exact byte comparison or the duration of source/runtime preparation, validation, teaching and cleanup.*

Open the `workshop` database's **Migration activities / table results** and inspect all three mapped workload tables: `workshop.batch_items`, `workshop.batches` and `workshop.items`.

![Native table results for the three MySQL workload tables](./images/portal-native-table-results.png)

*Each table shows Completed / All rows completed with an approximate count (~10) and rounded time 00:00:00. Approximate counts and rounded zero time do not establish exact row equality or an instantaneous migration. Continue with the independent schema, full ordered-row and TLS checks below.*

### 4.6. Compare the same read-only queries and workload schema

Use the independent comparison to establish **exactly 10 rows per workload table / 30 ordered rows total**, matching schema and unchanged source baseline, alongside verified SQL TLS connections. Do not substitute the Portal's approximate progress for those results.

Verify three workload tables, ten rows in each and thirty total. The representative join returns ten ordered rows and quantity sum 55. Compare actual columns, types, nullability, PK/FK/CHECK/unique constraints and all small ordered results, not only counts or sums. Seed the source once; do not seed the migration target. The shared memory API has no DB adapter, so SQL client success is not application DB connectivity. Physical target tables can include a service artifact. The small comparison script explicitly recognizes only the observed empty dms_persistent_objects with its expected metadata shape and records it separately; other unexplained extras fail. Do not DROP an artifact to force table count three or generalize this exception to every DMS workload. Inspect mapped InnoDB columns/keys/CHECK/collation and ordered rows alongside actual native output.

**Resources for this step**

- [Read-only verification queries](../../../shared/database-sample/verify.sql)
- [Native result and database comparison](./verify/compare-native.py)

### 4.7. Official native CLI/task alternative

Use the approved private Linux/VM Bash client with management rights and owner-private source/target connection/options files. Native checks include ConnectToSource.MySql, ConnectToTarget.AzureDbForMySql, GetUserTablesMySql and ValidateMigrationInput.MySql.AzureDbForMySql, followed by separately approved Migrate.MySql.AzureDbForMySql. The create command starts OfflineMigration: complete checks, writer control, empty-target confirmation and start approval first. Use task show --expand output to read server/DB/table results, and check the selected runtime subtype's output shape against the installed SDK. Keep secure input private. Run the linked comparison where protected credentials/client options and the original baseline are available; require AMW_MYSQL_NATIVE_COMPARE_PASS with the actual native/data values.

```bash
: "${DMS_GROUP:?Set the approved new group}"
: "${DMS_SERVICE:?Set the approved Premium service}"
: "${DMS_PROJECT:?Set the approved MySQL project}"
: "${DMS_ACTIVITY:?Set a unique approved activity name}"
: "${SOURCE_CONNECTION_FILE:?Set the owner-private source file}"
: "${TARGET_CONNECTION_FILE:?Set the owner-private target file}"
: "${DATABASE_OPTIONS_FILE:?Set the approved workshop-only options file}"
: "${AZURE_SUBSCRIPTION_ID:?Set the approved subscription}"
az dms project task create --name "$DMS_ACTIVITY" --project-name "$DMS_PROJECT" \
  --service-name "$DMS_SERVICE" --resource-group "$DMS_GROUP" --task-type OfflineMigration \
  --source-connection-json "$SOURCE_CONNECTION_FILE" \
  --target-connection-json "$TARGET_CONNECTION_FILE" \
  --database-options-json "$DATABASE_OPTIONS_FILE" --subscription "$AZURE_SUBSCRIPTION_ID" \
  --query '{name:name,state:properties.state,type:properties.taskType}'
az dms project task show --name "$DMS_ACTIVITY" --project-name "$DMS_PROJECT" \
  --service-name "$DMS_SERVICE" --resource-group "$DMS_GROUP" --expand output \
  --subscription "$AZURE_SUBSCRIPTION_ID" \
  --query '{state:properties.state,type:properties.taskType,errors:properties.errors,output:properties.output}'
```

```bash
python3 compare-native.py "$MYSQL_PROTECTED_DIRECTORY" "$AZURE_SUBSCRIPTION_ID" \
  "$DMS_GROUP" "$DMS_SERVICE" "$DMS_PROJECT" "$DMS_ACTIVITY"
```

**Resources for this step**

- [Database options.example.json](./lab/database-options.example.json)

### 4.8. Optional utility comparison and cutover/rollback

Compare mysqldump/client logical backup and restore only on separately approved synthetic inputs with supported clients/privileges and protected credential options, not argv. Review routines/events as source requirements, not automatic sample coverage. Dump/restore success is not DMS activity success. Cutover needs final writer/sync/connection approval; returning to source after new target writes is not data reconciliation.

**Resources for this step**

- [Cutover](../cutover/README.md)
- [Planning](../planning/README.md)

## 5. Verification and common failures

Check current source/target/version/region/tier experience instead of trusting a stale online URL (which may redirect to offline guidance). Separate management 403 from engine privilege/TLS/network failures. Check InnoDB/CHECK/SQL mode/DDL partial commits, target truncation risk and actual source-readonly scope. On native-complete/data-different inspect mapping, charset/FK, source changes and failed/skipped objects. Require task/table plus independent schema/data evidence.

## 6. Cleanup and ownership

Inspect active activities/sync/source settings without reverting preexisting configuration. Project/activity deletion differs from paid DMS instance, target DB/server and network deletion. List exact lab resources/new roles/private files/backups and obtain owner approval. Preserve external source/network/other projects and synthetic source until retention/recovery approval. Do not forget a Premium runtime after deleting its activity. Remove only exact temporary dump/credential artifacts; never add generic customer DROP/TRUNCATE/server-readonly commands.

## 7. Additional considerations for a real migration

Assess RDS/Aurora features, versions/table engines/collation/SQL mode/definers/triggers/routines/events, privileges/TLS/binlog/retention/change rate, backup/consistency/cutover, region/tier/quota/performance/egress and operational handoff. Small offline results do not certify all objects or online production migration.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.
