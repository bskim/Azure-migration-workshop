# Terraform — read the AWS example and redesign the Azure execution model

English | [한국어](./README-ko.md)

Extract application requirements from illustrative AWS IaC and the shared source, then compare a separate Azure Terraform deployment. AWS credentials, resources, AMI lookup, plan and apply are outside this lab.

## 1. Learning objectives and module boundaries

For engineers who read Terraform resources/variables/outputs; allow about 80 minutes. Choose source analysis through step 4.3, optional cloud-free static checks in 4.4, or an independently approved Azure target in 4.5. Analysis needs only source files; static checks need Terraform/download access; deployment consumes an existing approved image/registry/pull identity. Do not require the shared app server or another compute course. This Azure example is one Container Apps design, not a universal VM/AKS/DB conversion.

**Resources for this step**

- [Shared FastAPI application](../../../sample-app/app.py)
- [Container image](../../../shared/container-image/README.md)

### Choose analysis, static checks or an Azure target

Source analysis produces requirements and a non-equivalent service mapping without installing packages or logging in. Static fmt/init/validate adds local structural evidence only. Optional Azure deployment verifies its own new app and cleanup, consuming image/identity inputs rather than requiring Container Apps CLI deployment. End at the scope you selected.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Overview](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Container registry intro](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/overview)
- [Virtual networks overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)

## 3. Prerequisites, permissions and cost

Terraform commands use local PowerShell 7.4+ from this module directory. The configuration requires Terraform >=1.11,<2; the example baseline pins AWS provider 6.68.0, AzureRM 5.9.0 and Container App AVM 0.9.0 in source/lock files. init downloads providers/modules but does not deploy. Static checks need no cloud login/region/paid resources. Approve download sources; do not disable TLS. Azure deployment separately needs approved tenant/subscription/region/provider/quota/cost, new target rights and external identity assign rights. Protect tfvars/plans/state, which may contain sensitive data. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Read the illustrative AWS source

Inspect main.tf/variables.tf/outputs.tf, user_data and Dockerfile. Identify VPC/public subnet/route/Internet Gateway, a documented client CIDR for TCP8080 and EC2 Docker execution. 192.0.2.1/32, AMI and image placeholders are documentation inputs, not a live AWS environment. user_data prepares runtime, not business logic. Broad outbound is a teaching simplification for installation/pull; it is not a production AWS network recipe. Do not run AWS plan/apply or lookup credentials/AMI.

```text
VPC → public subnet → route / Internet Gateway
                   → Security Group: TCP 8080 from the client CIDR
                   → EC2: run the shared image with Docker
```

**Resources for this step**

- [Main.tf](./lab/aws/main.tf)
- [Variables.tf](./lab/aws/variables.tf)
- [Outputs.tf](./lab/aws/outputs.tf)
- [Shared Dockerfile](../../../sample-app/Dockerfile)

### 4.2. Read application execution requirements

Find Uvicorn/EXPOSE port8080, /health and /items read/write, two seed items/max100 and process-local memory in source/Dockerfile. No AWS/Azure SDK calls exist. Separate container base OS from unknown host OS. Local app execution can verify HTTP contracts but not EC2 boot/AWS networking.

**Resources for this step**

- [Shared FastAPI application](../../../sample-app/app.py)
- [Shared Dockerfile](../../../sample-app/Dockerfile)

### 4.3. Compare the mapping and separate Azure configuration

The example selects Container Apps to reduce OS management for a stateless HTTP container, not because EC2 always maps to VM. Compare managed environment versus custom VPC, HTTPS443 ingress versus container8080, ACR digest/MI versus an image placeholder, and new group/environment/app lifecycle/state. Network/security/routing are not equivalent automatic conversions. AVM is used only for the Container App; group/environment are small direct declarations, registry/UAI are inputs, telemetry is disabled and logs use streaming. Do not convert AWS state into Azure state or copy AVM internals.

**Resources for this step**

- [Main.tf](./lab/azure/main.tf)
- [Versions.tf](./lab/azure/versions.tf)
- [Variables.tf](./lab/azure/variables.tf)

### 4.4. Statically check both configurations without a cloud

Run fmt -check, init -backend=false -input=false and validate for each source folder. Expect Success! The configuration is valid for both. This checks syntax/provider schema/module inputs, not permission, region/quota/network/image execution or migration. No AWS credentials/login/plan/apply is needed.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
terraform version
terraform -chdir=.\lab\aws fmt -check
terraform -chdir=.\lab\aws init -backend=false -input=false
terraform -chdir=.\lab\aws validate
terraform -chdir=.\lab\azure fmt -check
terraform -chdir=.\lab\azure init -backend=false -input=false
terraform -chdir=.\lab\azure validate
```

### 4.5. Optional: review and apply only an approved Azure plan

Consume the approved image/registry/UAI or only relevant shared preparation steps. Copy example tfvars into a protected local workshop.tfvars with a fresh lab_id/new target group, not imports of existing groups. Show the exact account and verify group absence. Create a saved plan and inspect subscription/region/lab ID, new target group/environment/app only and no existing changes/deletes. Apply the exact saved plan only after explicit approval: saved-plan apply has no further confirmation. Verify this fresh target's HTTPS /health and write/read-back, not another app or actual AWS traffic/data migration.

```powershell
$SubscriptionId = "<sandbox-subscription-id>"
$TargetGroupName = "rg-amw-tf-<your-eight-character-lab-id>"
az login
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$Exists = az group exists --name $TargetGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Use a fresh target group; do not import or reuse an existing group." }
terraform -chdir=.\lab\azure validate
terraform -chdir=.\lab\azure plan -var-file=workshop.tfvars -out=workshop.tfplan
terraform -chdir=.\lab\azure show workshop.tfplan
```

```powershell
terraform -chdir=.\lab\azure apply workshop.tfplan
$BaseUrl = terraform -chdir=.\lab\azure output -raw app_url
if ($BaseUrl -notmatch "^https://") { throw "No HTTPS app URL was returned." }
Invoke-RestMethod "$BaseUrl/health"
```

```powershell
$Health = Invoke-RestMethod "$BaseUrl/health"
$Before = @(Invoke-RestMethod "$BaseUrl/items")
$Created = Invoke-RestMethod "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":"terraform-workshop-item"}'
$After = @(Invoke-RestMethod "$BaseUrl/items")
if ($Health.status -ne "ok" -or $After.Count -ne $Before.Count + 1 -or
    -not ($After | Where-Object { $_.id -eq $Created.id -and $_.name -eq $Created.name })) {
    throw "Terraform target HTTP verification failed."
}
```

**Resources for this step**

- [Container image](../../../shared/container-image/README.md)
- [Workshop.example.tfvars](./lab/azure/workshop.example.tfvars)

## 5. Verification and common failures

validate success is structural only. Investigate approved provider/module download/proxy/TLS, Azure authentication/provider/quota/scope, and registry digest/RBAC/identity assignment/propagation on deployment errors. Reject any request for AWS credentials or AWS plan/apply in this exercise. LLM conversions are reviewable drafts, not guaranteed semantic equivalence.

## 6. Cleanup and ownership

Static checking created no cloud resources; caches may be reused and dependency locks retained. For Azure use this target directory and its actual state, retain target group name before outputs disappear, inspect state and a saved destroy plan, approve only owned target deletion and apply that exact plan. Verify group absence/managed-state cleanup; accepted deletion or ScheduledForDelete is not final absence. Preserve input registry/UAI, other states and local recovery records until confirmation. Publisher cleanup follows the final consumer.

```powershell
$TargetGroupName = terraform -chdir=.\lab\azure output -raw resource_group_name
az group show --name $TargetGroupName --subscription $SubscriptionId --query "{name:name,tags:tags}" --output json
terraform -chdir=.\lab\azure state list
terraform -chdir=.\lab\azure plan -destroy -var-file=workshop.tfvars -out=cleanup.tfplan
terraform -chdir=.\lab\azure show cleanup.tfplan
```

```powershell
terraform -chdir=.\lab\azure apply cleanup.tfplan
$ExistsAfterCleanup = az group exists --name $TargetGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfterCleanup -ne "false") { throw "Terraform target group deletion has not been verified." }
```

**Resources for this step**

- [Container image](../../../shared/container-image/README.md#6-cleanup-and-ownership)

## 7. Additional considerations for a real migration

Reassess targets when source requires OS-dependent services or persistent state. Verify network/TLS/auth/source restrictions, durable logs, external data and operational equivalence separately. Plan cutover/rollback/downtime and manual review of AI IaC drafts. Name substitution or validate alone is never complete migration.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

The Container App AVM dependency is version 0.9.0 under the MIT license. It is consumed as a module, not copied into this repository or presented as a complete automatic AWS conversion.

**Resources for this step**

- [Overview](https://learn.microsoft.com/en-us/azure/developer/terraform/overview)
- [V0.9.0](https://github.com/Azure/terraform-azurerm-avm-res-app-containerapp/tree/v0.9.0)
- [Test cloud.py](../../onboarding/compute-container-apps/verify/test_cloud.py)
