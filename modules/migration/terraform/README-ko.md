# Terraform — AWS 예제를 읽고 Azure 실행 방식으로 재작성하기

[English](./README.md) | 한국어


## 1. 학습 목표


- 대상: Terraform resource·variable·output을 읽을 수 있는 엔지니어, 예상 80분.
- 구성: 선택 이전 접근법 모듈. **AWS 계정·자격증명·리소스는 만들지 않는다.**
- 목표: AWS IaC와 공통 앱 코드에서 실행 요구를 찾아 Azure 서비스 선택과 검증 기준을 설명한다.
- 결과물: 서비스 매핑표, 별도의 Azure Terraform, 정적 검증 결과. AWS 실제 이전 성공을 주장하지 않는다.
- 의존성: 정적 분석은 이 폴더의 샘플과 [앱 코드](../../../sample-app/app.py)만 필요하다. 선택 Azure 배포는 준비된 이미지·registry·pull identity를 입력받는다. 입력이 없을 때만 [공통 이미지 준비](../../../shared/container-image/README-ko.md)의 4.1~4.3을 사용하며 다른 컴퓨트 모듈은 완료하지 않는다.


### 선택 기준과 모듈 경계


| 선택 범위 | 입력 | 결과·완료 기준 | 필요 없는 선행 단계 |
|---|---|---|---|
| 4.1~4.3 소스 분석 | 포함된 AWS IaC·앱 소스 | 실행 요구·서비스 매핑·동등하지 않은 부분 설명 | 앱 실행·패키지 설치·Azure/AWS 로그인·컴퓨트 |
| 4.4 정적 검증 | Terraform·provider/module 다운로드 | 두 구성의 `fmt/init/validate` 결과 | 앱 서버·Docker·Azure/AWS 로그인·리소스 |
| 4.5 선택 Azure 배포 | 승인된 이미지·registry·pull identity·Azure 권한 | 별도 타깃 앱의 HTTP 계약과 정리 | Container Apps CLI 앱 배포·Identity/Storage 전체 실습 |

80분은 instruction의 기본 예상 시간이다. 분석만 원하면 4.3에서, 정적 검증만 원하면 4.4에서 완료하고 유료 실행은 생략한다. 현재 Azure 예제는 Container Apps 한 경로이며 VM·AKS·DB의 범용 변환 결과가 아니다.


## 2. 서비스 소개와 이전 방식 선택


| Azure 타깃·기능 | Microsoft Learn 소개 | 이 예제의 선택 |
|---|---|---|
| Container Apps | [Container Apps 개요](https://learn.microsoft.com/en-us/azure/container-apps/overview) | 공통 HTTP 앱의 재배포 |
| Container Registry | [ACR 소개](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-intro) | 미리 빌드한 같은 이미지 |
| Managed Identity | [Managed Identity 개요](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview) | ACR의 이미지 pull identity |
| Resource Manager | [Resource Manager 개요](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) | Azure resource group과 lifecycle |
| Azure Virtual Machines | [Azure VM 개요](https://learn.microsoft.com/en-us/azure/virtual-machines/overview) | OS 제어가 필요할 때 비교할 대안, 이 실습의 생성 범위에서 제외 |
| Azure Virtual Network | [VNet 개요](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview) | 네트워크 요구 비교, 이 타깃은 custom VNet을 생성하지 않음 |

“EC2는 VM이므로 Azure VM만 가능하다”가 아니다. 앱이 HTTP·컨테이너·외부 OS 의존성 없는 구조인지 읽고 Container Apps를 선택했다. EC2→VM처럼 서버를 유지하는 이전과 Container Apps 재배포의 차이를 설명한다.


## 3. 사전 준비


- **Terraform 명령 환경:** 로컬 PowerShell 7.4 이상, 현재 디렉터리는 이 instruction 폴더.
- Terraform 1.11 이상 2 미만. 이 예제는 Terraform 1.16.5로 정적 검증했다.
- `init`은 provider·module을 다운로드하지만 클라우드 리소스를 만들지 않는다. 조직의 외부 다운로드 정책을 확인한다.
- AWS provider 6.68.0, AzureRM 5.9.0, Container App AVM 0.9.0을 고정하고 provider 선택은 각 `.terraform.lock.hcl`에 기록한다.
- AWS에서는 `plan`·`apply`·AMI 조회를 실행하지 않는다. AMI·image·client CIDR는 문서용 값이다.
- Azure 정적 검증에는 로그인·리전·권한·과금이 필요하지 않다. 선택 배포에는 새 타깃 그룹 권한, 기존 identity의 연결 권한, region·provider 등록·쿼터·비용 승인이 필요하다.


## 4. 작은 단계별 실습


### 4.1 AWS 소스 읽기


소스: [main.tf](./lab/aws/main.tf), [variables.tf](./lab/aws/variables.tf), [outputs.tf](./lab/aws/outputs.tf).

```text
VPC → public subnet → route / Internet Gateway
                   → Security Group: client CIDR의 TCP 8080
                   → EC2: Docker로 공통 이미지 실행
```

**읽을 질문:**

1. `user_data`가 앱 소스를 구현하는가, 컨테이너 실행 환경만 준비하는가?
2. `-p 8080:8080`과 [Dockerfile](../../../sample-app/Dockerfile)의 listen 포트가 일치하는가?
3. ingress의 `192.0.2.1/32`는 문서용 주소이며 실제 참가자 IP가 아닌가?
4. AMI·이미지가 자리표시자인 구성에서 validate가 확인하는 구조와 실제 배포 준비는 어떻게 다른가?

출구 `0.0.0.0/0`은 Docker 설치·이미지 pull을 설명하기 위한 단순화다. 들어오는 8080은 문서용 client CIDR로 제한했으며 SSH를 열지 않았다. 이 소스는 프로덕션 네트워크 설계나 AWS 배포 지침이 아니다.


### 4.2 앱 실행 요구 읽기


[app.py](../../../sample-app/app.py)와 [Dockerfile](../../../sample-app/Dockerfile)에서 다음을 찾아 기록한다.

| 요구 | 코드에서 확인할 근거 |
|---|---|
| HTTP 8080 | `uvicorn`의 port, `EXPOSE 8080` |
| 헬스 | `GET /health` |
| 데이터 읽기·쓰기 | `GET /items`, `POST /items` |
| 저장 방식 | 프로세스 메모리, 초기 항목 2개, 최대 100개 |
| 제약 | worker/replica마다 별도 메모리, 재시작 시 초기화 |
| 클라우드 의존성 | AWS/Azure SDK 호출 없음 |

AWS가 없어도 앱은 로컬·컨테이너에서 실행하고 계약을 검증할 수 있다. 이를 실제 EC2 부팅·AWS 네트워크 검증과 혼동하지 않는다.


### 4.3 서비스 매핑과 Azure 예제 비교


| AWS 소스 | Azure 타깃 | 유지·변경의 이유 |
|---|---|---|
| EC2 + Docker | Container Apps | OS 관리 대신 이미지·CPU·메모리·replica 선언 |
| VPC·public subnet·IGW·route | Managed Environment | custom VNet을 생략한 교육용 선택. 보안·라우팅 동등성을 보장하지 않음 |
| SG의 HTTP 8080 | HTTPS ingress → target port 8080 | 외부 포트·TLS·접근 범위가 변경됨. 동일 규칙의 자동 변환이 아님 |
| 공개 이미지 자리표시자 | ACR digest + Managed Identity | 이미지와 pull 권한을 명시 |
| EC2 관리 단위 | Resource Group·Environment·AVM Container App | 타깃 lifecycle과 state를 새로 관리 |
| 앱 코드 | 동일한 앱·Dockerfile | 이 샘플은 클라우드 SDK가 없어 코드 변경 불필요 |

타깃: [main.tf](./lab/azure/main.tf), [versions.tf](./lab/azure/versions.tf), [variables.tf](./lab/azure/variables.tf).

AVM은 **Container App 하나**에 사용한다. Resource Group·Environment는 작은 직접 선언으로 준비하고 registry·identity는 기존 준비 결과를 입력받는다. AVM 내부 구현을 복사하거나 AWS state를 Azure state로 바꾸지 않는다. module telemetry는 끄고 로그는 stream만 사용한다.


### 4.4 두 구성의 정적 검증 — 클라우드 없이


```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
terraform version
terraform -chdir=.\lab\aws fmt -check
terraform -chdir=.\lab\aws init -backend=false -input=false
terraform -chdir=.\lab\aws validate
terraform -chdir=.\lab\azure fmt -check
terraform -chdir=.\lab\azure init -backend=false -input=false
terraform -chdir=.\lab\azure validate
```

**성공 기준:** 양쪽 모두 `Success! The configuration is valid.`다. 이것은 HCL·provider schema·module input 검사이며 권한·리전·quota·네트워크·이미지 실행을 검증하지 않는다. 이 단계에서는 state나 클라우드 리소스를 만들지 않는다.


### 4.5 선택: 승인된 Azure 환경에서만 plan·배포


이 단계는 AWS 환경 없이 Azure 타깃만 배포한다. 로컬 분석만 원하는 참가자는 건너뛴다.

1. 승인된 registry·앱 image digest·pull identity가 있으면 그대로 입력받는다. 없다면 [공통 이미지 준비](../../../shared/container-image/README-ko.md)의 **4.1~4.3만** 수행한다. Container Apps·AKS 모듈은 실행하지 않는다. 동일 앱 이미지·pull 권한·identity 연결 권한을 확인한다.
2. [workshop.example.tfvars](./lab/azure/workshop.example.tfvars)를 `workshop.tfvars`로 복사하고 승인된 값으로 채운다. 이 로컬 파일은 Git에서 제외한다.
3. 새 `lab_id`로 타깃 그룹을 준비한다. 기존 registry 그룹과 다른 `rg-amw-tf-...`이며 기존 그룹을 가져오거나 자동 import하지 않는다.
4. 승인된 구독·테넌트와 실제 plan을 확인한다.

```powershell
$SubscriptionId = "<sandbox-subscription-id>"
$TargetGroupName = "rg-amw-tf-<your-eight-character-lab-id>"
az login
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
$Exists = az group exists --name $TargetGroupName --subscription $SubscriptionId --output tsv
if ($Exists -ne "false") { throw "Use a fresh target group; do not import or reuse an existing group." }
terraform -chdir=.\lab\azure validate
terraform -chdir=.\lab\azure plan -var-file=workshop.tfvars -out=workshop.tfplan
terraform -chdir=.\lab\azure show workshop.tfplan
```

**검토:** tfvars의 구독·리전·lab ID가 표시한 대상과 일치하는지, 생성은 새 타깃 그룹·environment·앱뿐인지, 기존 리소스의 변경·삭제는 없는지 확인한다. 계획 파일·state에도 민감한 값이 들어갈 수 있으므로 공유·커밋하지 않는다.

비용·대상을 승인한 경우에만 저장한 계획을 적용한다. 저장 plan 적용은 추가 확인 prompt가 없으므로 아래 명령 자체가 승인 경계다.

```powershell
terraform -chdir=.\lab\azure apply workshop.tfplan
$BaseUrl = terraform -chdir=.\lab\azure output -raw app_url
if ($BaseUrl -notmatch "^https://") { throw "No HTTPS app URL was returned." }
Invoke-RestMethod "$BaseUrl/health"
```

이 모듈의 타깃 주소에서 쓰기·읽기도 확인한다. 다른 컴퓨트 instruction을 완료하지 않는다.

```powershell
$Health = Invoke-RestMethod "$BaseUrl/health"
$Before = @(Invoke-RestMethod "$BaseUrl/items")
$Created = Invoke-RestMethod "$BaseUrl/items" -Method Post -ContentType "application/json" -Body '{"name":"terraform-workshop-item"}'
$After = @(Invoke-RestMethod "$BaseUrl/items")
if ($Health.status -ne "ok" -or $After.Count -ne $Before.Count + 1 -or
    -not ($After | Where-Object { $_.id -eq $Created.id -and $_.name -eq $Created.name })) {
    throw "Terraform target HTTP verification failed."
}
```

**성공 기준:** 헬스 ok·개수 1 증가·생성 항목 read-back이다. 원본 AWS 인스턴스의 데이터·트래픽을 옮긴 것은 아니다.


## 5. 검증·대표 실패


| 결과·실패 | 해석·대응 |
|---|---|
| `validate` 성공 | 구조 검사만 통과. 클라우드 배포 성공이 아님 |
| provider/module 다운로드 실패 | 승인된 다운로드 경로·proxy·인증을 확인. TLS를 끄지 않음 |
| Azure 인증·provider 등록·quota 실패 | 강사와 승인된 scope·리전·provider 준비 확인. 권한을 무조건 넓히지 않음 |
| private image pull 실패 | 기존 ACR digest·RBAC mode·identity 연결·AcrPull 전파 확인 |
| AWS 실습을 위해 자격증명을 요구함 | 이 instruction에서는 AWS plan/apply를 하지 않음. 분석·로컬 앱 경로로 되돌아감 |


## 6. 정리


정적 검증만 했다면 삭제할 AWS/Azure 리소스가 없다. `.terraform` 다운로드 캐시는 다음 검증에 재사용할 수 있고 dependency lock은 Git에서 관리한다.

Azure 타깃을 실제 배포했다면 **타깃을 먼저 삭제**한다. 같은 target 디렉터리와 state를 사용하며 다른 실습 state를 가져오지 않는다. 이 Terraform은 registry·identity를 입력으로 소비할 뿐 소유하지 않으므로 해당 리소스를 destroy하지 않는다.

```powershell
$TargetGroupName = terraform -chdir=.\lab\azure output -raw resource_group_name
az group show --name $TargetGroupName --subscription $SubscriptionId --query "{name:name,tags:tags}" --output json
terraform -chdir=.\lab\azure state list
terraform -chdir=.\lab\azure plan -destroy -var-file=workshop.tfvars -out=cleanup.tfplan
terraform -chdir=.\lab\azure show cleanup.tfplan
```

타깃 그룹·environment·앱만 삭제되는지 확인하고 승인한 경우에만 적용한다.

```powershell
terraform -chdir=.\lab\azure apply cleanup.tfplan
$ExistsAfterCleanup = az group exists --name $TargetGroupName --subscription $SubscriptionId --output tsv
if ($ExistsAfterCleanup -ne "false") { throw "Terraform target group deletion has not been verified." }
```

destroy 후에는 output이 사라지므로 **삭제 전에 확인한 target group name**을 유지해 확인한다. 실습에서 새로 만든 registry·identity 준비 그룹은 마지막 소비자가 종료된 뒤 [공통 준비의 6절](../../../shared/container-image/README-ko.md#6-정리--마지막-소비자가-끝난-다음)에서 별도로 정리한다. 외부의 기존 입력 리소스는 정리하지 않는다. 로컬 plan·tfvars·state는 삭제 결과를 확인하기 전에 없애지 않는다.


## 7. 실제 이전 고려사항


- EC2의 OS 의존성이나 상주 프로세스 요구가 있으면 VM 등 다른 타깃을 재평가한다.
- 네트워크 경계, TLS, 인증, 접근 원본 제한, 운영 로그의 동등성은 별도로 검증한다.
- DB·Blob 등의 외부 데이터, 컷오버·롤백·중단 시간은 별도 이전 계획에서 다룬다.
- LLM의 Terraform 변환은 검토할 초안이다. 이름 치환이나 `validate` 성공만으로 완전한 이전이라고 말하지 않는다.


## 8. 출처
