# Container Apps — declare application execution instead of managing a server

English | [한국어](./README-ko.md)

Redeploy the shared HTTP container with an immutable image digest, Managed Identity pull and HTTPS ingress. This changes the operating model; it does not replicate an EC2 OS or disk.

## 1. Learning objectives and module boundaries

For EC2 + Docker/ECS users; allow 60–75 minutes plus optional image preparation. Required inputs: the approved image digest, registry hostname and user-assigned pull identity with AcrPull. Expect health/read/write observations and ownership-aware app-group cleanup. Skip VM, AKS, Functions, DB, Blob and Terraform. If inputs already exist, do not recreate them; otherwise use only the relevant shared image-preparation steps.

**Resources for this step**

- [Container image](../../../shared/container-image/README.md)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Overview](https://learn.microsoft.com/en-us/azure/container-apps/overview)
- [Container registry intro](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)

## 3. Prerequisites, permissions and cost

Use local PowerShell 7.4+ and Azure CLI from the root. Confirm Microsoft.App registration and Consumption capacity, app-group management and permission to attach the identity in its existing scope. The consumer does not create the registry, identity or new pull grants. Approve one replica's cost and the separate registry publisher's costs. Log streaming uses no new Log Analytics workspace. This is public HTTPS without application authentication: use synthetic payloads only and select another approved environment if public endpoints are prohibited. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Container image](../../../shared/container-image/README.md)
- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Confirm the target and shared inputs

Set verified values in this terminal rather than assuming another shell's variables persist. Inspect CLI versions and sign-in context, check the digest matches the registry and confirm identity pull/assign permissions. Core containerapp commands may be available without an extension. If extension show reports an absent optional extension, confirm core command availability; install only when the chosen command actually requires the extension.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az version
az extension show --name containerapp --query "{name:name,version:version}" --output table
az login
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$RegistryServer = "<approved-registry-login-server>"
$ContainerImage = "<approved-registry-login-server>/workshop/app@sha256:<digest>"
$PullIdentityId = "<approved-user-assigned-identity-resource-id>"
$ParsedId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedId) -or
    [string]::IsNullOrWhiteSpace($Location) -or $Location -like "<*" -or
    [string]::IsNullOrWhiteSpace($RegistryServer) -or $RegistryServer -like "<*" -or
    $ContainerImage -notmatch "^[a-z0-9.-]+/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$" -or
    [string]::IsNullOrWhiteSpace($PullIdentityId) -or $PullIdentityId -like "<*") {
    throw "Set the approved subscription, region, image, registry and pull identity."
}
if (-not $ContainerImage.StartsWith("$RegistryServer/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "The image does not belong to the selected registry."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ResourceGroupName = "rg-amw-aca-$LabId"
$EnvironmentName = "env-amw-$LabId"
$AppName = "app-amw-$LabId"
[pscustomobject]@{ Subscription = $SubscriptionId; Region = $Location; Group = $ResourceGroupName; Image = $ContainerImage } | Format-List
```

### 4.2. Create only this consumer's new app group

Reject any preexisting app group. After approval create the tagged dedicated group. The registry and identity stay in their owner's group; do not move or recreate them.

```powershell
$Exists = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Do not reuse an existing app group." }
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-container-apps LabId=$LabId --output table
```

### 4.3. Create the environment and application

Create the environment with logs-destination none and the app with the approved image/UAI. The returned HTTPS FQDN is the client endpoint; ingress forwards to container port 8080. One minimum/maximum replica and a single revision limit confusion from memory state, not an HA or persistence design. If CLI polling fails or a connection resets, inspect env show/containerapp show before any retry; a failed command and the later resource state are separate observations.

```powershell
az containerapp env create --name $EnvironmentName --resource-group $ResourceGroupName --location $Location --logs-destination none --enable-workload-profiles true --subscription $SubscriptionId --output table
az containerapp create --name $AppName --resource-group $ResourceGroupName --environment $EnvironmentName --image $ContainerImage --user-assigned $PullIdentityId --registry-identity $PullIdentityId --registry-server $RegistryServer --ingress external --target-port 8080 --transport auto --cpu 0.25 --memory 0.5Gi --min-replicas 1 --max-replicas 1 --revisions-mode single --subscription $SubscriptionId --output table
$Fqdn = az containerapp show --name $AppName --resource-group $ResourceGroupName --subscription $SubscriptionId --query properties.configuration.ingress.fqdn --output tsv
if ([string]::IsNullOrWhiteSpace($Fqdn)) { throw "No ingress hostname was returned." }
$BaseUrl = "https://$Fqdn"
$BaseUrl
```

### 4.4. Verify health, write/read-back and console logs

For a fresh single-process application, expect GET /health to return 200 with status ok, two initial items, POST /items to return 201, and the new item to appear on read-back. Invalid input returns 422 without changing the data. Restarting resets the in-memory dataset. A running resource or container is not enough: observe the actual HTTP responses and relevant logs. The linked cloud test is optional instructor tooling and requires an explicitly approved fresh endpoint/write. Do not rerun fresh-state tests against a mutated shared app or a customer URL. Inspect the printed Before/After/CreatedId summary and console request logs.

```powershell
$Health = Invoke-RestMethod "$BaseUrl/health"
if ($Health.status -ne "ok") { throw "Health response differs from the app contract." }
$Before = @(Invoke-RestMethod "$BaseUrl/items")
$Created = Invoke-RestMethod "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":"azure-workshop-item"}'
$After = @(Invoke-RestMethod "$BaseUrl/items")
if ($After.Count -ne $Before.Count + 1 -or -not ($After | Where-Object { $_.id -eq $Created.id -and $_.name -eq $Created.name })) {
    throw "The created item could not be read back."
}
[pscustomobject]@{ Health = $Health.status; Before = $Before.Count; After = $After.Count; CreatedId = $Created.id } | Format-List
az containerapp logs show --name $AppName --resource-group $ResourceGroupName --type console --tail 20 --subscription $SubscriptionId
```

In the Portal, open this app's **Revisions and replicas** and inspect the active revision, traffic allocation and replica count. The illustrated single-replica revision shows **Running at max**, **100% traffic** and **1 replica**: “at max” describes its configured replica limit, a scaling-limit observation; check metrics, resilience and HTTP behavior separately.

![Active Container Apps revision with its name masked](./images/portal-active-revision.png)

Open the selected revision's log stream, choose **Real-time** and **Application**, and verify that the selectors refer to your approved revision/replica/container. Correlate actual log lines with your HTTP requests: health/read success, creation, rejected input and an unknown route can produce 200, 201, 422 and 404 respectively. Do not share payloads or identifying log details.

![Revision log-stream controls, with the log body cropped](./images/portal-revision-log-stream.png)

*The stream image shows controls only; the body is cropped for privacy. Read HTTP status lines in the approved stream. **Stop** closes the stream view; it does not stop the app or end resource charges.*

**Resources for this step**

- [Test cloud.py](./verify/test_cloud.py)

## 5. Verification and common failures

On identity assignment errors, check rights at the input identity scope. On image-pull failures, check digest, registry RBAC/ABAC mode, ARM audience, the pull identity's AcrPull and propagation. For 502/503, inspect revision and system/console logs and target port. Treat data differences as failures; investigate restart/replica state rather than fabricating success.

## 6. Cleanup and ownership

List this group and confirm the exact lab name, Workshop tag and LabId before deletion approval. Delete only its environment/app and verify absence. Never delete input registry, identity or another consumer's resources. The image publisher cleans up after the last consumer, not when this app alone ends.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-aca-$LabId" -or $Group.tags.Workshop -ne "azure-migration-container-apps" -or $Group.tags.LabId -ne $LabId) {
    throw "The group does not match this app lab."
}
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$ExistsAfter = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfter -ne "false") { throw "App group deletion is not verified." }
```

**Resources for this step**

- [Container image](../../../shared/container-image/README.md#6-cleanup-and-ownership)

## 7. Additional considerations for a real migration

Review OS/runtime platform, external persistent data, revision consistency, authentication and network boundaries. Evaluate scale-to-zero, cold start, limits, durable logs, backup and operational cutover separately. ECS/Fargate and Container Apps responsibilities are comparable but not feature-identical.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Managed identity image pull](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull)
