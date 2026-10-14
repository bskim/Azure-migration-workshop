# 공통 준비 — Blob의 private 실행 경로

[English](./README.md) | 한국어

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성합니다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인합니다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따릅니다. 인증과 network는 다른 통제입니다.


[Blob 기초](../../modules/onboarding/storage/README-ko.md)와 [AzCopy 오브젝트 이전](../../modules/migration/objects/README-ko.md)에서 재사용하는 네트워크 입력을 안내합니다. 필요한 private client·DNS·endpoint만 준비합니다.


## 1. 선택과 최소 입력


| 선택 | 필요한 입력 | 실행 범위 |
|---|---|---|
| 개념·walkthrough | 아래 Learn 소개와 네트워크/권한 비교 | 클라우드 생성·데이터 작업 없음 |
| 기존 private 환경 사용 | 승인된 계정/Blob endpoint·DNS·private 클라이언트·실제 data identity | 입력을 확인하고 선택 모듈만 실행 |
| 강사의 임시 검사 환경 | 승인된 계정 resource ID·리전·비용·network/VM/role 권한 | 아래 작은 fixture만 준비. VM + Docker 트랙과 다른 목적 |

네트워크 입력이 없으면 읽기·강사 제공 환경으로 진행합니다. 개인 WSL이나 일반 Cloud Shell이 Azure VNet에 자동으로 연결된다고 가정하지 않습니다. Portal에서 계정 관리가 된다는 사실도 브라우저의 Blob 데이터 접근 가능성을 증명하지 않습니다.

기본 설정은 **public network Disabled, public firewall default Deny, bypass None, 익명 Blob 접근 금지, Shared Key 비활성화, HTTPS/TLS, Entra/RBAC**입니다. 각각 별개의 통제이며 Private Endpoint 생성만으로 public endpoint가 자동 차단되는 것은 아닙니다. 서비스 endpoint·IP firewall로 제한한 public 접근은 별도 승인 경로이지 private-only 정책의 대체가 아닙니다.


public network Disabled여도 기존 resource-instance/trusted-service 예외가 유지될 수 있으므로 [Storage network 제한](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-limitations)을 읽습니다. [Resource-instance rule](https://learn.microsoft.com/en-us/azure/storage/common/storage-network-security-resource-instances)은 **public endpoint network 접근**이며 data 권한이나 **Private Endpoint가 아닙니다.** 제공 샘플은 bypass None/resourceAccessRules 빈 설정을 사용합니다. 예외 추가는 승인되지 않았고 private 준수 해결책으로 제안하지 않습니다.

## 2. 서비스 소개와 역할


| 서비스/기능 | Microsoft Learn 소개 | 이 준비에서 맡기는 일 |
|---|---|---|
| Private Endpoint / Private Link | [Private Endpoint 개요](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview), [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints) | `blob` subresource를 VNet private IP로 접근 |
| Virtual Network | [VNet 개요](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview) | 실행 위치와 endpoint의 연결 |
| Private DNS | [Private DNS 개요](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview) | 원래 Blob hostname을 private IP로 해석 |
| Managed Identity / RBAC | [Managed Identity 개요](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview), [RBAC 개요](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview) | 비밀 없는 검사 identity와 data 역할 |
| 검사 VM / Run Command | [Linux VM 개요](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/overview), [Run Command](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command) | SSH inbound 없이 클라이언트를 실행·관찰 |
| 선택 NAT Gateway | [NAT Gateway 개요](https://learn.microsoft.com/en-us/azure/nat-gateway/nat-overview) | 필요한 공식 도구 설치에 명시적 outbound 제공 |


## 3. 기존 입력을 우선 재사용


강사/관리자는 계정 resource ID·owner, 해당 `blob` Private Endpoint 연결의 **Approved**, DNS zone/link, 실행 위치의 route와 NSG, 실제 data identity를 확인합니다. 그 입력이 이미 제공되면 새 VM·VNet·endpoint를 중복 생성하지 않습니다.

- 클라이언트는 `<account>.blob.core.windows.net`을 그대로 사용합니다. `privatelink` subdomain URL이나 IP 주소로 바꾸지 않습니다.
- **실제 실행 위치에서** DNS가 해당 승인 private IP로 해석되고 TCP 443·TLS·Entra data 요청이 통과하는지 확인합니다.
- Storage public Disabled 상태도 별도로 읽습니다. DNS/TCP 성공이나 role assignment 출력만으로 Blob 검증을 완료하지 않습니다.
- 두 계정의 copy는 양쪽 접근과 [공식 restricted-network topology](https://learn.microsoft.com/en-us/troubleshoot/azure/azure-storage/blobs/connectivity/copy-blobs-between-storage-accounts-network-restriction)를 함께 확인합니다. hub VNet 클라이언트와 서로 다른 spoke의 endpoint만으로는 `CannotVerifyCopySource`가 생길 수 있습니다.
- Storage Mover의 endpoint identity·job 지원은 그 서비스의 현재 흐름을 따릅니다. AzCopy에서 확인한 topology를 그대로 지원한다고 간주하지 않습니다.


## 4. 기존 입력이 없을 때의 작은 강사 fixture


기존 private 입력이 없을 때만 강사가 별도 범위·비용·권한 승인을 받아 최소 fixture를 제공합니다.

1. 기존 계정은 원 owner에 두고 전용 group/VNet·client/endpoint subnet을 준비합니다.
2. 선택 계정의 blob Private Endpoint·DNS zone/link·Approved 연결을 준비합니다.
3. 필요한 경우에만 public NIC IP·SSH inbound 없는 작은 x64 Linux 검사 VM과 명시적 outbound를 준비합니다.
4. actual canonical DNS/private IP/TLS/route·실행 위치의 MI data 역할을 확인합니다.
5. source 합성 준비용 새 Contributor grant는 기록해 준비 후 정확히 회수하고 copy에는 Reader/target Contributor만 사용합니다.

VM/disk/NAT/IP/PE/DNS·설치·diagnostic의 세부 조건은 [강사 fixture 가이드](../../guides/instructor-guide-ko.md)를 따릅니다. Blob 독자에게 다른 compute·DB 수강을 요구하지 않고 public access/정책/TLS를 낮춰 연결하지 않습니다.

## 5. 데이터 실행과 결과를 읽기


- private PowerShell 클라이언트가 있으면 모듈의 사용자 Entra CLI 흐름을 사용합니다. 로컬 관리 터미널에서 실행 위치만 바뀌었다고 identity가 자동 공유된다고 가정하지 않습니다.
- 이 Linux VM 흐름은 **VM Bash·Managed Identity**입니다. `az login --identity --allow-no-subscriptions`와 명시적 계정 이름을 사용하며 사람의 로그인 cache/비밀을 VM에 복사하지 않습니다.
- Blob 기초 [검증 script](../../modules/onboarding/storage/verify/verify-private.sh)는 원래 CLI의 upload/list/download와 20 bytes/SHA-256 계약을 확인합니다.
- AzCopy [준비 script](../../modules/migration/objects/verify/prepare-private.sh)는 작은 합성 원본을 source에만 준비하고 빈 target을 확인합니다. [copy/검증 script](../../modules/migration/objects/verify/verify-private.sh)의 복사는 공식 AzCopy이며 Python은 JSON 결과·짧은 hash 비교에만 사용합니다.
- Run Command의 `Enable succeeded`를 읽은 뒤 guest 실행 결과를 확인합니다. guest 오류/traceback·script의 마지막 성공 marker·실제 수치와 job/data 결과를 함께 점검합니다. 출력은 마지막 4,096 bytes로 제한되므로 전체 job/진단 파일은 보호된 작업 폴더에 보관합니다.
- source 원본 base64를 전달할 때 `name=value` parameter를 명시합니다. padding `=`를 bare parameter로 전달하면 CLI가 이름/값으로 오해할 수 있습니다. 합성 파일만 이 방식으로 전달하고 비밀·실제 고객 데이터는 넣지 않습니다.


## 6. 비용·소유권·정리


이 공개 retail 기준의 주요 비용은 Linux VM USD 0.026/시간, Standard NAT USD 0.045/시간, Standard Private Endpoint USD 0.01/개·시간, NAT IP USD 0.005/시간입니다. endpoint 3개면 합계 약 USD 0.106/시간이며 디스크·DNS·처리/전송량은 별도입니다. [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)와 현재 SKU/리전 가격을 다시 확인합니다. budget은 자동 과금 차단이 아닙니다.

| owner | 소유/삭제 대상 | 삭제하면 안 되는 입력 |
|---|---|---|
| Storage/Objects 모듈 | 자기 계정·container·합성 데이터·자기 grant | 외부 계정, 다른 모듈의 fixture |
| private fixture | 새 VM/MI·NIC/디스크·VNet/NSG·NAT/IP·endpoint/DNS와 그 identity에 추가한 정확한 grants | 소비한 기존 Storage 계정·source/target 데이터·앱/ACR |

데이터 모듈이 사용하는 동안 fixture를 삭제하지 않습니다. 정리 승인 후 VM identity의 계정 밖 grant를 먼저 제거하고 fixture 소유 리소스를 정리합니다. 기존 상위 role·기존 private client/DNS는 건드리지 않습니다. Private Endpoint 삭제와 입력 계정 삭제는 다르며 계정이 계속 Disabled라면 다음 접근 경로도 별도로 마련해야 합니다.
