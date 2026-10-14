# 네트워킹 — VNet·subnet·NSG로 통신 경계 읽기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: AWS VPC·subnet·Security Group 경험이 있는 엔지니어.
- 예상: 개념 읽기 20분, 네트워크 구성 30~40분, 선택 통신 실습 60~90분 + VM/guest agent 준비 대기. 실제 시간은 환경과 참가자 경험에 따라 달라집니다.
- 목표: Azure의 subnet 범위, NSG association·우선순위·기본 규칙을 읽고 **설정 확인과 실제 통신 확인을 구분**합니다.
- 결과: VNet·두 subnet·NSG 구성과 허용/차단 이유. 통신 실습을 선택하면 같은 경로의 허용→차단→허용 관찰.

| 선택 범위 | 최소 입력 | 필요 없는 완료 |
|---|---|---|
| 개념 읽기 | 이 문서의 주소·규칙 예제 | Azure 로그인·리소스 생성 전부 |
| 네트워크 구성 | 승인된 Azure 구독·리전·네트워크 권한 | 공통 앱·이미지·Docker·모든 컴퓨트 트랙 |
| 선택 통신 실습 | 이 모듈의 네트워크와 승인된 작은 VM 설정·공개키·Run Command 권한 | VM + Docker·AKS·Container Apps·Terraform·DB·Blob |

다른 트랙의 VNet·VM·NIC를 가져오거나 운영 네트워크를 수정하지 않습니다. 통신 실습의 endpoint는 **이 모듈이 새로 만드는 검사 전용 VM 2개**입니다. HTTP의 고정 JSON 응답은 통신 probe이며 별도의 business app이 아닙니다. 공통 앱과 이미지도 수정하지 않습니다.


## 2. 서비스 소개와 AWS 비교


| 서비스·기능 | Microsoft Learn 소개 | 이 모듈에서 볼 내용 |
|---|---|---|
| Azure Virtual Network | [VNet 개요](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview) | 주소 공간·subnet·기본 연결 |
| Network Security Group | [NSG 개요](https://learn.microsoft.com/en-us/azure/virtual-network/network-security-groups-overview) | association·stateful 규칙·우선순위 |
| Network Interface | [NIC 개요](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-network-interface) | VM의 IP와 NIC/subnet NSG |
| Public IP | [Public IP 개요](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses) | 선택 VM의 명시적 outbound 경로 |
| Virtual Machines | [VM 개요](https://learn.microsoft.com/en-us/azure/virtual-machines/overview) | 선택 통신 검사 endpoint |
| Run Command | [Run Command 개요](https://learn.microsoft.com/en-us/azure/virtual-machines/run-command-overview) | guest agent를 통한 제어 명령 |
| Resource Manager | [Resource Manager 개요](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) | 실습 전용 그룹과 소유권 |

| AWS에서 읽던 것 | Azure에서 비교할 것 | 중요한 차이 |
|---|---|---|
| VPC | VNet | 유사한 사설 네트워크 경계지만 기능·기본 라우팅·접근 정책이 같지는 않음 |
| AZ에 속한 subnet | 리전 VNet의 subnet | Azure subnet을 특정 AZ에 묶인 동일 단위로 매핑하지 않음 |
| ENI의 Security Group | NIC 또는 subnet의 NSG | NSG는 subnet에도 연결할 수 있고 명시적 Deny와 우선순위가 있음 |
| SG / Network ACL | NSG | SG의 allow-only·stateful, NACL의 stateless와 NSG를 1:1 동일시하지 않음 |
| Route table / NAT / gateway | System route / UDR / NAT Gateway 등 | NSG Allow만으로 경로·DNS·outbound가 생기지 않음. 이 실습은 고급 라우팅을 제외 |

NSG는 숫자가 **작은 priority부터** 평가합니다. 기본 inbound 규칙의 예는 `AllowVNetInBound` 65000, `AllowAzureLoadBalancerInBound` 65001, `DenyAllInBound` 65500입니다. 사용자 규칙의 priority 100/200은 기본 규칙보다 앞섭니다.

`VirtualNetwork` service tag는 언제나 현재 VNet의 주소만 뜻하는 문자열이 아닙니다. peering·gateway·route 구성에 따라 범위를 함께 읽어야 합니다. 이 실습은 그런 연결 없는 새 VNet으로 제한합니다.

NIC와 subnet 모두에 NSG가 있으면 필요한 두 경계의 평가를 함께 읽습니다. 양쪽 NSG 평가와 실제 경로·listener·통신 결과를 함께 확인합니다. Azure Virtual Network Manager의 security admin rule 등 상위 제약은 별도 고려사항입니다.


## 3. 사전 준비·비용·안전


- 명령은 **로컬 PowerShell 7.4 이상 + Azure CLI**, 저장소 루트에서 실행합니다. Run Command 안의 script만 Linux Bash/Python입니다.
- 승인된 샌드박스 구독·리전과 `Microsoft.Network` 등록, 새 그룹·VNet·subnet·NSG의 생성/조회/삭제 권한을 준비합니다.
- 예제 주소는 `10.70.0.0/16`, client subnet `10.70.1.0/24`, server subnet `10.70.2.0/24`입니다. 기존 네트워크와 peering·VPN·온프레미스 연결을 하지 않습니다.
- 기본 구성에는 VM·public IP·gateway·Load Balancer가 없습니다. **선택 통신 실습**에만 VM 2개·OS disk 2개·public IP 2개가 추가되므로 [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)로 별도 승인합니다.
- 선택 실습은 승인된 작은 x64 VM SKU·Ubuntu 24.04 Gen2 이미지·quota·공개 SSH key 파일을 입력받습니다. SKU·가격·quota는 강사가 선택 환경의 지원과 동작을 확인합니다.
- 선택 VM의 public IP는 **guest agent의 명시적 outbound** 준비용입니다. SSH·HTTP의 인터넷 inbound 허용 규칙은 만들지 않습니다. 앱/검사 endpoint가 인터넷 공개됐다고 해석하지 않습니다.
- Run Command에는 VM 실행 권한이 필요하며 guest에서 높은 권한으로 동작할 수 있습니다. 새 검사 VM에만 사용하고 secrets·고객 데이터를 script에 넣지 않습니다.
- guest agent는 Azure endpoint의 443 outbound가 필요합니다. Run Command 호출 성공은 VM 간 8080 통신 성공과 다릅니다.
- NAT Gateway·Bastion·Firewall·VPN·peering·Private Endpoint·flow log 플랫폼은 기본 실습에 추가하지 않습니다. 비용이 부담되면 개념·구성만 선택합니다.


## 4. 단계별 instruction — 선택 범위만 진행


### 4.1 클라우드 없이 경로·규칙 예측


```text
VNet 10.70.0.0/16
  client subnet 10.70.1.0/24
    [선택 client VM 10.70.1.4] → 새 TCP/HTTP 요청
  server subnet 10.70.2.0/24
    NSG: priority 순서로 inbound 평가
    [선택 server VM 10.70.2.4:8080] → 고정 probe 응답
```

다음 세 상태를 예측합니다.

| 상태 | server subnet NSG의 관련 규칙 | 새 client→server TCP 8080의 예상 |
|---|---|---|
| A | 사용자 규칙 없음, 기본 AllowVNetInBound | 허용 |
| B | priority 200, client subnet→server 8080 Deny | 차단 |
| C | B 유지 + priority 100, 정확한 client IP→server 8080 Allow | 허용 |

기존 flow는 NSG의 stateful 동작 때문에 규칙 변경 후에도 유지될 수 있습니다. 통신 실습은 매번 새 연결을 열어 비교합니다. 이 표는 아직 실험 결과가 아니라 **예상**입니다.


### 4.2 로컬 PowerShell — 대상과 새 그룹 확인


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

승인된 구독·테넌트·`Enabled` 상태와 주소·대상을 확인하고 리소스 생성을 승인한 뒤 진행합니다.


### 4.3 네트워크 구성 — 다른 컴퓨트 없이 완료 가능


```powershell
az group create --name $ResourceGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-networking LabId=$LabId --output table
az network vnet create --name $VnetName --resource-group $ResourceGroupName --location $Location --address-prefixes 10.70.0.0/16 --subnet-name $ClientSubnetName --subnet-prefixes 10.70.1.0/24 --subscription $SubscriptionId --output table
az network vnet subnet create --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --address-prefixes 10.70.2.0/24 --subscription $SubscriptionId --output table
az network nsg create --name $ServerNsgName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --output table
az network vnet subnet update --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --network-security-group $ServerNsgName --subscription $SubscriptionId --output table
az network vnet subnet show --name $ServerSubnetName --vnet-name $VnetName --resource-group $ResourceGroupName --subscription $SubscriptionId --query "{prefix:addressPrefix,nsg:networkSecurityGroup.id}" --output json
az network nsg show --name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --query defaultSecurityRules --output table
```

**관찰할 결과:** 두 subnet, server subnet의 NSG association, 기본 규칙입니다. subnet 구성 다음에는 VM/listener와 실제 8080 연결을 따로 확인합니다.

구성만 선택했다면 규칙의 우선순위는 4.6~4.7의 두 `az network nsg rule create` 명령만 사용해 관찰할 수 있습니다. VM·Run Command 부분은 생략합니다. 완료 기준은 **주소·association·규칙 이유를 설명하는 것**이며 통신 성공/차단으로 기록하지 않습니다. 정리는 6절의 그룹 삭제입니다.


### 4.4 선택 통신 실습 — 검사 endpoint 2개만 준비


VM + Docker 트랙을 따라갈 필요가 없습니다. 이 모듈의 새 그룹 안에서 검사 VM을 준비합니다. 승인된 공개키만 사용하며 개인키·SSH 접속은 이 실습에 필요하지 않습니다.

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

VM 2개·disk·IP의 비용과 Run Command 권한·outbound를 승인한 경우에만 다음을 실행합니다.

```powershell
az network nsg create --name $ClientNsgName --resource-group $ResourceGroupName --location $Location --subscription $SubscriptionId --output table
az network public-ip create --name $ClientPublicIpName --resource-group $ResourceGroupName --location $Location --sku Standard --allocation-method Static --subscription $SubscriptionId --output table
az network public-ip create --name $ServerPublicIpName --resource-group $ResourceGroupName --location $Location --sku Standard --allocation-method Static --subscription $SubscriptionId --output table
az network nic create --name $ClientNicName --resource-group $ResourceGroupName --location $Location --vnet-name $VnetName --subnet $ClientSubnetName --private-ip-address $ClientIp --network-security-group $ClientNsgName --public-ip-address $ClientPublicIpName --subscription $SubscriptionId --output table
az network nic create --name $ServerNicName --resource-group $ResourceGroupName --location $Location --vnet-name $VnetName --subnet $ServerSubnetName --private-ip-address $ServerIp --public-ip-address $ServerPublicIpName --subscription $SubscriptionId --output table
az vm create --name $ClientVmName --resource-group $ResourceGroupName --location $Location --nics $ClientNicName --image $ProbeImageUrn --size $ProbeVmSize --admin-username workshopadmin --authentication-type ssh --ssh-key-values $SshPublicKeyFile --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --subscription $SubscriptionId --output table
az vm create --name $ServerVmName --resource-group $ResourceGroupName --location $Location --nics $ServerNicName --image $ProbeImageUrn --size $ProbeVmSize --admin-username workshopadmin --authentication-type ssh --ssh-key-values $SshPublicKeyFile --storage-sku StandardSSD_LRS --os-disk-size-gb 32 --security-type TrustedLaunch --enable-vtpm true --enable-secure-boot true --subscription $SubscriptionId --output table
```

client는 NIC NSG, server는 subnet NSG를 사용합니다. server NIC에 추가 NSG를 만들지 않아 이 실습의 판정 경계를 명확히 합니다. 두 VM 모두 public SSH/HTTP 허용 규칙은 없습니다.


### 4.5 Server probeと状態A — まず成功経路を確認


Run Command는 guest agent를 통한 **제어 영역**입니다. API 호출 자체를 VM 간 통신 결과로 취급하지 않습니다. 새 검사 VM에만 아래 guest script를 실행합니다.

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

출력에서 script의 실제 stdout/stderr·service 상태를 읽습니다. 실패를 무시하고 client probe로 넘어가지 않습니다. 다음 probe는 고정 JSON을 읽고 하나의 명시적 결과를 출력합니다.

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

probe는 승인된 이 VNet의 private IP에 직접 연결하도록 요청별 proxy를 사용하지 않습니다. OS의 전역 proxy 설정은 바꾸지 않습니다. 조직 정책이 이 사설 경로도 proxy를 강제한다면 우회하지 말고 승인된 별도 실습 환경을 준비합니다.

probe 프로그램은 관찰을 완료하면 명시적 `outcome`을 출력합니다. timeout/error도 정상 통신으로 바꾸지 않고 결과에 기록하며 **로컬의 상태별 판정이 성공/실패를 결정**합니다. 프로그램·agent 자체 오류로 결과가 없거나 잘못됐으면 중단합니다. 이는 실패한 연결을 숨기거나 바깥 CLI 성공을 통신 성공으로 취급하는 방식이 아닙니다.


### 4.6 상태B — client subnet의 8080 차단


네트워크 구성을 읽는 참가자는 규칙 생성·조회만, 통신 실습 참가자는 새 probe까지 수행합니다.

```powershell
az network nsg rule create --name deny-client-http --nsg-name $ServerNsgName --resource-group $ResourceGroupName --priority 200 --direction Inbound --access Deny --protocol Tcp --source-address-prefixes 10.70.1.0/24 --source-port-ranges "*" --destination-address-prefixes "$ServerIp/32" --destination-port-ranges 8080 --subscription $SubscriptionId --output table
az network nsg rule list --nsg-name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --output table
```

**관찰:** 200의 Deny가 65000의 기본 AllowVNetInBound보다 먼저 평가될 것으로 예상합니다. 기존 연결 유지 여부는 이 새 연결 실험과 구분합니다.

```powershell
$RunB = az vm run-command invoke --name $ClientVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ProbeScript --subscription $SubscriptionId --output json | ConvertFrom-Json
$EvidenceB = Read-ProbeEvidence $RunB
$EvidenceB | Format-List
if ($EvidenceB.outcome -ne "timeout") { throw "Expected a new connection timeout after the denial rule." }
```

probe의 명시적 timeout은 이 상태에서의 **기대된 차단 결과**입니다. A의 연결 성공을 먼저 확인하고 같은 경로의 B timeout을 비교합니다. `connection refused`, guest script/agent 실패·결과 누락은 별도 오류이므로 해당 원인을 확인합니다.


### 4.7 상태C — 더 높은 우선순위로 정확한 client만 허용


```powershell
az network nsg rule create --name allow-exact-client-http --nsg-name $ServerNsgName --resource-group $ResourceGroupName --priority 100 --direction Inbound --access Allow --protocol Tcp --source-address-prefixes "$ClientIp/32" --source-port-ranges "*" --destination-address-prefixes "$ServerIp/32" --destination-port-ranges 8080 --subscription $SubscriptionId --output table
az network nsg rule list --nsg-name $ServerNsgName --resource-group $ResourceGroupName --subscription $SubscriptionId --output table
```

**관찰:** Deny 200을 지운 것이 아니라, 정확한 client `/32`의 Allow 100이 먼저 적용되는 예입니다. 다른 client IP까지 허용했다고 주장하지 않습니다.

```powershell
$RunC = az vm run-command invoke --name $ClientVmName --resource-group $ResourceGroupName --command-id RunShellScript --scripts $ProbeScript --subscription $SubscriptionId --output json | ConvertFrom-Json
$EvidenceC = Read-ProbeEvidence $RunC
$EvidenceC | Format-List
if ($EvidenceC.outcome -ne "connected") { throw "Communication did not recover for the exact client." }
```

**통신 실습 완료 기준:** 같은 주소·포트·응답의 A 연결 성공 → B 새 연결 timeout → C 연결 성공입니다. server 상태·association·rule을 함께 확인합니다.


## 5. 대표 실패


| 관찰·실패 | 확인할 사항 |
|---|---|
| NSG 규칙은 있는데 효과가 없음 | 올바른 subnet/NIC association·실제 source/destination/port·우선순위 확인 |
| Allow인데 연결 실패 | route·NSG 양쪽·guest firewall·listener·DNS·상위 정책을 구분. route·양쪽 NSG·guest listener를 함께 확인 |
| Deny 이후에도 통신 유지 | 기존 stateful flow인지 확인하고 새 연결로 비교 |
| Run Command/guest agent 오류 | VM 상태·443 outbound·agent·권한 확인. 결과 없는 실행을 probe 성공으로 표시하지 않음 |
| 8080 refused | HTTP probe service·bind IP·포트 확인. NSG timeout과 구분 |
| 예상 JSON이 아닌 응답 | 다른 endpoint·잘못된 주소·probe 내용을 확인하고 중단 |
| VM SKU/image/quota 오류 | 승인된 x64 Gen2 후보·리전·quota·비용을 재검토. 임의로 권한/비용 확대 금지 |

기본 구성의 통과는 **설정·해석**, 선택 확장의 통과는 **실제 통신**입니다. ping 하나나 제어 영역 호출 성공으로 전체 네트워크를 검증했다고 쓰지 않습니다.


## 6. 정리 — 이 모듈의 전용 그룹만


읽기만 했다면 Azure 삭제 대상이 없습니다. 기본 구성은 network 그룹, 선택 확장은 같은 그룹의 probe VM·disk·NIC·public IP도 정리합니다. 다른 컴퓨트 그룹·공유 이미지·입력 공개키는 삭제하지 않습니다.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-net-$LabId" -or $Group.tags.Workshop -ne "azure-migration-networking" -or $Group.tags.LabId -ne $LabId) {
    throw "The group does not match this networking lab."
}
```

선택했던 범위와 실제 삭제 목록을 대조해 승인한 뒤 실행합니다. NIC/subnet NSG를 다른 트랙에 재사용하지 않았다는 전제를 확인합니다.

```powershell
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$ExistsAfter = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfter -ne "false") { throw "Networking cleanup is not verified." }
```

중간 실패 시 생성된 단계만 정리합니다. subscription 전체의 Network Watcher·기존 정책·다른 resource group을 자동 탐색하거나 삭제하지 않습니다. 실제 과금과 잔여 리소스는 통합 검증에서 확인합니다.


## 7. 실제 이전에서 추가로 고려할 사항


- 주소 중복·IP 계획·DNS·UDR·peering·온프레미스 연결.
- public/private endpoint·명시적 outbound·NAT·bandwidth/egress 비용.
- SG/NACL→NSG 변환의 의미 차이, 실제 flow·guest firewall·상위 admin policy.
- 앱/DB/스토리지별 연결 방향·포트·최소 source·identity와 네트워크의 별도 권한.
- HA·zone·flow log·운영 진단. 이 작은 VNet이 고객 네트워크 설계를 대체하지 않습니다.


## 8. 출처


- 고정 probe·명령은 직접 작성했습니다. 외부 샘플 파일·business app을 복사하거나 기존 공통 앱을 변경하지 않았습니다.
- 집중 검증 때 region·SKU·OS·CLI/Python 버전, A/B/C 실제 결과·오류·소요 시간·잔여 리소스를 기록합니다.
