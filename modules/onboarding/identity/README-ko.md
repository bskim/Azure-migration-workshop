# Identity — 누가 무엇에 접근할 수 있는가

[English](./README.md) | 한국어


## 1. 학습 목표


- **대상:** AWS IAM을 사용해 봤지만 Azure 권한 모델이 낯선 엔지니어.
- **예상 시간:** 50분.
- **구성:** 온보딩 공통 개념. 조회 실습이며 새 리소스나 역할 할당을 만들지 않는다.
- **성공 기준:** 인증과 인가, principal·role·scope, 제어 영역과 데이터 영역을 예시로 설명한다.
- **의존성:** 다른 모듈·앱·컴퓨트 배포 없음.


### 선택 기준과 모듈 경계


| 항목 | 범위 |
|---|---|
| 선택할 때 | AWS IAM과 Entra ID/RBAC의 차이·scope·데이터 권한을 읽고 싶을 때 |
| 입력 | 조회 가능한 Azure 사용자 identity와 승인된 구독 |
| 결과 | 역할 정의·할당·scope를 구분하는 방법. 새 identity·role assignment 생성은 하지 않음 |
| 건너뛸 자료 | 공통 앱, 모든 컴퓨트, Storage 실습, Terraform, 데이터 이전 |
| 제외 | 앱의 Managed Identity 연결·실제 데이터 접근은 해당 선택 모듈에서 수행 |

권한 모델을 이미 이해하면 이 모듈을 완료하지 않고 다른 모듈의 최소 권한 준비부터 진행해도 된다.


## 2. 서비스 소개와 선택 이유


먼저 소개 페이지를 열고 아래 개념을 찾아본다.

| 서비스·기능 | Microsoft Learn 소개 | 이 instruction에서 볼 내용 |
|---|---|---|
| Microsoft Entra / Microsoft Entra ID | [Microsoft Entra 소개](https://learn.microsoft.com/en-us/entra/fundamentals/what-is-entra) | 제품군 중 Entra ID가 사용자·앱의 인증과 identity를 담당한다는 점 |
| Azure RBAC | [Azure RBAC란?](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview) | 누가, 어떤 역할로, 어느 scope에서 접근하는가 |
| Azure Resource Manager | [Azure Resource Manager란?](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/overview) | 리소스 계층과 제어 영역 |
| Managed Identity | [Azure 리소스의 Managed Identity란?](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview) | 앱이 직접 비밀을 관리하지 않고 인증하는 방법 |
| Azure Blob Storage | [Blob Storage 소개](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction) | 데이터 영역 권한을 구분할 예시 |

AWS IAM의 이름을 Azure 이름으로 치환하지 않는다.

| AWS에서 익숙한 개념 | Azure에서 읽을 개념 | 동일하다고 가정하면 안 되는 부분 |
|---|---|---|
| IAM 사용자·연동 identity | Entra ID 사용자·그룹·서비스 principal | 디렉터리 identity와 Azure 리소스 권한은 별도다. |
| IAM policy의 action·resource | RBAC role의 Actions/DataActions와 scope | policy 평가와 role assignment 구조가 같지 않다. |
| 인스턴스 역할 등 workload identity | Managed Identity | 비밀 없는 인증이라는 목표는 비슷하지만 연결·토큰·수명주기는 다르다. |
| Organizations·OU·Account | Management Group·Subscription·Resource Group | 역할과 경계를 비교하되 1:1 동일 계층으로 매핑하지 않는다. |


## 3. 사전 준비


- 로컬 PowerShell 7.4 이상과 현재 안정 Azure CLI. [공통 준비](../../../Readme-ko.md)를 확인한다.
- 승인된 샌드박스 구독에서 역할 정의 조회 권한이 필요하다. 새 권한을 만들 수 있는 Owner는 필요하지 않다.
- 리전·컴퓨트 쿼터는 조회 실습에 필요하지 않으며 새 서비스 사용료도 발생시키지 않는다.
- 조건부 액세스·MFA 정책을 우회하지 않는다. 로그인 실패는 강사·테넌트 관리자와 해결한다.


## 4. 단계별 실습


### 4.1 로그인과 구독 경계 확인


**실행 환경: 로컬 PowerShell.** 이 instruction만 선택해도 아래부터 시작할 수 있다.

```powershell
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true
az login
$SubscriptionId = "<sandbox-subscription-id>"
$ParsedSubscriptionId = [guid]::Empty
if (-not [guid]::TryParse($SubscriptionId, [ref]$ParsedSubscriptionId)) {
    throw "Replace SubscriptionId with the approved sandbox subscription ID."
}
az account show --subscription $SubscriptionId --query "{name:name,id:id,tenantId:tenantId,state:state}" --output table
```

**관찰:** 구독 ID는 리소스 명령의 대상, tenant ID는 identity가 속한 디렉터리다. 강사와 확인한 대상·`Enabled` 상태가 아니면 다음 단계로 진행하지 않는다.

**이유:** 로그인한 identity와 접근하려는 리소스 경계를 분리해서 읽어야 한다. 로그인 성공은 Blob 데이터 접근 성공을 의미하지 않는다.


### 4.2 역할 정의의 제어 영역 권한 읽기


```powershell
az role definition list --name "Reader" --subscription $SubscriptionId --query "[0].{role:roleName,permissions:permissions}" --output json
az role definition list --name "Contributor" --subscription $SubscriptionId --query "[0].{role:roleName,permissions:permissions}" --output json
```

**관찰:**

- `Reader`의 `actions`에서 읽기 범위를 확인한다.
- `Contributor`의 `actions`와 `notActions`에서 관리 권한과 제외 항목을 확인한다.
- `dataActions`도 함께 읽는다. 리소스를 관리하는 역할이라고 해서 모든 데이터 작업이 허용되는 것은 아니다.

이 명령은 **역할의 정의**를 읽는다. 해당 역할이 현재 사용자에게 할당됐다는 증거가 아니다.


### 4.3 Blob 데이터 역할과 비교하기


```powershell
az role definition list --name "Storage Blob Data Reader" --subscription $SubscriptionId --query "[0].{role:roleName,permissions:permissions}" --output json
az role definition list --name "Storage Blob Data Contributor" --subscription $SubscriptionId --query "[0].{role:roleName,permissions:permissions}" --output json
```

**관찰:** `dataActions`에서 Blob 읽기와 쓰기·삭제의 차이를 찾는다. 데이터 역할도 컨테이너 관리 등에 필요한 `actions`를 포함할 수 있으므로 “데이터 역할에는 DataActions만 읽는 대신 management Actions도 함께 확인한다.

**예시:** Storage 계정을 만드는 작업은 제어 영역, 컨테이너 안의 파일을 읽는 작업은 데이터 영역이다. Blob instruction은 `--auth-mode login`으로 Entra identity의 데이터 권한을 사용한다. 계정 키로 우회하지 않는다. Shared Key를 허용하는 환경에서는 키 조회 권한도 접근 경로가 될 수 있으므로 실제 환경의 키 정책까지 따로 검토해야 한다.


### 4.4 내 역할의 scope 읽기 — Azure portal


**실행 환경: 브라우저의 Azure portal.**

1. 승인된 **Subscriptions → 해당 구독 → Access control (IAM) → View my access**를 연다.
2. 역할과 scope, 직접/그룹/상속 접근 여부를 읽는다.
3. 구독에서 새 역할을 추가·삭제하지 않는다. 상위 관리 범위나 그룹 membership도 변경하지 않는다.

구독 전체 조회 권한이 없으면 관리자에게 **승인된 실습 리소스 그룹**의 같은 화면을 보여 달라고 요청한다. 화면을 열 수 없으면 관리자와 해당 scope의 조회 권한을 확인한다.

현재 Portal은 **Check access** 탭에서 자신의 Active/Eligible/Deny 접근을 보여줄 수 있다. 이 경우 **Looking for the previous check access view? Click here.**를 선택하면 기존 화면의 **View my access**로 이동한다. 아래 두 화면 중 현재 표시되는 경로를 따른다. 역할 추가/삭제 버튼은 이 조회 실습에서 사용하지 않는다.

![현재 IAM Check access의 이전 화면 진입 안내](./images/portal-iam-check-access.png)

![기존 IAM 화면의 View my access 진입 버튼](./images/portal-iam-view-my-access-entry.png)

*Portal 소개/설정 예시. 보이는 기본값을 승인 입력으로 사용하지 않고 실제 job 결과와 구분한다.*

**생각해 볼 상황:** 구독의 Contributor와 리소스 그룹의 Reader를 동시에 갖고 있다면 Reader가 상위 Contributor를 제한하는가? 일반적인 RBAC allow 권한은 합산되므로 그렇지 않다. deny assignment와 조건 등 별도 제약은 심화 주제다.


### 4.5 Managed Identity는 어디에 연결되는가


이 단계는 개념 읽기이며 identity·컴퓨트를 만들지 않는다.

```text
로컬 참가자 → az login → 참가자의 Entra identity → 허용된 데이터 작업
Azure 앱 → Managed Identity → 앱 identity의 RBAC → 허용된 데이터 작업
```

- System-assigned identity는 연결된 리소스와 수명주기를 공유한다.
- User-assigned identity는 독립 리소스이며 여러 지원 리소스에 연결할 수 있다.
- identity를 연결하는 것과 Blob 등에 역할을 부여하는 것은 별도다.
- 로컬 `az login`을 Managed Identity 사용 실습으로 설명하지 않는다. 실제 앱 연결은 선택한 컴퓨트 instruction에서 다룬다.


## 5. 검증과 대표 실패


| 확인 항목 | 기대 결과 |
|---|---|
| 인증/인가 | 로그인과 리소스·데이터 작업 허용 여부가 다른 단계라고 설명한다. |
| 역할 정의/할당 | 정의 조회 출력만으로 내 권한을 판단하지 않는다. |
| scope | 같은 역할도 구독·그룹·리소스 중 어디에 할당됐는지에 따라 영향 범위가 달라진다. |
| 데이터 권한 | Contributor만 보고 Blob 읽기/쓰기를 보장하지 않는다. |
| Managed Identity | 로컬 사용자와 배포 앱의 identity가 다르다고 설명한다. |

| 실패·오해 | 확인·해결 |
|---|---|
| 구독 조회가 실패하거나 대상이 다름 | 입력한 구독·로그인 테넌트·초대 사용자 접근을 확인하고 중단한다. |
| 역할 정의 조회 권한 부족 | 강사가 역할 정의를 보여 주거나 실습 범위의 조회 권한을 준비한다. Owner를 기본 해결책으로 부여하지 않는다. |
| 역할 정의 결과가 `null` | 역할 이름·클라우드 환경·조회 범위를 확인한다. 빈 출력을 성공으로 기록하지 않는다. |
| Entra 관리자라서 모든 Azure 리소스에 접근 가능하다고 생각함 | 디렉터리 역할과 Azure RBAC 역할의 별도 할당을 확인한다. |
| 낮은 scope의 Reader가 상위 권한을 제한한다고 생각함 | 상속·그룹·직접 할당을 함께 읽는다. |


## 6. 정리


조회와 개념 읽기만 했으므로 삭제할 Azure 리소스·역할 할당이 없다. 다른 instruction에서 만든 리소스를 이 모듈의 정리 대상으로 삼지 않는다.

개인 PC에서 후속 실습을 계속하면 로그인 상태를 유지할 수 있다. 공용 PC이거나 종료할 때는 로컬 PowerShell에서 `az logout`을 실행한다. Azure 역할·리소스를 삭제하는 명령은 아니다.


## 7. 실제 이전에서 추가로 확인할 사항


- 사람·앱 identity, 테넌트 경계, 사용자 초대와 그룹 membership.
- 앱의 Managed Identity 지원 여부, 기존 AWS 인증 코드 변경.
- 데이터별 최소 권한과 scope, 역할 전파 시간, 조건부 액세스.
- 비밀·키의 폐기와 교체, 감사 로그, 운영 인계.
- 규제·보안 심화 검토는 관련 전문가와 진행하며 이 실습으로 완결하지 않는다.


## 8. 출처


- 소개 링크와 RBAC/Managed Identity 설명은 위 Microsoft Learn 문서를 참고했다.
- 조회 instruction은 직접 작성했으며 외부 저장소 코드를 복사하지 않았다.
