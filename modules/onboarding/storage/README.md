# Storage — upload and read back one Blob

English | [한국어](./README-ko.md)

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.


Use Entra authentication on an approved private Blob path and verify a tiny synthetic file. This teaches Blob access, not S3 migration; choose the object-migration module for Storage Mover/AzCopy.

## 1. Learning objectives and module boundaries

For engineers familiar with S3; allow about 45 minutes plus role propagation. Inputs are an approved private client/DNS/endpoint, data identity, Azure account-management rights and one synthetic file. Expect exactly one hello.txt Blob, 20 bytes and an identical downloaded SHA-256. Other compute modules, the shared app, Terraform, DB and AWS are unnecessary. Choose private user PowerShell or diagnostic-VM Managed Identity, not both.

**Resources for this step**

- [Storage private access](../../../shared/storage-private-access/README.md)
- [Objects](../../migration/objects/README.md)

### When to choose this module

Choose Blob basics and authenticated private data access. Skip unrelated apps, compute, DB and IaC. The result is one verified Azure Blob; S3 credentials, actual object migration, incremental sync and operational cutover belong to other scopes.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Storage blobs introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction)
- [Storage account overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)
- [What is entra](https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)
- [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Private dns overview](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)

## 3. Prerequisites, permissions and cost

Management commands use local PowerShell 7.4+ and Azure CLI. Data commands require a genuinely private PowerShell location or the separate VM Bash/MI path. Account creation rights, roleAssignments/write and Blob data access are distinct. A qualified administrator grants Storage Blob Data Contributor at the new lab account scope; this scope is a teaching simplification for container creation. Standard LRS incurs storage/request/transfer costs and is not a production HA recommendation. The Blob default is public network Disabled, firewall default Deny and bypass None, HTTPS/TLS, anonymous Blob access disabled and Shared Key disabled. Entra/RBAC does not replace network isolation. Use an approved private client, Approved Blob Private Endpoints, canonical hostname DNS and routes to the selected accounts; never reopen public access to resolve a failure. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Storage private access](../../../shared/storage-private-access/README.md)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Display the approved target and generated names

Run management PowerShell, replace subscription/region placeholders and confirm tenant/Enabled state. Account names must be globally available lowercase alphanumeric strings; a random suffix does not guarantee availability. Review the new group, account, region and expected costs before approval.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az login
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$ParsedSubscriptionId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedSubscriptionId)) {
    throw "Replace SubscriptionId with the approved sandbox subscription ID."
}
if ($Location -like "<*" -or [string]::IsNullOrWhiteSpace($Location)) {
    throw "Replace Location with the approved Azure region name."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ResourceGroupName = "rg-amw-storage-$LabId"
$StorageAccountName = "stamw$LabId"
$ContainerName = "sample"
$BlobName = "hello.txt"
[pscustomobject]@{
    Subscription = $SubscriptionId
    Region = $Location
    ResourceGroup = $ResourceGroupName
    StorageAccount = $StorageAccountName
} | Format-List
```

### 4.2. Create the dedicated group and storage account

Reject existing groups and unavailable account names. After creation, inspect the actual provisioning, LRS, HTTPS/TLS and network/authentication settings rather than only the request response. Before data operations, obtain the approved blob Private Endpoint, DNS and client described in shared private-access preparation. If account creation fails after the group is created, the group can still require cleanup.

```powershell
$GroupExists = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($GroupExists -ne "false") {
    throw "The group already exists or the existence check was inconclusive. Do not reuse it."
}
$NameAvailable = az storage account check-name --name $StorageAccountName --subscription $SubscriptionId --query nameAvailable --output tsv
if ($NameAvailable -ne "true") {
    throw "The storage account name is unavailable. Choose a new lab suffix before creating resources."
}
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-storage LabId=$LabId --output table
az storage account create --name $StorageAccountName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --sku Standard_LRS --kind StorageV2 --https-only true --min-tls-version TLS1_2 --allow-blob-public-access false --allow-shared-key-access false --public-network-access Disabled --default-action Deny --bypass None --tags Workshop=azure-migration-storage LabId=$LabId --output table
$Account = az storage account show --name $StorageAccountName --resource-group $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
if ($Account.provisioningState -ne "Succeeded" -or $Account.sku.name -ne "Standard_LRS" -or
    $Account.minimumTlsVersion -ne "TLS1_2" -or $Account.enableHttpsTrafficOnly -ne $true -or
    $Account.publicNetworkAccess -ne "Disabled" -or
    $Account.networkRuleSet.defaultAction -ne "Deny" -or $Account.networkRuleSet.bypass -ne "None" -or
    $Account.allowSharedKeyAccess -ne $false -or $Account.allowBlobPublicAccess -ne $false) {
    throw "The actual storage network/authentication configuration differs from this lab."
}
$Account | Select-Object name, provisioningState, publicNetworkAccess, networkRuleSet | Format-List
```

**Resources for this step**

- [Storage private access](../../../shared/storage-private-access/README.md)

### 4.3. Prepare the data role separately

For the user path, resolve the participant object ID and exact lab account scope. Only an authorized administrator creates the assignment; if using another terminal, explicitly set the verified IDs and subscription. Protect identity output. If Graph lookup is unavailable, have the administrator verify the user ID rather than continuing with an empty value. Allow role propagation time; do not use Owner or account keys as a shortcut. The VM path uses the fixture identity's data role instead.

```powershell
$PrincipalId = az ad signed-in-user show --query id --output tsv
if ([string]::IsNullOrWhiteSpace($PrincipalId)) {
    throw "The signed-in user object ID could not be determined."
}
$StorageAccountId = az storage account show --name $StorageAccountName --resource-group $ResourceGroupName --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($StorageAccountId)) {
    throw "The storage account scope could not be determined."
}
[pscustomobject]@{ PrincipalId = $PrincipalId; Scope = $StorageAccountId } | Format-List
```

```powershell
az role assignment create --assignee-object-id $PrincipalId --assignee-principal-type User --role "Storage Blob Data Contributor" --scope $StorageAccountId --subscription $SubscriptionId --query "{principal:principalId,scope:scope,role:roleDefinitionId}" --output json
```

**Resources for this step**

- [Authorize data operations cli](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-data-operations-cli)

### 4.4. Create the container and upload synthetic content

Run on the confirmed private PowerShell client, where the canonical Blob hostname resolves to the approved private IP. --auth-mode login uses that client's Entra user; it does not create connectivity. Expect created: true for a fresh sample container. The UTF-8 file has no BOM/newline and is 20 bytes. --overwrite false protects existing content: stop if a container or Blob unexpectedly exists.

```powershell
az storage container create --account-name $StorageAccountName --name $ContainerName --auth-mode login --subscription $SubscriptionId --output json
$LabDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "azure-migration-storage-$LabId"
New-Item -ItemType Directory -Path $LabDirectory -ErrorAction Stop | Out-Null
$SourceFile = Join-Path $LabDirectory "hello.txt"
$DownloadedFile = Join-Path $LabDirectory "downloaded-hello.txt"
Set-Content -LiteralPath $SourceFile -Value "Hello Azure workshop" -Encoding utf8NoBOM -NoNewline
az storage blob upload --account-name $StorageAccountName --container-name $ContainerName --name $BlobName --file $SourceFile --type block --content-type text/plain --overwrite false --auth-mode login --subscription $SubscriptionId --output json
```

### 4.5. Compare count, byte length and downloaded content

List without filters and require exactly hello.txt. Compare actual content length with the original, download without overwrite, and compare SHA-256 hashes. Expected summary: Count 1, Bytes 20, ContentMatch True. An HTTP/CLI success without this content evidence is incomplete.

```powershell
$Blobs = @(az storage blob list --account-name $StorageAccountName --container-name $ContainerName --auth-mode login --subscription $SubscriptionId --query "[].{name:name,bytes:properties.contentLength}" --output json | ConvertFrom-Json)
$Blobs | Format-Table
if ($Blobs.Count -ne 1 -or $Blobs[0].name -ne $BlobName) {
    throw "Expected exactly one blob named hello.txt."
}
$SourceBytes = (Get-Item -LiteralPath $SourceFile).Length
if ($Blobs[0].bytes -ne $SourceBytes) {
    throw "Blob size differs from the source file."
}
az storage blob download --account-name $StorageAccountName --container-name $ContainerName --name $BlobName --file $DownloadedFile --overwrite false --auth-mode login --subscription $SubscriptionId --output json
$SourceHash = (Get-FileHash -LiteralPath $SourceFile -Algorithm SHA256).Hash
$DownloadedHash = (Get-FileHash -LiteralPath $DownloadedFile -Algorithm SHA256).Hash
if ($SourceHash -ne $DownloadedHash) {
    throw "Downloaded content differs from the source file."
}
[pscustomobject]@{
    Count = $Blobs.Count
    Bytes = $SourceBytes
    ContentMatch = ($SourceHash -eq $DownloadedHash)
} | Format-List
```

### 4.6. Alternative: diagnostic VM Managed Identity

Use this path only when the instructor provides approved fixture VM, network, account, endpoint IP, guest directory and MI data role. Run management PowerShell from the repository root to send the linked script; it executes VM Bash and az login --identity. Do not copy a person's login cache or secrets to the VM. Require AMW_STORAGE_VERIFY_PASS and reject AMW_STORAGE_VERIFY_FAIL even if the outer API call succeeded. A fresh run requires a fresh sample container; phase=verify-existing-blob is a read-only recheck of preserved content, not a new upload.

```powershell
if (-not $StorageAccountName -or -not $ExpectedPrivateIp -or -not $InspectionVmName -or
    -not $InspectionGroupName -or -not $GuestWorkDirectory) {
    throw "Set the approved private fixture inputs."
}
$ScriptPath = Join-Path $PWD "modules\onboarding\storage\verify\verify-private.sh"
$Result = az vm run-command invoke --name $InspectionVmName --resource-group $InspectionGroupName --command-id RunShellScript --scripts "@$ScriptPath" --parameters "account=$StorageAccountName" "privateIP=$ExpectedPrivateIp" "workdir=$GuestWorkDirectory" --subscription $SubscriptionId --output json | ConvertFrom-Json
$Messages = @($Result.value | ForEach-Object { $_.message }) -join "`n"
$Messages
if ($Messages -notmatch "(?m)^AMW_STORAGE_VERIFY_PASS\s*$" -or $Messages -match "AMW_STORAGE_VERIFY_FAIL") {
    throw "Guest Blob validation failed or has no success evidence."
}
```

**Resources for this step**

- [Storage private access](../../../shared/storage-private-access/README.md)
- [Private data verification](./verify/verify-private.sh)

## 5. Verification and common failures

Compare the actual user/MI, data-role scope and propagation on AuthorizationPermissionMismatch. Management AuthorizationFailed is a different permission problem. Check private DNS/routes and public-disabled settings on network failures; never enable Shared Key or relax policy. Reject unexpected preexisting content and byte/hash differences. Explain the separate responsibilities of RBAC, anonymous access, private DNS and public-network control.

## 6. Cleanup and ownership

Own only the dedicated group, account, synthetic file and lab-specific grants. Preserve external private network/client fixtures and other consumers' inputs. If the account is still being consumed, agree on the final cleanup owner and deadline. Follow the inventory and deletion steps below; verify remaining grants/resources and cost reporting after its update delay.

### 6.1. Inspect exact lab resources and ownership

Restore this lab's verified variables if using a new terminal. List the group, tags and full resource inventory and confirm no other purpose or active consumer. Tags alone do not prove ownership. Do not auto-discover production resources as cleanup targets.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
$Group | Select-Object name, location, tags | Format-List
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-storage-$LabId" -or $Group.tags.Workshop -ne "azure-migration-storage" -or $Group.tags.LabId -ne $LabId) {
    throw "The group does not match this storage lab. Do not delete it."
}
```

### 6.2. Delete the approved group and verify absence

Group deletion removes every resource and Blob in that group. Obtain approval after the inventory check and respond to the CLI confirmation; do not add --yes. Verify group exists returns false. Remove only the two generated local files and their empty directory if they exist. Account-scope lab assignments must be accounted for, but inherited roles are not cleanup targets. Group absence does not erase accrued charges or external resources.

```powershell
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$GroupExistsAfterCleanup = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($GroupExistsAfterCleanup -ne "false") {
    throw "The lab group still exists or deletion could not be verified."
}
Write-Output "The storage lab resource group no longer exists."
```

```powershell
$SourceFile
$DownloadedFile
Remove-Item -LiteralPath $SourceFile
Remove-Item -LiteralPath $DownloadedFile
Remove-Item -LiteralPath $LabDirectory
```

## 7. Additional considerations for a real migration

Review S3 permissions, bandwidth/egress, names, metadata, versions, retention and access policies. S3 ETag is not always MD5. Plan incremental change, final write freeze, cutover/rollback, backup and appropriate replication. Production completeness and performance need larger, workload-specific checks.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Storage quickstart blobs cli](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli)
- [Authorize data operations cli](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-data-operations-cli)
