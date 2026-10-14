# Shared preparation — publish only the application image

English | [한국어](./README-ko.md)

Create image inputs reused by VM + Docker, AKS, Container Apps and the selected Terraform target. This preparation deploys no app, VM or cluster; skip it when an approved image already exists.

## 1. Learning objectives and module boundaries

Allow 30–40 minutes plus build/role propagation. Inputs: shared sample-app, approved Azure scope/region/rights. Outputs: immutable image digest, RegistryServer and RegistryId. Only Container Apps/current Terraform also need PullIdentityId, so use steps 4.1–4.3; VM/AKS use 4.1–4.2 and grant their own identity/kubelet access in their module. These identities are not interchangeable.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Container registry intro](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)
- [Container registry tasks overview](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-overview)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)
- [Sample app](../../sample-app/README.md)

## 3. Prerequisites, permissions and cost

Use local PowerShell 7.4+/Azure CLI at the root, with WSL Docker only for the chosen local-image publication branch. Approve ContainerRegistry and optional ManagedIdentity registration, new group/registry/build rights and separate roleAssignments/write. ACR Basic/build/storage/transfer can cost money even with no app. Use approved base-image/package/build sources and no secrets/internal feed tokens in context/Dockerfile/logs. This example uses RBAC-mode ACR with admin disabled, not an ABAC-role tutorial. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Confirm the target and fresh preparation group

Read CLI version and approved account/tenant/Enabled state. Generate dedicated image group/registry/optional identity names and verify group absence/name availability. Review resources/costs before approval.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az version
az login
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$ParsedId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedId) -or
    [string]::IsNullOrWhiteSpace($Location) -or $Location -like "<*") {
    throw "Set the approved subscription ID and region."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$ImageLabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ImageGroupName = "rg-amw-image-$ImageLabId"
$RegistryName = "acramw$ImageLabId"
$IdentityName = "id-amw-image-$ImageLabId"
[pscustomobject]@{ Subscription = $SubscriptionId; Region = $Location; Group = $ImageGroupName; Registry = $RegistryName } | Format-List
$Exists = az group exists --name $ImageGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Do not reuse an existing group." }
$Available = az acr check-name --name $RegistryName --subscription $SubscriptionId --query nameAvailable --output tsv
if ($Available -ne "true") { throw "Choose a different image lab suffix before creating resources." }
```

### 4.2. Create registry and publish the same image through one path

Create only ACR Basic with admin disabled/RBAC and read actual login server/resource ID. Choose A: official ACR Tasks cloud build if builder package/image supply and costs are approved, or B: publish an approved WSL Docker image. Do not execute both automatically or extend a local feed exception to cloud builder. B validates linux/amd64, obtains token safely, passes it by stdin, tags/pushes and removes only the isolated Docker auth config on success/failure. Preserve the person's existing Docker config. --expose-token yields an ACR refresh credential used by Docker, not a generic registry REST bearer token. After the chosen path succeeds, resolve SHA-256 digest and deliver digest/server/ID, not credentials. VM/AKS stop here.

```powershell
az group create --name $ImageGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-image LabId=$ImageLabId --output table
az acr create --name $RegistryName --resource-group $ImageGroupName --location $Location --sku Basic --admin-enabled false --role-assignment-mode rbac --subscription $SubscriptionId --output table
$RegistryServer = az acr show --name $RegistryName --subscription $SubscriptionId --query loginServer --output tsv
$RegistryId = az acr show --name $RegistryName --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($RegistryServer) -or [string]::IsNullOrWhiteSpace($RegistryId)) {
    throw "Registry information was not returned."
}
```

```powershell
az acr build --registry $RegistryName --image workshop/app:0.1.0 --platform linux/amd64 --subscription $SubscriptionId .\sample-app
```

```powershell
$LocalImage = "<approved-local-image-tag>"
$WslDistribution = "<approved-wsl-distribution>"
if ($LocalImage -like "<*" -or [string]::IsNullOrWhiteSpace($LocalImage) -or
    $WslDistribution -like "<*" -or [string]::IsNullOrWhiteSpace($WslDistribution)) {
    throw "Set the verified local image and WSL distribution."
}
$Platform = wsl -d $WslDistribution --exec docker image inspect $LocalImage --format "{{.Os}} {{.Architecture}}"
if ($Platform -ne "linux amd64") { throw "The verified image must be linux/amd64." }
$AuthDirectory = "/tmp/amw-acr-auth-$ImageLabId"
wsl -d $WslDistribution --exec mkdir --mode=700 $AuthDirectory
$Auth = $null
$LoggedIn = $false
try {
    $Auth = az acr login --name $RegistryName --subscription $SubscriptionId --expose-token --output json | ConvertFrom-Json
    if (-not $Auth.accessToken -or $Auth.loginServer -ne $RegistryServer) {
        throw "ACR credential or registry hostname did not match."
    }
    $Auth.accessToken | wsl -d $WslDistribution --exec docker --config $AuthDirectory login $RegistryServer --username 00000000-0000-0000-0000-000000000000 --password-stdin
    $LoggedIn = $true
    wsl -d $WslDistribution --exec docker tag $LocalImage "$RegistryServer/workshop/app:0.1.0"
    wsl -d $WslDistribution --exec docker --config $AuthDirectory push "$RegistryServer/workshop/app:0.1.0"
} finally {
    $Auth = $null
    try {
        if ($LoggedIn) {
            wsl -d $WslDistribution --exec docker --config $AuthDirectory logout $RegistryServer
        }
    } finally {
        wsl -d $WslDistribution --exec rm -f "$AuthDirectory/config.json"
        wsl -d $WslDistribution --exec rmdir $AuthDirectory
    }
}
```

```powershell
$Digest = az acr repository show --name $RegistryName --image workshop/app:0.1.0 --subscription $SubscriptionId --query digest --output tsv
if ([string]::IsNullOrWhiteSpace($RegistryServer) -or [string]::IsNullOrWhiteSpace($RegistryId) -or
    $Digest -notmatch "^sha256:[a-f0-9]{64}$") {
    throw "Registry information or image digest was not returned."
}
$ContainerImage = "$RegistryServer/workshop/app@$Digest"
[pscustomobject]@{ Image = $ContainerImage; RegistryServer = $RegistryServer; RegistryId = $RegistryId } | Format-List
```

### 4.3. Optional: Container Apps/Terraform pull identity

Create a user-assigned identity only for consumers that need it. An authorized administrator verifies principal/registry scope and grants AcrPull, then inspects authentication-as-arm enabled. Do not change registry policy or use admin passwords as an automatic workaround. Allow propagation and supply only confirmed identity/image inputs to the chosen consumer.

```powershell
$Identity = az identity create --name $IdentityName --resource-group $ImageGroupName --location $Location --subscription $SubscriptionId --output json | ConvertFrom-Json
$PullIdentityId = $Identity.id
$PullPrincipalId = $Identity.principalId
if (-not $PullIdentityId -or -not $PullPrincipalId) { throw "Identity IDs were not returned." }
[pscustomobject]@{ Principal = $PullPrincipalId; RegistryScope = $RegistryId } | Format-List
```

```powershell
az role assignment create --assignee-object-id $PullPrincipalId --assignee-principal-type ServicePrincipal --role AcrPull --scope $RegistryId --subscription $SubscriptionId --output table
az acr config authentication-as-arm show --registry $RegistryName --subscription $SubscriptionId
```

## 5. Verification and common failures

Require an immutable workshop/app@sha256 digest rather than tag-only equivalence. Build/push is not runtime/pull/app verification. Record group/LabId and active consumers privately. For failures inspect build/download rights/quota/sources, name availability, registry role mode and propagation; manually retry only the diagnosed approved step.

## 6. Cleanup and ownership

The publisher owns only the newly created image group/registry/optional UAI. Each consumer deletes its own VM/cluster/app/target and exact registry grants first. After the last consumer ends, list publisher group/tags/resources and approve deletion; verify absence and cost update delay. External preexisting image/identity inputs are never publisher deletion targets. Do not revoke inherited/unrelated roles.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ImageGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ImageGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ImageGroupName -ne "rg-amw-image-$ImageLabId" -or
    $Group.tags.Workshop -ne "azure-migration-image" -or $Group.tags.LabId -ne $ImageLabId) {
    throw "The group is not this image preparation lab."
}
az group delete --name $ImageGroupName --subscription $SubscriptionId
$ExistsAfter = az group exists --name $ImageGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfter -ne "false") { throw "Image preparation group deletion is not verified." }
```

## 7. Additional considerations for a real migration

Review supply-chain approvals/signing/vulnerabilities/licenses/rebuild policy, RBAC versus ABAC and private registry network support, image platform/digest/base-image updates. An identical image does not guarantee equivalent cloud operation.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Managed identity image pull](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull)
