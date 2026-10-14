# Azure Migration Workshop

[English](./Readme.md) | 한국어

AWS에 익숙한 엔지니어가 Azure 개념·작은 앱 재배포·이전 도구 선택·결과 검증·정리를 배우는 모듈형 워크샵이다. 필요한 모듈만 선택하며 production 이전 제품이나 모든 트랙 배포 자동화가 아니다.

**AWS 안내:** 실제 AWS 환경은 만들지 않았다. AWS Terraform은 소스 분석 예제다. Azure의 합성 파일·DB·앱 배포는 학습용이며 실제 EC2·S3·RDS/Aurora 이전 성공 근거가 아니다.

## 1. 내 workload에 맞는 모듈 선택

| 목표/source | 선택 자료 | 결과·최소 입력 | 건너뛸 트랙 |
|---|---|---|---|
| IAM·권한 scope | [Identity](./modules/onboarding/identity/README-ko.md) | 승인 user/read scope로 정의·할당 읽기 | 앱·compute·DB·Terraform |
| VPC/subnet/SG | [네트워킹](./modules/onboarding/networking/README-ko.md) | VNet/NSG 해석, 선택 probe | 다른 compute·앱·data |
| S3 사용자 Blob 기초 | [Storage](./modules/onboarding/storage/README-ko.md) | private DNS/client/data identity로 파일1개 비교 | 앱·compute·IaC·DB |
| 오브젝트 이전 도구 | [Storage Mover/AzCopy](./modules/migration/objects/README-ko.md) | Mover 소개만·별도 private AzCopy 실습(3개/109 bytes) | 앱·compute·DB·Terraform |
| EC2/ECS HTTP 앱, 서버 관리 축소 | [Container Apps](./modules/onboarding/compute-container-apps/README-ko.md) | 승인 digest/UAI, HTTPS 읽기·쓰기 | VM·AKS·Functions·data |
| EC2+Docker 운영 모델 | [VM+Docker](./modules/onboarding/compute-vm/README-ko.md) | 승인 image/VM/network, OS/Docker/MI/HTTP | 다른 compute |
| EKS/Kubernetes 모델 | [AKS](./modules/onboarding/compute-aks/README-ko.md) | manifest 또는 승인 cluster 입력, Pod/Service/probe | 다른 compute·DB·Blob |
| Lambda/HTTP trigger | [Functions](./modules/onboarding/compute-functions/README-ko.md) | 같은 source/ASGI·host/auth, local/cloud 입력 | 다른 compute·ACR image |
| 기존 OS/disk/service 보존 | [Azure Migrate 서버](./modules/migration/servers/README-ko.md) | 합성 CSV import/Portal assessment·견적 해석, 복제에는 별도 실제 source 필요 | 컨테이너 재배포로 대체 |
| PostgreSQL | [전용 migration service](./modules/migration/database-postgresql/README-ko.md) | 접근 가능한 source, Validate/offline·schema/data | 다른 engine·앱 |
| MySQL | [MySQL DMS](./modules/migration/database-mysql/README-ko.md) | 승인 Premium/runtime/source, native·data | 다른 engine·앱 |
| SQL Server | [타깃/DMS/SqlPackage](./modules/migration/database-sqlserver/README-ko.md) | 기능 우선 선택, data-only B2 또는 준비 데모 | 다른 engine·앱 |
| IaC 분석/재작성 | [Terraform](./modules/migration/terraform/README-ko.md) | 요구/정적 검사, 선택 Azure consumer | AWS login/plan/apply |
| 의사결정만 | [계획](./modules/migration/planning/README-ko.md)+[컷오버](./modules/migration/cutover/README-ko.md) | 합성 계획/runbook, cloud 불필요 | live job/resource |
| 상태/log/비용 해석 | [관측성](./modules/onboarding/observability/README-ko.md) | 카드 또는 기존 승인 resource/read scope | 새 필수 compute |

[공통 앱](./sample-app/README-ko.md)은 재사용 자산이지 전원의 선행 수강이 아니다. [이미지 준비](./shared/container-image/README-ko.md)·[private Blob 입력](./shared/storage-private-access/README-ko.md)·[합성 DB 입력](./shared/database-sample/README-ko.md)은 필요한 입력의 선택 제공 방법이다. 기존 승인 입력이 있으면 준비와 다른 트랙 수강을 생략한다.

## 2. 선택 mode의 준비만 수행

[참가자 준비](./guides/participant-preparation-ko.md)에서 읽기/Portal walkthrough/준비된 강사 데모/승인 합성 실습을 선택한다. 강사는 [강사 가이드](./guides/instructor-guide-ko.md)와 [모듈 조합](./guides/module-combinations-ko.md)을 사용한다.

CLI는 local PowerShell7.4+, 앱/local host는 WSL/Linux Bash, guest는 VM Bash 또는 private Windows PowerShell을 명시한다. Windows/WSL venv를 공유하지 않고 선택 도구만 승인 source에서 설치한다. CLI 인증이 필요한 경우에만 아래를 따른다.

```powershell
$PSVersionTable.PSVersion
az version
```

실패 중단과 승인된 login/MFA 경로를 적용한다.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az login
```

기본 구독을 바꾸지 않고 정확한 대상을 확인한다.

```powershell
$SubscriptionId = "<sandbox-subscription-id>"
$ParsedSubscriptionId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedSubscriptionId)) {
    throw "Replace SubscriptionId with the approved sandbox subscription ID."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
```

기대값은 합의한 tenant/subscription·Enabled다. login은 data 권한을 자동 부여하지 않는다. [PowerShell 설치](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell)·[Azure CLI 설치](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)를 참고한다.

## 3. Azure resource 경계 이해

필요할 때 [Resource Manager 소개](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview)를 읽는다.

```text
Management Group
  └─ Subscription
       └─ Resource Group
            └─ Resource
```

AWS Organizations/Account/tag group과1:1 동일하지 않다. Subscription은 비용·접근 경계다. group location은 관리 metadata이며 내부 resource가 모두 같은 리전에 있어야 하는 조건은 아니다. RBAC와 tag의 상속 동작도 다르다. group 삭제는 포함 resource를 삭제하므로 소유권을 먼저 확인한다.

## 4. 서비스 선택부터, 실제 결과로 검증

서버에는 [Azure Migrate](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview), 오브젝트에는 [Storage Mover](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview)와 [AzCopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10), DB에는 [DMS](https://learn.microsoft.com/en-us/azure/dms/dms-overview)를 도구 실습과 함께 소개한다. PostgreSQL은 [전용 service](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql), SQL [SqlPackage](https://learn.microsoft.com/en-us/sql/tools/sqlpackage/sqlpackage?view=sql-server-ver17)는 DMS와 다른 Export/Import다.

source·현재 지원 조건에 따라 live 범위를 정한다. Migrate CSV 항목만으로 복제할 수 없고 private AzCopy가 Mover 연결을 보장하지 않는다. SQL Database/MI/SQL VM은 기능·mode·인증 경계가 다르다. 소개/screenshot과 실제 native job·app/data/schema 근거를 구분한다.

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성한다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인한다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따른다. 인증과 network는 다른 통제다.

## 5. 안전·비용·소유자 정리

승인 sandbox·합성 data만 사용한다. 실제 customer inventory/data·내부 문서·credential/token·민감 log/식별정보를 Git/prompt/screenshot에 넣지 않는다. Blob 기본은 public Disabled와 private endpoint/DNS/client·Entra/RBAC이며 identity가 network 격리를 대체하지 않는다. TLS·Shared Key 제한·조직 정책을 해제해 오류를 해결하지 않는다.

대상·최소권한·지원/quota·비용·파괴 영향을 확인하고 승인한다. [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)는 견적이지 청구 상한이 아니다. [Cost Management](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management) budget은 알림이지 자동 중지 보장이 아니다.

consumer는 자기 app/cluster/VM/job·정확한 새 grant만 정리하고 publisher는 마지막 consumer 이후 공유 입력을 정리한다. source/backup은 acceptance/retention/rollback 승인까지 보존한다. job 삭제·VM 정지는 모든 disk/storage/runtime 비용 삭제가 아니다. target 새 쓰기 이후에는 접속 복귀와 data 복구를 구분한다.

## 6. 선택 확장 — GitHub Copilot

수동 절차를 먼저 이해한 뒤 선택 module만 위임한다. 관리형 replication/CDC/copy/scheduler를 새 코드로 재구현하지 않고 분석·작성·승인 실행을 분리한다.

```text
선택 모듈은 <module>, 목표는 <학습 목표>다.
입력·결과·최소 의존성·건너뛸 트랙을 읽어줘.
Azure 서비스/공식 도구와 Portal/native 흐름부터 설명해줘.
실제 source 필요 단계와 합성/강사 데모를 구분해줘.
IaC/앱 분석을 선택한 경우에만 해당 source 근거를 읽어줘.
AWS 환경·credential/AMI 조회·plan/apply는 하지 마.
분석 중 배포·권한 변경·유료 resource를 만들지 마.
```

분석 검토 후:

```text
선택한 module의 configuration/instruction만 작성해줘.
native assessment/validation/job status/오류·기대 결과를 설명해줘.
같은 앱과 승인 image/identity/DB 입력을 재사용해줘.
관리형 replication/CDC/copy/scheduler 플랫폼은 만들지 마.
검증·owner별 정리를 문서화해줘.
다른 트랙의 설치·테스트·배포는 추가하지 마.
Azure plan/apply/destroy·commit/push는 별도 승인 없이 실행하지 마.
```

승인된 실행 회차:

```text
승인한 sandbox/module/mode만 보조해줘.
tenant/subscription/region/group/입력/권한/비용·영향을 보여줘.
role·생성·migration 시작·쓰기마다 별도 승인을 받아줘.
Terraform이면 saved plan을 보여주고 apply 승인을 받아줘.
실제 native 상태와 선택 app/data/schema 기준을 확인해줘.
명령 제안과 실행을 구분하고 실제 exit/error·unknown을 보고해줘.
정확한 cleanup 대상·영향을 보여주고 삭제 승인을 받아줘.
```

변경 파일·실제 명령/exit/응답·owned resource/grant·정리·미확인을 검토한다. AI 제안은 운영 cutover 승인이 아니다. [IDE Copilot](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-in-ides)·[GitHub Copilot](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github)을 참고한다.
