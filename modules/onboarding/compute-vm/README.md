# VM + Docker — manage the server and run the same container

English | [한국어](./README-ko.md)

Choose this track when you want to compare OS, network, identity and Docker responsibilities with EC2. Docker is a way to execute the app on a VM, not a separate Azure compute service.

## 1. Learning objectives and module boundaries

Choose reading (20–30 minutes) or an approved VM lab (90–120 minutes plus provisioning/roles/packages). Inputs: the same image digest/registry, approved x64 VM image/size, permissions and either restricted SSH keys/client access or a private VM/Run Command path. Skip AKS, Container Apps, Functions, DB, Blob and Terraform deployment. VM uses its own system-assigned identity; no Container Apps pull identity is needed. This is a new-VM app redeployment, not EC2 OS/disk/data replication.

**Resources for this step**

- [Container image](../../../shared/container-image/README.md)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/overview)
- [Virtual networks overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Network security groups overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)
- [Public ip addresses](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Container registry intro](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro)
- [Overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)

## 3. Prerequisites, permissions and cost

Control commands run local PowerShell 7.4+/Azure CLI; guest commands run Ubuntu 24.04 x64 Bash, not local WSL. For SSH, approve the public egress /32, keys and host fingerprint; do not disable host-key checking or expose port 8080. The image is linux/amd64, so do not substitute Arm sizes. Approve Compute/Network/ManagedIdentity registration, Gen2 Trusted Launch support, quota, VM/disk/public-IP costs and registry-scope grants. Burstable B-family credits/throttling differ from fixed D-family capacity. Deallocation does not remove disk/IP/registry cost. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [B family](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/b-family)
- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Read execution requirements without deploying

Inspect the common app, Dockerfile and illustrative AWS Terraform. Distinguish the human VM administrator, VM Managed Identity and non-root container user. A non-root app does not make Docker daemon administration unprivileged. Reading needs no VM or registry access.

```text
EC2 example: Linux preparation → Docker → image → HTTP 8080
Azure lab: new Ubuntu VM → Docker → same digest image → VM localhost 8080
Client: approved SSH → tunnel → HTTP API on VM localhost
```

**Resources for this step**

- [Sample app](../../../sample-app/README.md)
- [Shared Dockerfile](../../../sample-app/Dockerfile)
- [Main.tf](../../migration/terraform/lab/aws/main.tf)

### 4.2. Local PowerShell: confirm VM, SSH and image inputs

Replace every placeholder and inspect tenant/Enabled state, approved public IPv4 /32, key files, registry/subscription and digest. Confirm image architecture, Gen2/Trusted Launch, SKU and cost. Keep private keys outside repository/prompts/build contexts. This block is for the SSH branch; private Run Command uses the separately approved inputs in step 4.9.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$VmSize = "<approved-small-x64-vm-size>"
$VmImageUrn = "<approved-ubuntu-24.04-x64-gen2-image-urn>"
$AdminCidr = "<approved-public-admin-ip>/32"
$SshPublicKeyFile = "<approved-public-key-file>"
$SshPrivateKeyFile = "<approved-private-key-file>"
$RegistryServer = "<approved-registry-login-server>"
$RegistryId = "<approved-registry-resource-id>"
$ContainerImage = "<approved-registry-login-server>/workshop/app@sha256:<digest>"
$ParsedId = [guid]::Empty
$ParsedAddress = [System.Net.IPAddress]::None
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedId) -or
    [string]::IsNullOrWhiteSpace($Location) -or $Location -like "<*" -or
    [string]::IsNullOrWhiteSpace($VmSize) -or $VmSize -like "<*" -or
    [string]::IsNullOrWhiteSpace($VmImageUrn) -or $VmImageUrn -like "<*" -or
    $AdminCidr -notmatch "^\d{1,3}(\.\d{1,3}){3}/32$" -or
    -not [System.Net.IPAddress]::TryParse(($AdminCidr -split "/")[0], [ref]$ParsedAddress) -or
    -not (Test-Path -LiteralPath $SshPublicKeyFile -PathType Leaf) -or
    -not (Test-Path -LiteralPath $SshPrivateKeyFile -PathType Leaf) -or
    [string]::IsNullOrWhiteSpace($RegistryServer) -or $RegistryServer -like "<*" -or
    [string]::IsNullOrWhiteSpace($RegistryId) -or $RegistryId -like "<*" -or
    $ContainerImage -notmatch "^[a-z0-9.-]+/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$") {
    throw "Set the approved VM, SSH and image inputs."
}
if (-not $RegistryId.StartsWith("/subscriptions/$SubscriptionId/", [System.StringComparison]::OrdinalIgnoreCase) -or
    -not $ContainerImage.StartsWith("$RegistryServer/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Use the selected registry and approved subscription."
}
$RegistryName = ($RegistryId -split "/")[-1]
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ResourceGroupName = "rg-amw-vm-$LabId"
$VmName = "vm-amw-$LabId"
$VnetName = "vnet-amw-$LabId"
$SubnetName = "snet-app"
$NsgName = "nsg-amw-$LabId"
$PublicIpName = "pip-amw-$LabId"
$NicName = "nic-amw-$LabId"
$AdminUser = "workshopadmin"
$LabDirectory = Join-Path (Join-Path $PWD "lab-output") "vm-$LabId"
$GrantFile = Join-Path $LabDirectory "registry-grant-id.txt"
az login
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
[pscustomobject]@{ Subscription = $SubscriptionId; Region = $Location; Group = $ResourceGroupName; VM = $VmName; Size = $VmSize; ImageUrn = $VmImageUrn; SshSource = $AdminCidr; AppImage = $ContainerImage } | Format-List
```

### 4.3. Create the minimal network and VM after approval

Use only the fresh tagged group and isolated example address ranges. Create NSG/NIC/public IP with SSH restricted to the approved /32; do not add HTTP 8080 inbound. Review again before VM creation, then confirm Succeeded, MI principal and expected address. Provisioning creates a VM, not Docker or a working app.

```powershell
$Exists = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Do not reuse an existing VM group." }
New-Item -ItemType Directory -Path $LabDirectory -ErrorAction Stop | Out-Null
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-vm LabId=$LabId --output table
az network vnet create --name $VnetName --resource-group $ResourceGroupName --location $Location --address-prefixes 10.60.0.0/16 --subnet-name $SubnetName --subnet-prefixes 10.60.1.0/24 --subscription $SubscriptionId --output table
az network nsg create --name $NsgName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --output table
az network nsg rule create --name allow-admin-ssh --nsg-name $NsgName --resource-group $ResourceGroupName --priority 100 --direction Inbound --access Allow --protocol Tcp --source-address-prefixes $AdminCidr --source-port-ranges "*" --destination-address-prefixes "*" --destination-port-ranges 22 --subscription $SubscriptionId --output table
az network public-ip create --name $PublicIpName --resource-group $ResourceGroupName --location $Location --sku Standard --allocation-method Static --subscription $SubscriptionId --output table
az network nic create --name $NicName --resource-group $ResourceGroupName --location $Location --vnet-name $VnetName --subnet $SubnetName --network-security-group $NsgName --public-ip-address $PublicIpName --subscription $SubscriptionId --output table
```

```powershell
az vm create --name $VmName --resource-group $ResourceGroupName --location $Location --nics $NicName --image $VmImageUrn --size $VmSize --admin-username $AdminUser --authentication-type ssh --ssh-key-values $SshPublicKeyFile --assign-identity "[system]" --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --subscription $SubscriptionId --output table
$Vm = az vm show --name $VmName --resource-group $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
$VmPrincipalId = $Vm.identity.principalId
$VmIp = az network public-ip show --name $PublicIpName --resource-group $ResourceGroupName --subscription $SubscriptionId --query ipAddress --output tsv
if ($Vm.provisioningState -ne "Succeeded" -or -not $VmPrincipalId -or [string]::IsNullOrWhiteSpace($VmIp)) {
    throw "VM provisioning, managed identity or public IP is incomplete."
}
[pscustomobject]@{ VM = $VmName; Address = $VmIp; Principal = $VmPrincipalId; RegistryScope = $RegistryId } | Format-List
```

### 4.4. Administrator: grant the VM identity registry pull access

Only an authorized administrator grants AcrPull to the new VM principal at the selected registry. Save the exact new assignment ID immediately and transfer it through a safe channel. The participant records only this grant. VM management and image pull are different permissions; wait for propagation instead of using registry admin passwords.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$RegistryGrantId = az role assignment create --assignee-object-id $VmPrincipalId --assignee-principal-type ServicePrincipal --role AcrPull --scope $RegistryId --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($RegistryGrantId)) { throw "The VM pull role assignment ID was not returned." }
$RegistryGrantId
```

```powershell
if ([string]::IsNullOrWhiteSpace($RegistryGrantId) -or
    -not $RegistryGrantId.StartsWith("$RegistryId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Record only the registry grant created for this VM."
}
Set-Content -LiteralPath $GrantFile -Value $RegistryGrantId -Encoding utf8NoBOM
```

### 4.5. Local SSH to VM Bash: prepare tools

Verify the host fingerprint, SSH to the approved VM and run the Bash installation commands there. Use approved OS/package sources and inspect the downloaded official Azure CLI installer before authorizing execution. Explicit sudo docker avoids automatically adding users to the root-equivalent Docker group. Do not disable TLS/signature checks on package failures.

```powershell
ssh -i $SshPrivateKeyFile "$AdminUser@$VmIp"
```

```bash
set -euo pipefail
sudo apt-get update
sudo apt-get install --yes docker.io curl ca-certificates python3
sudo systemctl enable --now docker
sudo docker version
```

```bash
curl --fail --silent --show-error --location \
  https://aka.ms/InstallAzureCLIDeb --output install-azure-cli.sh
```

```bash
sudo bash install-azure-cli.sh
az version
rm -- install-azure-cli.sh
```

**Resources for this step**

- [Install azure cli linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux)

### 4.6. VM Bash: pull by Managed Identity

Use the exact approved registry/image values. The subshell signs in with the VM identity, obtains an ACR token, checks the returned registry, passes the token through stdin and removes registry login state on success/failure. Never echo tokens, enable shell tracing or copy the local participant login cache. This is registry access, not app data authorization.

```bash
(
  set -euo pipefail
  SUBSCRIPTION_ID="<sandbox-subscription-id>"
  REGISTRY_NAME="<approved-registry-name>"
  REGISTRY_SERVER="<approved-registry-login-server>"
  CONTAINER_IMAGE="<approved-registry-login-server>/workshop/app@sha256:<digest>"
  if [[ "$SUBSCRIPTION_ID" == "<"* || "$REGISTRY_NAME" == "<"* ||
        "$REGISTRY_SERVER" == "<"* || "$CONTAINER_IMAGE" == "<"* ]]; then
    printf 'Replace the approved image and registry inputs.\n' >&2
    exit 1
  fi
  az login --identity --output none
  trap 'unset AUTH_JSON ACR_TOKEN; sudo docker logout "$REGISTRY_SERVER"' EXIT
  AUTH_JSON="$(az acr login --name "$REGISTRY_NAME" --subscription "$SUBSCRIPTION_ID" \
    --expose-token --output json)"
  TOKEN_SERVER="$(printf '%s' "$AUTH_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["loginServer"])')"
  if [[ "$TOKEN_SERVER" != "$REGISTRY_SERVER" ||
        "$CONTAINER_IMAGE" != "$REGISTRY_SERVER/"* ]]; then
    printf 'The token response and selected image do not match the approved registry.\n' >&2
    exit 1
  fi
  ACR_TOKEN="$(printf '%s' "$AUTH_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["accessToken"])')"
  unset AUTH_JSON
  if [[ -z "$ACR_TOKEN" ]]; then
    printf 'No registry access token was returned.\n' >&2
    exit 1
  fi
  printf '%s' "$ACR_TOKEN" | sudo docker login "$REGISTRY_SERVER" \
    --username 00000000-0000-0000-0000-000000000000 --password-stdin
  unset ACR_TOKEN
  sudo docker pull "$CONTAINER_IMAGE"
)
```

### 4.7. VM Bash: bind the app only to localhost

Set the digest again because subshell variables do not survive. Reject an existing workshop container and start only this lab's container with CPU/memory limits, non-root image user, read-only rootfs, dropped capabilities and no-new-privileges. Expect 10001:10001, healthy and app logs; Running alone is insufficient.

```bash
set -euo pipefail
CONTAINER_IMAGE="<approved-registry-login-server>/workshop/app@sha256:<digest>"
if [[ "$CONTAINER_IMAGE" == "<"* || -z "$CONTAINER_IMAGE" ]]; then
  printf 'Set the approved digest image.\n' >&2
  exit 1
fi
sudo docker info >/dev/null
EXISTING="$(sudo docker ps --all --filter 'name=^/workshop$' --format '{{.Names}}')"
if [[ -n "$EXISTING" ]]; then
  printf 'The workshop container already exists. Inspect it before changing anything.\n' >&2
  exit 1
fi
sudo docker run --detach --name workshop --restart unless-stopped \
  --publish 127.0.0.1:8080:8080 --cpus 0.25 --memory 256m \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  "$CONTAINER_IMAGE"
sudo docker ps --filter 'name=^/workshop$'
sudo docker inspect --format '{{.Config.User}} {{.State.Health.Status}}' workshop
sudo docker logs --tail 20 workshop
```

### 4.8. Local PowerShell: tunnel and verify the HTTP contract

Maintain the SSH localhost tunnel in a separate terminal. In the first local terminal use the matching local URL. For a fresh single-process application, expect GET /health to return 200 with status ok, two initial items, POST /items to return 201, and the new item to appear on read-back. Invalid input returns 422 without changing the data. Restarting resets the in-memory dataset. A running resource or container is not enough: observe the actual HTTP responses and relevant logs. If port 8080 is occupied, stop only your own process or change tunnel and client ports together. Optional docker restart demonstrates reset, not durability or zero downtime.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$SshPrivateKeyFile = "<approved-private-key-file>"
$AdminUser = "workshopadmin"
$VmIp = "<this-lab-vm-public-ip>"
ssh -i $SshPrivateKeyFile -N -L "127.0.0.1:8080:127.0.0.1:8080" -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 "$AdminUser@$VmIp"
```

```powershell
$BaseUrl = "http://127.0.0.1:8080"
$Health = Invoke-RestMethod "$BaseUrl/health"
$Before = @(Invoke-RestMethod "$BaseUrl/items")
if ($Health.status -ne "ok" -or $Before.Count -ne 2) { throw "Expected a healthy fresh app with two seed items." }
$Created = Invoke-RestMethod "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":"vm-workshop-item"}' -StatusCodeVariable PostStatus
$After = @(Invoke-RestMethod "$BaseUrl/items")
if ($PostStatus -ne 201 -or $After.Count -ne 3 -or
    -not ($After | Where-Object { $_.id -eq $Created.id -and $_.name -eq "vm-workshop-item" })) {
    throw "VM write/read verification failed."
}
$Invalid = Invoke-WebRequest "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":""}' -SkipHttpErrorCheck
if ($Invalid.StatusCode -ne 422 -or @(Invoke-RestMethod "$BaseUrl/items").Count -ne 3) {
    throw "Invalid input changed the data or did not return 422."
}
```

### 4.9. Alternative: approved private VM and Run Command

Choose this instead of the public SSH branch when private network/outbound inputs are already approved. Keep no VM public IP or SSH inbound and grant only the VM MI's required registry access. An authorized administrator can execute the same guest Bash and localhost HTTP checks through official Run Command. Explicitly invoke Bash for pipefail scripts because the default shell may be /bin/sh. Read actual guest stdout/errors and pass criteria; ARM Enable succeeded is not app evidence. Fixture-specific token exchange, network preparation and diagnostics are instructor responsibilities.

An existing approved private client VM can also host the Docker exercise when its owner approves that use. Reuse the image, identity and network inputs without creating a second VM or changing other consumers. Preserve this supplied VM during consumer cleanup.

In the Portal, open the selected **VM Overview → Monitoring → Platform metrics** and read the CPU metric, aggregation and time range. The example chart is **Average CPU over Last 24 hours**, approximately **2.2026%**. CPU activity describes the VM host; use the localhost HTTP and Docker checks above to assess the app. Viewing this chart needs no Performance Diagnostics installation, VM Insights or new Log Analytics workspace.

![VM platform CPU chart with Average aggregation over Last 24 hours](./images/portal-vm-cpu-metric.png)

*Running status and a CPU chart are host observations. Read container health, logs and HTTP responses separately; this metric value is an example for its selected period, not a workload performance guarantee.*

**Resources for this step**

- [Run command](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command)

## 5. Verification and common failures

Investigate approved image/SKU/quota, NSG associations and actual SSH egress IP, keys/fingerprint, packages/outbound, Docker daemon, registry identity/mode/digest and propagation, or app logs/limits. Do not widen inbound access or bypass host-key/TLS checks. Inspect current VM state independently of earlier HTTP observations.

## 6. Cleanup and ownership

Own only the dedicated VM assets and exact consumer-added grants. In a private branch, also track owned subnet/configuration and grants on external VNet/NAT/registry scopes without deleting those shared inputs. Use the detailed checks below. Obtain approval for deletion or restart/deallocation rather than treating them as automatic consequences of a test.

### 6.1. VM Bash: stop only the lab container

End the tunnel with Ctrl+C. Inspect the exact container name/image on the correct VM, obtain removal approval, then stop/remove only workshop. Do not run Docker global prune; the disk lifecycle is handled by the approved group cleanup.

```bash
sudo docker inspect --format '{{.Name}} {{.Config.Image}}' workshop
```

```bash
sudo docker stop workshop
sudo docker rm workshop
exit
```

### 6.2. Administrator: revoke only this VM's registry grant

Read the saved assignment ID, validate its registry scope, and inspect the exact principal/scope before approval to delete it. Do not remove existing user grants or unrelated registry permissions.

```powershell
$RegistryGrantId = (Get-Content -Raw -LiteralPath $GrantFile).Trim()
if (-not $RegistryGrantId.StartsWith("$RegistryId/providers/Microsoft.Authorization/roleAssignments/", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Unexpected registry grant scope."
}
az role assignment list --scope $RegistryId --subscription $SubscriptionId --query "[?id=='$RegistryGrantId'].{id:id,principal:principalId,scope:scope}" --output table
```

```powershell
az role assignment delete --ids $RegistryGrantId --subscription $SubscriptionId
```

### 6.3. Local PowerShell: delete the dedicated VM group

List the exact subscription/group, tags and resources. Confirm only owned VM, OS disk, NIC, network and selected public IP are present, then approve deletion and verify group absence. Remove only the grant record and empty local lab directory. Preserve input SSH keys, all other lab-output folders and the registry publisher's resources until its last consumer finishes.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-vm-$LabId" -or $Group.tags.Workshop -ne "azure-migration-vm" -or $Group.tags.LabId -ne $LabId) {
    throw "The group is not this VM lab."
}
```

```powershell
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$ExistsAfter = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfter -ne "false") { throw "VM group cleanup is not verified." }
Remove-Item -LiteralPath $GrantFile
Remove-Item -LiteralPath $LabDirectory
```

**Resources for this step**

- [Container image](../../../shared/container-image/README.md#6-cleanup-and-ownership)

## 7. Additional considerations for a real migration

Decide whether to preserve the existing OS/services/disks with Azure Migrate or redeploy only the app. Review patching/hardening, backups, remote access, image supply chain, sizing/CPU credits, disk performance, HA, durable logs, external DB/storage and cutover/rollback. This small VM lab is not a production operating design.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Container registry authentication managed identity](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication-managed-identity)
- [Install azure cli linux](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-linux)
