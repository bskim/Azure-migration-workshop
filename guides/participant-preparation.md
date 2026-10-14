# Participant preparation — only what your selected module needs

English | [한국어](./participant-preparation-ko.md)

Start at the [workload selector](../Readme.md) and choose your objective, module and learning mode. Reading, a Portal walkthrough, a prepared instructor demonstration and an approved synthetic lab have different prerequisites. You do not need to install every tool or deploy every track.

**AWS disclaimer:** This workshop uses illustrative AWS source and synthetic Azure samples; it does not create an AWS environment. AWS Terraform is analytical input, and Azure synthetic files/DBs/apps are learning samples, not actual AWS migration evidence.

## 1. Choose the scope

1. Read your module's inputs, outcomes, excluded work and cleanup owner.
2. Choose one compute model or one DB engine only if that is your goal; Blob/IaC/planning learners do not need an app server.
3. Agree on reading/walkthrough/demo/live synthetic scope with your instructor.
4. Use the matching preparation row below and the module's actual tool/version/environment requirements.

Use [module combinations](./module-combinations.md) for optional routes. Timing estimates are planning aids; deployment/permission/job waits vary.

## 2. Share safe requirements, not sensitive values

Tell your instructor the source type (for example EC2, EKS, S3 or a DB engine), objective, Azure/CLI/SQL/Kubernetes experience, preferred mode, Windows/WSL/client availability and policy constraints. Indicate whether sandbox, roles, region/quota and cost approval are ready.

Do not put customer names, real inventory/data, subscription/tenant IDs, credentials, tokens or internal documents in public surveys, Git, prompts or screenshots. Actual environment values belong in an approved private channel. Never share MFA codes or bypass sign-in policy.

## 3. Prepare only the required tools

| Selected mode | Prepare | Do not add automatically |
|---|---|---|
| Planning/cards/source reading | Browser/text/CSV/SQL reader | Azure/AWS login or deployments |
| Portal service selection/observations | Approved user and appropriate read/management scope | Full CLI/Terraform toolchain |
| Migrate synthetic CSV assessment | Approved dedicated project/assessment permissions, browser and the [one-row CSV](../modules/migration/servers/lab/synthetic-inventory.csv); allow post-import wait | Actual AWS/source VM, replication appliance, new target VM |
| Identity/network CLI | PowerShell 7.4+, Azure CLI | App/compute/DB |
| Blob data operations | Approved private endpoint/DNS/client and actual data identity; selected CLI/MI path | Docker/ACR/app/other compute course |
| Local shared app | WSL/Linux Bash, uv, Python 3.12 | Azure login/DB/cloud SDK |
| Optional local container | Working Docker daemon and approved image/package supply | Mandatory Azure registry |
| VM + Docker | Selected image/registry/VM/MI; SSH branch needs keys/tunnel, private branch needs Run Command/outbound | Public IP/SSH in the private branch; other compute |
| AKS | Supported kubectl/kubelogin, cluster/network/image/roles; private API needs reachable private client/DNS | Public API opening or another compute course |
| Container Apps | Supported CLI/core commands, image and approved UAI pull/assign rights | Optional extension unless required; VM/AKS |
| Functions HTTP | Reading: source; local: Python/Core Tools v4/Azurite; cloud: supported hosting/storage/auth/deployment | Same ACR image or every event trigger |
| Terraform static checks | Terraform and approved provider/module downloads | AWS login/plan/apply or paid Azure execution |
| One DB engine | Supported SQL client/source/empty target and selected native tool connectivity/privilege | Other engines or shared-app DB adapter |
| SQL B2 | Official SqlPackage/private Windows client, protected BACPAC, source TLS/Windows auth, target MI/empty DB and approved import/restoration permissions | DMS/SHIR/Blob/SQL target password |
| AzCopy object lab | Official utility and source Reader/target Contributor with both private paths and supported topology | Mover execution or custom copy code |

Keep PowerShell, local WSL Bash and VM Bash distinct. Windows .venv and WSL .venv-wsl are not interchangeable. See [PowerShell install](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) and [Azure CLI install](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli). Use approved package/image sources; do not disable TLS/signature checks or add fallback feeds.

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.

## 4. Confirm network and identity inputs

Login does not grant management, data, engine or Kubernetes access automatically. Contributor is not role-assignment permission or DB superuser. A local user, VM MI, AKS kubelet and Container Apps UAI are different principals. Use [Identity](../modules/onboarding/identity/README.md) concepts if needed without requiring its whole lab.

Blob defaults to public network Disabled, Deny/bypass None, no anonymous/Shared Key and approved private endpoint/DNS/client. Canonical hostname resolution and routes must work from the actual execution location. Local WSL, Cloud Shell and Portal account management do not imply private data access. Reuse approved [private inputs](../shared/storage-private-access/README.md), or use an instructor fixture/walkthrough; do not open public access.

Native migration needs source/tool/target connectivity, actual supported versions and separate DB privileges. Storage Mover is introduction-only; participants prepare only the selected AzCopy source Reader/target Contributor scopes. CSV assessment is not a replication source. Where the participant's applicable policy requires Entra-only SQL, the selected tool must support that authentication; generic target Entra support alone is not enough. This is not an Azure-wide authentication requirement.

Functions local settings are emulator-only, excluded from Git/publication. Cloud storage MI, HTTP function keys and per-user application authentication are distinct. Prebuilt source packaging and Core Tools remote publication are separate supported paths; confirm the cloud builder's approved package sources separately.

If approved image/identity/source/client inputs are supplied, skip their generation rather than completing another track. [Image preparation](../shared/container-image/README.md) does not deploy an app or cluster.

## 5. Cost and safety agreement

Confirm exact directory/subscription/region/group/owner/mode, current support/quota, minimum permissions, costs and stop/cleanup conditions. The [calculator](https://azure.microsoft.com/en-us/pricing/calculator/) is an estimate; budgets are alerts, not enforced caps. AKS nodes/disks/outbound, Premium DMS, SQL runtime/MI/VM, private fixtures/storage/backup and egress can incur substantial costs.

Do not change source readonly/writers, truncate/overwrite target data, Complete migration, assign roles or delete resources without the applicable explicit approval. Read-only/demo alternatives are valid when live prerequisites are unavailable. Keep source/backups for the agreed retention/recovery decision.

## 6. Stop when evidence or scope is wrong

Stop for an unexpected target/owner; unsupported source/version/mode; missing source/network/rights/cost approval; requests for public credentials; preexisting target data; actual output differing from expected; unresolved schema/features despite job success; or unknown target writers/rollback responsibility.

Do not replace errors with defaults, broaden permissions, delete data or invent migration code. Record the actual error and ask the instructor/administrator to resolve the approved path.

## 7. Finish with owner-specific cleanup

Follow your chosen module: consumers remove their own resources and exact new grants first; shared publishers clean up only after the final consumer. Do not delete external sources/backups/teacher inputs, keys, other groups or entire working folders. Verify actual resources/data/grants and delayed cost, retaining only safe records. Preparation, timing and diagnostic fixture responsibilities are in the [instructor guide](./instructor-guide.md).
