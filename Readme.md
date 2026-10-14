# Azure Migration Workshop

English | [한국어](./Readme-ko.md)

A modular workshop for engineers familiar with AWS who want to understand Azure, redeploy a small app and learn migration-tool selection, validation and cleanup. Choose the modules that match your workload; this is not a production migration product or an all-tracks deployment.

**AWS disclaimer:** AWS Terraform is analysis-only input. The workshop uses synthetic Azure files, databases and app deployments for learning; it creates no AWS environment and transfers no real EC2, S3 or RDS/Aurora workload.

## 1. Choose modules for your workload

| Your goal/source | Choose | Outcome/minimum inputs | Skip |
|---|---|---|---|
| IAM concepts and access scopes | [Identity](./modules/onboarding/identity/README.md) | Read definitions/assignments; approved user/read scope | App, compute, DB, Terraform |
| VPC/subnet/SG concepts | [Networking](./modules/onboarding/networking/README.md) | Interpret VNet/NSG; optional dedicated probes | Other compute/app/data |
| S3 user learning Blob | [Storage](./modules/onboarding/storage/README.md) | One private authenticated Blob/read-back; private DNS/client/data identity | App, compute, IaC, DB |
| Object-migration tools | [Storage Mover/AzCopy](./modules/migration/objects/README.md) | Mover introduction only; separate private AzCopy lab (3 objects/109 bytes) | App, compute, DB, Terraform |
| EC2/ECS HTTP app with less server management | [Container Apps](./modules/onboarding/compute-container-apps/README.md) | Shared digest/UAI pull, HTTPS/read-write; approved inputs | VM, AKS, Functions, data |
| EC2 + Docker operating model | [VM + Docker](./modules/onboarding/compute-vm/README.md) | OS/Docker/MI/localhost HTTP; approved image/VM/network | AKS, Container Apps, Functions |
| EKS/Kubernetes operating model | [AKS](./modules/onboarding/compute-aks/README.md) | Deployment/Pod/Service/probes; manifest or approved cluster inputs | Other compute, DB, Blob |
| Lambda/HTTP trigger concepts | [Functions](./modules/onboarding/compute-functions/README.md) | Same source/ASGI adapter, host and auth; selected local/cloud inputs | Other compute and ACR image |
| Existing OS/disk/services must remain | [Azure Migrate servers](./modules/migration/servers/README.md) | Synthetic CSV import/Portal assessment and estimate interpretation; replication needs a separate actual source | Container redeployment as a substitute |
| PostgreSQL | [Dedicated migration service](./modules/migration/database-postgresql/README.md) | Validate/offline/native plus schema/data; supported reachable source | Other engines/app |
| MySQL | [MySQL DMS](./modules/migration/database-mysql/README.md) | Current native checks/activity plus data; approved Premium/runtime inputs | Other engines/app |
| SQL Server | [SQL targets, DMS and SqlPackage](./modules/migration/database-sqlserver/README.md) | Target functionality first; data-only B2 or prepared feature demo | Other engines/app |
| IaC analysis/redesign | [Terraform](./modules/migration/terraform/README.md) | Requirements/static checks; optional new Azure consumer | AWS login/plan/apply |
| Decision-making only | [Planning](./modules/migration/planning/README.md) + [Cutover](./modules/migration/cutover/README.md) | One synthetic plan/runbook; no cloud required | Live jobs/resources |
| Interpret status/logs/cost | [Observability](./modules/onboarding/observability/README.md) | Cards or one existing approved resource/read scope | New mandatory compute |

The [shared app](./sample-app/README.md) is a reuse asset, not a prerequisite for every learner. [Image preparation](./shared/container-image/README.md), [private Blob inputs](./shared/storage-private-access/README.md) and [synthetic DB inputs](./shared/database-sample/README.md) are optional ways to supply inputs. Approved existing inputs let you skip preparation, without taking their producing track.

## 2. Prepare only for the selected mode

Start with [participant preparation](./guides/participant-preparation.md). Choose reading, a Portal walkthrough, a prepared instructor demonstration or an approved synthetic lab. Instructors use the [instructor guide](./guides/instructor-guide.md) and [module combinations](./guides/module-combinations.md), not the learner modules as session reports.

CLI examples use local PowerShell 7.4+; app/local host examples use WSL/Linux Bash; guest steps explicitly use VM Bash or private Windows PowerShell. Do not share virtual environments across Windows and WSL. Install only the tools your chosen mode needs, from approved sources.

If your selected CLI mode needs authentication, inspect versions:

```powershell
$PSVersionTable.PSVersion
az version
```

Use fail-fast behavior and the approved sign-in/MFA path:

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az login
```

Confirm the exact subscription without changing a person's default:

```powershell
$SubscriptionId = "<sandbox-subscription-id>"
$ParsedSubscriptionId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedSubscriptionId)) {
    throw "Replace SubscriptionId with the approved sandbox subscription ID."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
```

Expected: the agreed tenant/subscription and Enabled state. Login does not grant data access. See [PowerShell installation](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) and [Azure CLI installation](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli).

## 3. Understand the Azure resource boundary

Read the [Resource Manager introduction](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) when needed:

```text
Management Group
  └─ Subscription
       └─ Resource Group
            └─ Resource
```

These are not one-to-one AWS Organizations/Account/tag-group equivalents. Subscription is an important billing/access boundary. Group location is management metadata, not a requirement that every contained resource use that region. RBAC can inherit down scopes; tags do not inherit the same way. Deleting a group deletes its contained resources, so ownership matters.

## 4. Services first, verification second

Introduce [Azure Migrate](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview) alongside servers, [Storage Mover](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview) alongside [AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10), and [DMS](https://learn.microsoft.com/en-us/azure/dms/dms-overview) alongside engine-specific tools. PostgreSQL uses its [dedicated migration service](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql); SQL [SqlPackage](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage?view=sql-server-ver17) Export/Import is not DMS.

Source availability and current support determine which steps can be live. Migrate CSV assessment cannot replicate an imported item. Mover private service connectivity is not proven by private AzCopy. SQL Database/MI/SQL VM have different feature/mode/authentication boundaries. Introductions and screenshots illustrate selection; native status must be accompanied by observable app/data/schema evidence.

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.

## 5. Safety, cost and cleanup

Use synthetic data and approved sandbox targets only. Never publish credentials, real customer inventory/data, internal documents, tokens, sensitive logs or identifiers in prompts/screenshots. Blob defaults to public Disabled with private endpoint/DNS/client and Entra/RBAC; identity controls do not replace private networking. Do not disable TLS, Shared Key restrictions or organization policy to make a lab work.

Confirm scope, minimum rights, quota, current support, costs and destructive effects before approval. The [pricing calculator](https://azure.microsoft.com/en-us/pricing/calculator/) is an estimate, not an invoice or enforced spending cap. [Cost Management](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management) budgets are alerts, not guaranteed shutdown.

Consumers clean up only their owned apps/clusters/VMs/jobs and exact new grants; publishers remove shared inputs after the last consumer. Protect source/backups through accepted retention/rollback decisions. A deleted job or stopped VM does not erase all disk/storage/runtime costs. Target new writes require data recovery, not simply a connection reversal.

## 6. Optional: use GitHub Copilot with explicit boundaries

Understand the manual procedure first. Delegate only your selected module, not every track; do not replace managed replication/CDC/copy/scheduling with new code. Keep analysis, drafting and approved execution separate.

```text
My selected module is <module>, and my goal is <learning objective>.
Read its inputs, outcomes, minimum dependencies and excluded tracks.
Explain the Azure service/official tool and native Portal flow first.
Distinguish actual-source requirements from synthetic examples and demos.
Use source/IaC/app evidence only when that is my selected objective.
Do not create AWS resources or query AWS credentials/AMI, plan or apply.
Do not deploy, change permissions or create paid resources during analysis.
```

After reviewing the analysis:

```text
Draft only the selected module's configuration/instructions.
Explain native assessment/validation/job status/errors and expected outcomes.
Reuse the same app and approved image/identity/DB inputs.
Do not implement a managed replication/CDC/copy/scheduler platform.
Document verification and owner-specific cleanup.
Do not add tools/tests/deployments from unrelated tracks.
Do not execute Azure plan/apply/destroy, commits or push without approval.
```

For an approved execution session:

```text
Assist only with the approved sandbox/module/mode.
Show tenant/subscription/region/group/inputs/permissions/cost and effects.
Obtain separate approval for assignments, creation, migration start and writes.
If Terraform is selected, show the saved plan before apply approval.
Check actual native status plus the selected app/data/schema criteria.
Report actual exit codes, errors and unknowns, not proposed commands as results.
Show exact cleanup targets and obtain separate deletion approval.
```

Review changed files, actual commands/exit codes/responses, owned resources/grants, cleanup and unresolved support/evidence. AI suggestions do not authorize operational cutover. See [Copilot in IDEs](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-in-ides) and [Copilot on GitHub](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github).
