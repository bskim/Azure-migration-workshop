# PostgreSQL — 전용 migration service로 validation·이전 결과 읽기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: RDS/Aurora PostgreSQL 또는 일반 PostgreSQL의 Azure 이전을 검토하는 엔지니어.
- 목표: **Azure Database for PostgreSQL의 전용 migration service**에서 source validation·offline/online·작업·cutover와 데이터 결과를 구분합니다.
- 기본 도구는 Flexible Server의 Portal migration 경험입니다. DMS Classic·dump/restore·자체 CDC로 대체하지 않습니다.
- 예상: 읽기 30분, 선택 합성 준비/서비스 validation 45~60분, offline migration/확인/정리 45~60분 + 환경 준비 대기. 시간은 회차 설계용 추정치입니다.

| 모드 | 입력 | 범위 |
|---|---|---|
| A: 개념/walkthrough | 공식 문헌·SQL·합성 사례 | Azure/AWS 로그인·DB/데이터/job 생성 없이 읽기 |
| B: native 합성 실습 | 승인된 private PostgreSQL source·빈 Flexible Server target·서비스 연결/권한 | Portal 또는 공식 CLI의 Validate → 별도 승인한 offline job → schema/data 결과 |
| C: 선택 비교 | 별도로 승인한 local source/target·현재 client 도구 | pg_dump/restore의 작은 비교. B의 서비스 성공으로 보고하지 않음 |

MySQL·SQL Server·컴퓨트·Terraform·공통 앱의 완료가 필요 없습니다. 실제 AWS는 만들지 않으므로 B는 **서비스가 지원하고 접근 가능한 준비된 합성 PostgreSQL source**를 입력받습니다. 강사가 source를 제공해도 해당 compute 트랙 수강을 요구하지 않습니다. 이 실행은 기존 private 검사 VM을 source/client로 재사용했으며 새 앱·AWS 환경을 만들지 않았습니다.


## 2. 서비스 소개·source와 도구 선택


### 2.1 Portal에서 DMS 소개와 PostgreSQL 전용 서비스를 함께 비교


MySQL/SQL Server와 같은 [DMS Get started 소개](../database-mysql/README-ko.md#21-dms-개념과-엔진별-선택을-실제-portal에서-읽기)를 먼저 읽습니다. DMS라는 포괄적 이름만으로 모든 엔진을 같은 service/task/API로 처리하지 않습니다.

![PostgreSQL 선택이 target Flexible Server의 전용 migration service로 연결되는 화면](./images/portal-postgresql-service-selection.png)

*actual Portal screenshot, Subscription 마스킹. 새 source/target/job을 생성하지 않았습니다. 기존 실습 target는 이미 삭제돼 여기서는 target 선택/Go to target server 이후를 실행하지 않았습니다.*

참가자는 이 화면과 [전용 서비스 소개](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql)를 읽고 PostgreSQL과 MySQL의 도구·validation·offline 절차 차이를 설명합니다. 도구를 선택한 뒤 native job과 schema/data 결과를 각각 확인합니다.

| 서비스/기능 | Microsoft Learn 소개 | 이 모듈에서 볼 내용 |
|---|---|---|
| PostgreSQL Flexible Server | [서비스 개요](https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview) | 관리형 target·version·운영 책임 |
| PostgreSQL migration service | [전용 서비스 소개](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql) | 엔진별 validation·offline/online·migration 경험 |
| Source/target network | [Migration network guide](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/how-to-network-setup-migration-service) | 실제 service→DB 연결 |
| Azure RBAC | [RBAC 개요](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview) | Azure 관리 권한과 DB login/privilege의 구분 |

전용 서비스는 RDS/Aurora PostgreSQL·Azure VM/on-premises 등 source별 흐름을 제공합니다. **지원되는 source 이름과 현재 OS/engine/extension·권한·network의 실제 준비는 다른 것**입니다.

기본 교육은 소량 offline을 선택합니다. online은 initial copy 뒤 변화 추적·최종 sync/cutover와 source 영향·제약이 추가되므로 별도 확장입니다. “online”을 무중단으로 번역하지 않습니다. pg_dump/restore는 목적/중단/데이터 흐름을 비교하는 공식 utility이며 전용 Portal job을 대체하는 자체 engine을 만들지 않습니다.


## 3. 사전 준비·권한·비용


- A는 문서/SQL 읽기만 합니다. B의 제어 환경은 **Azure portal**, source load/결과 비교만 현재 `psql`·pgAdmin 등 승인된 client를 사용합니다.
- 계획 사례의 PostgreSQL 15는 가상 요구입니다. 선택한 source는 16.15, target은 18.6이며 `workshop`만 이전했습니다. 15의 이전 성공이나 다른 workload의 major upgrade 호환성을 이 결과로 보장하지 않습니다. 현재 서비스·리전/version·extension 지원을 먼저 확인합니다.
- 새 target·migration 관리 권한과 **engine user/role**을 별도로 승인합니다. Azure Contributor/Owner가 DB superuser라는 뜻이 아닙니다.
- native service가 읽는 source와 만드는 target object의 현재 필요한 privilege·TLS/auth를 확인합니다. 비밀번호를 command line·SQL asset·Git·Copilot에 넣지 않습니다.
- Portal의 승인된 비밀 입력 또는 개인 protected properties 파일을 사용합니다. [migration.example.json](./lab/migration.example.json)은 placeholder뿐이며 실제 값은 Git 제외 경로·private VM의 제한된 파일에만 작성합니다. credentials/property 파일은 owner 전용 권한으로 보관하고 전체 migration JSON/`secretParameters`를 공유 로그에 출력하지 않습니다.
- 실제 service의 source reachability·DNS·TLS·5432·`pg_hba.conf` 조건을 확인합니다. 로컬 Docker가 켜져 있다는 것으로 Azure에서 접근 가능하다고 하지 않습니다. source를 전체 인터넷에 열거나 TLS를 끄지 않습니다.
- 같은 VNet의 private VM → **VNet-integrated target**은 별도 runtime 없이 확인한 경로입니다. target이 Private Endpoint만 사용한다면 private source로의 outbound를 위해 [migration runtime server](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/concepts-migration-service-runtime-server)가 필요할 수 있습니다. 두 방식의 연결·DNS·권한·추가 비용을 혼동하지 않습니다.
- 데이터 포트 5432는 승인된 source와 DB subnet 사이에만 허용합니다. 임시 검사 환경을 재사용해도 Blob/다른 입력의 private 설정을 해제하지 않습니다. 실제 계정/target의 public Disabled·delegated subnet·DNS·TLS·auth를 확인합니다.
- [현재 migration 제한](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/concepts-known-issues-migration-service)은 native source SSL을 Prefer/Require로 설명합니다. 이 AzureVM source에는 Require를 명시했습니다. source/target SQL 클라이언트는 별도로 `verify-full`을 확인했으며 이것이 native worker의 CA/hostname verification까지 증명한다고 말하지 않습니다.
- PostgreSQL provider quota CLI가 BadRequest이면 0/무제한 quota로 해석하지 않습니다. supported SKU·현재 사용량·공식 한도/Portal 확인과 실제 생성 결과를 구분합니다. 이 요청한 2 vCore target은 실제 Ready로 확인했지만 이후 capacity를 보장하지 않습니다.
- 비용: synthetic source 준비, Flexible Server target·storage/backup·필요 runtime/network. HA·read replica·큰 data는 제외한 새 교육용 target만 사용합니다. [가격 계산기](https://azure.microsoft.com/en-us/pricing/calculator/)로 한도를 승인합니다.
- native migration이 모든 source parameter·global user/role·superuser privilege를 옮겨 준다고 하지 않습니다. source/target role·extension·parameter는 별도 검토입니다.
- source가 제공되지 않거나 service 연결을 준비할 수 없으면 A/강사 walkthrough만 선택합니다. 새 CLI wrapper로 준비 조건을 숨기지 않습니다.


## 4. 순서별 instruction — B는 선택 범위 승인 후 실행


### 4.1 사례·입력·owner 정하기


[이전 계획](../planning/README-ko.md)의 `postgresql-sample`을 고릅니다. 이 기본 dataset은 [공통 DB sample](../../../shared/database-sample/README-ko.md)의 3 tables·30 rows이며 실제 RDS/Aurora 데이터가 아닙니다.

source owner, 새 target `rg-amw-pg-<lab-id>`/server, 선택 runtime, network·role·비용·보존 조건을 정합니다. 기존 target DB는 가져오지 않습니다. source 정보/인증은 native service의 승인된 경로로만 전달하고 여기에는 비밀 값을 기록하지 않습니다.


### 4.2 합성 source만 준비 — target에는 seed하지 않음


1. 강사/DB 관리자가 승인된 **새 source DB `workshop`**와 접속·오류 중단 설정을 준비합니다.
2. 실제 server/DB/session/owner·`public` schema를 대조합니다. source와 target의 data/읽기 query session은 `SET search_path = public;`로 같은 선택 범위를 명시합니다. localhost source면 local comparison일 뿐 native 서비스가 접근 가능한지 별도로 확인합니다.
3. [PostgreSQL schema](./lab/schema.sql)를 source에 한 번 실행합니다.
4. [seed.sql](../../../shared/database-sample/seed.sql)을 source에 한 번 실행합니다.
5. [verify.sql](../../../shared/database-sample/verify.sql)의 source baseline을 기록합니다. 기대값은 table별 10, join 10, quantity 합계 55입니다.

실행 도구는 승인된 SQL client이며 `psql`을 쓰면 `ON_ERROR_STOP=1`과 정확한 DB/SSL 설정을 적용합니다. source가 기존/운영이거나 object/data가 있으면 중단합니다. 실패 후 DROP·TRUNCATE·중복 seed로 “성공”을 만들지 않습니다.

**관찰할 결과:** synthetic schema·PK/FK/CHECK/unique와 30 rows baseline. 이 SQL은 PostgreSQL 16.15 local에서 확인했고 재현 범위는 [공통 SQL 검증](../../../shared/database-sample/README-ko.md)을 따릅니다. target에 같은 data를 먼저 넣으면 migration 결과를 구분할 수 없으므로 seed는 source-only입니다.


### 4.3 새 Flexible Server target와 Portal task 준비


1. 승인된 tenant/subscription/region에서 별도 작은 target을 만듭니다. source와 DB version·support·storage/backup·network/TLS를 확인합니다.
2. Portal target의 **Migration → Create** 또는 현재 공식 경험을 엽니다.
3. unique migration 이름을 정하고 **실제 준비 source의 유형**을 선택합니다. 합성 Azure VM source면 그 유형을 고르며 실제 AWS가 없는데 RDS/Aurora source를 연결한 것으로 표시하지 않습니다.
4. 첫 migration option은 **Validate**만 고릅니다. `Validate and migrate`는 validation 성공 시 실제 이전을 시작할 수 있으므로 두 버튼을 같은 의미로 쓰지 않습니다.
5. 기본 mode는 **Offline**입니다. 필요한 runtime server와 source/target connection·권한·TLS·service network를 검토합니다.
6. native credential 입력은 Portal의 승인된 service 필드에서 수행합니다. source/target test connection 결과를 읽고 실패하면 다음으로 넘어가지 않습니다.
7. 선택 DB는 `workshop`만, 시스템/다른 workload DB는 제외합니다. target이 기존 데이터와 충돌하지 않는지 확인합니다.

**관찰할 결과:** source/target·선택 DB·validation task의 준비입니다. 아직 job 성공이 아닙니다. source credential을 기초 모듈의 Managed Identity 토큰과 같은 것으로 설명하지 않습니다.

target create의 비동기 접수 응답에는 resource `properties`가 없을 수 있습니다. 같은 이름을 재생성하지 말고 공식 `show`/`wait`로 Ready와 실제 network를 확인합니다. 최종 network 구성은 Ready 이후 show 출력으로 확인합니다.


### 4.4 Native validation 결과부터 읽기


1. DB·mode·network·권한·비용/영향을 대조하고 승인한 후 validation을 시작합니다.
2. Portal의 validation 결과·warning/error·source/target readiness를 읽습니다.
3. engine version·extension·parameter·role·connection·schema 문제를 확인해 조치/미확인 항목을 적습니다.
4. 오류가 남으면 migration을 시작하지 않습니다. validation 성공도 source 변화·전체 app 호환성·runtime 성능을 보장하지 않습니다.

**기대 결과:** service가 검사한 범위와 남은 조치를 설명합니다. “Portal 작업 생성”이나 “source test connection 성공”만으로 migration 완료를 보고하지 않습니다.

**공식 CLI 대안, 관리 권한을 가진 승인된 실행 위치:** 첫 create는 아래처럼 `Validate`를 명시합니다. 기본값 `ValidateAndMigrate`는 검증 후 복사를 시작할 수 있습니다. target overwrite도 기본적으로 허용될 수 있으므로 예제의 `overwriteDbsInTarget: False`와 실제 빈 target 검사를 유지합니다.

```bash
: "${PG_GROUP:?Set the approved new PostgreSQL group}"
: "${PG_TARGET:?Set the approved private target}"
: "${PG_VALIDATE_NAME:?Set a unique validation name}"
: "${PG_PROPERTIES_FILE:?Set the owner-private properties file path}"
: "${AZURE_SUBSCRIPTION_ID:?Set the approved subscription}"
az postgres flexible-server migration create \
  --resource-group "$PG_GROUP" --server-name "$PG_TARGET" --name "$PG_VALIDATE_NAME" \
  --properties "$PG_PROPERTIES_FILE" --migration-mode offline --migration-option Validate \
  --subscription "$AZURE_SUBSCRIPTION_ID" \
  --query '{name:name,option:migrationOption,mode:migrationMode,status:currentStatus}'
az postgres flexible-server migration show \
  --resource-group "$PG_GROUP" --server-name "$PG_TARGET" --name "$PG_VALIDATE_NAME" \
  --subscription "$AZURE_SUBSCRIPTION_ID" \
  --query '{name:name,option:migrationOption,mode:migrationMode,status:currentStatus}'
```

properties 파일을 사용하는 첫 create의 전체 응답도 비밀이 포함될 수 있으므로 개인 protected 기록으로만 보관합니다. 공유 화면에서는 필요한 name/option/mode/currentStatus만 선택합니다. CLI의 JSON shape와 enum은 [공식 migration schema](https://learn.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/2024-08-01/flexibleservers/migrations)와 설치된 version으로 확인합니다. `overwriteDbsInTarget`, `startDataMigration` 등은 schema의 `False`/`True` 문자열이며 임의의 boolean/default로 바꾸지 않습니다.


### 4.5 승인된 offline migration과 모니터링


1. source writes가 멈춘 실습 DB이며 baseline·backup/복구·owner가 확인됐는지 대조합니다.
2. native 경험에서 검증된 입력으로 실제 migration을 선택합니다. 현재 option의 실행 영향과 target DB 생성/충돌 처리를 확인합니다.
3. 시작 승인을 받고 service의 전체/DB별 상태·단계·error·시간을 관찰합니다.
4. service 실패를 짧은 자체 retry loop/CDC로 대체하지 않습니다. 원인·지원 조치를 읽고 source/target을 보호합니다.
5. 완료되면 4.6의 schema/data 확인을 수행합니다. source는 삭제하지 않습니다.

Online은 별도 선택 확장입니다. replication/source 권한·parameters·primary key/제약·change rate·target writes·최종 sync/cutover와 비용을 별도로 검토하며 기본 offline 실습에 자동 추가하지 않습니다.

Source writer를 통제하고 baseline을 보존합니다. `default_transaction_read_only=on`은 owner가 override할 수 있어 운영 writer 중단·connection drain·승인을 대신하지 않습니다. 실제 job에는 검증한 입력과 별도 승인한 Migrate/Offline·startDataMigration=True·overwrite=False를 사용합니다.


### 4.6 같은 SQL로 source/target 데이터 확인

승인 **target Flexible Server → Migration → 선택 offline migration → DB details**에서 **`workshop`**의 Migration Succeeded·message를 읽습니다.

![workshop의 PostgreSQL native migration DB 결과](./images/portal-native-migration-result.png)

*예시 DB row는 Migration Succeeded / Migration successful·표시 DB duration00:00:04입니다. DB 단계와 전체 job duration은 포함 작업이 다릅니다. service 완료와 아래 독립 schema/전체행/TLS/source baseline을 함께 확인합니다.*

제공 합성 schema는 **column 8개·PK/FK/CHECK/unique constraint 7개·전체 30행**을 비교합니다. native offline job의 완료 table 3개·table error 0, 원래 source baseline 불변, source/target SQL connection의 독립적인 `verify-full` 검증을 함께 확인합니다. NOT NULL column attribute와 version별 constraint catalog 표현은 구분합니다.


source 동결 상태에서 target `workshop`를 명시적으로 선택합니다. 읽기 전용 [verify.sql](../../../shared/database-sample/verify.sql)을 source와 target 각각 실행하고 결과를 비교합니다.

| 확인 | 기대 기준 |
|---|---|
| Schema | 3 tables, column/type·PK/FK/CHECK/unique를 확인 |
| Row counts | 각각 10, 총 30 |
| 대표 query | join rows 10, quantity sum 55 |
| 정렬된 join 전체 | id·label·name·quantity 10행의 source/target 일치 |
| Native evidence | 실제 task 상태·검사/이전 범위·warning/error와 data 비교 결과를 함께 기록 |

count/sum만 같다는 것으로 전체 DB를 검증했다고 하지 않습니다. service/schema/data가 다르면 failure로 기록하고 source 변화·mapping·role·unsupported object를 확인합니다.

**공통 앱은 현재 memory API이며 DB adapter가 없습니다.** 앱/DB 연결은 선택 확장으로 별도 작성·검증할 대상이고 지금 앱 연결 성공을 주장하지 않습니다.

[compare-native.py](./verify/compare-native.py)는 승인된 private Linux client에서 **읽기 전용**으로 native job 상태·source/target을 비교합니다. Python 3·psql·관리 조회용 Azure CLI, owner 전용 `credentials.json`(`sourcePassword`/`targetPassword`), source CA·원래 verify SQL/baseline이 보호된 작업 폴더에 있어야 합니다. 예제 fixture의 DB/user는 `workshop`/`workshopadmin`이며 실제 고객 DB의 범용 비교 도구가 아닙니다.

아래는 해당 비교 프로그램을 승인된 방법으로 private client에 전달한 뒤 **그 파일이 있는 폴더의 VM/Linux Bash**에서 실행합니다. 비밀 파일은 다른 실행 위치로 복사하지 않습니다. 읽기 비교의 입력 변수도 승인된 실제 source/target와 native job 이름으로 명시합니다.

```bash
python3 compare-native.py \
  "$PG_SOURCE_HOST" "$PG_TARGET_HOST" "$PG_PROTECTED_DIRECTORY" \
  "$AZURE_SUBSCRIPTION_ID" "$PG_GROUP" "$PG_TARGET" "$PG_MIGRATION_NAME"
```

Run Command로 프로그램을 전달할 때 큰 Python source를 base64 **parameter**에 넣으면 Windows `az.cmd` 길이 제한·guest argument parsing 문제가 생길 수 있습니다. 코드는 script 파일 payload로 보내고 짧은 입력만 parameter로 줍니다. Run Command의 외부 성공과 실제 guest pass/실패를 구분합니다.


### 4.7 작은 utility 비교·cutover/rollback


[컷오버·롤백](../cutover/README-ko.md)의 카드/runbook으로 native 완료·개인 읽기 client 전환·새 writes 이후 data 복구를 구분합니다. 없는 앱 DB adapter를 연결한 것처럼 실행하지 않습니다.

A/B의 목표를 바꾸지 않는 선택 비교로 `pg_dump`/`pg_restore`의 logical backup/복원·중단/권한·client version·globals/role 한계를 읽습니다. 승인된 synthetic source/target 외에서는 dump/복원을 실행하지 않으며 비밀/고객 data를 Git에 저장하지 않습니다.

이 비교 결과를 native migration service job 성공으로 쓰지 않습니다. 실제 cutover는 [계획](../planning/README-ko.md)의 최종 sync·쓰기 정지·go/no-go·connection 변경·target 관찰/rollback을 따릅니다. target 새 writes 뒤 connection만 되돌리는 것은 data rollback이 아닙니다.


**선택 마무리:** native 작업과 schema/data 비교를 마친 뒤, 승인된 SQL client로 target FQDN·`workshop`에 새 연결을 만들고 기존 검증 query를 읽기 실행합니다. [target client 마무리](../cutover/README-ko.md#45a-이전-결과를-새-client에서-사용하는-마무리)에 실제 대상·총 30행·join 10행·sum 55와 관찰 결과를 기록합니다. source·backup과 원래 profile은 보존합니다. 앱 adapter 없이 진행하며, [실제 source 준비 과제](../planning/README-ko.md#48-합성-source를-실제-source로-바꿀-때의-준비-과제)에서 엔진/extension·권한·연결·변경분·복구 질문을 정리합니다.

## 5. 대표 실패


| 실패 | 조치 방향 |
|---|---|
| service가 source에 접근 못함 | 실제 network/DNS/TLS/5432·engine auth·runtime 조건 확인. 광범위 공개/TLS 해제 금지 |
| validation version/extension/role 실패 | 현재 support와 source 기능·parameter/global role의 수동 조치 확인 |
| source load 실패 | 새 DB/session·DDL transaction/오류 중단·기존 object·권한 확인. 자동 삭제/reseed 금지 |
| migration job 성공·query 다름 | source 변화·table/schema mapping·constraints·warnings와 실제 data 비교 |
| online 준비 부족 | offline과 다르게 필요한 replication/PK/source permission/cutover를 확인. 무중단 보장 금지 |


## 6. 정리 — source/target/job/runtime은 각각 owner가 다를 수 있음


A는 삭제 대상이 없습니다. B/C를 실제 실행했다면 service job·target·runtime·synthetic source·backup/임시 파일·role/network를 목록으로 대조하고 보존/rollback을 승인합니다.

1. 실행 중 task·sync·connection이 남지 않았는지 현재 서비스 상태를 확인합니다.
2. Portal job 삭제/cancel의 영향과 target DB/server 삭제를 구분합니다. job만 지웠다고 DB 비용이 없어졌다고 하지 않습니다.
3. 이 모듈의 새 target/runtime 그룹·lab 식별·resource 목록을 확인하고 승인 후 소유한 것만 정리합니다.
4. 강사가 제공한 외부 source·network·credential·다른 target은 삭제/변경하지 않습니다. 자신이 만든 synthetic source도 retention/복구 기준·owner 승인 이후 정리합니다.
5. temporary dump 등은 정확한 해당 파일만 제거하고 입력 SQL·전체 `lab-output`을 일괄 삭제하지 않습니다.
6. 실제 잔여 data/resource·role·비용을 확인합니다.

이 문서에는 customer DB의 DROP·TRUNCATE나 광범위 source 삭제 명령을 넣지 않았습니다.


## 7. 실제 이전에서 추가로 고려할 사항


- RDS/Aurora 기능·source version·extension·collation·encoding·sequence/large object·partition/trigger.
- source/target role·parameter·superuser 제약·connection pool·성능 baseline.
- backup/RPO/RTO·change rate·일관성·cutover/rollback·DNS/앱·운영 인계.
- 비용·network/egress·security/규제. 작은 offline sample이 실제 AWS/production 이전 검증은 아닙니다.


## 8. 출처


- source schema·공통 data/읽기 query·instruction은 직접 작성했습니다. 실제 DB·service output을 복사하지 않았습니다.
