# SQL Server — choose the target before the migration tool

English | [한국어](./README-ko.md)

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.


Compare Azure SQL Database, SQL Managed Instance and SQL Server on Azure VM, then introduce target-specific DMS and official SqlPackage. A data-only BACPAC exercise cannot satisfy SQL Agent or cross-database preservation requirements.

## 1. Learning objectives and module boundaries

For RDS SQL Server/general SQL Server users (not Aurora). Choose A: functionality/tool walkthrough (30–45 minutes), B: separately supported DMS offline data exercise, B2: approved private Entra-only SqlPackage Export/Import, or C: a prepared MI/SQL VM feature-preserving demonstration. Preparation and lab each need roughly 45–60 minutes plus runtime/target wait; estimates vary. No other engine/compute/IaC/shared-app completion is required. No real AWS environment was constructed; Azure synthetic source results are learning evidence only. B/B2 deliberately shrink to three-table data and are not the original SQL Agent/cross-DB case's solution.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

SQL Database is database-centered PaaS; MI offers broader instance/cross-database compatibility; SQL VM retains OS/instance control with greater patching/backup responsibility. The referenced DMS paths indicate offline SQL Database migration and offline/online MI or SQL VM migration. Confirm the current matrix for your exact source/target/mode rather than extrapolating a generic Yes. SQL Agent jobs, logins, encryption and instance settings are not automatically preserved just because table data moved. Online still has final synchronization/cutover interruption.

### 2.1. Introduce DMS and target selection even when using SqlPackage

Open the DMS introduction and SQL Server source scenario. Compare SQL Database, MI and SQL VM choices, authentication policy and source features before selecting a tool. DMS provides managed migration/runtime/tasks/progress/errors; SqlPackage provides schema/table portability. Neither an introductory target list nor a successful utility import proves DMS/SHIR support or instance-feature preservation. If SQL-auth DMS cannot meet Entra-only policy, choose a separately approved supported B2 or a walkthrough, never a policy bypass.

![Portal dms sql scenario](../database-mysql/images/portal-dms-sql-scenario.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

**Resources for this step**

- [Database mysql](../database-mysql/README.md#21-introduce-dms-and-compare-engine-selection-in-the-portal)
- [Sql database paas overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview)
- [Sql managed instance paas overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview)
- [Sql server on azure vm iaas what is overview](https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/sql-server-on-azure-vm-iaas-what-is-overview)
- [Dms overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Resource scenario status](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status)
- [Overview](https://learn.microsoft.com/en-us/data-migration/sql-server/overview)
- [Sqlpackage](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage?view=sql-server-ver17)
- [Authentication azure ad only authentication](https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-azure-ad-only-authentication?view=azuresql)

The B2 sample uses an Entra-only target and Managed Identity client. Confirm the selected tool supports the target's configured authentication and the applicable policies before execution.

## 3. Prerequisites, permissions and cost

Use Portal plus approved current SSMS/sqlcmd/SqlPackage, not retired extensions or generic .bak restore on every target. Confirm SQL versions/compatibility/collation/client driver and support. Management, DB/schema privileges, backup access and runtime registration differ. DMS may need SHIR and mode-specific wider rights; prepare only a supported source/target/runtime/DNS/TLS/network path after approval. Entra-only target support in SQL Database itself does not prove a chosen DMS authentication path supports it; stop on policy/tool mismatch without disabling Entra-only or finding another subscription to evade policy. B2 needs Windows-authenticated source TLS, private canonical SQL target DNS/MI, a fresh empty DB, protected BACPAC folder and official SqlPackage. A BACPAC is not encrypted or an instance backup. db_owner alone may not suffice for Import when target users conflict; any temporary MI Entra administrator workflow belongs only to a fresh isolated logical server with explicit approval and guaranteed restoration. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Sqlpackage download](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage-download?view=sql-server-ver17)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Reject targets that cannot preserve the source requirements

The synthetic sqlserver-sample needs SQL Agent and cross-database queries. Assess MI/SQL VM candidates before considering SQL Database, which does not automatically preserve those requirements. Separate known/unknown logins/users/roles/jobs/operators/linked servers/CLR/TDE/backups/compatibility. Native assessment/readiness/SKU recommendation is not migration execution, and not every DMS Portal performs every assessment function.

**Resources for this step**

- [Planning](../planning/README.md)

### 4.2. Prepare source-only T-SQL synthetic data

A DB administrator confirms a new synthetic workshop database and dbo on the exact source/server/owner. Run this module's schema.sql, seed.sql and read-only verify.sql baseline once. These are distinct T-SQL assets, not the shared PostgreSQL/MySQL START TRANSACTION seed. XACT_ABORT/transactions/rollback/rethrow and DB-name guards do not prove a server is a sandbox: confirm owner first. Stop on errors or existing data without DROP/TRUNCATE/reseed. Do not create source instance features merely to fake compatibility or seed target data.

**Resources for this step**

- [Source schema](./lab/schema.sql)
- [Source-only synthetic seed](./lab/seed.sql)
- [Read-only verification queries](./lab/verify.sql)
- [Source-only synthetic seed](../../../shared/database-sample/seed.sql)

### 4.3. B: separately supported DMS offline SQL Database lab

Use B only when source/target/mode/runtime/authentication and organizational policy all permit it. Approve a dedicated group, new logical server/empty workshop DB, current SQL migration service and SHIR; MySQL Premium DMS is a different resource/experience. Follow current SQL Database offline guidance, supported SHIR version and source/target FQDN/TLS/credentials. Data-only CLI may require preexisting empty target tables; Migrate Missing Schema in the Portal is not the same action. Inspect permissions and object-level schema results as well as rows: some non-table schema errors may allow data migration to continue. Approve workshop/three-table mapping, writer control/baseline/recovery and Start migration separately. Do not deploy an expensive source/runtime before authentication/policy support is established. MI/VM tiers/licenses/network/backup costs are separate and can justify a prepared demo.

**Resources for this step**

- [Self hosted integration runtime](https://learn.microsoft.com/en-us/data-migration/sql-server/self-hosted-integration-runtime)
- [Sql db](https://learn.microsoft.com/en-us/cli/azure/datamigration/sql-db?view=azure-cli-latest)
- [Sql server to sql db](https://github.com/Azure-Samples/data-migration-sql/blob/main/CLI/sql-server-to-sql-db.md)
- [Authentication azure ad only authentication](https://learn.microsoft.com/en-us/azure/azure-sql/database/authentication-azure-ad-only-authentication?view=azuresql)
- [Database migration service](https://learn.microsoft.com/en-us/data-migration/sql-server/database/database-migration-service)

### 4.3.1. B2: SqlPackage schema/data migration to an Entra-only target

Use official Export/Import for an offline reduced workload. This is not DMS, CDC, SHIR, Blob upload or full instance backup. Prepare consistent frozen source, empty target and protected artifact; run the detailed sequence below in private Windows PowerShell. Source Windows authentication, target MI, DB permissions, Entra administrator and private network are separate inputs.

**Resources for this step**

- [Sqlpackage export](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage-export?view=sql-server-ver17)
- [Sqlpackage import](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage-import?view=sql-server-ver17)

#### Inputs and administrator-approved permissions

Confirm a new source workshop/Windows authenticated client with matching TLS hostname and trusted chain. Seed only source and save baseline. Prepare a new Entra-only/public-disabled Azure SQL logical server, empty Basic workshop DB, Approved Private Endpoint/DNS and private client where canonical server.database.windows.net resolves correctly. Proxy/TCP1433 and Redirect have different network needs. Install official self-contained SqlPackage (the example baseline is 170.4.83.3) in an approved protected location. Direct Import needs no Blob/SAS/key. Import may try to drop a target-contained MI user absent from the BACPAC; review the required import privileges beyond db_owner. If an administrator chooses temporary MI Entra-admin context, restrict it to a new isolated logical server, handle only the exact new MI user, record the original administrator and restore it after success or failure. Fresh Windows source SQL-admin recovery and temporary certificates are instructor fixture matters, not instructions to change an existing server.

**Resources for this step**

- [Source schema](./lab/schema.sql)
- [Source-only synthetic seed](./lab/seed.sql)
- [Read-only verification queries](./lab/verify.sql)
- [Connect to sql server when system administrators are locked out](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/connect-to-sql-server-when-system-administrators-are-locked-out?view=sql-server-ver17)

#### Freeze the source and perform official Export

The source owner confirms no other writers and a saved baseline, then in the correct synthetic source SQL session approves ALTER DATABASE workshop SET READ_ONLY WITH NO_WAIT. Investigate failure; do not force-close other sessions. Read-only can be changed by an owner and does not replace operational writer control. In private Windows source/client PowerShell set exact environment inputs/executable/protected folder. Use integrated source authentication, Encrypt True/TrustServerCertificate False, reject an existing BACPAC, check process exit codes and record its SHA-256. Do not weaken TLS or alter a participant's global trust. BACPAC contains schema/table data and must remain owner-protected.

```powershell
foreach ($name in @("WORKSHOP_SQL_SOURCE", "WORKSHOP_SQL_TARGET", "WORKSHOP_SQLPACKAGE", "WORKSHOP_SQL_ARTIFACT_DIR")) {
    if (-not [Environment]::GetEnvironmentVariable($name)) { throw "$name input is required." }
}
$sourceServer = $env:WORKSHOP_SQL_SOURCE
$targetServer = $env:WORKSHOP_SQL_TARGET
$sqlpackage = $env:WORKSHOP_SQLPACKAGE
$artifactDir = $env:WORKSHOP_SQL_ARTIFACT_DIR
if (-not (Test-Path -LiteralPath $sqlpackage -PathType Leaf)) { throw "The SqlPackage executable does not exist." }
if (-not (Test-Path -LiteralPath $artifactDir -PathType Container)) { throw "The approved protected folder does not exist." }
$bacpac = Join-Path $artifactDir "workshop.bacpac"
if (Test-Path -LiteralPath $bacpac) { throw "Do not overwrite an existing BACPAC." }
$sourceConnection = "Server=tcp:$sourceServer,1433;Initial Catalog=workshop;Integrated Security=True;Encrypt=True;TrustServerCertificate=False;Connection Timeout=60"
& $sqlpackage /Version
if ($LASTEXITCODE -ne 0) { throw "SqlPackage version check failed" }
& $sqlpackage /Action:Export "/SourceConnectionString:$sourceConnection" "/TargetFile:$bacpac" /p:VerifyExtraction=True
if ($LASTEXITCODE -ne 0) { throw "SqlPackage Export failed" }
Get-FileHash -LiteralPath $bacpac -Algorithm SHA256
```

#### Import with MI and immediately restore administrator privileges

Confirm a new schema-empty target, unchanged BACPAC hash and approved import identity/context. Execute in the same private Windows PowerShell session. Successfully imported is tool evidence, not row/schema verification. Restore the original Entra administrator regardless of outcome and recheck SID/Entra-only/public-disabled settings. If the source read-only database option is imported, approve READ_WRITE only on the new SQL Database target session; do not unfreeze the source or reseed/reimport. After restoration, prepare only the approved MI contained user/db_owner within workshop as needed. Azure RBAC, DB user/role and Entra administrator are distinct; do not add tenant Directory Readers or subscription Owner as an automatic shortcut.

```powershell
if (-not (Test-Path -LiteralPath $bacpac -PathType Leaf)) { throw "The approved source BACPAC does not exist." }
$targetConnection = "Server=tcp:$targetServer,1433;Initial Catalog=workshop;Authentication=Active Directory Managed Identity;Encrypt=True;TrustServerCertificate=False;Connection Timeout=60"
& $sqlpackage /Action:Import "/SourceFile:$bacpac" "/TargetConnectionString:$targetConnection" /p:DatabaseEdition=Basic /p:DatabaseServiceObjective=Basic
if ($LASTEXITCODE -ne 0) { throw "SqlPackage Import failed. Inspect the target before retrying." }
```

```sql
IF DB_NAME() <> N'workshop' OR CONVERT(int, SERVERPROPERTY('EngineEdition')) <> 5
    THROW 50005, 'Use only the approved new Azure SQL Database target session.', 1;
SELECT DATABASEPROPERTYEX('workshop', 'Updateability') AS updateability;
ALTER DATABASE workshop SET READ_WRITE WITH NO_WAIT;
```

#### Independent verification and portability limits

In the Portal, open the approved **SQL server Overview** and read the `workshop` database's **Online / Basic** state. Then use **Settings → Microsoft Entra ID** to inspect the sample's Entra-only authentication setting without changing it.

![SQL Database workshop shown Online on Basic](./images/portal-sql-online-database.png)

![Sample server setting allowing only Microsoft Entra authentication](./images/portal-sql-entra-only.png)

*Online is a database availability state. The checked Entra-only option describes this sample server's authentication configuration; select compatible client authentication and DB permissions accordingly. Verify the SqlPackage import through the schema/complete-row/TLS/source-baseline comparisons below.*

Run verify.sql and compare.sql read-only in the exact source/target workshop sessions. Compare three tables, eight columns, five key-column rows (compound unique expands column rows), two FKs, one CHECK, seven key/check constraints and all thirty sorted table rows. Include names, column order/type/nullability/collation, referential actions, trust/disabled flags and CHECK definitions, plus unchanged source baseline, source READ_ONLY, target READ_WRITE and actual MI DB privilege/encrypted connection. Require representative join ten/sum 55. Read SqlPackage platform/physical-file warnings rather than generalizing compatibility. Export/Import service with Managed Identity or service-managed Private Link is a separate preview route with different UAMI/Blob/PE prerequisites, not the direct client exercise.

**Resources for this step**

- [Read-only verification queries](./lab/verify.sql)
- [Complete SQL schema and row comparison](./verify/compare.sql)
- [Database import export managed identity](https://learn.microsoft.com/en-us/azure/azure-sql/database/database-import-export-managed-identity?view=azuresql)
- [Database import export private link](https://learn.microsoft.com/en-us/azure/azure-sql/database/database-import-export-private-link?view=azuresql)

### 4.4. C: read MI/SQL VM backup and cutover paths

Without approved C inputs, discuss current MI/SQL VM guidance only. Compare instance/cross-DB and OS-control needs, licensing/costs, supported offline/online modes, actual source/version/writers/backups, runtime/storage/backup sequence, separate login/Agent job/operator plans and actual feature tests. Do not apply generic .bak restoration to SQL Database. RDS backup/permission limitations need actual authorized source evidence. Arc/tracking resources, MI Link/LRS/native restore are alternatives only when their particular source/target requirements fit, not mandatory combined methods.

**Resources for this step**

- [Guide](https://learn.microsoft.com/en-us/data-migration/sql-server/managed-instance/guide)
- [Database migration service offline](https://learn.microsoft.com/en-us/data-migration/sql-server/virtual-machines/database-migration-service-offline)

### 4.5. Compare native job evidence and identical data queries

Verify three workload tables, ten rows in each and thirty total. The representative join returns ten ordered rows and quantity sum 55. Compare actual columns, types, nullability, PK/FK/CHECK/unique constraints and all small ordered results, not only counts or sums. Seed the source once; do not seed the migration target. The shared memory API has no DB adapter, so SQL client success is not application DB connectivity. Use this module's explicit dbo/T-SQL assets. For DMS inspect DB/object/table errors/skips and required instance features beyond overall Complete; for B2 inspect tool output plus complete comparison. The sample contains no Agent/cross-DB feature evidence, so C needs separate actual feature criteria/results.

**Resources for this step**

- [Read-only verification queries](./lab/verify.sql)

### 4.6. Plan cutover and rollback separately

Apply source write stop, final sync/backup, native/schema/data/feature evidence, owner go/no-go, connection/DNS change and observation. DMS SQL Database's indicated path is offline; MI/SQL VM online support depends on the current matrix and still involves cutover downtime/consistency decisions. New target business writes require explicit reconciliation/recovery; source reconnection alone is not data rollback. Logins/users/jobs/operators/instance settings may require separate work.

**Resources for this step**

- [Cutover](../cutover/README.md)
- [Planning](../planning/README.md)

## 5. Verification and common failures

On a feature mismatch reassess target rather than claiming data-only success preserves SQL Agent/cross-DB. Check SHIR/version/network/TLS/backup permissions independently. On Entra-only policy or unsupported DMS auth stop without bypass tags, authentication changes or subscription evasion. On B2 current-MI-user DROP errors inspect actual target state and approved isolated import context, never invent user-preservation flags or edit the BACPAC model. Handle readonly only on the new target. Inspect schema failures even if data proceeds; do not accept count-only comparisons or assume instance objects migrated.

## 6. Cleanup and ownership

List actual jobs/sync/backups/writer state and all owned resources before separate deletion approval. DMS tracking/runtime/instance, SHIR deregistration, target server/MI/VM/disks and backups have distinct effects. B2 has no DMS/SHIR: account for source/client VM-local TLS/keys/trust, BACPAC/baseline, target MI user/temporary-admin restoration, DB/server and owned PE/DNS/subnet/grants. Preserve externally supplied source/client/MI/network and source/backups until acceptance/retention approval. Remove only exact protected artifacts after confirming restoration and resource cleanup; do not add generic production DROP/TRUNCATE/encryption disable/source-stop commands.

## 7. Additional considerations for a real migration

Assess versions/compatibility/edition/license/collation/Agent/cross-DB/linked servers/CLR/TDE, RDS backup permissions, change rate/backup chain/runtime/network/bandwidth, BACPAC consistency/protection/space/DB options/import privileges, logins/jobs/HA/performance/monitoring, operational handoff and rollback. SQL Database DMS offline and MI/SQL VM offline/online support must be rechecked for the actual source/target; online is not a no-downtime guarantee.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.
