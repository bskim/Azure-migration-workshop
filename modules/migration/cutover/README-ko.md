# 컷오버·롤백 — 전환 승인과 데이터 복귀를 따로 판단하기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: 서버·오브젝트·DB 이전의 마지막 전환/실패 대응을 배우려는 엔지니어.
- 목표: **go/no-go → source 쓰기 통제·최종 확인 → 연결 전환·관찰 → 복귀/data 복구 판단**의 담당자와 확인할 결과를 정합니다.
- 기본 방법은 tabletop 카드·작은 runbook과 native 서비스의 상태 읽기입니다. 전환 orchestrator·reverse replication·자동 복구 platform을 만들지 않습니다.
- 예상: 카드·runbook 30~40분, 선택 읽기 client 전환 20~30분, 복귀 판단 15분. 실제 시간은 기록합니다.

| 모드 | 입력 | 수행/제외 범위 |
|---|---|---|
| A: tabletop | 포함된 합성 결정 카드와 runbook | resource/job·app/DNS·SQL/data를 변경하지 않고 판단 |
| B: 읽기 전환 | 강사 또는 선택 모듈이 준비한 소유권 명확한 작은 source/target·읽기 client·baseline | client의 개인 실습 profile/URL만 전환. production DNS/app 설정·새 business writes는 하지 않음 |
| 실제 운영 cutover | 현재 범위 밖 | 실제 writers·최종 sync·복구·보안/운영 승인과 source/target별 별도 설계 필요 |

전체 DB·컴퓨트·오브젝트 모듈을 완료하지 않습니다. B에 필요한 **선택 워크로드 하나의 입력**을 제공받는 것이 해당 모듈을 수강해야 한다는 뜻은 아닙니다.

공통 앱은 memory API이며 DB adapter가 없습니다. DB client 연결을 바꾼 결과를 앱 DB 전환 성공이라고 하지 않고, 두 memory API의 읽기 비교도 영속 데이터 이전/rollback으로 표시하지 않습니다.


## 2. 서비스 소개·native 동작과 전환의 차이


| 선택 경로 | Microsoft Learn 소개/흐름 | 이 모듈에서 구분할 것 |
|---|---|---|
| Azure Migrate | [Migrate 개요](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview), [서버 migration 흐름](https://learn.microsoft.com/en-us/azure/migrate/tutorial-migrate-physical-virtual-machines) | test cleanup·final migration·Complete migration·source/target 전환 |
| Storage Mover/AzCopy | [Mover 개요](https://learn.microsoft.com/en-us/azure/storage-mover/service-overview), [AzCopy 소개](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10) | copy 완료와 source 쓰기 정지·delta·consumer URL 전환 |
| PostgreSQL migration service | [서비스 소개](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/overview-migration-service-postgresql), [online cutover 흐름](https://learn.microsoft.com/en-us/azure/postgresql/migrate/migration-service/tutorial-migration-service-iaas-online) | Waiting for user action·최종 changes·source writes·target 접속 |
| Azure DMS | [DMS 개요](https://learn.microsoft.com/en-us/azure/dms/dms-overview), [타깃별 지원](https://learn.microsoft.com/en-us/azure/dms/resource-scenario-status) | offline/online·job/restore 상태·instance 기능·consumer 전환 |
| Azure Monitor | [Monitor 개요](https://learn.microsoft.com/en-us/azure/azure-monitor/overview) | 관리 이벤트·native job·실제 app/data 관찰의 다른 근거 |

**서비스 job 성공 ≠ 새 연결 수용 ≠ 운영 cutover 완료**입니다. Cancel/stop replication/Complete migration은 각각의 data 영향이 있으며 일반적인 data rollback 명령이 아닙니다. source/target에 어떤 changes가 남는지 현재 service 문헌과 실제 상태로 확인합니다.

Online도 최종 sync·쓰기 정지·DNS/connection·consumer 재시작/재연결로 중단이 발생할 수 있습니다. lag가 낮다는 사실만으로 중단 0·data 유실 0을 보장하지 않습니다.


## 3. 사전 준비·권한·비용·안전


- A는 문서 편집기/표와 카드만 사용합니다. Azure/AWS 로그인·도구 설치가 필요 없습니다.
- B는 승인된 source/target 이름·owner·native 결과·data baseline·읽기 client/profile을 준비합니다. client는 선택 DB의 승인된 SQL 도구 또는 Blob 읽기 URL/Portal 등 **하나**입니다.
- profile/URL에는 실제 target 확인 정보가 필요하지만 password·token·connection secret은 runbook·Git·Copilot에 넣지 않습니다. 기록에는 alias/안전한 evidence만 사용합니다.
- native replication/migration이 target에 만드는 data와 **새 business writes**를 구분합니다. B에는 일반 app·batch·queue 등의 외부 writer를 붙이지 않습니다.
- source freeze/resume, native cutover, client config, writer 허용, cleanup은 owner와 필요한 권한/승인이 다릅니다. 테스트 client만 읽었다고 전체 workload의 쓰기가 없었다고 하지 않습니다.
- 기본 실습은 실제 DNS·production app/connection pool·source DB global readonly·NSG·권한을 변경하지 않습니다.
- B의 source/target는 기존 실습 비용이 계속 발생할 수 있습니다. 새 backup/replica·runtime·target 등은 별도 비용 승인 없이는 만들지 않습니다.
- source·backup·이전 client profile을 보존하고 rollback을 없애는 job completion/삭제를 자동 호출하지 않습니다.
- data/state가 unknown이거나 실제 입력이 없으면 A만 진행합니다. 이 경우 B가 성공했다고 기록하지 않습니다.


## 4. 단계별 instruction — 한 workload만


### 4.1 카드 하나와 runbook 범위 선택


[합성 결정 카드](./lab/decision-cards-ko.md) A~D 중 하나를 고르고 [runbook.csv](./lab/runbook.csv)를 개인 실습 표로 읽습니다. CSV의 owner는 미지정, status는 `not_checked`, evidence는 `evidence_missing`이므로 이미 승인/검사가 끝난 계획이 아닙니다.

선택 워크로드·교육 모드·source/target alias·관찰 범위·중단 목표·owner를 채웁니다. 기존 customer 식별정보나 source 인증을 넣지 않습니다. 자동 실행/승인 schema로 CSV를 사용하지 않습니다.


### 4.2 준비 게이트 — GO 전에 필요한 증거


| 게이트 | 확인·승인할 것 |
|---|---|
| Scope/ownership | source/target·job·client·선택 data가 자기 실습 범위이며 보호할 외부 대상이 없는가 |
| Source protection | backup/복구·source 보존·원래 profile/접근과 유지 기간이 정해졌는가 |
| Writers | app·scheduler·queue·DB job·수동 client 등 쓰기 주체가 파악됐는가 |
| Native action | 선택 service의 현재 상태·변경 영향·필요 마지막 sync/cutover가 확인됐는가 |
| Data/feature | source/target 실제 schema/내용/대표 읽기와 필요한 기능이 기준에 맞는가 |
| Consumer/관측 | target로 실제 읽는지 확인할 client·scope·시각·log/error 관찰 방법이 있는가 |
| Approval/rollback | GO/NO-GO·복귀/data 복구·source 재개·삭제의 승인자를 정합니다. |

확인하지 못한 항목은 미확인으로 유지합니다. **미지정 owner·빈 evidence·CSV 기대값만으로 GO하지 않습니다.**


### 4.3 Source 쓰기 통제·최종 sync의 의미 읽기


A는 owner에게 요청할 실제 evidence만 토론합니다. B는 외부 writer 없는 synthetic source·target와 baseline을 owner가 확인합니다. production service를 정지하거나 server 전체 readonly를 누르지 않습니다.

선택 native 경로에 따라 필요한 상태를 읽습니다.

| 경로 | 전환 직전에 확인할 것·실행 경계 |
|---|---|
| Azure Migrate | 실제 supported source의 test 결과·source 정지 책임·final 복제·target boot/service. CSV assessment만으로 여기까지 준비됐다고 하지 않음 |
| Objects | source 변화 정지·마지막 copy/delta의 범위·정확한 key/bytes/내용/선택 metadata. job 종료는 consumer URL 전환이 아님 |
| PostgreSQL online | current Waiting/cutover state·source writes 중지·latency/마지막 changes·서비스 최종 처리. 최소 lag를 data/app accept의 대체로 쓰지 않음 |
| MySQL/SQL DMS | 해당 offline/online·backup/최종 sync/restore·table/schema/object 결과와 source 변경. 모든 target에 같은 cutover 버튼을 적용하지 않음 |

실제 native action은 해당 service 모듈의 현재 절차와 별도 승인을 따릅니다. copy/job 취소나 stop replication을 “이전 전 상태로 자동 복구”라고 표시하지 않습니다.


### 4.4 GO/NO-GO와 client 읽기 전환


1. 준비/최종 data·기능·native 상태를 기록합니다.
2. owner가 GO 또는 NO-GO와 이유를 결정합니다. unknown/불일치/목표 시간·비용 초과면 중단합니다.
3. B의 client에는 이전 **SOURCE** profile/URL을 보존하고 별도의 **TARGET** 읽기 profile/URL을 준비합니다. 설정·secret을 overwrite하거나 공개 export하지 않습니다.
4. 실제 server/account·DB/container·namespace가 승인된 target인지 client/Portal에서 대조합니다. 이름/데이터가 비슷하다는 이유만으로 맞다고 하지 않습니다.
5. 승인 후 개인 실습 client의 읽기 대상만 TARGET으로 바꾸고 기존 session/cache가 아닌 **새 연결/요청**으로 확인합니다.
6. 이 단계에서는 새 business writes를 허용하지 않습니다. DNS/production app/전체 connection pool 전환을 실행하지 않습니다.

**관찰할 결과:** 새 읽기 client가 승인된 target를 읽는지 확인합니다. 전체 앱/운영 traffic 전환은 별도 범위로 진행하며 native task 완료 이후 실제 client 읽기를 점검합니다.


### 4.5 선택 workload의 같은 기준으로 관찰


| 선택 입력 | 읽기 전환 때 쓸 기준 |
|---|---|
| PostgreSQL/MySQL synthetic DB | 해당 모듈의 schema·각 table 10/total 30·join 10/sum 55·정렬된 10행과 source/target 비교 |
| SQL Server synthetic DB | dbo·해당 T-SQL·같은 data 기준. 작은 결과를 SQL Agent/cross-DB 기능 검증으로 쓰지 않음 |
| Objects synthetic 입력 | Portal root 목록 3개·actual bytes·SHA-256·선택 content type/metadata |
| 준비된 서버/앱 | 실제 test target의 boot/service·승인된 대표 읽기/설정·기능·관측. source가 없으면 합성 토론만 |

값은 각 자료의 **기대 기준**이며 실제 실행 결과와 구분합니다. native/schema·app/data·연결·관측을 구분합니다. B의 읽기 전환에서 기본 앱은 memory API이므로 실제 DB migration/app adapter가 확인됐다고 하지 않습니다.


### 4.6 실패 카드 — 새 쓰기 전/후/unknown을 나누기


기본은 tabletop입니다. B에서 접속 실패를 관찰하려면 **새 isolated 실패 profile**만 준비합니다. 예를 들어 강사가 지정한 `invalid.example.invalid`의 가상 target를 읽는 별도 연습 profile을 사용하고 실제 credential·정상 profile·production network/DNS를 변경하지 않습니다.

| 상태 | 할 수 있는 판단 | 하면 안 되는 것 |
|---|---|---|
| 새 target business writes가 없음을 확인한 상태 | source가 안전하고 이전 profile/권한/기준·owner 승인 조건이 맞으면 개인 읽기 client를 SOURCE로 복귀 | 확인 없이 writer를 재개하거나 native job/target를 삭제 |
| 새 target business writes 있음 | 승인된 writes 중지·target/source 보존·차이 확인·reconciliation/restore·허용 유실/RPO·복구 승인 계획 | connection만 되돌려 data rollback 성공으로 보고 |
| 쓰기 상태 unknown | NO-GO/복귀 승인 대기, owner와 실제 log/data를 확보 | “우리 test는 read-only”라는 이유로 전체 no-write로 기본 처리 |

source 복귀는 **config/읽기 경로 복귀**, data rollback은 **데이터 일관성·복구 문제**입니다. 카드 C/D는 실제 reverse copy·DELETE·복구 SQL을 실행하지 않습니다. 자동으로 target data를 덮거나 source에 합치지 않습니다.

B에서 개인 읽기 client를 SOURCE로 복귀했으면 actual source identity·baseline 읽기를 다시 확인합니다. write 재개는 owner의 별도 승인과 근거가 필요하며 이 read-only 실습에서는 수행하지 않습니다.


### 4.7 Acceptance·writer 허용·관찰 기간


선택 native 작업·target data/필요 기능·새 읽기 연결이 맞아도 writer를 켜는 것은 별도 결정입니다.

- 실제 cutover에서는 writer 허용·모니터링 기간·오류/latency·새 data 확인·stop 조건을 owner가 정합니다.
- 처음 target 새 write가 accepted되는 시점과 승인자를 기록합니다. 그 뒤 rollback 기준은 pre-write와 달라집니다.
- source backup/보존·native replication 종료·권한 회수·source 해지 시점은 acceptance/복구 조건과 연결합니다.
- Portal의 Complete/Cancel·service job 삭제·source DB 삭제를 하나의 “정리” 행동으로 묶지 않습니다.

현재 A/B의 기본 학습은 판단/읽기 전환뿐이며 실제 writer·source 해지는 하지 않습니다.


## 5. 완료 기준·대표 실패


| 완료/실패 판단 | 설명해야 할 것 |
|---|---|
| Tabletop 완료 | 카드별 GO/NO-GO·미확인·owner·source 보호·config 복귀/data 복구 차이를 설명 |
| 선택 B | 한 owned workload의 actual 읽기 target·새 연결·baseline·승인된 SOURCE 복귀 관찰 |
| Native status만 있음 | data/기능·consumer 연결·writer 근거가 없으면 운영 accept 아님 |
| 읽기는 되는데 owner/쓰기 상태 불명 | 쓰기 발생/복구 책임·근거부터 확인. no-write 기본값 금지 |
| 같은 count지만 data/target가 다름 | actual destination·전체 작은 결과·mapping·필요 기능을 확인 |
| 연결 복귀 후 target event가 빠짐 | data rollback 미완료. 보존·writes 중지·복구 계획 필요 |


## 6. 정리 — 보존해야 할 것을 먼저 확인


A는 Azure 삭제 대상이 없습니다. B는 만든 개인 읽기/실패 test profile과 안전한 기록만 정리하고 이전 승인 profile을 덮지 않습니다. credential은 해당 client의 승인된 보관/정리 방법을 따릅니다.

source/target·job·appliance/runtime·backup·임시 storage·group은 **원 소유 모듈**이 정리합니다. 이 module에서 다른 모듈의 resource를 일괄 삭제하지 않습니다.

1. source 보호·target 새 writes·rollback/보존 상태·수용 승인을 확인합니다.
2. owner별 생성/삭제 대상·service action 영향·grants·보존 기간을 목록으로 대조합니다.
3. 모든 소비자가 종료되기 전 공유 image/input·source/backup을 삭제하지 않습니다.
4. source 해지·복제 종료/권한 회수·target 보존을 필요한 승인 순서로 실행합니다.
5. 실제 잔여 resource/data/role·비용과 미확인 항목을 기록합니다.

“복귀했으니 target/source를 전부 지운다”거나 job가 취소됐다는 이유로 target data도 원래대로 돌아갔다고 하지 않습니다.


## 7. 실제 이전에서 추가로 고려할 사항


- 모든 writer·외부 dependency·DNS TTL/cache/connection pool·부분 전환/이중 쓰기.
- source/target consistency·RPO/RTO·최종 delta·backup/restore·reverse/reconciliation 지원.
- native cutover의 되돌릴 수 없는 경계·모니터링·보안/규제·운영 인계.
- 팀/승인/incident·communication·비용/보존. 작은 tabletop은 production runbook 승인·실제 migration 시험을 대신하지 않습니다.


## 8. 출처
