# Migration planning — select the path for your workload

English | [한국어](./README-ko.md)

Choose an Azure service or official tool from one source requirement, then define an achievable learning mode and evidence. This is a planning exercise, not discovery or migration automation.

**Resources for this step**

- [..](../../../Readme.md)

## 1. Learning objectives and module boundaries

For AWS engineers considering Azure; allow 50–60 minutes for one case. Inputs are the synthetic workloads.csv and official introductions; only the app case also uses shared source. Produce a short plan with target/tool rationale, rejected alternative, unknowns, prerequisites, tests, go/no-go, cutover/rollback, cost and cleanup owners. No login, installation, resource/job creation or completion of other modules is required.

**Resources for this step**

- [Identity](../../onboarding/identity/README.md)
- [Networking](../../onboarding/networking/README.md)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Migrate services overview](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
- [Tutorial migrate aws virtual machines](https://learn.microsoft.com/en-us/azure/migrate/tutorial-migrate-aws-virtual-machines)
- [Service overview](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview)
- [Storage use azcopy v10](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Storage use azcopy s3](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-s3)
- [Overview migration service postgresql](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql)
- [Overview](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview)
- [Dms overview](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Resource scenario status](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status)
- [Overview](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [What is aks](https://learn.microsoft.com/en-us/azure/aks/what-is-aks)
- [Sql database paas overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview)
- [Sql managed instance paas overview](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview)
- [Sql server on azure vm iaas what is overview](https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/sql-server-on-azure-vm-iaas-what-is-overview)

**Workshop delivery boundary:** Storage Mover is **service introduction only**: what it manages, suitable source/workload scenarios, region/cost/permission/network considerations and official documentation. This workshop does not create its endpoints/projects/job definitions, grant its execution roles or start/verify its copy engine. The hands-on object path is the separate official **private AzCopy** exercise with three synthetic objects/109 bytes. This delivery choice is not a claim that Storage Mover is universally unsupported. Future customer execution requires their own supported official scenario and administrator approval.

## 3. Prerequisites, permissions and cost

Read the six fictional CSV scenarios as discussion inputs, not discovered resources or supported versions. This workshop CSV is not Azure Migrate/DMS's official import format. Downtime is a planning target, not a tool achievement. Reading creates no paid resources; plan appliance/replica/temporary storage/target/runtime/DB/network/egress costs separately. Record permission kind/scope and responsible owner without credentials or private inventory. No real AWS environment was constructed; supported synthetic Azure samples are for learning only. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Synthetic workload scenarios](./lab/workloads.csv)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Select one case and identify its evidence level

app-sample compares VM/AKS/Container Apps execution without OS preservation; server-sample preserves Windows OS/disk/service/local state through a Migrate candidate; objects-sample compares Mover/AzCopy with archive/metadata/permissions; postgresql-sample uses the dedicated service; mysql-sample uses current MySQL DMS; sqlserver-sample requires cross-DB/SQL Agent and first evaluates MI/SQL VM. App source/Dockerfile/AWS Terraform reveal ports/memory/SDK dependencies, not actual host discovery. Linux_x64_host_OS_unknown remains unknown. CSV rows and source names are not assessment evidence.

**Resources for this step**

- [Shared FastAPI application](../../../sample-app/app.py)
- [Shared Dockerfile](../../../sample-app/Dockerfile)
- [Main.tf](../terraform/lab/aws/main.tf)

### 4.2. Separate preservation, allowed change and unknowns

Write what must remain (OS/services/engine/data/keys/app contract), what may change (compute/network/identity/connections), and unknowns/stop conditions (extensions/privilege/archive restoration/write rates/downtime). IaC does not capture every application dependency. Do not default missing information to none.

### 4.3. Choose the target/tool and reject one alternative

State the target and preservation/change rationale, the official service's responsibility, one rejected alternative, support/version/region/source/target unknowns and the learning mode. An OS/local-state server cannot be satisfied by only a new Container Apps deployment. SQL Database cannot be assumed to satisfy Agent/cross-DB; MI/SQL VM also require compatibility/cost/operation evidence rather than being automatic answers.

### 4.4. Define what native evidence must show

Without creating a job, read official flows or a safely prepared instructor result. Migrate inventory/assessment/warnings/sizing/test/replication differs from fictional CSV. Mover endpoint/job progress/error differs from resource creation. AzCopy exit/job evidence needs independent count/content/property checks. PostgreSQL validation/offline/online/cutover is not a dump restore. DMS engine/target experiences differ, and not every tool performs assessment. Label walkthrough/prepared result/actual observation accurately.

### 4.5. List prerequisites, tests and stop conditions

Separate management/source-data/target-data/engine permissions and assign owners for grants/revocation. Map source→service/agent→target DNS/TLS/ports/bandwidth. Check engine/OS/extensions/features/support/preview, appliance/replica/backup/target/egress costs and isolated test criteria. Stop for missing source evidence/rights, unsupported functionality, data differences or exceeded budget/time. Leave GPU/HA/large data/complex network as future considerations, not mandatory sample code.

### 4.6. Write cutover and rollback criteria first

Plan backups/restore, source write-stop method, final sync/verification, connection/DNS/TTL changes and approving owners. GO requires native, data, app/client and operational evidence; unknown is NO-GO. After switching, assign read/write/error/latency/new-data observation. Define who/when/how to return, source resume criteria, target new-write reconciliation and recovery time. Online does not guarantee zero downtime, and connection reversal after target writes is not data rollback.

### 4.7. Complete a small plan and choose only the next relevant module

Record scenario/evidence level; target/tool/rationale/rejected alternative; reading/walkthrough/demo/synthetic-lab mode; source/compatibility/network/permission unknowns and owners; native-plus-data/app test criteria; GO/cutover/writers; rollback responsibility/data/time; costs/limits/cleanup/source retention. Choose only the matching next server/object/engine/app track. Add Terraform only for IaC learning, and observability/cutover only as needed. Provided source/image/identity inputs do not require another course.

**Resources for this step**

- [Compute vm](../../onboarding/compute-vm/README.md)
- [Compute aks](../../onboarding/compute-aks/README.md)
- [Compute container apps](../../onboarding/compute-container-apps/README.md)
- [Terraform](../terraform/README.md)
- [Servers](../servers/README.md)
- [Objects](../objects/README.md)
- [Database postgresql](../database-postgresql/README.md)
- [Database mysql](../database-mysql/README.md)
- [Database sqlserver](../database-sqlserver/README.md)
- [Cutover](../cutover/README.md)
- [Observability](../../onboarding/observability/README.md)

### 4.8. Prepare to replace the synthetic source with a real source

**Optional time:** 10–15 minutes. Complete this table in personal notes for one selected server, object or database scenario. Do not query a real source, create AWS resources or obtain credentials. Use synthetic aliases rather than customer inventories or internal documents.

| Topic | This exercise's inputs and results | Additional real-source questions | Check method, owner and proceed condition |
|---|---|---|---|
| Tool support | Source/target, tool and offline/online mode | OS/engine/version, required features and current support | Identify engine-specific official support guidance and the assessment owner. |
| Connectivity | Client/service/agent location, DNS, TLS and ports | Source → execution actor → target route, bandwidth and egress | The network owner defines an approved route and bounded test. |
| Authentication/permissions | Management roles, data roles and engine privileges | Supported authentication, minimum scopes and grant/revocation owner | Record permissions and approvers, never secret values. |
| Data/features | Small schema/files and content/property comparisons | Size, change rate, consistency, retained properties and extension/object compatibility | The data owner defines comparisons and synthetic test inputs. |
| Switch | A personal client's fresh read connection | Writers, final synchronization, DNS/cache/pools and allowed interruption | The app owner defines write control, GO/NO-GO criteria and switch order. |
| Recovery/cleanup | Source retention and personal-file removal | Backup/restore tests, RTO/RPO, recovery after target writes and retention | Separate recovery responsibility from deletion approval. |

1. For each row record known facts and at least one additional question. Unresolved items require an owner/check method and defer execution.
2. Distinguish managed copy/replication/CDC from compatibility, data and client checks performed by participants. Do not implement another managed migration engine.
3. Once prepared, adapt the [target client completion](../cutover/README.md#45a-use-the-migrated-result-through-a-fresh-client) to the real workload's fresh connections and reads. Operational execution requires separate approval.

**Submission:** explain all six rows for one workload, check methods, owners, proceed/stop criteria and recovery before/after target writes. A completed managed copy does not complete every preparation item. With Mover, write only service-adoption prerequisites; the separate workshop execution path is AzCopy.

This task creates personal notes only; it does not change resources, roles or source configuration.

## 5. Verification and common failures

Complete when you can justify the target/tool, reject an alternative, retain unknowns, choose an honest source-appropriate mode and define tests/GO/rollback/cost/cleanup. Common errors: target by product-name similarity, unknown→none, rewriting managed replication/CDC in code, online→zero downtime and target-write connection reversal→data rollback. Seek missing evidence and current support, not optimistic defaults.

## 6. Cleanup and ownership

This module creates no source changes, resources or jobs, so no Azure deletion is needed. Keep notes synthetic/private as appropriate. Future project/job/appliance/replica/temporary storage/target assets have separate owners; deleting a project does not erase target cost. Preserve source/backup until rollback/retention approval.

## 7. Additional considerations for a real migration

A real plan requires dependency/write-rate evidence, RPO/RTO, backup/restore, compatibility, security/regulation, consistency, licensing/network/egress, monitoring gaps, operational handoff and failure recovery. A small synthetic plan is not production approval.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.
