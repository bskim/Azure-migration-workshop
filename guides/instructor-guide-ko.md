# 강사 가이드 — 준비·시간·diagnostic fixture·소유권

[English](./instructor-guide.md) | 한국어

학습자 module은 실행 단계·관찰 결과·정리를 설명하고 회차 설계·강사 준비·진단은 이 가이드에 둡니다. [선택표](../Readme-ko.md)·[참가자 준비](./participant-preparation-ko.md)·[조합](./module-combinations-ko.md)을 먼저 사용합니다.

**AWS 경계:** Terraform 분석·Azure 합성 data·공식 walkthrough로 학습합니다. 실제 AWS 환경 구축과 AWS resource·credential/AMI 조회·plan/apply는 실습 범위에서 제외합니다.

## 1. 회차 범위 합의

목표/source/module/mode와 사용할 browser/localPowerShell/WSL/VM/client를 정합니다. 승인된 target/region·비용 owner·image/digest/identity/source/target/private 입력을 확인합니다. 지원/version/quota·관리/data/engine/Kubernetes 권한·비용/timebox·관찰/stop/복구 기준과 생성/보존/cleanup owner를 비공개 기록으로 관리합니다.

선택한 트랙에 필요한 설치와 배포만 진행합니다. 읽기/walkthrough/준비 데모/live 합성 실습의 입력과 결과를 구분합니다. 사용할 endpoint의 현재 상태를 확인하고 native 복제/CDC/copy/scheduler/retry는 공식 platform에 맡깁니다.

## 2. 역할과 입력

| 역할 | 책임 |
|---|---|
| 강사 | module/mode선택·서비스설명·안전입력/데모·근거/timebox |
| 관리자/비용owner | tenant/scope/provider/region/quota·grant/회수·비용승인 |
| source/DBowner | 지원/권한/TLS/writer/backup/보존·복구 |
| 참가자 | 정확한대상·선택단계·오류관찰·자기정리 |

Contributor와 data/engine/Kubernetes 권한을 각각 확인합니다. 데모에는 준비된 합성 source만 사용합니다. 실제 값은 승인된 private 경로로 전달하고 Git/prompt/screenshot에는 넣지 않습니다.

앱은 DBadapter가 없는 memory API 하나입니다. VM/AKS/CAA는 같은 digest를 사용하고 Functions는 같은 source+adapter/host를 사용합니다. 이미지 준비 자료가 ACR/선택 UAI를 소유하며 consumer는 해당 입력을 보존합니다. PG/MySQL은 논리 SQL을 공유하고 SQLServer는 별도 T-SQL을 사용합니다. seed는 source에만 실행하고 target은 빈 상태로 준비합니다. 카드/계획 CSV는 사례 토론에 사용하고 서비스 import에는 공식 형식의 입력을 사용합니다.

## 3. Utility보다 서비스부터 소개

module의 MicrosoftLearn과 Portal 자료를 사용해 Mover→AzCopy, Migrate→VM/서버, DMS/engine/target→DButility/SqlPackage를 설명합니다. PG는 target 전용 migrationservice를 선택합니다.

screenshot에서 stage/field를 읽은 뒤 선택한 실습의 실제 결과를 확인합니다. IAM에서는 Checkaccess의 이전 view 링크로 Viewmyaccess에 진입할 수 있습니다. 공개 화면에서 userrow/식별정보를 제외합니다. form의 group/region은 승인된 입력과 대조하고 form 열기와 제출을 구분합니다.

### Storage Mover 제공 경계

**워크샵 제공 경계:** Storage Mover는 **서비스 소개만** 제공합니다. 관리 기능·적합한 source/workload·리전/비용/권한/network와 공식 문헌을 배우고 endpoint/project/job definition 생성·실행 role·copy 시작/검증은 실습하지 않습니다. 오브젝트 hands-on은 별도 공식 **private AzCopy**의 합성3개/109 bytes입니다. 이 선택은 Mover 전반의 미지원 결론이 아닙니다. 실제 고객 실행은 해당 지원 공식 시나리오와 고객 관리자 승인을 별도로 따릅니다.

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성합니다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인합니다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따릅니다. 인증과 network는 다른 통제입니다.

수업 밖 실행은 공식 source별 시나리오·관리 리전/metadata residency·비용·identity/data 권한·연결을 관리자와 확인합니다. 워크샵 오브젝트 실행 일정은 AzCopy만 대상으로 합니다.

## 4. Private Blob diagnostic fixture

기존 승인 endpoint/DNS/client를 우선 재사용합니다. 입력이 없으면 별도 범위·비용 승인 후 최소 group/VNet/subnet/PE/DNS와 선택 x64LinuxVM을 준비합니다. VMpublicNICIP/SSHinbound 없이 관리 RunCommand·선택 dataMI 권한을 사용합니다. NATpublicIP는 outbound용이며 Blob의 public 설정은 그대로 유지합니다. VM/disk/NAT/IP/PE/DNS/처리 비용을 확인하고 선택한 실습에 필요한 입력만 제공합니다.

publicDisabled/Deny/bypassNone·HTTPS/TLS·익명/SharedKey 금지 설정을 유지합니다. 실제 실행 위치에서 ApprovedPE/canonicalDNS/privateIP/TLS/data 요청을 확인합니다. hubclient와 서로 다른 spokePE 사이의 copy에서 CannotVerifyCopySource가 발생하면 공식 topology를 검토합니다. Mover의 지원 조건은 해당 서비스 문헌에서 확인합니다.

agent/설치 outbound를 승인합니다. HTTP/HTTPSport 규칙과 FQDNallowlist의 범위를 각각 검토하고 필요하면 승인된 proxy/mirror/preinstalled 도구를 제공합니다. AzurePlatformDNSAllow를 사용할 수 없으면 지원되는 platformDNS/IP 설정을 확인하고 정책은 유지합니다. wrapped/nullNICcreate 응답은 actualnicshow로 확인합니다. base64padding에는 명시적인 name=value를, 긴 source에는 scriptpayload를 사용합니다. secret은 argument로 전달하지 않습니다.

RunCommand 응답 이후 stdout/stderr/traceback/exit·정확한 PASS/FAIL과 guest/data 결과를 확인합니다. 출력 제한이 있으므로 전체 진단은 보호된 위치에 보관합니다. Blob 수업에는 DB 설치를 추가하지 않으며 client의 DBsource 재사용은 별도 승인 범위로 진행합니다.

## 5. DB·SQLImport fixture

이전 전 source 연결·version·native runtime·network·DB 권한을 준비합니다. local SQL 검사와 Azure 서비스의 source 접속을 각각 확인합니다. PostgreSQL의 VNet 통합 target과 PE-only/runtime 조건을 구분하고, SQL client와 native worker의 TLS 검증 조건을 각각 확인합니다.

PostgreSQL validation 오류는 code/native details·연결·지원·source 조건을 읽고 해결합니다. 재시도는 owner 승인과 검토한 입력으로 Validate를 명시하며 migration 시작은 별도 승인합니다. 완료 후 schema·전체 행·TLS·source baseline을 비교합니다.

MySQLoffline은 공식 문헌의 Premium tier와 runtime 연결 조건을 확인합니다. managementversion과 SELECTVERSION()을 각각 읽습니다. globalreadonly·targettruncate는 별도로 승인합니다. target의 빈 dms_persistent_objects는 workload 3개 외의 serviceartifact로 조사하며 추가 객체를 삭제하거나 비교에서 임의로 제외하지 않습니다.

SQL은 보존 요구부터 검토합니다. SQLDatabase3table 데모와 Agent/crossDB 기능 검사를 구분합니다. 사용할 Entra-only 설정과 DMS 도구의 인증 지원을 확인한 뒤 승인된 paidsource/SHIR를 준비합니다. genericEntra 지원과 선택 도구의 인증을 각각 확인하고 적용 정책을 유지합니다.

B2directSqlPackage는 privateWindowssource/client·공식 tool·sourceTLS/Windowsauth·targetDNS/MI·owner-onlyBACPAC을 준비합니다. BACPAC은 암호화되지 않은 파일이므로 소유자만 접근할 수 있는 위치에 보관합니다. 빈 target에 Import하고 기존 MIuserDROP 충돌이 발생하면 새 isolatedlogicalserver에 한정해 임시 MIEntraadmin·정확한 user 정리를 별도로 승인합니다. 결과와 관계없이 원래 admin·DB 권한 범위로 복구합니다. importedREAD_ONLY는 새 target에서만 복구하고 source 동결을 유지합니다.

새 SQL source는 승인된 SQL 관리자 권한·TLS 신뢰를 준비합니다. OS 관리자와 SQL sysadmin은 별도입니다. source 복구·임시 권한이 필요하면 새 sandbox만 별도 승인하고 정상 서비스·원래 권한·정확한 임시 artifact 정리를 확인합니다.

## 6. Functions·compute fixture

WSL에서 actualLinuxCoreTools/Azuritepath/version과 지원 설치 경로를 확인합니다. Windowsnpmpath가 있더라도 실제 Linux 도구 실행을 확인합니다. Python/source/package·승인 feed를 명시하고 .funcignore/localsettings 제외를 점검합니다. prebuilt/build-remotefalse와 CoreToolsremotepublish를 구분하며 localfeed와 cloudbuilder의 공급 경로를 각각 승인합니다.

host/deploymentstorageMI/role/private와 HTTPfunctionkey를 구분합니다. key는 private하게 보관하고 header로 전달하며 URL/log에는 넣지 않습니다. localauth와 Azureenforcement를 각각 점검하고 단일 instance HTTP 검사·scale-out 공유 상태를 별도 항목으로 확인합니다. 실습에서 시작한 host/emulator/port-forward만 종료합니다.

VMprivateRunCommand/publicSSH와 AKSprivateMIclient/localuserpublic32는 각각의 접근 경로입니다. 선택한 경로의 DNS/auth/role/flag와 systempool2node·지원/quota/cost를 확인합니다. externalregistry/VNet/NAT/DNS에 추가한 정확한 grant를 추적하고 consumer는 shared 입력을 보존합니다.

### 공통 마무리 연습 준비

[모듈 조합의 공통 연습](./module-combinations-ko.md#공통-마무리-연습-선택)에서 회차에 필요한 항목만 선택합니다.

- **target client:** 이전 모듈의 검증을 먼저 완료하고 source/profile을 보존합니다. 참가자에게 target alias·DB/container·읽기 client·기대값을 제공합니다. 새 앱·writer는 추가하지 않으며 CSV assessment는 실제 test target 없이 준비 과제로 마칩니다.
- **오류 구분:** 권한/네트워크 카드는 합성 토론으로 준비합니다. 실제 역할·NSG·DNS를 바꾸지 않습니다. 로컬 앱 관찰을 선택하면 기존 WSL 앱의 8080 loopback과 로그를 확인하고 다른 writer를 사용하지 않습니다. 404/422와 curl transport exit를 별도로 읽도록 안내합니다.
- **실제 source 준비:** 여섯 행의 개인 표에서 확인 방법·담당자·진행 조건을 설명하도록 합니다. 미확인 항목을 확인 담당자에게 연결하며 고객 정보·credential·실제 AWS 접속은 사용하지 않습니다.
- **종료:** 개인 profile·다운로드 파일·기록만 정리합니다. 원래 앱과 source/target·backup·공유 identity/network는 원 소유자가 관리합니다. 각 연습의 10~15분은 준비·대기와 구분해 배정합니다.

## 7. 시간·근거 해석

360+120분 일정과 module 시간은 회차 설계용 추정치입니다. 강사 setup·설명/질문·인증/권한·provision/job·검증·정리를 나누어 계획합니다. 실제 workload의 data 크기·리전·준비 조건에 따라 시간을 조정합니다.

### CSV import·앱 화면 준비

[서버 모듈](../modules/migration/servers/README-ko.md)의 [합성 inventory CSV](../modules/migration/servers/lab/synthetic-inventory.csv)는 가상 1행을 제공합니다. All projects → Create project → Start discovery → Using import → Server inventory (CSV) → Download .CSV file → Browse → Import 순서로 진행합니다. 공식 template의 27-column·합성 capacity/unknown을 유지하며 계획 workloads.csv는 사례 토론에만 사용합니다.

Portal의 **import 후 15분 대기**를 설명·assessment 시간과 나누어 계획합니다. Completed / Rows processed 1로 합성 inventory 수용을 확인한 뒤 assessment를 생성합니다. 다른 참가자·실제 discovery/replication source에 영향을 주지 않는 전용 owned project를 사용합니다.

CSV assessment는 **project Overview → Create assessment → Add workloads → 가상 imported server1개 → Add selection**을 가르칩니다. General/Advanced/Review 가정을 검토해 해당 assessment만 생성하고 Decide and plan → Assessments에서 읽습니다. [서버 모듈](../modules/migration/servers/README-ko.md)의 설정/review/source/target/견적 화면5개로 live source·target VM 없이 결과를 해석합니다.

없는 utilization/IOPS·표시 기본0은 측정 idle이 아닙니다. hardware 입력·저장 sizing 설정·추천 설명을 비교하고 단일 label만 믿지 않습니다. 고객 설계 수용 전 상충/default 가정을 확인하며 lifecycle·assessment 적합성·배포 가용성·실제 boot/app 준비를 구분합니다.

31×24시간 retail/noAHB/no예약의 예시 견적은 Defender 비용을 제외해 계산합니다. 실제 protection 설정은 유지합니다. 299.42USD를 선택 가정의 견적으로 읽고 실제 비용은 배포 계획·사용량·invoice에서 확인합니다. CSV-imported 항목은 assessment 범위로 다루며 실제 migration에는 지원되는 source와 별도 복제 준비가 필요합니다.

[Container Apps 모듈](../modules/onboarding/compute-container-apps/README-ko.md)은 active replica1 revision과 Real-time/Application stream controls를 보여줍니다. 승인된 실제 stream에서 200/201/422/404 요청을 대조할 수 있지만 privacy-cropped screenshot에는 해당 line이 없습니다. 상태/traffic/replica와 HTTP 근거를 따로 설명하고 Stop이 앱이 아니라 stream 보기를 닫는다는 점을 확인합니다. 새 capture는 selector/revision 식별정보를 가리고 payload를 제외한 뒤 공개합니다.

[MySQL native 결과](../modules/migration/database-mysql/README-ko.md)는 기존 owned classic service/project/Offline activity의 workshop과 table3개에서 읽습니다. 근사 ~10행·반올림 00:00:00·DB activity7초는 정확한 비교나 전체 회차 시간이 아닙니다. native 완료와 독립 30행/schema/source baseline/TLS 근거를 연결합니다.

[Objects 모듈](../modules/migration/objects/README-ko.md)은 Mover 소개·별도 AzCopy 실행입니다. 참가자 일정에 Mover setup/role/run/cleanup을 넣지 않습니다.


actualversion/region/mode/native/data/feature·오류/exit·writer·승인 scope·잔여 resource/grant/cost를 비공개 강사 기록에 정리합니다. 공개 자료에는 실제 ID/email/tenant를 넣지 않고 선택 입력·승인은 회차별로 확인합니다.

### Cost analysis·budget walkthrough 준비

[관측성 모듈](../modules/onboarding/observability/README-ko.md)의 날짜 preset·grouping·비용 차트·budget 입력·alert 조건 화면을 사용합니다. 승인 scope와 관찰 기간을 먼저 정합니다. 예시 차트는 Last 7 days·Group by Resource group으로 그룹 하나의 과거 사용 비용 $0.06을 보여줍니다. 현재 전체 비용은 scope·기간을 다시 선택해 읽고 invoice를 별도로 확인합니다. forecast가 없으면 필요한 사용 이력과 평가 조건을 확인합니다.

Cost analysis 화면 오류가 발생하면 정상 인증 SSO를 사용하는 새 Portal 탭에서 다시 조회합니다. 승인된 billing scope·인증 설정은 유지하고 비용 데이터가 표시되면 기간·금액을 확인합니다. navigation/loading/인증 대응 시간은 교육 내용과 나누어 계획합니다.

budget 소개에서는 form 입력을 읽습니다. 예시 값은 100 USD/Monthly·Actual cost 80%(80 USD)·Action group None입니다. 종료일은 실습 기간에 맞게 선택합니다. 실제 생성 전 scope/name/종료일/수신자·cleanup owner를 별도로 승인하고 생성 후 저장된 설정·알림 전달을 확인합니다. 기존 budget은 변경하지 않습니다.

## 8. 진행·대체 mode

목표/mode/input/cost/owner/stop부터 설명합니다. 공식 서비스 지원과 승인 단계를 확인하면서 기대 결과·실제 출력을 대조합니다. 긴 대기에는 상태·다음 확인 항목을 설명하고 SKU/권한은 자동 확대하지 않습니다. nativeerror/source 조건을 읽고 수정 승인 후 재검사합니다. native+data/app/feature 결과와 owner별 정리·보존으로 마무리합니다.

AWS가 없으면 guided/합성/prepared 결과를 사용하고 discovery/replication/S3/RDS 출력을 만들지 않습니다. Mover는 이 워크샵에서 항상 소개만 제공합니다. DB source/runtime 지원이 없으면 해당 walkthrough/demo를 선택하고 AzCopy/dump를 native 근거로 쓰지 않습니다. timebox 초과 시 선택 실행 module의 추후 관찰/준비 데모를 정확히 표시합니다. 카드 A-D의 가정 준비/pre-write 복귀/post-write 복구/unknown NO-GO를 구분합니다.

## 9. 정리·회차 결과

consumer는 자기 app/VM/cluster/namespace/target/job·정확한 새 grant만 정리합니다. publisher는 마지막 consumer 이후 image/UAI를 정리합니다. fixture owner는 data consumer가 끝난 뒤 자기 VM/network/PE/DNS/newrole을 정리하며 입력 계정·source는 보존합니다. cancel/definition/project/stopreplication/target 삭제/datarollback의 영향을 각각 확인하고 source/backup은 acceptance/복구/retention 승인까지 보존합니다.

정확한 scope/name/labtag/resource/grant·영향을 목록화해 삭제 승인받고 잔여 resource·지연 비용을 확인합니다. deallocated/Nodata 상태에서는 남은 disk·storage·권한과 비용 반영을 점검합니다. data/backup/role/network/artifact를 구분하고 전체 폴더 재귀 삭제·구독 탐색 삭제·customerDROP/TRUNCATE·자동 writer 변경은 하지 않습니다.

선택 mode·지원 input/version·actualnative/data/app·오류/unknown·ownedcleanup/보존·다음 조치를 간단히 기록합니다. 학습자는 단계별 결과와 정리 범위를 확인하며 강사는 필요한 준비·대응을 비공개 기록으로 관리합니다.

### 강사용 local T-SQL 검사 도구

강사는 repository root의 WSL·승인 Docker/image/package와 기존 sample-app pytest 환경을 검사 도구로 재사용합니다. 참가자의 앱 수강과 별개로 선택 engine만 검사합니다. 새 network-isolated container·비공개 port·SQLDeveloper EULA 동의·오류/rollback/제약을 확인하고 검사에서 만든 container/volume만 정리합니다. native service 연결과 실제 이전은 해당 모듈에서 별도로 확인하며 version/digest·exit/오류는 private 기록에 남깁니다.

```bash
docker pull mcr.microsoft.com/mssql/server:2019-latest
cd sample-app
WORKSHOP_SQLSERVER_ACCEPT_EULA=Y UV_PROJECT_ENVIRONMENT=.venv-wsl \
  uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k sqlserver
```

### 강사용 로컬 SQL 검증 도구

강사용 선택 격리 검증이며 참가자의 공통 앱 수강/실행 요구가 아닙니다. repository root의 WSL과 승인 Docker/image/package를 사용하고 기존 sample-app pytest 환경은 검사도구로만 재사용합니다. 선택 engine만 검사합니다. 새 network-isolated container/비공개 port·SQLDeveloper EULA 동의·실제 오류/rollback/제약을 확인하고 자기 container/volume만 정리합니다. 통과는 native service/AWS 이전 근거가 아니며 실제 version/digest·exit/오류는 private 기록에 남깁니다.

```bash
docker pull postgres:16
cd sample-app
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k postgresql
```
## Functions HTTP 검증 도구

Local adapter/host 검사는 repository `lab-output/functions-<id>` stage의 WSL Bash에서만 실행합니다. source/adapter/host·승인 Python3.12 dependency·stage venv가 준비되어야 합니다. pytest/httpx는 검사환경에만 설치하고 runtime requirements에 추가하지 않습니다. host 검사는 새 단일 worker/Azurite·localhost7071을 요구합니다. 재실행 전 state를 확인하고 자기 host/emulator만 종료합니다.

마지막 cloud 검사는 `sample-app` 디렉터리의 기존 pytest 환경에서 수행하며 앱 수강 요구가 아닙니다. 새 승인 HTTPS/max1 Functions·보호 function-level key파일·명시 synthetic-write 승인만 사용하고 고객/변경된 기존 endpoint에는 실행하지 않습니다. no-key/wrong-key401·health200·POST201/read-back·invalid422 불변·404를 확인하며 scale-out 영속성이나 모든 trigger를 인증하지 않습니다.

```bash
uv pip install --python .venv pytest
PYTHONPATH=. .venv/bin/python -m pytest -q \
  ../../modules/onboarding/compute-functions/verify/test_adapter.py
```

```bash
uv pip install --python .venv httpx
WORKSHOP_FUNCTIONS_LOCAL_URL=http://127.0.0.1:7071 PYTHONPATH=. \
  .venv/bin/python -m pytest -q \
  ../../modules/onboarding/compute-functions/verify/test_adapter.py \
  ../../modules/onboarding/compute-functions/verify/test_host.py
```

```bash
: "${WORKSHOP_FUNCTIONS_CLOUD_URL:?승인된 새 HTTPS Function App URL 필요}"
: "${WORKSHOP_FUNCTIONS_KEY_FILE:?보호된 function-level key 파일 필요}"
: "${WORKSHOP_CLOUD_WRITE_APPROVED:?합성 쓰기 승인 필요}"
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run --frozen --no-sync pytest -q -s \
  ../modules/onboarding/compute-functions/verify/test_cloud.py
```
