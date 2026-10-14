# Cutover and rollback — decide connection changes and data recovery separately

English | [한국어](./README-ko.md)

Use a tabletop runbook for one workload. Native migration completion, target-read acceptance and operational cutover are distinct decisions; do not build a new cutover/reverse-replication platform.

## 1. Learning objectives and module boundaries

Choose A: synthetic cards/runbook (30–40 minutes), or B: separately approved personal read-only client/profile switch (20–30 minutes plus 15 minutes rollback discussion). B consumes one known source/target/native result/baseline, not every migration/compute module. It changes only a personal lab read profile/URL, not production DNS/app/pools or new business writes. Real operational cutover is outside this lab. The shared app has no DB adapter and memory API comparisons are not durable migration.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Migrate services overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
- [Tutorial migrate physical virtual machines](https://learn.microsoft.com/en-us/azure/migrate/tutorial-migrate-physical-virtual-machines)
- [Service overview](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview)
- [Storage use azcopy v10](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Overview migration service postgresql](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql)
- [Tutorial migration service iaas online](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/tutorial-migration-service-iaas-online)
- [Dms overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Resource scenario status](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/overview)

## 3. Prerequisites, permissions and cost

A needs only documents. B needs actual approved source/target aliases/owners, native evidence, baseline and one SQL/Blob read client. Keep secrets out of runbooks/Git/prompts; record safe aliases. Distinguish native writes from new business writes, and identify every app/job/queue/manual writer. Source freeze/resume, native cutover, client configuration, writer allowance and cleanup need distinct permissions/approvals. Preserve original profile/source/backups; do not automatically Complete/Cancel a job or change global readonly/NSG/DNS. If data/writer state is unknown, use tabletop mode only. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Choose one decision card and define the runbook

Read one card A–D and runbook.csv as a template. owner_unassigned, not_checked and evidence_missing are deliberately unresolved, not approvals. Fill only chosen workload/mode/source-target aliases/observation/downtime/owners using synthetic or safely private evidence. The CSV is not an execution/approval engine.

**Resources for this step**

- [Synthetic cutover decision cards](./lab/decision-cards.md)
- [Cutover runbook template](./lab/runbook.csv)

### 4.2. Require evidence before GO

Check scope/ownership; protected source/backups/original access/retention; all writers; native state/impact/final sync; actual data/features; a real read client and time-scoped observations; and named owners for GO/NO-GO/config return/data recovery/source resume/deletion. Keep unknowns unresolved. Missing owner or a CSV expected value cannot authorize GO.

### 4.3. Understand writer control and final synchronization

A discusses what evidence to ask owners for. B requires synthetic inputs with no external writers and a confirmed baseline, without stopping production services or making a server globally read-only. Migrate needs actual source test/final replication/boot; objects need final keys/bytes/content/properties/delta; PostgreSQL online needs current waiting/cutover/changes state; MySQL/SQL depend on their supported offline/online/backup/restore path. Low lag or a completed copy alone is not consumer acceptance. Native actions follow the original module and separate approval.

### 4.4. Record GO/NO-GO and switch only the personal read client

Record final data/features/native state, then the owner decides with reason. Unknown/difference/time/cost violations mean stop. Preserve SOURCE and create a separate TARGET read profile. Verify actual server/account/DB/container/namespace, not merely similar names/data. After approval create a new connection/request against TARGET rather than trusting cached sessions. Do not allow new business writes or change production DNS/app pools. Evidence is this client's actual target read, not full workload cutover.

### 4.5. Observe the chosen workload with the same criteria

For PG/MySQL use schema/ten rows per table/thirty total/join ten/sum55 and ordered results. SQL uses its own dbo/T-SQL and needs separate Agent/cross-DB feature evidence. Objects require three root names, actual bytes/hash and selected content type/metadata. A server demo needs actual boot/service/representative features/read/config. Without source these remain discussion criteria. Native state, schema/data, client connection and observability are separate evidence.

### 4.6. Separate failure before, after and unknown target writes

Use tabletop by default. Any optional failed-read profile must be isolated (for example invalid.example.invalid), with no real credentials or modification of healthy profiles/production DNS. With verified no-new-business-write evidence and safe source/baseline/owner approval, a personal SOURCE read return may be appropriate; writer resume is separate. With target business writes, stop approved writers, preserve both sides, inspect differences and plan reconciliation/restore/RPO/approval before return. Unknown writes remain NO-GO, even if your own test was read-only. Do not run reverse copy/DELETE/recovery SQL from these cards.

### 4.7. Acceptance, writer authorization and retention

Even correct native/data/read connection evidence does not authorize writers. Define who allows new writes, observation period/error/latency/new-data criteria and stop conditions. Record the first accepted target business write and approver because rollback obligations change afterward. Connect backup retention, replication completion, grant revocation and source retirement to acceptance/recovery decisions. Do not bundle Complete/Cancel/job/source deletion into one cleanup action.

## 5. Verification and common failures

Tabletop completion explains each card's GO/NO-GO, unknowns/owner/source protection and config-return versus data recovery. Optional B needs real target read/new connection/baseline and an approved SOURCE read-back. Native status alone is not acceptance; unknown writer/owner prevents no-write assumptions. Matching counts do not prove matching destination/content. Missing target events after a return mean data recovery remains unresolved.

**Resources for this step**

- [Cutover runbook template](./lab/runbook.csv)

## 6. Cleanup and ownership

Reading has no Azure deletion. B removes only its own personal test/read/failure profiles and exact temporary safe records, preserving original profiles and protected credentials according to client policy. The original modules own source/target/job/runtime/appliance/backup/storage/group cleanup. Confirm writer state, acceptance/retention, action effects and grants before approved deletion. Keep shared inputs until last consumer and source/backups until recovery approval; Cancel does not automatically revert target data.

## 7. Additional considerations for a real migration

Identify every writer/dependency, DNS TTL/cache/pool, partial switch/dual writes, consistency/RPO/RTO/final delta/restore/reconciliation support, irreversible native boundaries, incident communications, regulation, operating handoff and retention/cost. A tabletop is not an approved or tested production runbook.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Planning](../planning/README.md)
