# Instructor guide — setup, timing, diagnostic fixtures and ownership

English | [한국어](./instructor-guide-ko.md)

Learner modules explain usable steps, expected observations and cleanup. This guide contains session design and instructor-only preparation/diagnostics. Start with the [selector](../Readme.md), [participant preparation](./participant-preparation.md) and [route examples](./module-combinations.md).

**AWS boundary:** This workshop uses illustrative AWS source and synthetic Azure samples; it does not create an AWS environment. Do not create one, query credentials/AMI or run AWS plan/apply. Use the supplied analytical Terraform, synthetic Azure data and official walkthroughs; these do not establish real EC2/S3/RDS migration.

## 1. Agree on one session scope

Privately record objective/source/module/mode; browser/local PowerShell/WSL/VM/client environments; approved target/region/cost owner; image/digest/identity/source/target/private client inputs; current support/versions/quota; management/data/engine/Kubernetes permissions; cost and timebox; expected evidence/stop/recovery; and creation/retention/cleanup owners.

Do not turn the whole workshop into an automation schema or mandatory all-tracks install. Reading, walkthrough, prepared demo and live synthetic execution have different evidence. Recheck live inputs rather than assuming a prior endpoint remains available. Service-native replication/CDC/copy/scheduling/retry stays with the official platform.

## 2. Roles and inputs

| Role | Responsibility |
|---|---|
| Instructor | Select module/mode, explain service, prepare safe inputs/demo, guide evidence and timebox |
| Azure administrator/cost owner | Confirm tenant/scope/providers/region/quota, approve grants/revocation and charges |
| Source/DB owner | Confirm source support/privileges/TLS/writers/backup/retention and recovery |
| Participant | Confirm exact targets, follow selected steps, observe errors and clean up owned resources |

Contributor is not all data/engine/Kubernetes permission. Never request nonexistent source credentials or customer inventory just to fill a demonstration. Use approved private channels for actual values, never Git/prompts/screenshots.

The shared app is one memory API, without DB adapters. VM/AKS/Container Apps consume the same digest; Functions consumes the same source with its adapter/host. Image preparation owns ACR and optional CAA UAI; consumers preserve those inputs. PG/MySQL share logical SQL, while SQL uses separate T-SQL. Seed source only and keep target empty. Server cards/planning CSV are fictional inputs, not official import or discovery output.

## 3. Introduce the service before the utility

Open the module's Microsoft Learn introduction and Portal examples. Explain Mover before AzCopy, Migrate before VM/server comparisons, and DMS/engine/target selection before DB utilities or SqlPackage. For PostgreSQL select the dedicated target migration service, not a generic classic task.

Use screenshots to explain visible stages/fields, not as evidence of a successful job. Follow current UI labels; IAM may show Check access with a previous-view link to View my access. Do not capture user rows or identifiers. Default region/group selections in forms are not approved inputs. Opening a form is not submitting it.

### Storage Mover delivery boundary

**Workshop delivery boundary:** Storage Mover is **service introduction only**: what it manages, suitable source/workload scenarios, region/cost/permission/network considerations and official documentation. This workshop does not create its endpoints/projects/job definitions, grant its execution roles or start/verify its copy engine. The hands-on object path is the separate official **private AzCopy** exercise with three synthetic objects/109 bytes. This delivery choice is not a claim that Storage Mover is universally unsupported. Future customer execution requires their own supported official scenario and administrator approval.

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.

For execution beyond the lesson, check the official source-specific scenario, management region/metadata residency, cost, identities/data roles and connectivity with the administrator. The workshop schedules only AzCopy object execution.

## 4. Private Blob diagnostic fixture

Reuse approved private endpoint/DNS/client inputs first. If missing, get separate scope/cost approval for the minimal diagnostic group/VNet/subnets/PEs/DNS and optional small x64 Linux VM. The VM has no public NIC IP/inbound SSH, uses management Run Command, and has only the selected Blob data roles. A Standard NAT/outbound public IP is not Blob public access. Approve VM/disk/NAT/IP/PE/DNS/processing charges; remove unused fixture components rather than making them everyone's prerequisite.

Keep public Disabled, default Deny, bypass None, HTTPS/TLS and anonymous/Shared Key disabled. Verify Approved PE and canonical Blob DNS/private IP/TLS/data requests from the actual client. A hub client with PEs in different spokes can fail server-to-server copy; consult the official restricted-network topology. Mover support is independent.

Guest-agent and installation outbound must be approved. HTTP/HTTPS port rules are not a domain allowlist; provide approved proxy/mirror/preinstalled tools where required. AzurePlatformDNS service-tag Allow can be unsupported in an NSG rule; follow supported platform-DNS/IP semantics instead of weakening global policy. Inspect actual NIC show output when create responses are wrapped/null. Use explicit name=value for synthetic base64 padding and script payloads for long source; do not send secrets through arguments.

Run Command's outer success is not a guest/data pass. Inspect stdout/stderr/traceback/exit and exact final pass/fail markers; output limits can truncate evidence, so keep protected full diagnostics. Do not install DB engines just for a Blob class. Reusing a diagnostic client as a DB source/client is a separately approved module scope, not a new learner prerequisite.

## 5. Database and SQL import fixture notes

Reachable source, supported versions, native-runtime topology and DB privileges must be ready before a live migration. Local containers prove SQL behavior, not Azure service reachability. PostgreSQL VNet-integrated target and Private Endpoint-only target/runtime are different; SQL client verify-full is a separate check from native-worker CA/hostname verification.

On PostgreSQL validation errors, inspect native details, connectivity, support and source conditions. A retry needs owner approval and reviewed inputs with explicit Validate; migration start is a separate approval. Compare completed schema, all rows, TLS connections and the unchanged source baseline.

MySQL offline currently needs the documented Premium tier and appropriate runtime networking. Inspect actual SELECT VERSION(), not just the management version identifier. Keep source readonly/global parameters and target truncation behind explicit approval. A target can contain the empty, specifically inspected dms_persistent_objects artifact in addition to three workload tables: record it, never DROP it to force expected counts or ignore arbitrary extras.

SQL target selection preserves requirements first: SQL Database does not replace Agent/cross-DB with a cheap three-table demo. Entra-only policy and a selected DMS tool's auth support must agree before creating paid source/SHIR. Do not bypass policy or infer DMS auth from generic Azure SQL Entra support.

For B2 direct SqlPackage, prepare private Windows client/source, official self-contained tool, valid source TLS/Windows auth, target private DNS/MI and owner-only BACPAC (not encrypted). Import into a fresh schema-empty DB. If existing contained MI user conflicts with Import, only a separately approved new isolated logical server may use temporary MI Entra-admin context and exact new-user cleanup. Always restore the original administrator and re-limit MI to the chosen DB after success/failure. Handle imported READ_ONLY only on the new target, preserving source freeze.

Prepare an approved SQL administrator and valid TLS trust for a fresh source. OS administration and SQL sysadmin are separate permissions. Any recovery or temporary elevation needs approval limited to the sandbox, followed by restoration of service/rights and cleanup of the exact temporary artifacts.

## 6. Functions and compute fixtures

Verify actual Linux Core Tools/Azurite paths/version launchers and supported installation method in WSL; Windows npm PATH entries are not Linux readiness. Keep Python/source/package support and approved feeds explicit. .funcignore/local-settings exclusions matter. Prebuilt Linux packages with build-remote false and Core Tools remote publishing are separate options; local feed exceptions do not authorize cloud builders.

Cloud host/deployment storage MI/roles/private network differs from function-level caller keys. Store keys privately and use headers, not URLs/logs; distinguish local host auth from Azure enforcement. Fresh max-one-instance HTTP tests do not prove global state across scale-out. Stop only owned emulator/host/port-forward processes.

VM private Run Command and public SSH/tunnel are separate access branches. AKS private MI client and local user/public /32 have different DNS/auth/rights; do not combine flags blindly. Preserve the documented two-node system pool and approved quota/cost. Track every new grant on external registry/VNet/NAT/DNS scopes and never delete the supplied shared inputs during consumer cleanup.

### Prepare shared completion exercises

Choose only the relevant items from [shared exercises in module combinations](./module-combinations.md#choose-shared-completion-exercises).

- **Target client:** complete the original module's verification first and retain source/profile inputs. Provide target alias, database/container, read client and expected results. Do not add an app or writer; CSV assessment ends with preparation questions unless a real test target is separately available.
- **Error distinction:** prepare permission/network cards as synthetic discussion, without changing roles, NSGs or DNS. For optional local observation, check the existing WSL app's loopback8080 and logs and avoid other writers. Teach HTTP404/422 separately from curl transport exit codes.
- **Real-source preparation:** ask participants to explain check methods, owners and proceed conditions in all six rows. Route unresolved items to their owners without using customer information, credentials or real AWS connections.
- **Finish:** clean up only personal profiles, downloads and notes. Original owners retain control of app shutdown and source/target, backup, shared identity/network cleanup. Allocate each 10–15 minute exercise separately from preparation/waits.

## 7. Timing and evidence discipline

The 360+120 minute days and module durations are hypotheses, not measured human learning clocks. Separately measure instructor setup, explanation/questions, sign-in/access, provisioning/jobs, verification and cleanup. Small rows/files and one region cannot predict production scale.

### CSV-import and application-view preparation

The [server module](../modules/migration/servers/README.md) links the one-row [synthetic inventory CSV](../modules/migration/servers/lab/synthetic-inventory.csv) and the accepted-import view. The current route is All projects → Create project → Start discovery → Using import → Server inventory (CSV) → Download .CSV file → Browse → Import. Use Download .CSV file to obtain the official template and preserve its 27-column structure and fictional capacity/unknowns. Do not upload the planning workloads.csv.

Schedule the Portal's **15-minute post-import wait** separately from explanation and later assessment. Completed / Rows processed 1 is only synthetic inventory acceptance; do not mark assessment, readiness, replication or migration complete from it. Use a dedicated owned project so cleanup cannot affect another participant or a discovered/replicating source.

For CSV assessment, teach **project Overview → Create assessment → Add workloads → select one fictional imported server → Add selection**. Review General/Advanced/Review assumptions and create only that assessment, then interpret it in Decide and plan → Assessments. The five assessment illustrations in the [server module](../modules/migration/servers/README.md) show settings, review, source/target summaries and estimates without requiring a live source or target VM.

Treat omitted utilization/IOPS and displayed default zeros as missing evidence, not measured idle data. Compare hardware input, saved sizing settings and recommendation explanations rather than relying on a single label; resolve conflicting/default assumptions before accepting a customer design. Keep support lifecycle, assessment suitability, deployment availability and actual boot/app readiness separate.

The example's 31×24-hour retail/no-AHB/no-reservation calculation excludes Defender cost; excluding that cost is not disabling protection. A USD299.42 estimate is not a deployment charge, invoice or guaranteed price. A recommended Server Migration tool does not remove the official CSV-import limitation. Do not deploy a VM, create replication or publish operation timing to demonstrate an assessment result.

The [Container Apps module](../modules/onboarding/compute-container-apps/README.md) shows an active one-replica revision and Real-time/Application stream controls. The actual approved stream can corroborate 200/201/422/404 requests, but the privacy-cropped screenshot contains no such lines. Teach status/traffic/replica observations separately from HTTP evidence, and demonstrate that Stop closes the stream rather than stopping the app. Mask selectors/revision names and crop payloads before publishing new captures.

For the [MySQL native result views](../modules/migration/database-mysql/README.md), use the existing owned classic service/project/Offline activity, then workshop and its three table results. Approximate ~10 row progress, rounded 00:00:00 table times and a seven-second database activity display are not exact comparisons or a full lab clock. Pair native completion with the independent thirty-row/schema/source-baseline/TLS evidence.

Storage Mover is introduction-only in the [Objects module](../modules/migration/objects/README.md). Teach the separate approved AzCopy result; do not schedule Mover setup, permission grants, copy runs or cleanup as participant work.


Keep actual versions/region/mode/native state/data/feature checks/errors/exit codes, source-write status, approved scope and residual resources/grants/cost in safe instructor records. Do not print actual IDs/emails/tenant details here. Validate the selected inputs and approvals for each session.

### Cost-analysis and budget walkthrough preparation

The [observability module](../modules/onboarding/observability/README.md) includes five privacy-reviewed screenshots for date presets, grouping, a narrowly filtered historical chart, budget inputs and alert conditions. Prepare an approved scope and observation period before teaching; the demonstrated chart applied Last 7 days, Group by Resource group and a filter for only a previous workshop Container Apps group. Its $0.06 was historical accrued cost after deletion, not an invoice or current full-workshop total. Forecast was unavailable with only one cost point.

If an older Portal tab fails to render Cost analysis (for example a React prewarmer error), try a fresh Portal tab using the normal authenticated SSO flow. Do not bypass sign-in, change billing scope or treat a broken view as zero cost. Reserve navigation/loading/authentication recovery time separately from teaching time; no new duration is asserted for these views.

Keep the budget demonstration as a form preview unless creation is separately approved. The example used 100 USD/Monthly and Actual cost 80% (80 USD), with no action group; the visible two-year default end date is not a workshop recommendation. No recipient was entered, final Create was not submitted and existing budgets were unchanged. Do not report previewed fields as a saved budget or tested alert. If a live budget is approved later, assign its exact scope/name/end date/recipient and cleanup owner independently.

## 8. Teaching flow and fallback

Explain goal/mode/inputs/cost/owners/stop boundaries first. Read the official service purpose/support. Execute approved steps one at a time, compare expected/actual evidence, and explain long waits rather than auto-upgrading SKU/rights. On failure inspect native error/source conditions, stop and obtain correction approval. End with native plus data/app/feature evidence and owner cleanup/retention.

Without AWS source use a guided flow/synthetic case/prepared result, never fabricated discovery/replication/S3/RDS output. Storage Mover always remains introduction-only in this workshop. Without a supported DB runtime/source, use the appropriate walkthrough/demo; Compare utility output separately from native service results. If the timebox ends, reserve later observation or use an explicitly prepared demonstration for a selected execution module. Cards A–D distinguish assumed readiness, verified pre-write personal return, post-write recovery and unknown/NO-GO.

## 9. Cleanup responsibility and session outcome

Consumers own only their new app/VM/cluster/namespace/target/jobs and exact new grants. Publisher deletes shared image/UAI only after last consumer. Fixture deletes its own VM/network/PE/DNS/new roles after data consumers finish, preserving input accounts/source. Native job cancel/definition deletion/project removal/stop replication/target destruction/data rollback are different actions. Source/backups remain until acceptance/recovery/retention approval.

List exact scope/name/lab tags/resources/grants and impact before deletion approval, then independently verify remnants and billing reporting delays. Do not infer zero cost from deallocation or immediate No data. Track source/target/data/backup/roles/network/artifacts separately. Avoid broad recursive folder deletion, subscription discovery-and-delete, customer DROP/TRUNCATE or automatic writer changes.

Report selected mode, supported inputs/versions, actual native/data/app observations, errors/unknowns, owned cleanup versus retained inputs and next steps. This is a short educational record, not a migration orchestration schema. Preserve privacy and real safety/support limits without putting authoring/debug history into learner instructions.

### SQL Server — choose the target before the migration tool — Isolated local T-SQL tests

Optional instructor-only isolated validation. This is not a learner requirement to take/run the shared app. Use the repository-root WSL environment and approved Docker/image/dependency sources; the existing sample-app pytest environment is only reused as test tooling. Select only the engine being taught. Tests create new network-isolated containers, publish no ports, require explicit SQL Server Developer EULA acceptance when selected, and remove only their own containers/volumes. They test real error/rollback/constraint behavior; a pass is not native service or AWS migration evidence. Record actual versions/digests and exit/errors privately.

```bash
docker pull mcr.microsoft.com/mssql/server:2019-latest
cd sample-app
WORKSHOP_SQLSERVER_ACCEPT_EULA=Y UV_PROJECT_ENVIRONMENT=.venv-wsl \
  uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k sqlserver
```

### Shared synthetic database inputs — Isolated PostgreSQL/MySQL engine tests

Optional instructor-only isolated validation. This is not a learner requirement to take/run the shared app. Use the repository-root WSL environment and approved Docker/image/dependency sources; the existing sample-app pytest environment is only reused as test tooling. Select only the engine being taught. Tests create new network-isolated containers, publish no ports, require explicit SQL Server Developer EULA acceptance when selected, and remove only their own containers/volumes. They test real error/rollback/constraint behavior; a pass is not native service or AWS migration evidence. Record actual versions/digests and exit/errors privately.

```bash
docker pull postgres:16
cd sample-app
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k postgresql
```
## Functions HTTP validation tooling

Run local adapter/host checks only in WSL Bash in a repository `lab-output/functions-<id>` stage containing the shared source/adapter/host, approved Python 3.12 dependencies and stage venv. Install pytest/httpx only in this validation environment, not cloud runtime requirements. Host tests need a fresh single-worker localhost:7071 host and Azurite; inspect state before repeating and stop only your own host/emulator.

Run the final cloud command from `sample-app`, reusing its existing pytest tooling without requiring learners to take/run that app course. Use only an explicitly approved fresh HTTPS/max-one-instance Function App, protected function-level key file and synthetic-write authorization. Never target customer or mutated shared endpoints. Expect no-key/wrong-key 401, health 200, POST 201/read-back, invalid 422 without mutation and 404; durable scale-out state and other triggers need their own tests.

```bash
uv pip install --python .venv pytest
PYTHONPATH=. .venv/bin/python -m pytest -q \
  ../../modules/onboarding/compute-functions/verify/test_adapter.py
```

```bash
uv pip install --python .venv httpx
WORKSHOP_FUNCTIONS_LOCAL_URL=http://127.0.0.1:7071 PYTHONPATH=. \
  .venv/bin/python -m pytest -q \
  ../../modules/onboarding/compute-functions/verify/test_adapter.py \
  ../../modules/onboarding/compute-functions/verify/test_host.py
```

```bash
: "${WORKSHOP_FUNCTIONS_CLOUD_URL:?Set the approved fresh HTTPS Function App URL}"
: "${WORKSHOP_FUNCTIONS_KEY_FILE:?Set the protected function-level key file}"
: "${WORKSHOP_CLOUD_WRITE_APPROVED:?Explicit synthetic write approval is required}"
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run --frozen --no-sync pytest -q -s \
  ../modules/onboarding/compute-functions/verify/test_cloud.py
```
