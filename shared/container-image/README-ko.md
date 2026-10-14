# 공통 준비 — 앱 이미지만 준비하기

[English](./README.md) | 한국어


VM + Docker·Container Apps·AKS·Terraform 선택 배포가 재사용하는 준비 instruction입니다. **어떤 앱·VM·클러스터도 배포하지 않습니다.** 승인된 이미지가 이미 있으면 이 자료를 건너뛰고 해당 컴퓨트 모듈의 입력으로 사용합니다.


## 1. 선택 기준·입력·결과


- 대상: 공통 앱의 HTTP 계약을 이해하는 참가자, 예상 30~40분 + 빌드·역할 전파 대기.
- 입력: 저장소의 `sample-app`, 승인된 Azure 구독·리전·권한.
- 결과: ACR에 빌드된 동일 앱의 digest와 registry 정보. Container Apps/현재 Terraform 타깃을 선택한 경우에만 pull identity도 준비합니다.
- 제외: Container Apps environment·앱, AKS·Pod, VM·DB·Storage는 만들지 않습니다.

| 소비 경로 | 필요한 결과 | 실행할 준비 범위 |
|---|---|---|
| Container Apps CLI / 현재 Azure Terraform | `ContainerImage`, `RegistryServer`, `PullIdentityId` | 4.1~4.3 |
| AKS | `ContainerImage`, `RegistryServer`, `RegistryId` | 4.1~4.2만. AKS kubelet의 pull 권한은 AKS 모듈에서 부여 |
| VM + Docker | `ContainerImage`, `RegistryServer`, `RegistryId` | 4.1~4.2만. VM system-assigned identity의 pull 권한은 VM 모듈에서 부여 |

VM system-assigned identity·AKS kubelet identity·Container Apps user-assigned identity는 같은 이름만 바꾼 동일 권한 모델이 아닙니다. VM/AKS만 선택하면 4.3을 생략합니다.


## 2. 서비스 소개와 선택 이유


| 서비스·기능 | Microsoft Learn 소개 | 이 준비에서 볼 내용 |
|---|---|---|
| Azure Container Registry | [ACR 소개](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro) | 같은 이미지·digest 보관 |
| ACR Tasks | [ACR Tasks 개요](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tasks-overview) | 로컬 Docker 없이 클라우드 빌드 |
| Managed Identity | [Managed Identity 개요](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview) | 선택 소비자의 암호 없는 pull |
| Azure RBAC | [Azure RBAC 개요](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview) | registry scope의 데이터 권한 |
| Resource Manager | [Resource Manager 개요](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) | 이미지 준비 전용 그룹과 소유권 |

AWS registry·계정은 필요하지 않습니다. AWS/Azure SDK 없는 [공통 앱](../../sample-app/README-ko.md)을 같은 Dockerfile로 빌드합니다. 태그가 아닌 digest를 입력으로 넘겨 같은 이미지인지 확인합니다.


## 3. 사전 준비·권한·비용


- **실행 환경:** 로컬 PowerShell 7.4 이상 + Azure CLI, 저장소 루트. 앱의 WSL Bash 명령과 섞지 않습니다.
- `Microsoft.ContainerRegistry`, 선택 identity의 `Microsoft.ManagedIdentity` provider 등록·리전 지원·quota를 강사가 확인합니다.
- 새 그룹·ACR·빌드·조회·삭제 권한이 필요합니다. 4.3 역할 할당은 별도의 `roleAssignments/write` 권한이 있는 승인된 관리자가 수행합니다.
- 비용 대상은 **ACR Basic·빌드·이미지 저장/전송**입니다. 앱을 안 만들어도 registry 비용이 발생합니다. [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)로 승인 한도를 확인합니다.
- 고객의 승인된 이미지·패키지 공급망을 사용합니다. 사내 feed·토큰·비밀을 build context나 Dockerfile·명령 출력에 넣지 않습니다.
- ACR은 `rbac` mode로 준비합니다. ABAC registry의 다른 권한 모델은 기본 실습에서 다루지 않습니다.


## 4. 단계별 준비 — PowerShell


### 4.1 대상과 새 준비 그룹 확인


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

**관찰:** 승인된 구독·테넌트·`Enabled` 상태와 생성 대상입니다. 비용·대상을 확인하고 승인된 경우에만 다음 단계로 진행합니다.


### 4.2 Registry와 동일 앱 이미지 준비 — 게시 경로 하나 선택


```powershell
az group create --name $ImageGroupName --location $Location --subscription $SubscriptionId --tags Workshop=azure-migration-image LabId=$ImageLabId --output table
az acr create --name $RegistryName --resource-group $ImageGroupName --location $Location --sku Basic --admin-enabled false --role-assignment-mode rbac --subscription $SubscriptionId --output table
$RegistryServer = az acr show --name $RegistryName --subscription $SubscriptionId --query loginServer --output tsv
$RegistryId = az acr show --name $RegistryName --subscription $SubscriptionId --query id --output tsv
if ([string]::IsNullOrWhiteSpace($RegistryServer) -or [string]::IsNullOrWhiteSpace($RegistryId)) {
    throw "Registry information was not returned."
}
```

**A: ACR Tasks cloud build.** cloud builder에서 사용할 패키지/이미지 source와 build 권한·비용을 승인한 경우에만 선택합니다. 로컬 WSL의 패키지 정책 예외를 cloud build에 자동 적용하지 않습니다. A는 cloud builder 공급망·비용을 별도로 승인한 경우에 선택합니다.

```powershell
az acr build --registry $RegistryName --image workshop/app:0.1.0 --platform linux/amd64 --subscription $SubscriptionId .\sample-app
```

**B: 이미 검증한 WSL Docker image 게시.** 승인된 local image가 있을 때 선택합니다. 관리 Azure CLI는 PowerShell, Docker는 승인된 WSL distro에서 실행합니다. tag를 새 registry로 지정할 뿐 business app이나 새 copy/build engine을 만들지 않습니다.

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

token은 변수·stdin으로만 전달하며 argv/로그/공유 화면에 출력하지 않습니다. `--expose-token` 필드의 credential은 Docker가 교환해 사용하는 ACR refresh token이며 registry REST API의 직접 bearer token이라고 설명하지 않습니다. 임시 config만 지우고 기존 개인 Docker login/config는 건드리지 않습니다.

A 또는 B가 성공한 뒤 같은 digest 입력을 확인합니다.

```powershell
$Digest = az acr repository show --name $RegistryName --image workshop/app:0.1.0 --subscription $SubscriptionId --query digest --output tsv
if ([string]::IsNullOrWhiteSpace($RegistryServer) -or [string]::IsNullOrWhiteSpace($RegistryId) -or
    $Digest -notmatch "^sha256:[a-f0-9]{64}$") {
    throw "Registry information or image digest was not returned."
}
$ContainerImage = "$RegistryServer/workshop/app@$Digest"
[pscustomobject]@{ Image = $ContainerImage; RegistryServer = $RegistryServer; RegistryId = $RegistryId } | Format-List
```

**관찰:** 선택한 build 또는 publish 결과와 digest입니다. `.dockerignore`의 allowlist는 앱·manifest·lock·Dockerfile만 포함합니다. 그룹 생성 뒤 실패했다면 준비 그룹은 남을 수 있으므로 6절에서 확인합니다.

**VM/AKS만 선택했다면 여기서 완료합니다.** 위 3개 결과를 선택 instruction에 입력하고 4.3 identity는 만들지 않습니다. VM identity/AKS kubelet에 권한을 부여해야 하며 다른 서비스용 identity를 만들었다고 자동 인증하는 것이 아닙니다.


### 4.3 선택: Container Apps/Terraform용 pull identity


```powershell
$Identity = az identity create --name $IdentityName --resource-group $ImageGroupName --location $Location --subscription $SubscriptionId --output json | ConvertFrom-Json
$PullIdentityId = $Identity.id
$PullPrincipalId = $Identity.principalId
if (-not $PullIdentityId -or -not $PullPrincipalId) { throw "Identity IDs were not returned." }
[pscustomobject]@{ Principal = $PullPrincipalId; RegistryScope = $RegistryId } | Format-List
```

승인된 관리자가 identity principal·registry scope·구독을 확인한 뒤 실행합니다. 다른 터미널이면 확인한 변수 값을 설정합니다.

```powershell
az role assignment create --assignee-object-id $PullPrincipalId --assignee-principal-type ServicePrincipal --role AcrPull --scope $RegistryId --subscription $SubscriptionId --output table
az acr config authentication-as-arm show --registry $RegistryName --subscription $SubscriptionId
```

**관찰:** 새 identity의 registry scope 역할과 ARM audience 인증 `enabled`입니다. disabled면 관리자가 해당 registry의 정책을 검토합니다. admin 암호나 정책 변경으로 자동 우회하지 않습니다. 역할 전파 후 소비 모듈로 이동합니다.


## 5. 검증·소비 모듈로 전달


- 이미지가 `workshop/app@sha256:...`인지 확인합니다. 태그만 같다는 것으로 동일 이미지를 보장하지 않습니다.
- 각 모듈은 자기 입력을 검증합니다. 여기의 build 성공은 앱 실행·image pull 성공이 아닙니다.
- 다른 터미널에서는 해당 모듈의 입력 변수에 확인한 값을 넣습니다. 토큰·registry 암호를 전달하지 않습니다.
- 준비 그룹의 이름·LabId와 소비 중인 모듈을 로컬 실습 기록에 보관합니다. 실습 출력은 `lab-output` 등 Git 제외 경로만 사용합니다.
- 대표 실패: build 권한/쿼터, base image·package 다운로드 차단, registry 이름 중복, 역할 전파 지연. 원인을 확인하고 해당 단계만 수동 재시도합니다.


## 6. 정리 — 마지막 소비자가 끝난 다음


소유권은 **이 준비 자료가 만든 이미지 그룹**에 있습니다. VM·Container Apps·AKS·Terraform 소비자는 자기 VM·앱·클러스터·타깃만 정리하고 입력 registry를 삭제하지 않습니다. VM/AKS가 registry scope에 추가한 identity 역할도 해당 소비자 정리에서 먼저 제거합니다.

모든 소비자가 종료했는지 확인하고, 이 자료에서 **새로 만든 준비 그룹만** 삭제합니다. 외부의 기존 승인 입력을 사용했다면 이 삭제 명령의 대상이 아닙니다.

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

목록이 이미지 준비 리소스뿐인지 확인하고 CLI의 삭제 확인에 응답합니다. 상위 scope의 기존 역할이나 다른 그룹은 삭제하지 않습니다. 삭제 결과와 비용 반영 지연도 확인합니다.


## 7. 실제 이전 고려사항


- 조직의 이미지·패키지 소스, 서명·취약점 검사·라이선스, 재빌드 정책.
- registry의 RBAC/ABAC mode·네트워크·private endpoint, pull 대상 identity.
- 이미지 플랫폼, digest 배포와 base image 갱신. 같은 앱 이미지라도 클라우드 설정의 동등성을 보장하지 않습니다.


## 8. 출처


- 소개 문서는 2절, [Managed Identity image pull](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull) 참고.
- 코드·명령은 직접 작성했고 외부 저장소 파일을 복사하지 않았습니다.
