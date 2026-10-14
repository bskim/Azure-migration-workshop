# Networking — read VNet, subnet and NSG boundaries

English | [한국어](./README-ko.md)

Compare AWS networking concepts with Azure addresses, NSG associations and actual communication evidence. Configuration inspection and a successful connection are different achievements.

## 1. Learning objectives and module boundaries

Choose concept reading (about 20 minutes), a new network configuration (30–40 minutes), or an optional two-VM communication probe (60–90 minutes plus preparation). No shared app, image, Docker or other compute course is required. Use a fresh isolated VNet and dedicated probe endpoints, not another track's resources. The fixed JSON HTTP probe is a diagnostic fixture, not a second business application.

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Virtual networks overview](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview)
- [Network security groups overview](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview)
- [Virtual network network interface](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface)
- [Public ip addresses](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses)
- [Overview](https://learn.microsoft.com/en-us/azure/virtual-machines/overview)
- [Run command overview](https://learn.microsoft.com/en-us/azure/virtual-machines/run-command-overview)
- [Overview](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)

## 3. Prerequisites, permissions and cost

Commands use local PowerShell 7.4+ and Azure CLI from the repository root; only Run Command payloads execute Linux Bash/Python in the VM. Approve Microsoft.Network registration and network management rights. Basic configuration has no VM, gateway, public IP or load balancer. The optional probe adds two x64 Ubuntu Gen2 VMs, two OS disks and two public IPs for explicit guest-agent outbound, not public SSH/HTTP inbound. Approve SKU, image, quota, public key, Run Command access and costs separately. Run Command may execute with elevated guest privileges. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Predict the path and rules without deploying

Use VNet 10.70.0.0/16, client subnet 10.70.1.0/24 and server subnet 10.70.2.0/24. Predict A: default AllowVNetInBound allows a new TCP 8080 connection; B: Deny priority 200 blocks it; C: an exact-client /32 Allow priority 100 wins over the Deny. Smaller priority numbers are evaluated first. These are predictions until observed. Existing flows may survive a stateful rule change, so each probe must create a new connection.

```text
VNet 10.70.0.0/16
  client subnet 10.70.1.0/24
    [optional client VM 10.70.1.4] → new TCP/HTTP request
  server subnet 10.70.2.0/24
    NSG: inbound evaluation in priority order
    [optional server VM 10.70.2.4:8080] → fixed probe response
```

### 4.2. Confirm the target and fresh group in PowerShell

Set the approved subscription and region, inspect tenant and Enabled state, and display names and address ranges. The generated group must not already exist. Review cost and creation scope before proceeding. These examples do not peer the VNet with production or on-premises networks.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
$SubscriptionId = "<sandbox-subscription-id>"
$Location = "<approved-region>"
$ParsedId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedId) -or
    [string]::IsNullOrWhiteSpace($Location) -or $Location -like "<*") {
    throw "Set the approved sandbox subscription and region."
}
az login
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$ResourceGroupName = "rg-amw-net-$LabId"
$VnetName = "vnet-amw-net-$LabId"
$ClientSubnetName = "snet-client"
$ServerSubnetName = "snet-server"
$ServerNsgName = "nsg-amw-server-$LabId"
$ClientNsgName = "nsg-amw-client-$LabId"
$ClientIp = "10.70.1.4"
$ServerIp = "10.70.2.4"
[pscustomobject]@{ Subscription = $SubscriptionId; Region = $Location; Group = $ResourceGroupName; VNet = "10.70.0.0/16"; Client = "10.70.1.0/24"; Server = "10.70.2.0/24" } | Format-List
$Exists = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Use a fresh networking lab group." }
```

### 4.3. Create the network without another compute track

Create the dedicated group, two subnets and server NSG association. Observe subnet prefixes and default rules, including priority 65000 AllowVNetInBound and 65500 DenyAllInBound. After subnet configuration, inspect the endpoints and test the HTTP connection. Configuration-only learners may inspect the rule creation commands in steps 4.6–4.7 and then clean up; do not run VM probes in that mode.

```powershell
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-networking LabId=$LabId --output table
az network vnet create --name $VnetName --resource-group $ResourceGroupName --location $Location --address-prefixes 10.70.0.0/16 --subnet-name $ClientSubnetName --subnet-prefixes 10.70.1.0/24 --subscription $SubscriptionId --output table
az network vnet subnet create --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --address-prefixes 10.70.2.0/24 --subscription $SubscriptionId --output table
az network nsg create --name $ServerNsgName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --output table
az network vnet subnet update --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --network-security-group $ServerNsgName --subscription $SubscriptionId --output table
az network vnet subnet show --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --subscription $SubscriptionId --query "{prefix:addressPrefix,nsg:networkSecurityGroup.id}" --output json
az network nsg show --name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --query defaultSecurityRules --output table
```

### 4.4. Optional: prepare two diagnostic endpoints

Select an approved small x64 VM size, Ubuntu 24.04 Gen2 image and public SSH key file. No private key or SSH session is required for this probe. Approve two VMs, disks, public IPs and outbound/guest-agent access before creation. The client has a NIC NSG and the server a subnet NSG; the example intentionally avoids a second server NSG boundary. No internet SSH or HTTP allow rule is added.

```powershell
$ProbeVmSize = "<approved-small-x64-vm-size>"
$ProbeImageUrn = "<approved-ubuntu-24.04-x64-gen2-image-urn>"
$SshPublicKeyFile = "<approved-public-key-file>"
if ([string]::IsNullOrWhiteSpace($ProbeVmSize) -or $ProbeVmSize -like "<*" -or
    [string]::IsNullOrWhiteSpace($ProbeImageUrn) -or $ProbeImageUrn -like "<*" -or
    -not (Test-Path -LiteralPath $SshPublicKeyFile -PathType Leaf)) {
    throw "Set approved probe VM size, image and public key."
}
$ClientVmName = "vm-amw-client-$LabId"
$ServerVmName = "vm-amw-server-$LabId"
$ClientNicName = "nic-amw-client-$LabId"
$ServerNicName = "nic-amw-server-$LabId"
$ClientPublicIpName = "pip-amw-client-$LabId"
$ServerPublicIpName = "pip-amw-server-$LabId"
[pscustomobject]@{ Client = $ClientVmName; Server = $ServerVmName; Size = $ProbeVmSize; Image = $ProbeImageUrn; PublicIps = 2 } | Format-List
```

```powershell
az network nsg create --name $ClientNsgName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --output table
az network public-ip create --name $ClientPublicIpName --resource-group $ResourceGroupName --location $Location --sku Standard --allocation-method Static --subscription $SubscriptionId --output table
az network public-ip create --name $ServerPublicIpName --resource-group $ResourceGroupName --location $Location --sku Standard --allocation-method Static --subscription $SubscriptionId --output table
az network nic create --name $ClientNicName --resource-group $ResourceGroupName --location $Location --vnet-name $VnetName --subnet $ClientSubnetName --private-ip-address $ClientIp --network-security-group $ClientNsgName --public-ip-address $ClientPublicIpName --subscription $SubscriptionId --output table
az network nic create --name $ServerNicName --resource-group $ResourceGroupName --location $Location --vnet-name $VnetName --subnet $ServerSubnetName --private-ip-address $ServerIp --public-ip-address $ServerPublicIpName --subscription $SubscriptionId --output table
az vm create --name $ClientVmName --resource-group $ResourceGroupName --location $Location --nics $ClientNicName --image $ProbeImageUrn --size $ProbeVmSize --admin-username workshopadmin --authentication-type ssh --ssh-key-values $SshPublicKeyFile --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --subscription $SubscriptionId --output table
az vm create --name $ServerVmName --resource-group $ResourceGroupName --location $Location --nics $ServerNicName --image $ProbeImageUrn --size $ProbeVmSize --admin-username workshopadmin --authentication-type ssh --ssh-key-values $SshPublicKeyFile --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --subscription $SubscriptionId --output table
```

### 4.5. Start the server probe and establish baseline A

Run the guest server script only on the new diagnostic server. Read stdout/stderr and the actual active service state. Then invoke the client probe to request the server's private IP with a fresh connection. Baseline A must be connected with HTTP 200 and the exact module/result JSON. An outer Run Command success is not this evidence. The probe uses a request-local direct path, not a global proxy change; if policy requires a proxy even here, obtain an approved fixture instead of bypassing it. Missing, malformed or multiple AMW_PROBE records are failures.

```powershell
$ServerScript = @'
set -euo pipefail
if [ -e /var/lib/amw-network-probe ]; then
  printf 'Probe directory already exists; inspect before changing it.\n' >&2
  exit 1
fi
umask 022
mkdir /var/lib/amw-network-probe
printf '%s' '{"module":"networking","result":"ok"}' > /var/lib/amw-network-probe/health.json
systemd-run --unit=amw-network-probe --property=User=nobody \
  --property=WorkingDirectory=/var/lib/amw-network-probe \
  /usr/bin/python3 -m http.server 8080 --bind 10.70.2.4
systemctl is-active amw-network-probe
'@
az vm run-command invoke --name $ServerVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ServerScript --subscription $SubscriptionId --output json
```

```powershell
$ProbeScript = @'
set -euo pipefail
python3 - <<'PY'
import json
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

url = "http://10.70.2.4:8080/health.json"
opener = build_opener(ProxyHandler({}))
try:
    with opener.open(Request(url, headers={"Connection": "close"}), timeout=5) as response:
        body = json.load(response)
        valid = response.status == 200 and body == {"module": "networking", "result": "ok"}
        print("AMW_PROBE=" + json.dumps({"outcome": "connected" if valid else "unexpected-response", "status": response.status, "body": body}))
except TimeoutError as error:
    print("AMW_PROBE=" + json.dumps({"outcome": "timeout", "error": str(error)}))
except URLError as error:
    outcome = "timeout" if isinstance(error.reason, TimeoutError) else "error"
    print("AMW_PROBE=" + json.dumps({"outcome": outcome, "error": str(error)}))
PY
'@
function Read-ProbeEvidence($RunResult) {
    $Messages = @($RunResult.value | ForEach-Object { $_.message }) -join "`n"
    $Records = [regex]::Matches($Messages, 'AMW_PROBE=(\{[^\r\n]*\})')
    if ($Records.Count -ne 1) { throw "No single probe result was returned. Inspect Run Command stdout/stderr." }
    return ($Records[0].Groups[1].Value | ConvertFrom-Json)
}
$RunA = az vm run-command invoke --name $ClientVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ProbeScript --subscription $SubscriptionId --output json | ConvertFrom-Json
$EvidenceA = Read-ProbeEvidence $RunA
$EvidenceA | Format-List
if ($EvidenceA.outcome -ne "connected") { throw "Baseline communication failed; do not infer an NSG denial." }
```

### 4.6. State B: deny client-subnet TCP 8080

Configuration-only learners create and read the rule; probe learners also run the new client request. Priority 200 precedes the default allow. Expect an explicit timeout only after baseline A succeeded. Connection refused, guest-agent failures or missing evidence are not equivalent to NSG denial.

```powershell
az network nsg rule create --name deny-client-http --nsg-name $ServerNsgName --resource-group $ResourceGroupName --priority 200 --direction Inbound --access Deny --protocol Tcp --source-address-prefixes 10.70.1.0/24 --source-port-ranges "*" --destination-address-prefixes "$ServerIp/32" --destination-port-ranges 8080 --subscription $SubscriptionId --output table
az network nsg rule list --nsg-name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --output table
```

```powershell
$RunB = az vm run-command invoke --name $ClientVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ProbeScript --subscription $SubscriptionId --output json | ConvertFrom-Json
$EvidenceB = Read-ProbeEvidence $RunB
$EvidenceB | Format-List
if ($EvidenceB.outcome -ne "timeout") { throw "Expected a new connection timeout after the denial rule." }
```

### 4.7. State C: allow only the exact client at higher priority

Keep Deny 200 and add exact client /32 Allow 100. Observe the rule order, then expect the same private HTTP path to reconnect. The complete optional observation is A connected → B new-connection timeout → C connected. Do not generalize this exact-client allow to other client addresses.

```powershell
az network nsg rule create --name allow-exact-client-http --nsg-name $ServerNsgName --resource-group $ResourceGroupName --priority 100 --direction Inbound --access Allow --protocol Tcp --source-address-prefixes "$ClientIp/32" --source-port-ranges "*" --destination-address-prefixes "$ServerIp/32" --destination-port-ranges 8080 --subscription $SubscriptionId --output table
az network nsg rule list --nsg-name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --output table
```

```powershell
$RunC = az vm run-command invoke --name $ClientVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ProbeScript --subscription $SubscriptionId --output json | ConvertFrom-Json
$EvidenceC = Read-ProbeEvidence $RunC
$EvidenceC | Format-List
if ($EvidenceC.outcome -ne "connected") { throw "Communication did not recover for the exact client." }
```

## 5. Verification and common failures

Verify address ranges, NSG associations and priority interpretation in configuration mode. In probe mode require all three actual results. Check both NIC/subnet NSGs, routes, upper-level policies, guest firewall, listener and source/destination ports. VirtualNetwork service tag scope can include more than the current VNet depending on routing/peering. A ping or successful management API call is not a complete network test.

## 6. Cleanup and ownership

Reading creates no resources. Configuration and optional VMs belong to this dedicated group. List its resources, compare exact name, Workshop tag and LabId, obtain deletion approval and verify group absence. Do not delete other compute groups, shared images, input public keys, existing policy or a subscription-wide Network Watcher. Handle partial creation by listing what actually exists.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-net-$LabId" -or $Group.tags.Workshop -ne "azure-migration-networking" -or $Group.tags.LabId -ne $LabId) {
    throw "The group does not match this networking lab."
}
```

```powershell
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$ExistsAfter = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfter -ne "false") { throw "Networking cleanup is not verified." }
```

## 7. Additional considerations for a real migration

Consider overlapping address space, DNS, UDRs, peering and on-premises routes; private/public endpoints and explicit outbound; egress cost; and SG/NACL-to-NSG semantic differences. Azure subnets are regional rather than AWS AZ-bound units. NSG Allow alone does not establish a route or DNS. Advanced HA, diagnostics and network architecture remain separate.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.

**Resources for this step**

- [Run command](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command)
