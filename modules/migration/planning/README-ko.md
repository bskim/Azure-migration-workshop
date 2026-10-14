# 이전 계획·도구 선택 — 내 워크로드에 맞는 경로 정하기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: AWS 워크로드의 Azure 이전을 검토하는 엔지니어.
- 예상: 50~60분. 한 사례만 선택해 완료하며 모든 서버·오브젝트·DB 경로를 작성하지 않습니다.
- 목표: source 요구·제약을 읽고 **Azure 제공 서비스/공식 도구와 실행 가능한 교육 범위**를 고릅니다.
- 결과: 타깃·도구 선택 근거, 미확인 사항, 사전 준비·성공 기준·test migration·cutover/rollback을 담은 작은 계획표.
- 기본 방법은 문헌·합성 사례·Portal 흐름 읽기입니다. CLI wrapper·replication/CDC·이전 scheduler를 만들지 않습니다.

| 항목 | 범위 |
|---|---|
| 입력 | 포함된 합성 workload CSV와 필요한 공식 서비스 소개. 앱 사례만 공통 앱 소스 추가 |
| 필요 없는 준비 | Azure/AWS 로그인·resource 생성·도구 설치·모든 온보딩/컴퓨트·Terraform 실행 |
| 선택 확대 | 강사가 준비한 안전한 assessment/job 결과를 읽는 설명. 새 project/job은 생성하지 않음 |
| 제외 | 실제 AWS discovery·복제·S3/DB 접근·production 계획 확정·무중단 보장 |

Azure 기본 지식이 필요하면 [Identity](../../onboarding/identity/README-ko.md)·[네트워킹](../../onboarding/networking/README-ko.md)의 필요한 설명만 참고합니다. 수강 완료를 요구하지 않습니다.


## 2. 먼저 읽을 서비스·공식 도구


| source 요구 | 소개 링크 | 맡기는 일과 읽을 결과 |
|---|---|---|
| 기존 서버·OS·디스크 유지 | [Azure Migrate 개요](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview), [AWS VM 이전 흐름](https://learn.microsoft.com/en-us/azure/migrate/tutorial-migrate-aws-virtual-machines) | discovery/assessment·readiness/경고·sizing·복제·test migration·cutover |
| 오브젝트 이전·작업 관리 | [Azure Storage Mover](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview) | 지원 endpoint·project/job·진행/실패·결과. source별 준비와 metadata 한계 |
| 작은 copy utility | [AzCopy 소개](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10), [S3 copy 절차](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-s3) | 공식 copy·인증·오류·작업 결과. 자체 엔진을 구현하지 않음 |
| PostgreSQL | [PostgreSQL migration service](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql), [Flexible Server 소개](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview) | 엔진별 source validation·offline/online·작업·cutover·제약 |
| MySQL | [DMS 소개](https://learn.microsoft.com/en-us/azure/dms/dms-overview), [지원 매트릭스](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status), [MySQL 타깃 소개](https://learn.microsoft.com/en-us/azure/mysql/flexible-server/overview) | 현재 MySQL 도구 경험·source/target·offline/online·진행·오류 |
| SQL Server | [DMS](https://learn.microsoft.com/en-us/azure/dms/dms-overview), [지원 매트릭스](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status) | 타깃별 지원·backup/연결·migration 결과. assessment·SKU 추천은 별도 확인 |
| 앱 실행 모델 변경 | [VM](https://learn.microsoft.com/en-us/azure/virtual-machines/overview), [Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/overview), [AKS](https://learn.microsoft.com/en-us/azure/aks/what-is-aks) | 같은 앱을 재배포할 타깃의 운영 모델. 실제 서버/데이터 이전과 구분 |

SQL 타깃은 [Azure SQL Database](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview), [SQL Managed Instance](https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview), [SQL VM](https://learn.microsoft.com/en-us/azure/azure-sql/virtual-machines/windows/sql-server-on-azure-vm-iaas-what-is-overview)의 기능·관리 책임을 비교합니다. 도구 이름부터 고정한 뒤 source 기능을 무시하지 않습니다.

“EC2→VM”, “S3→Blob”, “RDS→같은 엔진”은 첫 후보이지 완성된 이전 설계가 아닙니다. source 기능·OS·버전·확장·데이터·network/identity·중단 허용 시간을 확인하고 선택합니다.


**워크샵 제공 경계:** Storage Mover는 **서비스 소개만** 제공합니다. 관리 기능·적합한 source/workload·리전/비용/권한/network와 공식 문헌을 배우고 endpoint/project/job definition 생성·실행 role·copy 시작/검증은 실습하지 않습니다. 오브젝트 hands-on은 별도 공식 **private AzCopy**의 합성3개/109 bytes입니다. 이 선택은 Mover 전반의 미지원 결론이 아닙니다. 실제 고객 실행은 해당 지원 공식 시나리오와 고객 관리자 승인을 별도로 따릅니다.

## 3. 사전 준비·교육 모드·비용


- [합성 사례 CSV](./lab/workloads.csv)를 텍스트 또는 spreadsheet로 엽니다. 실행 script·패키지는 없습니다.
- CSV의 모든 값은 **가상 요구**입니다. VM/DB/객체가 생성되어 있거나 실제 정보가 수집됐다는 뜻이 아닙니다.
- 이 CSV는 **이 워크샵의 사례표**이며 Azure Migrate/DMS의 공식 import 형식이 아닙니다. 그대로 서비스에 업로드하지 않습니다. 추후 공식 import를 쓰면 그때 현재 template·필드·근거를 별도로 맞춥니다.
- source_example과 engine_or_os의 제품·버전은 선택 토론용입니다. 지원·호환성·region/quota를 인증하지 않습니다.
- 허용 중단 시간은 계획의 입력이지 도구가 달성했다고 주장하는 수치가 아닙니다.
- 이 모듈은 읽기·계획 작성으로 새 Azure 비용을 발생시키는 리소스를 만들지 않습니다. 실제 migration project/appliance·target·복제/임시 storage·DB·network/egress 비용은 계획표에 별도로 넣습니다.
- 실제 customer inventory·계정·키·내부 문서를 사례표나 Copilot에 넣지 않습니다. 서비스가 권한을 필요로 한다면 **종류·scope**만 계획하고 비밀 값은 기록하지 않습니다.

교육 모드를 먼저 고릅니다.

| 모드 | 할 수 있는 것 | 성공했다고 말하면 안 되는 것 |
|---|---|---|
| 개념·합성 사례 | source 요구·도구·미확인 사항·기준 결정 | 실제 discovery/readiness·이전 완료 |
| Guided walkthrough | 공식 Portal/도구 흐름에서 입력·출력·제약을 설명 | 화면을 읽었으니 실제 job이 성공했다는 결론 |
| 강사 준비 데모 | 허용된 준비 환경·평가/job 결과를 관찰 | 준비된 결과가 현재 참가자의 AWS source를 검증했다는 결론 |
| 승인된 합성 실제 실습 | 현재 서비스가 지원하는 작은 대체 source/target을 준비해 실행 | Blob→Blob·로컬 DB 결과를 실제 S3/RDS 이전으로 대체 |

이 모듈은 사례를 읽고 계획하는 범위입니다. 합성 Azure 결과로 CSV의 가상 요구나 실제 AWS readiness가 검증됐다고 하지 않습니다.


## 4. 단계별 계획 실습


### 4.1 사례 하나와 근거를 고르기


CSV의 6개 행 중 자기 workload와 비슷한 **하나만** 고릅니다.

| 사례 | 주된 질문 | 첫 검토 후보·주의점 |
|---|---|---|
| `app-sample` | OS 보존 필요성과 HTTP 컨테이너 실행 목표를 확인합니다. | Container Apps/AKS/VM 중 운영 목표로 선택. 앱 재배포는 Azure Migrate 서버 복제가 아님 |
| `server-sample` | Windows OS·disk·service/local state의 보존 요구를 확인합니다. | Azure Migrate의 서버 경로와 target VM 검토. 앱만 새로 배포하는 것으로 요구를 충족했다고 하지 않음 |
| `objects-sample` | 관리형 job과 작은 utility copy의 용도를 비교합니다. | Storage Mover/AzCopy 비교. archive class·metadata·source 권한 확인 전 readiness를 확정하지 않음 |
| `postgresql-sample` | 같은 엔진 target의 schema/data 이전 조건을 확인합니다. | PostgreSQL 전용 migration service, extension·권한·복제 제약 확인 |
| `mysql-sample` | 테이블 엔진·버전·source 권한을 확인합니다. | 현재 MySQL DMS 경험·지원 매트릭스 검토. 오래된 online URL을 실행 방법으로 확정하지 않음 |
| `sqlserver-sample` | target의 cross-database·SQL Agent 지원을 확인합니다. | Managed Instance/SQL VM 후보를 먼저 비교. Azure SQL Database를 이름만 보고 자동 선택하지 않음 |

앱 사례는 [app.py](../../../sample-app/app.py)·[Dockerfile](../../../sample-app/Dockerfile)·[AWS Terraform](../terraform/lab/aws/main.tf)에서 포트·실행 명령·memory 저장·SDK 의존성을 읽습니다. 앱 서버·AWS 환경은 실행하지 않습니다.

host OS는 코드만으로 확정하지 않습니다. Docker base OS와 source VM OS도 별개입니다. 앱 행은 코드로 읽을 수 있는 요구와 합성 host inventory를 섞은 사례이므로 `Linux_x64_host_OS_unknown`을 실제 발견된 OS 이름처럼 취급하지 않습니다.

그 밖의 행은 합성 inventory일 뿐입니다. **CSV의 행 수·source 이름은 discovery evidence가 아닙니다.** 실제 assessment 없이 “Azure ready”라고 채우지 않습니다.


### 4.2 유지할 것·바꿀 것·모르는 것을 분리


다음 세 칸을 채웁니다.

| 구분 | 예시 |
|---|---|
| 유지 요구 | OS·service·DB engine·데이터·key/path·앱 계약 |
| 변경 가능 | compute 운영 모델·network 구조·identity·connection 설정 |
| 미확인·중단 조건 | 버전/extension·source 권한·archive 복원·실제 데이터 변화량·중단 목표 달성 |

Terraform에 resource가 있다고 실제 서버의 application dependency를 다 알 수 있는 것은 아닙니다. extension·SQL Agent·쓰기량 같은 값은 source 측 추가 근거가 필요합니다. 모르는 항목을 “없음”으로 기본 처리하지 않습니다.


### 4.3 타깃과 도구를 고르고 대안을 하나 배제


선택한 사례에 대해 다음을 적습니다.

1. 목표 타깃과 보존/변경 이유.
2. 사용할 Azure service/공식 utility와 **서비스가 맡는 동작**.
3. 쓰지 않을 대안 하나와 이유.
4. service/version/region/source/target 지원에서 아직 확인할 항목.
5. 이 교육 모드와 source 없어서 할 수 없는 단계.

예를 들어 `server-sample`은 OS·disk·local state 유지가 요구이므로 Azure Migrate 서버 경로를 후보로 정하고 **Container Apps 새 배포만으로 대체하는 선택을 배제**합니다. 실제 AWS가 없어 discovery·replication을 실행하지 못하므로 공식 흐름/준비된 강사 결과를 읽는 모드를 택합니다.

`sqlserver-sample`의 기능 요구가 SQL Database와 맞는지 평가하지 않았다면 그 target을 확정하지 않습니다. SQL Managed Instance/SQL VM도 비용·기능·운영·이전 방식의 대안이지 자동 정답이 아닙니다.


### 4.4 Portal/native 도구에서 읽어야 할 근거 정하기


새 project/job을 만들지 않습니다. 공식 문서 또는 강사가 준비한 안전한 화면/결과가 있다면 **어느 부분이 선택 근거인지** 읽습니다.

| 경로 | 읽을 서비스 결과 | 혼동하지 말 것 |
|---|---|---|
| Azure Migrate | 발견된 inventory·assessment target/readiness·경고·sizing·test migration/replication 상태 | 합성 CSV가 실제 발견/성능 수집 결과는 아님 |
| Storage Mover | 지원 endpoint·project/job·transfer/progress·오류/metadata 처리 | 관리 리소스 생성과 data transfer 완료는 다름 |
| AzCopy | native copy 결과·오류·작업 범위, 별도 개수/내용 확인 | process 완료만으로 metadata·version·전체 정합성을 보장하지 않음 |
| PostgreSQL service | source validation·offline/online 선택·job·cutover/제약 | 작은 dump 복원 성공이 해당 서비스 실행 성공은 아님 |
| DMS | 선택 engine/target의 현재 migration 경험·validation/job/error | SQL Portal과 MySQL 경험·assessment 기능을 같은 것으로 가정하지 않음 |

소개 화면만 읽었으면 “walkthrough”, 실제 service 결과를 관찰했으면 어떤 준비 환경/범위였는지 구분합니다. 실습 대상의 준비 상태는 현재 입력·권한·연결 결과로 확인합니다.


### 4.5 사전 준비·test migration·중단 조건


계획표에 다음을 넣습니다.

- **권한:** control plane, source/target data, engine privilege를 분리. 누가 부여·회수하는지와 scope만 기록.
- **네트워크:** source→service/agent→target의 실제 연결·DNS·TLS·ports·bandwidth. source 연결 없이 job 시작 가능하다고 하지 않음.
- **호환성:** OS/engine version·extension·source 기능·target 제한·support/preview.
- **비용:** source appliance/agent·replica·backup/임시 storage·target·egress. 관리 화면이 무료여도 전체 이전 비용은 아닐 수 있음.
- **test migration:** 운영 전환과 분리한 target·network·검사 데이터/앱. source·production DNS/connection을 자동 변경하지 않음.
- **중단 조건:** source 근거/권한 없음, unsupported 기능, 검사 불일치, 비용/시간 초과. 진행을 성공처럼 계속하지 않음.

큰 data·GPU·HA·복잡한 network는 작은 기본 실습에 구현하지 않습니다. 실제 이전 검토 항목으로 남깁니다.


### 4.6 Cutover·rollback 기준을 먼저 쓰기


실제 전환을 하지는 않습니다. 계획 단계에서 승인자·조건·순서를 정합니다.

| 시점 | 계획할 내용 |
|---|---|
| 전환 전 | backup/복구 확인, source 쓰기 중지 방식, 최종 sync·검사, connection/DNS·TTL·앱 설정 전환 승인 |
| 전환 직전 go/no-go | native job/validation 결과·data 기준·앱 연결·운영 준비를 모두 확인합니다. 확인하지 못한 항목이 있으면 중단합니다. |
| 전환 후 | 읽기·쓰기·오류율·latency·새 데이터의 확인 책임과 관찰 시간 |
| rollback | 언제 누가 원래 연결로 되돌리는지, source 재개 조건·target 쓰기 데이터 처리·복구 시간 |

**Online은 무중단 보장이 아닙니다.** 최종 sync·쓰기 정지·전환 동안 중단이 생길 수 있습니다. target에 새 쓰기가 발생한 뒤 connection만 되돌리는 것은 데이터 rollback이 아닙니다.


### 4.7 작은 계획표와 다음 모듈 고르기


문서 편집기/개인 실습 메모에 다음 필드만 채웁니다. 플랫폼이나 새 config schema를 만들 필요 없습니다.

| 필드 | 작성할 내용 |
|---|---|
| 사례·근거 수준 | CSV scenario ID, 코드 근거/합성 inventory/실제 관찰의 구분 |
| target·도구·이유 | 사용할 service, 맡길 동작, 배제한 대안 |
| 교육 모드 | 개념/walkthrough/강사 데모/합성 실제 실습과 source 필요 단계·소개 전용 범위 |
| 선행 조건·미확인 | 권한·network·compatibility·source 정보, 담당자·확인 방법 |
| test·성공 기준 | native 결과 + data/app 검사. count·내용·대표 쿼리·health 같은 구체 기준 |
| go/no-go·cutover | 쓰기 중지·최종 확인·전환 승인·관찰 범위 |
| rollback | 되돌릴 조건·책임자·data 처리·시간 |
| 비용·정리 | 예상 비용 항목·한도·owner·임시 리소스·source 보호·삭제 승인 |

다음 자료는 **선택한 경로 하나만** 읽습니다.

- 앱 재배포: [VM + Docker](../../onboarding/compute-vm/README-ko.md)·[AKS](../../onboarding/compute-aks/README-ko.md)·[Container Apps](../../onboarding/compute-container-apps/README-ko.md) 중 선택.
- IaC 표현이 목표인 경우에만 [Terraform](../terraform/README-ko.md)을 추가합니다. 도구 선택의 필수 실행 단계가 아닙니다.
- OS/disk/service 보존이 목표면 [Azure Migrate 서버 이전](../servers/README-ko.md)의 모드 A/B/C 중 필요한 범위만 선택합니다. CSV assessment를 실제 source 복제로 연결하지 않습니다.
- object는 [Storage Mover/AzCopy](../objects/README-ko.md)의 Mover/S3 소개만·별도 private AzCopy 실행를 선택합니다. 대체 Azure 결과를 실제 S3 인증·copy로 표시하지 않습니다.
- DB는 [PostgreSQL](../database-postgresql/README-ko.md) 또는 [MySQL](../database-mysql/README-ko.md) 중 실제 엔진 하나만 선택합니다. 공통 data 의미는 같아도 서비스·권한·version·Portal/DDL 동작은 다릅니다.
- SQL Server는 [타깃별 DMS 모듈](../database-sqlserver/README-ko.md)에서 data-only 축소 실습과 SQL Agent/cross-DB 기능 보존 요구를 구분합니다. 원래 `sqlserver-sample`을 SQL Database sample로 자동 대체하지 않습니다.
- [컷오버·롤백](../cutover/README-ko.md)에서는 선택한 workload 하나의 합성 카드·go/no-go와 write 상태별 판단을 다룹니다. 기본은 tabletop이며 선택 읽기 profile 전환을 실제 운영/data rollback으로 표시하지 않습니다.
- 결과/비용을 읽는 방법이 필요하면 [관측성](../../onboarding/observability/README-ko.md)의 필요한 부분만 참고합니다.


### 4.8 합성 source를 실제 source로 바꿀 때의 준비 과제

**선택 시간:** 10~15분입니다. 방금 선택한 서버·오브젝트·DB 사례 하나에 대해 다음 표를 개인 기록에 작성합니다. source를 실제로 조회하거나 AWS 환경·credential을 준비하지 않습니다. 고객 inventory·내부 문서는 사용하지 않으며 이름은 합성 alias로 기록합니다.

| 항목 | 이번 실습의 입력과 결과 | 실제 source에서 추가 확인할 것 | 확인 방법·담당자·진행 조건 |
|---|---|---|---|
| 도구 지원 | 선택 source/target·도구·offline/online mode | OS/엔진/버전·대상 기능·현재 지원 | 엔진별 공식 지원 문서와 평가 담당자를 지정합니다. |
| 연결 | client/service/agent의 실행 위치·DNS·TLS·포트 | 실제 source → 실행 주체 → target 경로·대역폭·egress | 네트워크 담당자가 승인된 경로와 시험 범위를 정합니다. |
| 인증·권한 | 관리 역할·데이터 역할·엔진 privilege | 실제 인증 방식·최소 scope·부여/회수 owner | 비밀 값을 적지 않고 필요한 권한과 승인자를 기록합니다. |
| 데이터·기능 | 작은 schema/파일·내용/속성 비교 | 크기·변화량·일관성·보존 속성·확장/객체 호환성 | 데이터 owner가 실제 비교 기준과 합성 test 입력을 정합니다. |
| 전환 | 개인 client의 새 읽기 연결 | writer·최종 sync·DNS/cache/connection pool·허용 중단 | 앱 owner가 쓰기 통제·GO/NO-GO 기준과 전환 순서를 정합니다. |
| 복구·정리 | source 보존·개인 파일 정리 | backup/복원 시험·RTO/RPO·새 target 쓰기 이후 복구·보존 기간 | 복구 담당자와 삭제 승인자를 구분합니다. |

1. 각 행에 현재 아는 사실과 추가 질문을 하나 이상 적습니다. 확인할 수 없는 항목은 담당자와 확인 방법을 정하고 실행을 보류합니다.
2. 선택 도구가 처리하는 copy·replication·CDC와 참가자가 확인하는 호환성·데이터·client 결과를 구분합니다. 관리형 이전 엔진을 별도 코드로 만들지 않습니다.
3. 준비가 완료되면 [target client 마무리](../cutover/README-ko.md#45a-이전-결과를-새-client에서-사용하는-마무리)의 새 연결·읽기 기준을 실제 workload에 맞춰 정합니다. 실제 운영 실행은 별도 승인을 따릅니다.

**제출 기준:** 한 workload의 여섯 행, 확인 방법·담당자·진행/중단 조건, 쓰기 전/후 복구 차이를 설명합니다. 관리형 복사 성공만으로 작성한 모든 준비 항목을 완료 처리하지 않습니다. Mover를 선택하면 서비스 도입 준비만 작성하며, 이 워크샵의 실행 경로는 별도 AzCopy입니다.

이 과제는 작성한 개인 표만 남기며 리소스·역할·source 설정을 변경하지 않습니다.

## 5. 완료 기준·대표 실패


**이 모듈의 완료는 계획 학습이지 migration 성공이 아닙니다.**

1. source 요구에 맞는 target·도구를 고르고 서비스가 맡는 기능을 설명합니다.
2. 대안 하나를 배제하는 근거와 미확인 사항을 명시합니다.
3. source 제약에 맞는 교육 모드·실습 범위와 제외 단계를 표시합니다.
4. test/go-no-go·cutover/rollback·비용·정리 책임을 정합니다.
5. 선택한 다음 모듈만 참조하고 모든 트랙을 선행 조건으로 만들지 않습니다.

대표 실패는 resource 이름만으로 target 선택, unknown을 없음으로 취급, 공식 job 기능을 자체 코드로 재구현, 문헌의 online을 무중단으로 번역, target 새 쓰기 이후 단순 연결 복귀를 rollback으로 간주하는 것입니다. 추가 source 근거·도구 제약부터 확인합니다.


## 6. 정리


이 모듈은 resource·job·source 변경을 만들지 않으므로 Azure 삭제 명령이 없습니다. 개인 메모·교육 기록은 비밀/고객 정보 없이 관리합니다.

실제 service를 사용하면 **job/project·source appliance·replica·임시 backup/storage·target**의 owner·보존·삭제 대상을 각각 구분합니다. project나 job을 삭제했다고 target·모든 비용이 없어지지는 않습니다. source는 rollback 조건·보존 기간·승인 없이 삭제하지 않습니다.


## 7. 실제 이전에서 추가로 고려할 사항


- 실제 dependency·쓰기량·RPO/RTO·backup/restore·호환성·보안/규제.
- data 일관성·network/egress·license·운영 인계·모니터링 공백.
- service 지원 변화·region/quota·비용과 실패 시 복구.
- 작은 합성 계획은 customer production 이전 승인·실제 assessment를 대신하지 않습니다. 관련 전문가 검토 항목을 연결합니다.


## 8. 출처


- CSV와 사례·계획표는 직접 작성한 교육 자료입니다. 외부 sample·실제 inventory·assessment 출력은 복사하지 않았습니다.
- 집중 검증 때 현재 service/version/region·source/target·준비/데모 수준·실제 확인한 결과와 미확인 범위를 기록합니다.
