# Module combinations — design only the route you need

English | [한국어](./module-combinations-ko.md)

Use the [workload selector](../Readme.md) and [participant preparation](./participant-preparation.md) to choose one main objective. Add foundation concepts only where needed; every combination does not need compute and a database. Detailed setup, timing observations and diagnostic fixtures belong to the [instructor guide](./instructor-guide.md).

## 1. Suggested routes

| Objective | Suggested modules | Exclude by default |
|---|---|---|
| Small HTTP app with less server work | Needed Identity/network concepts + Container Apps + observability | VM, AKS, DB and migration |
| EC2 + Docker operations | VM + Docker + needed identity/network + observability | AKS/Container Apps/DB as prerequisites |
| EKS/Kubernetes team | AKS manifest/cluster + identity/network differences | Other compute and all DB engines |
| Lambda/HTTP concepts | Functions adapter/host/auth + needed observation | Same ACR image, all triggers and other compute |
| S3/object priority | Optional Blob basics + Mover introduction/private AzCopy lab + planning/cutover | App/compute/DB/Terraform |
| One DB engine | PostgreSQL service OR MySQL DMS OR SQL target/DMS/SqlPackage + planning/cutover | Other engines and app adapter |
| Existing OS/services must remain | Migrate synthetic CSV/Portal assessment + planning/cutover; real replication is a separately prepared scope | App redeployment as a substitute; target VM deployment during assessment |
| IaC analysis only | Terraform reading/static checks + relevant resource concepts | AWS execution and mandatory Azure deployment |
| Decisions only | Planning + cutover synthetic cards | Resource creation and live native jobs |

Links to all selected modules and their minimum inputs are in the root selector. A supplied approved image/identity/source/private client can replace preparation, not the explanation of its scope/owner. Blob routes need approved private endpoint/DNS/client inputs, not a VM+Docker course or public-network exception.

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.

## 2. One-day onboarding example

This is a planning hypothesis of 360 instructional minutes plus 120 minutes for lunch/breaks/environment response, not a measured learner duration or mandatory syllabus.

| Topic | Planned minutes |
|---|---:|
| Scope and resource hierarchy | 30 |
| Identity/RBAC/management versus data | 50 |
| Network concepts/configuration, no optional probe VMs | 35 |
| Optional private Blob basics | 45 |
| Image/digest and publisher/consumer boundaries | 30 |
| Selected Container Apps deployment/expected outcomes | 65 |
| Portal observability/cost interpretation | 45 |
| Owner-specific cleanup and unknowns | 30 |
| Compute comparison/recap/optional Copilot boundaries | 30 |
| Total | 360 |

Do not squeeze AKS/VM into the same 65-minute slot by weakening support/safety. Reduce optional topics, prepare approved inputs ahead or schedule another session. If live inputs are unavailable, clearly choose walkthrough/demo instead.

## 3. One-day migration example

Choose one supported synthetic object/DB path or a prepared server demonstration, not a nonexistent AWS job. The same 360+120 minute hypothesis can allocate:

| Topic | Planned minutes |
|---|---:|
| Preservation requirements and native tool choice | 50 |
| Source/target/permissions/network/cost | 45 |
| Portal/native validation/assessment and impact gates | 50 |
| One approved tool execution or prepared demo | 70 |
| Native progress/error/support interpretation | 35 |
| Data/schema/needed features | 30 |
| Cutover tabletop or approved personal read-client switch | 40 |
| Ownership/retention/cleanup | 20 |
| Real-migration checklist/recap | 20 |
| Total | 360 |

Objects introduce Mover and execute only the separate private AzCopy lab, DB chooses one engine/current native path, and Migrate separates CSV assessment from real replication/test. Expensive MI/runtime/appliance or long preparation may justify a prepared demo; do not report it as the participant's own source migration.

## 4. Half-day or self-guided route

End after one independent goal and its observable criteria. Reuse existing approved inputs, keep long setup/job waits outside the learning segment and add only necessary concept reading. Replace an execution segment with Terraform only when IaC is the goal; do not remove service/tool introductions from migration education.

No real AWS environment was constructed; synthetic Azure results are learning substitutes, not actual AWS authentication/discovery/transfer. Online is not guaranteed zero downtime. A new-write target requires data recovery, not only connection return. Instructors measure actual explanation, questions, setup, waits and cleanup and adjust the next session rather than treating this timetable as measured.
