# Object migration — Storage Mover introduction and AzCopy lab

English | [한국어](./README-ko.md)

Learn Storage Mover's managed-service role, then use official AzCopy for the small synthetic Blob-to-Blob exercise. The tools have different identities, network requirements and result formats. Real S3 migration requires a separately authorized source and migration plan.

> **Management geography:** Mover management-resource availability is a separate input from the source/target storage regions. For adoption beyond this introduction, consult current official availability and administrator approval; do not reuse a Blob region without checking.

## 1. Learning objectives and module boundaries

For S3 users, allow about 20 minutes of service/tool concepts, 30 minutes of approved AzCopy input preparation, 30–45 minutes for the utility and wait, and 20 minutes of verification/cleanup. Choose introduction-only reading or the approved private Blob-to-Blob AzCopy lab. No app, compute course, IaC or DB is required. The actual source is three tiny flat files; 100 objects/10 MiB in the planning case is fictional.

**Workshop delivery boundary:** Storage Mover is **service introduction only**: what it manages, suitable source/workload scenarios, region/cost/permission/network considerations and official documentation. This workshop does not create its endpoints/projects/job definitions, grant its execution roles or start/verify its copy engine. The hands-on object path is the separate official **private AzCopy** exercise with three synthetic objects/109 bytes. This delivery choice is not a claim that Storage Mover is universally unsupported. Future customer execution requires their own supported official scenario and administrator approval.

- [Blob basics](../../onboarding/storage/README.md)
- [Private client inputs](../../../shared/storage-private-access/README.md)
- [Synthetic workload case](../planning/lab/workloads.csv)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

### 2.1. Introduce Storage Mover alongside AzCopy in the Portal

In a browser search Services for Storage movers and open the current Get started experience, which may appear under Storage center. Read when-to-use and source-specific migration paths. Mover manages endpoints/projects/jobs/progress/errors; AzCopy performs an explicitly scoped utility transfer. Review the official Blob-to-Blob procedure even if an introductory UI lists only S3/SMB/NFS. Optionally open Create Storage Mover to inspect Basics, Monitoring, Tags and Review fields without submitting. The management region/name is not the source/target location. Check copy-log/workspace collection and retention costs; do not enable them automatically or reuse a preselected operational group. Screenshots illustrate selection, not job/data success.

![Portal storage mover introduction](./images/portal-storage-mover-introduction.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

![Portal storage mover instance options](./images/portal-storage-mover-instance-options.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

![Portal storage mover monitoring](./images/portal-storage-mover-monitoring.png)

*Portal illustration: observe the selected service and fields. Visible defaults are not approved deployment inputs; confirm the current interface and your own scope.*

**Resources for this step**

- [Azure to azure migration](https://learn.microsoft.com/en-us/azure/storage-mover/azure-to-azure-migration)
- [Service overview](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview)
- [Storage use azcopy v10](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10)
- [Storage use azcopy blobs copy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-blobs-copy)
- [Storage blobs introduction](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction)
- [Storage account overview](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview)
- [What is entra](https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Private dns overview](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-arc/overview)

## 3. Prerequisites, permissions and cost

Service reading needs only a browser; it does not require Mover registration, deployment or roles. The AzCopy lab needs approved owned source/target accounts, an empty target container, official AzCopy v10 and a reachable private PowerShell or VM/MI client. Confirm exact tenant/account ownership, DNS/routes, source Storage Blob Data Reader and target Storage Blob Data Contributor. If source seeding temporarily needs Contributor, track/revoke only the new preparation grant afterward.

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.

Previously configured resource-instance or trusted-service exceptions may remain effective even with public network Disabled; read the [Storage network limitations](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-limitations). [Resource-instance rules](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-resource-instances) govern **public endpoint network access**, do not grant data permissions and are **not Private Endpoints**. The provided samples use bypass None and empty resourceAccessRules. Adding such exceptions is neither approved here nor a private-compliant workaround.

Review storage/request/transfer and optional inspection-fixture costs. Never broaden permissions, disable TLS, expose secrets or add unrelated compute. Future Mover adoption separately requires current source-specific support, management geography/metadata residency, native identity roles and connectivity review with its administrator; this is not workshop execution preparation.

- [Private input preparation](../../../shared/storage-private-access/README.md)
- [Pricing calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

### 3.1. Separate management-region and storage-region inputs

Read the official [Storage Mover creation guidance](https://learn.microsoft.com/en-us/azure/storage-mover/storage-mover-create). The Portal's Instance details note explains that the Mover resource need not be co-located with the storage accounts. This does not remove the need to verify current resource availability or the selected copy topology.

| Input or boundary | Approved example / required decision |
|---|---|
| Mover management-resource region | West US 3 (`westus3`), illustrative location; verify current availability for future adoption |
| Source storage-account region | Korea Central (`koreacentral`), unchanged |
| Target storage-account region | Korea Central (`koreacentral`), unchanged |
| Copy engine and data path | Review the selected engine and source/target topology to identify the transfer path, and record it separately from the management location |
| Management metadata residency | Review the location and treatment of endpoint/project/job configuration and any enabled logs under organizational requirements before approval |

Management locations can differ from storage availability. Confirm the current storageMovers location list and any required registration for the chosen subscription before a separately approved deployment. Introduction-only reading needs no registration. The pictured West US 3 management location is an example, not a required workshop region or evidence about Korea Central migration support.

The Blob sample accounts and private endpoint/DNS configuration are separate from the illustrated management location. Record both region inputs explicitly, then review the selected copy-data path and private-network requirements. Any relocation of storage, databases or compute needs its own approval.

![Storage Mover Essentials showing management location West US 3](./images/portal-management-region.png)

*This tightly cropped Essentials view shows the actual Mover **management-resource location** only. It is a management-location illustration, not a copy result. Source/target Korea Central regions and private settings are not visible here; those require independent resource checks. The image does not verify endpoints, roles, a job, copy-data path or private-copy support.*

Review copy-data routing and private topology support separately from the management location. Future execution follows the source-specific official scenario and separate customer approvals; this workshop stops at service introduction.

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. A: read the real S3 prerequisites and limits

Compare Storage Mover cloud-to-cloud with AzCopy S3 documentation. Real S3 requires authorized AWS account/bucket/object access and authentication; Mover also follows current Arc connector preparation for that source. This workshop does not create AWS resources, connectors or keys or issue S3 copy requests. Glacier/Deep Archive may require source restoration with cost; automatic rehydration is not guaranteed. Review metadata/tags/versions/archive/path/delta/egress, and never treat S3 ETag as always MD5. Reading may finish here.

**Resources for this step**

- [Cloud to cloud migration](https://learn.microsoft.com/en-us/azure/storage-mover/cloud-to-cloud-migration)
- [Storage use azcopy s3](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-s3)

### 4.2. Prepare only the AzCopy synthetic source and target

After approval use rg-amw-objects-<lab-id>, two available distinct account names and private source/target containers. Confirm actual network/auth settings and private data-client reachability, not merely Portal account management. Upload exactly notes.txt, catalog.csv and info.json at source root from lab/data; leave target empty. Set text/plain, text/csv and application/json respectively, and lowercase metadata workshop=amw-objects. Metadata differs from index tags. Freeze source through verification; ETag/last-modified are not content hashes and need not match.

Reuse approved owned source/target inputs only when their owner and empty-target conditions match. Preserve any earlier results; do not clear or overwrite another destination.

**Resources for this step**

- [Storage private access](../../../shared/storage-private-access/README.md)
- [Data](./lab/data)
- [Notes.txt](./lab/data/notes.txt)
- [Catalog.csv](./lab/data/catalog.csv)
- [Info.json](./lab/data/info.json)

### 4.3. Understand Storage Mover without executing it

Read the official [service overview](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview), [Azure-to-Azure scenario](https://learn.microsoft.com/en-us/azure/storage-mover/azure-to-azure-migration) and source-specific documentation linked above. Explain why managed endpoint/job orchestration can suit larger migration workflows, while AzCopy fits this explicitly bounded small exercise. Identify future source/target, mode, metadata, identity, cost and network questions for a customer's administrator. Do not create native resources, permissions or copy jobs as part of this lesson.

### 4.4. Perform one official AzCopy transfer

Run only on the approved private PowerShell user client, or choose the VM/MI branch instead. Verify canonical hostnames resolve privately and the tenant/two different accounts match. Display flat root source/target, recursive false and overwrite false before approval. The transfer is official server-to-server BlobBlob with property preservation, not a custom client-side copy engine. Observe job ID/status/count/failed/skipped/logs. Do not use sync/delete/overwrite or expose tokens/SAS in logs.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$TenantId = "<approved-tenant-id>"
$SourceAccount = "<this-lab-source-account>"
$TargetAccount = "<this-lab-target-account>"
$ParsedTenantId = [guid]::Empty
if (-not [guid]::TryParse($TenantId, [ref]$ParsedTenantId) -or
    $SourceAccount -notmatch "^[a-z0-9]{3,24}$" -or $TargetAccount -notmatch "^[a-z0-9]{3,24}$" -or
    $SourceAccount -eq $TargetAccount) {
    throw "Set the approved tenant and two different lab accounts."
}
$SourceUrl = "https://$SourceAccount.blob.core.windows.net/source"
$TargetUrl = "https://$TargetAccount.blob.core.windows.net/target"
[pscustomobject]@{ Source = "$SourceUrl/*"; Target = $TargetUrl; Overwrite = $false; Recursive = $false } | Format-List
azcopy login --tenant-id $TenantId
```

```powershell
azcopy copy "$SourceUrl/*" $TargetUrl --from-to=BlobBlob --recursive=false --overwrite=false --s2s-preserve-properties=true
```

### 4.5. Verify names, byte lengths, content and selected properties

With source unchanged, inspect unfiltered root lists on both sides: exactly catalog.csv, info.json and notes.txt with case-sensitive names and no extras. Compare real byte lengths, content types and workshop metadata. Download each source/target Blob to distinct private folders and compare SHA-256 with the original checkout bytes. Use the local PowerShell comparison only after all six downloads complete; it verifies content but does not itself discover hidden target Blobs or verify properties. Total sample bytes are 109 for the intended checkout; compute actual source lengths rather than using rounded KiB. Require official AzCopy transfer evidence plus complete list/bytes/hash/type/metadata evidence.


```powershell
$ErrorActionPreference = "Stop"
$LabId = "<this-lab-id>"
if ($LabId -notmatch "^[a-z0-9]{8}$") { throw "Use the eight-character lab ID." }
$DataPath = Join-Path $PWD "modules\migration\objects\lab\data"
$DownloadRoot = Join-Path (Join-Path $PWD "lab-output") "objects-$LabId"
$SourceDownload = Join-Path $DownloadRoot "source"
$TargetDownload = Join-Path $DownloadRoot "target"
New-Item -ItemType Directory -Path $SourceDownload -ErrorAction Stop | Out-Null
New-Item -ItemType Directory -Path $TargetDownload -ErrorAction Stop | Out-Null
```

```powershell
$ExpectedNames = @("catalog.csv", "info.json", "notes.txt")
$SourceFiles = @(Get-ChildItem -LiteralPath $SourceDownload -File)
$TargetFiles = @(Get-ChildItem -LiteralPath $TargetDownload -File)
if ($SourceFiles.Count -ne 3 -or $TargetFiles.Count -ne 3 -or
    (Compare-Object -ReferenceObject ($ExpectedNames | Sort-Object) -DifferenceObject ($SourceFiles.Name | Sort-Object) -CaseSensitive) -or
    (Compare-Object -ReferenceObject ($ExpectedNames | Sort-Object) -DifferenceObject ($TargetFiles.Name | Sort-Object) -CaseSensitive)) {
    throw "Expected exactly the three flat sample names in both downloads."
}
$TotalBytes = 0L
foreach ($Name in $ExpectedNames) {
    $OriginalFile = Join-Path $DataPath $Name
    $SourceFile = Join-Path $SourceDownload $Name
    $TargetFile = Join-Path $TargetDownload $Name
    $OriginalLength = (Get-Item -LiteralPath $OriginalFile).Length
    if ((Get-Item -LiteralPath $SourceFile).Length -ne $OriginalLength -or
        (Get-Item -LiteralPath $TargetFile).Length -ne $OriginalLength) {
        throw "Byte length mismatch: $Name"
    }
    $OriginalHash = (Get-FileHash -LiteralPath $OriginalFile -Algorithm SHA256).Hash
    if ((Get-FileHash -LiteralPath $SourceFile -Algorithm SHA256).Hash -ne $OriginalHash -or
        (Get-FileHash -LiteralPath $TargetFile -Algorithm SHA256).Hash -ne $OriginalHash) {
        throw "Content mismatch: $Name"
    }
    $TotalBytes += $OriginalLength
}
[pscustomobject]@{ Files = 3; TotalBytes = $TotalBytes; ContentMatch = $true } | Format-List
```

### 4.6. Connect the result to cutover and rollback planning

Copy preserves the source and does not switch an application/consumer URL. Use the planning/cutover modules for source write freeze, final delta, target read-back, owner approval and retention. A synthetic Blob URL switch is not real S3 traffic cutover. Returning a URL after new target business writes does not reconcile those writes or constitute data rollback.

**Resources for this step**

- [Cutover](../cutover/README.md)
- [Planning](../planning/README.md)

### 4.7. Alternative: private Linux diagnostic VM with Managed Identity

The shared private-access inputs provide approved account/endpoint/DNS/client roles. prepare-private.sh uses VM Bash/MI, validates private canonical hostnames, seeds only the three source files with properties and checks an empty target. Record/revoke only the temporary new source-preparation Contributor grant, keeping source Reader/target Contributor. verify-private.sh uses official AzCopy with flat root/no-overwrite/property preservation, stores private native job JSON/log/plan, and independently checks source/target content. Management PowerShell sends these scripts from the repository root with explicit name=value parameters; base64 contains only synthetic source bytes, never credentials/customer data. Require the PREPARE/VERIFY PASS markers and reject FAIL even when outer Run Command succeeds. phase=verify-existing-job is a read-only job/data recheck, not another transfer. AzCopy summaries may have JobStatus and numeric-string metrics; unsupported shapes must fail, not silently pass.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
if (-not $SourceAccount -or -not $TargetAccount -or $SourceAccount -eq $TargetAccount -or
    -not $SourcePrivateIp -or -not $TargetPrivateIp -or -not $GuestWorkDirectory -or
    -not $InspectionVmName -or -not $InspectionGroupName -or -not $SubscriptionId) {
    throw "Set the approved private source/target/fixture inputs."
}
$DataPath = Join-Path $PWD "modules\migration\objects\lab\data"
$Catalog = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $DataPath "catalog.csv")))
$Info = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $DataPath "info.json")))
$Notes = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $DataPath "notes.txt")))
$PreparePath = Join-Path $PWD "modules\migration\objects\verify\prepare-private.sh"
$Prepared = az vm run-command invoke --name $InspectionVmName --resource-group $InspectionGroupName --command-id RunShellScript --scripts "@$PreparePath" --parameters "source=$SourceAccount" "sourceIP=$SourcePrivateIp" "target=$TargetAccount" "targetIP=$TargetPrivateIp" "workdir=$GuestWorkDirectory" "catalog=$Catalog" "info=$Info" "notes=$Notes" --subscription $SubscriptionId --output json | ConvertFrom-Json
$Messages = @($Prepared.value | ForEach-Object { $_.message }) -join "`n"
$Messages
if ($Messages -notmatch "(?m)^AMW_OBJECT_PREPARE_PASS\s*$" -or $Messages -match "AMW_OBJECT_PREPARE_FAIL") {
    throw "Guest source preparation failed or has no success evidence."
}
```

```powershell
$VerifyPath = Join-Path $PWD "modules\migration\objects\verify\verify-private.sh"
$Verified = az vm run-command invoke --name $InspectionVmName --resource-group $InspectionGroupName --command-id RunShellScript --scripts "@$VerifyPath" --parameters "source=$SourceAccount" "target=$TargetAccount" "workdir=$GuestWorkDirectory" --subscription $SubscriptionId --output json | ConvertFrom-Json
$Messages = @($Verified.value | ForEach-Object { $_.message }) -join "`n"
$Messages
if ($Messages -notmatch "(?m)^AMW_OBJECT_VERIFY_PASS\s*$" -or $Messages -match "AMW_OBJECT_VERIFY_FAIL") {
    throw "Guest official copy/data verification failed or has no success evidence."
}
```

**Resources for this step**

- [Storage private access](../../../shared/storage-private-access/README.md)
- [Prepare the private synthetic source](./verify/prepare-private.sh)
- [Private data verification](./verify/verify-private.sh)

**Optional completion:** after copy and complete file comparisons, read target `notes.txt` through a fresh request from the same private client. Record the account/container, new local path, SHA-256 and Content-Type criteria from [target client completion](../cutover/README.md#45a-use-the-migrated-result-through-a-fresh-client). Retain source/shared inputs and do not add an app or compute track. In the [real-source preparation task](../planning/README.md#48-prepare-to-replace-the-synthetic-source-with-a-real-source), identify S3 access, object properties, changes and switch prerequisites without connecting to AWS.

## 5. Verification and common failures

Require the actual AzCopy job to finish with three completed transfers, zero failed/skipped and the expected source byte total, plus unfiltered names, download hashes and required content type/user metadata. A successful utility process alone is not content verification. On 403 inspect actual tenant/identity/data scopes, propagation, approved DNS/routes and account configuration using the [Blob 403 guide](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/blobs/authentication/storage-troubleshoot-403-errors). Preserve errors, stop on mismatches and obtain approval for corrections; do not relax network/key/TLS controls. S3 ETag, versions, index tags and access tier require their own chosen criteria.

Private AzCopy evidence is not Mover service-run or real S3/AWS migration evidence. Storage Mover copy-engine execution is not offered by this workshop; future support decisions require the customer's official source-specific path rather than extrapolation from this lab.

## 6. Cleanup and ownership

Service-introduction reading creates no Mover assets or cleanup obligations. For the AzCopy lab confirm the selected transfer ended, retain safe evidence and close its login session. Inventory exact owned accounts/containers/new preparation grants and optional fixture inputs before deletion approval. Consumers preserve externally supplied accounts, previous results, shared private clients and other roles. The original owners handle resource/fixture cleanup after their last consumer. Remove only the exact six downloaded files and empty local directories shown below, not all lab-output. Verify remaining resources/grants and delayed cost.

```powershell
$SourceDownload
$TargetDownload
foreach ($Name in @("catalog.csv", "info.json", "notes.txt")) {
    Remove-Item -LiteralPath (Join-Path $SourceDownload $Name)
    Remove-Item -LiteralPath (Join-Path $TargetDownload $Name)
}
Remove-Item -LiteralPath $SourceDownload
Remove-Item -LiteralPath $TargetDownload
Remove-Item -LiteralPath $DownloadRoot
```

## 7. Additional considerations for a real migration

Review S3 classes, versions, ACL/retention, names/case, metadata versus tags, multipart/encrypted ETags and Blob semantics. Plan change rate/delta/final freeze, consistency, backup, cutover/rollback, identity/connectors/private topology, bandwidth/egress/restore and scale/service limits. Three matching synthetic files do not certify a production migration.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Azure to azure migration](https://learn.microsoft.com/en-us/azure/storage-mover/azure-to-azure-migration)
- [Cloud to cloud migration](https://learn.microsoft.com/en-us/azure/storage-mover/cloud-to-cloud-migration)
- [Storage use azcopy blobs copy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-blobs-copy)
- [Storage use azcopy s3](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-s3)
