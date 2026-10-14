# Storage — Blob 하나를 쓰고 다시 읽어 보기

[English](./README.md) | 한국어

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성합니다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인합니다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따릅니다. 인증과 network는 다른 통제입니다.


## 1. 학습 목표


- **대상:** S3의 bucket·object 개념을 아는 엔지니어.
- **예상 시간:** 45분 + 역할 전파 대기.
- **구성:** 온보딩 공통 개념과 작은 실습.
- **성공 기준:** 합성 파일 하나를 Entra 인증으로 업로드·다운로드하고 개수·바이트·SHA-256을 비교합니다.
- **의존성:** 승인된 private Blob 실행 경로·DNS·data identity가 필요합니다. 기존 입력을 쓰면 다른 컴퓨트 모듈·공통 앱·AWS 계정은 필요 없습니다. 없다면 [private 준비](../../../shared/storage-private-access/README-ko.md)의 강사 fixture 또는 읽기 모드를 선택합니다.

읽기만이면 리소스를 만들지 않습니다. 실제 데이터 작업은 **private 사용자 PowerShell(4.3~4.5)** 또는 **검사 VM Managed Identity(4.6)** 하나만 선택합니다. 후자는 4.3의 사용자 role 대신 fixture identity의 data role을 준비합니다.

이 실습은 Blob 사용 방법을 배우는 것이며 S3 → Blob 마이그레이션 실습이 아닙니다.

이전 도구·service job·copy 결과를 배우려면 [오브젝트 이전](../../migration/objects/README-ko.md)을 선택합니다. 그 모듈은 자체 최소 source/target 준비를 제공하므로 이 기초 실습을 완료할 필요는 없습니다.


### 선택 기준과 모듈 경계


| 항목 | 범위 |
|---|---|
| 선택할 때 | S3 경험을 바탕으로 Blob 구조·인증된 데이터 작업·내용 검증을 배우고 싶을 때 |
| 입력 | 작은 합성 파일·Azure 권한·승인된 private endpoint/DNS/클라이언트. 계정·container만 이 instruction에서 준비 |
| 결과 | 업로드한 1개 파일의 개수·바이트·내용 일치 확인 |
| 건너뛸 자료 | 공통 앱·모든 컴퓨트·Terraform·DB 이전. Identity 수강 완료도 필수 아님 |
| 제외 | S3 접근·실제 객체 이전·증분·컷오버는 이 기초 모듈의 결과가 아님 |
| 정리 소유권 | 이 모듈이 새로 만든 전용 그룹·Storage 계정·합성 파일만 정리 |


## 2. 서비스 소개와 선택 이유


| 서비스·기능 | Microsoft Learn 소개 | 이 instruction에서 볼 내용 |
|---|---|---|
| Azure Blob Storage | [Blob Storage 소개](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) | Storage account → container → blob |
| Azure Storage account | [Storage account 개요](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview) | 계정의 namespace, 리전과 복제 선택 |
| Microsoft Entra / Microsoft Entra ID | [Microsoft Entra 소개](https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra) | 로그인한 사용자의 identity |
| Azure RBAC | [Azure RBAC 소개](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview) | 계정 관리와 Blob 데이터 권한의 구분 |
| Azure Resource Manager | [Azure Resource Manager 소개](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) | 실습 전용 리소스 그룹과 정리 범위 |
| Private Endpoint / Private DNS | [Storage private endpoints](https://learn.microsoft.com/en-us/azure/storage/common/storage-private-endpoints), [Private DNS 개요](https://learn.microsoft.com/en-us/azure/dns/private-dns-overview) | public Disabled 상태의 실제 private 접근 |

| AWS S3 | Azure Blob Storage | 비교할 점 |
|---|---|---|
| Bucket | Container | Azure는 container 위에 Storage account가 있습니다. 권한·namespace 경계가 동일하지 않습니다. |
| Object key | Blob name | 이름에 `/`가 있어도 기본 Blob 계정에서 실제 디렉터리라고 가정하지 않습니다. |
| IAM 기반 접근 | Entra ID + Azure RBAC | 제어 영역 역할과 Blob 데이터 역할을 구분합니다. |
| Presigned URL | SAS | 제한된 URL 접근이라는 목적은 비슷하지만 발급·권한·취소 방식이 같지 않습니다. 이 실습은 SAS를 발급하지 않습니다. |

**선택 이유:** 승인된 private 클라이언트를 재사용해 앱 배포 없이 데이터 작업·인증·네트워크 격리를 관찰합니다. 새 검사 VM은 입력이 없을 때의 별도 선택 준비이며 VM + Docker 수강 단계가 아닙니다. 계정은 작은 Standard LRS로 제한합니다.


## 3. 사전 준비와 비용


- **실행 환경:** 관리 단계는 로컬 PowerShell 7.4 이상 + Azure CLI, 데이터 단계는 private 경로를 가진 PowerShell 클라이언트입니다. 별도 검증한 Linux 검사 VM 경로는 아래 4.6의 **VM Bash·Managed Identity**이며 로컬 PowerShell/WSL과 혼동하지 않습니다.
- 승인된 샌드박스 구독·리전. `Microsoft.Storage` provider 등록과 계정 생성 가능 여부를 강사가 확인합니다.
- 새 리소스 그룹·Storage account 생성/조회/삭제 권한이 필요합니다. 참가자에게 구독 전체 Contributor를 자동 부여하지 않습니다. 그룹 생성 권한이 없으면 강사가 아래 **새 전용 그룹 생성 단계**를 함께 수행하고 이후 그룹 범위 권한을 준비합니다.
- 역할 할당에는 별도의 `Microsoft.Authorization/roleAssignments/write` 권한이 필요합니다. Contributor만으로 할당할 수 없습니다. 승인된 범위의 Role Based Access Control Administrator 등 적절한 관리자가 아래 역할 할당 단계를 수행합니다.
- 데이터 실습에는 해당 **실습 계정 scope**의 Storage Blob Data Contributor가 필요합니다. 계정 전체 scope는 컨테이너 생성도 학습하기 위한 단순화이며 운영 앱은 필요한 container scope 등을 검토합니다.
- 사용자 로그인 실습입니다. 서비스 principal·Managed Identity 로그인으로 그대로 따라 하지 않습니다.
- 파일 하나라도 저장·요청·전송 비용이 발생할 수 있습니다. [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)에서 승인된 리전의 Blob Storage Standard LRS·소량 요청을 확인합니다. 작업 후 계정을 삭제합니다.
- 기본은 public network Disabled·firewall default Deny·bypass None과 Blob Private Endpoint입니다. 익명 공개·Shared Key 비활성화는 네트워크 격리를 대신하지 않습니다. 필요한 입력·권한·DNS·실행 위치·비용과 정리 owner는 [private 준비](../../../shared/storage-private-access/README-ko.md)를 따릅니다. public endpoint를 다시 켜서 오류를 해결하지 않습니다.


## 4. 단계별 실습


### 4.1 대상과 이름을 먼저 표시하기


4.1~4.3은 관리 PowerShell에서 수행합니다. 4.4~4.5는 확인한 변수와 실제 data identity를 준비한 **private PowerShell 실행 위치**에서 수행합니다. 같은 private 클라이언트가 두 권한을 갖고 있으면 같은 터미널을 쓸 수 있습니다. 전체 문서를 하나의 스크립트로 실행하지 않습니다.

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

**관찰할 결과:** 승인된 구독·테넌트·`Enabled` 상태인지 확인합니다. 계정 이름은 소문자·숫자만 사용하며 전역에서 유일해야 합니다. 랜덤 접미사도 유일성을 보장하지 않으므로 아래에서 가용성을 확인합니다.

**다음 단계 전에:** 예상 비용과 생성 대상을 확인합니다. 진행 승인이 없으면 만들지 않습니다.


### 4.2 새 실습 그룹과 Storage account 만들기 — 제어 영역


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

**관찰:** 생성 요청뿐 아니라 실제 network/auth 설정을 확인합니다. 계정 관리 성공은 Blob 읽기·쓰기 성공이 아닙니다. data 단계 전에 [private 준비](../../../shared/storage-private-access/README-ko.md)에서 이 계정의 `blob` 연결 Approved·DNS·private 클라이언트를 준비합니다.

**이유:** 기존 그룹을 재사용하지 않아 정리 범위를 제한합니다. LRS는 실습 비용·구성을 줄이는 선택이며 운영 복구·가용성 요구의 정답이 아닙니다. 그룹 생성 후 계정 생성이 실패해도 빈 그룹은 남을 수 있으므로 6절에서 확인합니다.


### 4.3 Blob 데이터 역할 준비하기 — 별도의 인가


참가자 터미널에서 identity와 계정 scope를 확인합니다. 출력은 관리자에게 안전한 경로로 전달하고 저장소에 넣지 않습니다.

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

**역할 할당 권한이 있는 관리자만**, 참가자 object ID·새 계정 scope·구독을 확인하고 실행합니다. 관리자 터미널이 다르면 세 변수를 확인한 실제 값으로 설정해야 합니다. 계정을 만든 사용자와 역할을 받는 참가자를 혼동하지 않습니다.

```powershell
az role assignment create --assignee-object-id $PrincipalId --assignee-principal-type User --role "Storage Blob Data Contributor" --scope $StorageAccountId --subscription $SubscriptionId --query "{principal:principalId,scope:scope,role:roleDefinitionId}" --output json
```

**관찰:** 할당 출력의 `principal`과 `scope`가 승인된 참가자·실습 계정입니다. 역할 할당이 됐어도 전파 지연으로 데이터 명령이 바로 성공하지 않을 수 있습니다. 몇 분 대기 후 다음 단계를 수동 재시도합니다. 계속 실패하면 scope·identity·정책을 확인하며 Owner나 계정 키로 우회하지 않습니다.

권한 분리 설명: [Azure CLI 데이터 인증 방식](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-data-operations-cli).


### 4.4 Container 생성과 합성 파일 업로드 — 데이터 영역


이후는 **private 경로가 있는 참가자 PowerShell**에서 수행합니다. 원래 Blob hostname이 승인 private IP로 해석되는지 먼저 확인합니다. `--auth-mode login`은 이 실행 위치의 참가자 Entra identity를 사용하며 네트워크 연결을 대신하지 않습니다.

```powershell
az storage container create --account-name $StorageAccountName --name $ContainerName --auth-mode login --subscription $SubscriptionId --output json
$LabDirectory = Join-Path ([System.IO.Path]::GetTempPath()) "azure-migration-storage-$LabId"
New-Item -ItemType Directory -Path $LabDirectory -ErrorAction Stop | Out-Null
$SourceFile = Join-Path $LabDirectory "hello.txt"
$DownloadedFile = Join-Path $LabDirectory "downloaded-hello.txt"
Set-Content -LiteralPath $SourceFile -Value "Hello Azure workshop" -Encoding utf8NoBOM -NoNewline
az storage blob upload --account-name $StorageAccountName --container-name $ContainerName --name $BlobName --file $SourceFile --type block --content-type text/plain --overwrite false --auth-mode login --subscription $SubscriptionId --output json
```

**관찰:** 새 container는 `created: true`이며 업로드 응답이 반환됩니다. 합성 파일은 UTF-8 BOM·개행 없는 20바이트입니다. 업로드 성공 여부는 다음 단계에서 열거·다운로드로 다시 확인합니다.

`--overwrite false`는 같은 이름의 Blob을 덮어쓰지 않기 위한 선택입니다. 반복 실행 중 기존 데이터가 발견되면 멈추고 대상을 확인합니다. `--overwrite true`로 바꿔 오류를 없애지 않습니다.


### 4.5 다운로드 후 개수·바이트·내용 비교하기


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

**성공 기준:** `Count: 1`, `Bytes: 20`, `ContentMatch: True`입니다. 로컬 내용 비교 없이 HTTP/CLI 성공 응답만으로 완료하지 않습니다.


### 4.6 선택 경로 — 검사 VM의 Managed Identity


기존 private PowerShell 입력이 없을 때 강사가 [private fixture](../../../shared/storage-private-access/README-ko.md)를 승인받아 제공할 수 있습니다. VM identity의 Blob data 역할과 endpoint/DNS를 먼저 확인합니다. 사람의 login cache·비밀을 VM에 복사하지 않습니다.

[검증 script](./verify/verify-private.sh)는 **VM Bash**의 `az login --identity`와 원래 CLI upload/list/download를 사용합니다. 원본 20 bytes·개수·SHA-256을 확인하며 실패는 `AMW_STORAGE_VERIFY_FAIL`, 모든 계약이 통과한 마지막 줄은 `AMW_STORAGE_VERIFY_PASS`입니다.

관리 PowerShell에서 해당 script를 Run Command로 보낼 때 입력은 계정 이름·승인 endpoint IP·fixture 작업 폴더입니다. 이미 승인된 실제 값을 사용합니다.

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

첫 실행은 새 `sample` container·새 합성 파일을 요구합니다. 보존한 Blob을 다시 읽기 검증할 때만 위 parameters에 `phase=verify-existing-blob`을 추가합니다. 이때 새 업로드/덮어쓰기는 하지 않고 새로운 로컬 비교 폴더에 내려받습니다. Run Command의 외부 성공만으로 guest 결과를 accept하지 않습니다.


## 5. 검증과 대표 실패


| 실패·결과 | 확인·해결 |
|---|---|
| `AuthorizationFailed`로 계정 생성 불가 | 제어 영역 권한과 scope를 확인합니다. Blob 데이터 역할은 계정 생성 권한의 대체재가 아닙니다. |
| `AuthorizationPermissionMismatch`로 Blob 접근 불가 | 실제 로그인 사용자, 데이터 역할·scope, 전파 대기를 확인합니다. 관리자가 로그인한 터미널과 참가자 터미널을 구분합니다. |
| `az ad signed-in-user show` 실패 | 사용자 로그인인지와 Graph 조회 정책을 확인합니다. 관리자가 해당 테넌트의 참가자 object ID를 확인한 뒤 변수에 명시적으로 설정합니다. 실패를 빈 ID로 넘기지 않습니다. |
| 네트워크 차단 또는 정책 위반 | Storage 네트워크·테넌트 정책을 강사와 확인합니다. 정책을 끄거나 공유 키를 켜지 않습니다. |
| 계정 이름 사용 불가 | 생성 전 새 실습 접미사를 선택합니다. 기존 계정에 연결하지 않습니다. |
| container `created: false` 또는 Blob 존재 오류 | 반복 실행 여부와 대상을 확인합니다. 기대한 새 환경이 아니므로 그대로 완료하지 않습니다. |
| 개수·바이트·해시 불일치 | 로컬 파일 내용·인코딩, 업로드 이름·계정·container를 확인합니다. 불일치를 성공으로 기록하지 않습니다. |

**확인 항목:** 계정 관리와 데이터 요청의 권한·연결 차이를 설명합니다. RBAC·익명 접근·private DNS·public network가 각각 통제하는 범위를 정리합니다.


## 6. 정리 — 반드시 대상 확인 후 실행


이 모듈이 만든 리소스를 다른 모듈에서 아직 사용 중이면 삭제를 보류하고 정리 책임·기한을 기록합니다.


### 6.1 리소스와 실습 태그 확인


**실행 환경: 참가자 또는 승인된 삭제 담당자의 로컬 PowerShell.** 동일 실습의 변수 값을 사용합니다. 터미널을 닫았다면 이름·구독·LabId를 기록한 값으로 복구하며 운영 리소스를 자동 탐색하지 않습니다.

```powershell
az account show --subscription $SubscriptionId --query "{name:name,id:id}" --output table
$Group = az group show --name $ResourceGroupName --subscription $SubscriptionId --output json | ConvertFrom-Json
$Group | Select-Object name, location, tags | Format-List
az resource list --resource-group $ResourceGroupName --subscription $SubscriptionId --query "[].{name:name,type:type,id:id}" --output table
if ($ResourceGroupName -ne "rg-amw-storage-$LabId" -or $Group.tags.Workshop -ne "azure-migration-storage" -or $Group.tags.LabId -ne $LabId) {
    throw "The group does not match this storage lab. Do not delete it."
}
```

**확인:** 생성한 Storage account와 이 실습만을 위한 리소스 그룹인지 확인합니다. 태그만으로 소유권을 보장하지 못하므로 목록에 다른 용도의 리소스가 있으면 중단합니다.


### 6.2 그룹 삭제와 결과 확인


아래 명령은 그룹 안의 모든 리소스와 데이터를 삭제합니다. 앞의 목록을 확인한 경우에만 실행하고 CLI의 확인 요청에도 대상을 대조한 뒤 응답합니다. 확인을 건너뛰는 `--yes`는 사용하지 않습니다.

```powershell
az group delete --name $ResourceGroupName --subscription $SubscriptionId
$GroupExistsAfterCleanup = az group exists --name $ResourceGroupName --subscription $SubscriptionId --output tsv
if ($GroupExistsAfterCleanup -ne "false") {
    throw "The lab group still exists or deletion could not be verified."
}
Write-Output "The storage lab resource group no longer exists."
```

계정과 그 안의 Blob 데이터가 삭제되며 해당 계정 scope의 역할 할당도 정리 대상입니다. 상위 scope의 기존 역할을 삭제하지 않습니다. 삭제 실패나 잠금이 있으면 승인된 관리자에게 문의하고 남은 대상을 기록합니다.

로컬에는 합성 파일만 생성했습니다. 4.4~4.5를 완료한 경우 아래 **정확한 두 파일**을 삭제하고 빈 폴더를 제거합니다. 중간 실패로 파일 하나가 없다면 존재하는 파일만 개별 삭제합니다.

```powershell
$SourceFile
$DownloadedFile
Remove-Item -LiteralPath $SourceFile
Remove-Item -LiteralPath $DownloadedFile
Remove-Item -LiteralPath $LabDirectory
```

그룹 삭제 확인은 해당 그룹의 정리를 의미합니다. 별도로 만든 리소스나 이미 발생한 사용료를 지우는 것은 아닙니다. 구독의 비용 화면은 반영 지연을 고려해 강사와 다시 확인합니다.


## 7. 실제 이전에서 추가로 고려할 사항


- S3 소스 권한, 네트워크 대역폭과 AWS egress 비용.
- 객체 수·용량뿐 아니라 메타데이터, 버전, 접근 정책, 파일 이름 처리.
- S3 ETag를 항상 MD5로 가정하지 않기. 이 실습은 다운로드 바이트의 SHA-256만 비교합니다.
- 증분 변경, 최종 쓰기 중지, 데이터 일관성, 컷오버·롤백 기준.
- LRS 이외의 복제·복구 요구, 최소 권한·네트워크 경계, 운영 모니터링.
- 작은 파일 하나의 검증은 프로덕션 이전 완전성이나 대규모 성능 검증이 아닙니다.


## 8. 출처


- 서비스 개념: 2절의 Microsoft Learn 소개 링크.
- 절차 참고: [Azure CLI Blob quickstart](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-cli), [Azure CLI 데이터 인증 방식](https://learn.microsoft.com/en-us/azure/storage/blobs/authorize-data-operations-cli).
- 외부 저장소 파일을 복사하지 않고 교육용 명령을 직접 구성했습니다. 기존 quickstart의 개념을 참고해 PowerShell·로그인 인증·덮어쓰기 방지·내용 검증·대상 확인을 명시했습니다.
