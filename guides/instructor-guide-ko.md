# 강사 가이드 — 준비·시간·diagnostic fixture·소유권

[English](./instructor-guide.md) | 한국어

학습자 module은 실행 단계·관찰 결과·정리를 설명하고 회차 설계·강사 준비·진단은 이 가이드에 둔다. [선택표](../Readme-ko.md)·[참가자 준비](./participant-preparation-ko.md)·[조합](./module-combinations-ko.md)을 먼저 사용한다.

**AWS 경계:** 실제 AWS 환경은 만들지 않았다. AWS resource·credential/AMI 조회·plan/apply는 실행하지 않는다. 분석Terraform·Azure합성 data·공식 walkthrough를 사용하며 실제EC2/S3/RDS이전 근거로 표현하지 않는다.

## 1. 회차 범위 합의

목표/source/module/mode·browser/localPowerShell/WSL/VM/client·승인target/region/비용owner·image/digest/identity/source/target/private입력·지원/version/quota·관리/data/engine/Kubernetes권한·비용/timebox·관찰/stop/복구·생성/보존/cleanupowner를 private하게 정한다.

전체 설치/트랙배포·자동화schema로 확대하지 않는다. 읽기/walkthrough/준비데모/live합성의 근거는 다르다. 과거endpoint가 살아있다고 가정하지 않고 native복제/CDC/copy/scheduler/retry는 공식platform에 맡긴다.

## 2. 역할과 입력

| 역할 | 책임 |
|---|---|
| 강사 | module/mode선택·서비스설명·안전입력/데모·근거/timebox |
| 관리자/비용owner | tenant/scope/provider/region/quota·grant/회수·비용승인 |
| source/DBowner | 지원/권한/TLS/writer/backup/보존·복구 |
| 참가자 | 정확한대상·선택단계·오류관찰·자기정리 |

Contributor는 모든data/engine/Kubernetes권한이 아니다. 없는source credential이나 customer inventory를 데모입력으로 요청하지 않는다. 실제값은 승인private경로로만 준비하고Git/prompt/screenshot에 넣지 않는다.

앱은 DBadapter없는 memory API하나다. VM/AKS/CAA는같은digest, Functions는같은source+adapter/host다. 이미지준비는ACR/선택UAI를소유하고consumer는보존한다. PG/MySQL은논리SQL을공유하고SQLServer는별도T-SQL이다. seed는source만,target은빈상태다. 카드/계획CSV는공식import/discovery출력이아니다.

## 3. Utility보다 서비스부터 소개

module의MicrosoftLearn과Portal자료로Mover→AzCopy, Migrate→VM/서버, DMS/engine/target→DButility/SqlPackage를설명한다. PG는target전용migrationservice를선택한다.

screenshot은stage/field를보여주는자료이지job성공근거가아니다. 현재IAM은Checkaccess의이전view링크를통해Viewmyaccess로진입할수있다. userrow/식별정보는캡처하지않는다. form기본group/region을승인입력으로쓰지않고form열기와제출을구분한다.

### Storage Mover 제공 경계

**워크샵 제공 경계:** Storage Mover는 **서비스 소개만** 제공한다. 관리 기능·적합한 source/workload·리전/비용/권한/network와 공식 문헌을 배우고 endpoint/project/job definition 생성·실행 role·copy 시작/검증은 실습하지 않는다. 오브젝트 hands-on은 별도 공식 **private AzCopy**의 합성3개/109 bytes다. 이 선택은 Mover 전반의 미지원 결론이 아니다. 실제 고객 실행은 해당 지원 공식 시나리오와 고객 관리자 승인을 별도로 따른다.

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성한다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인한다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따른다. 인증과 network는 다른 통제다.

수업 밖 실행은 공식 source별 시나리오·관리 리전/metadata residency·비용·identity/data 권한·연결을 관리자와 확인한다. 워크샵 오브젝트 실행 일정은 AzCopy만 대상으로 한다.

## 4. Private Blob diagnostic fixture

기존승인endpoint/DNS/client를우선재사용한다. 없으면별도범위/비용승인후최소group/VNet/subnet/PE/DNS·선택x64LinuxVM을준비한다. VMpublicNICIP/SSHinbound는없고관리RunCommand·선택dataMI권한을쓴다. NATpublicIP는outbound이지Blobpublic허용이아니다. VM/disk/NAT/IP/PE/DNS/처리비용을승인하고전원필수수강으로만들지않는다.

publicDisabled/Deny/bypassNone·HTTPS/TLS·익명/SharedKey금지를유지한다. 실제위치에서ApprovedPE/canonicalDNS/privateIP/TLS/data요청을확인한다. hubclient와서로다른spokePE의copy는CannotVerifyCopySource가날수있으므로공식topology를검토하며Mover는별도지원이다.

agent/설치outbound를승인한다. HTTP/HTTPSport규칙은FQDNallowlist가아니다. 필요시승인proxy/mirror/preinstalled도구를준다. AzurePlatformDNSAllow가미지원이면지원platformDNS/IP의미를따르고정책을넓히지않는다. wrapped/nullNICcreate는actualnicshow로확인한다. base64padding은명시name=value,긴source는scriptpayload를사용하며secret은argument로보내지않는다.

RunCommand외부성공은guest/datapass가아니다. stdout/stderr/traceback/exit·정확한PASS/FAIL을확인하고출력제한때문에전체진단은보호보관한다. Blob수업때문에DB를설치하지않고client의DBsource재사용은별도승인scope다.

## 5. DB·SQLImport fixture

live이전전reachable source/version/native runtime/network/DB권한을준비한다. localcontainerSQL은Azure접근근거가아니다. PGVNet통합target과PE-only/runtime는다르며clientverify-full은nativeworkerCA/hostname검증증거가아니다.

PostgreSQL validation 오류는 code/native details·연결·지원·source 조건을 읽고 해결한다. 재시도는 owner 승인과 검토한 입력으로 Validate를 명시하며 migration 시작은 별도 승인한다. 완료 후 schema·전체 행·TLS·source baseline을 비교한다.

MySQLoffline은현재문헌Premium과runtime연결을검토한다. managementversion뿐아니라SELECTVERSION()을읽는다. globalreadonly·targettruncate는별도승인이다. target의빈dms_persistent_objects는workload3개외serviceartifact로조사기록하고DROP하거나임의extra를무시하지않는다.

SQL은보존요구우선이다. SQLDatabase3table데모는Agent/crossDB를대체하지않는다. Entra-only정책과DMS도구인증지원이맞는지확인한뒤paidsource/SHIR를만든다. genericEntra지원으로DMS인증을가정하거나정책을우회하지않는다.

B2directSqlPackage는privateWindowssource/client·공식tool·sourceTLS/Windowsauth·targetDNS/MI·owner-onlyBACPAC을준비한다(BACPAC은암호화파일이아님). 빈target에Import한다. 기존MIuserDROP충돌이면새isolatedlogicalserver만별도승인한임시MIEntraadmin/정확한user정리를사용한다. 성공/실패와무관하게원래admin복구·DB권한재제한을한다. importedREAD_ONLY는새target만복구하고source동결은유지한다.

새 SQL source는 승인된 SQL 관리자 권한·TLS 신뢰를 준비한다. OS 관리자와 SQL sysadmin은 별도다. source 복구·임시 권한이 필요하면 새 sandbox만 별도 승인하고 정상 서비스·원래 권한·정확한 임시 artifact 정리를 확인한다.

## 6. Functions·compute fixture

WSL의actualLinuxCoreTools/Azuritepath/version·지원설치를확인한다. Windowsnpmpath는준비완료가아니다. Python/source/package와승인feed를명시하고.funcignore/localsettings제외를확인한다. prebuilt/build-remotefalse와CoreToolsremotepublish는다르며localfeed예외를cloudbuilder에확대하지않는다.

host/deploymentstorageMI/role/private와HTTPfunctionkey는다르다. key는private보관/header사용이며URL/log에넣지않는다. localauth와Azureenforcement를구분하고freshmax1test를globalstate/scale증거로쓰지않는다. 자기host/emulator/port-forward만종료한다.

VMprivateRunCommand/publicSSH와AKSprivateMIclient/localuserpublic32는별도branch다. DNS/auth/role/flag를섞지않고systempool2node·지원/quota/cost를유지한다. externalregistry/VNet/NAT/DNS의정확한새grant를추적하고consumer가shared입력을삭제하지않는다.

## 7. 시간·근거 해석

360+120분일정/module시간은가설이며사람학습실측이아니다. 강사setup·설명/질문·인증/권한·provision/job·검증·정리를따로잰다. 작은data/리전하나로production시간을예측하지않는다.

### CSV import·앱 화면 준비

[서버 모듈](../modules/migration/servers/README-ko.md)의 [합성 inventory CSV](../modules/migration/servers/lab/synthetic-inventory.csv)는 가상 1행이며 import 수용 화면과 연결된다. 현재 동선은 All projects → Create project → Start discovery → Using import → Server inventory (CSV) → Download .CSV file → Browse → Import다. 공식 template을 Download .CSV file로 받아 27-column·합성 capacity/unknown을 유지하며 계획 workloads.csv를 올리지 않는다.

Portal의 **import 후 15분 대기**는 설명과 이후 assessment 시간에서 구분한다. Completed / Rows processed 1은 합성 inventory 수용뿐이며 assessment/readiness/복제/migration 완료로 표시하지 않는다. 다른 참가자·실제 discovery/replication source에 영향 없는 전용 owned project를 사용한다.

CSV assessment는 **project Overview → Create assessment → Add workloads → 가상 imported server1개 → Add selection**을 가르친다. General/Advanced/Review 가정을 검토해 해당 assessment만 생성하고 Decide and plan → Assessments에서 읽는다. [서버 모듈](../modules/migration/servers/README-ko.md)의 설정/review/source/target/견적 화면5개로 live source·target VM 없이 결과를 해석한다.

없는 utilization/IOPS·표시 기본0은 측정 idle이 아니다. hardware 입력·저장 sizing 설정·추천 설명을 비교하고 단일 label만 믿지 않는다. 고객 설계 수용 전 상충/default 가정을 확인하며 lifecycle·assessment 적합성·배포 가용성·실제 boot/app 준비를 구분한다.

31×24시간 retail/noAHB/no예약의 예시 계산은 Defender 비용을 제외했지만 protection을 끈 것이 아니다. 299.42USD는 배포 요금/invoice/보장 가격이 아니다. 추천 Server Migration 도구가 공식 CSV-import 제한을 없애지 않으며 assessment를 설명하려고 VM/복제를 만들거나 operation 시간 기록을 공개하지 않는다.

[Container Apps 모듈](../modules/onboarding/compute-container-apps/README-ko.md)은 active replica1 revision과 Real-time/Application stream controls를 보여준다. 승인된 실제 stream에서 200/201/422/404 요청을 대조할 수 있지만 privacy-cropped screenshot에는 해당 line이 없다. 상태/traffic/replica와 HTTP 근거를 따로 설명하고 Stop이 앱이 아니라 stream 보기를 닫는다는 점을 확인한다. 새 capture는 selector/revision 식별정보를 가리고 payload를 제외한 뒤 공개한다.

[MySQL native 결과](../modules/migration/database-mysql/README-ko.md)는 기존 owned classic service/project/Offline activity의 workshop과 table3개에서 읽는다. 근사 ~10행·반올림 00:00:00·DB activity7초는 정확한 비교나 전체 회차 시간이 아니다. native 완료와 독립 30행/schema/source baseline/TLS 근거를 연결한다.

[Objects 모듈](../modules/migration/objects/README-ko.md)은 Mover 소개·별도 AzCopy 실행이다. 참가자 일정에 Mover setup/role/run/cleanup을 넣지 않는다.


actualversion/region/mode/native/data/feature·오류/exit·writer·승인scope·잔여resource/grant/cost는안전private강사기록에둔다. 실제ID/email/tenant를이문서에적지않고선택 입력·승인은 회차별로 확인한다.

### Cost analysis·budget walkthrough 준비

[관측성 모듈](../modules/onboarding/observability/README-ko.md)에 날짜 preset·grouping·제한된 과거 비용 차트·budget 입력·alert 조건의 privacy-reviewed 화면 5개가 있다. 승인 scope와 관찰 기간을 먼저 준비한다. 예시 차트는 Last 7 days·Group by Resource group·이전 Container Apps 실습 그룹 하나만 filter한 결과다. $0.06은 그룹 삭제 후 반영된 과거 사용 비용이지 invoice나 현재 전체 워크샵 비용이 아니다. cost point가 하나여서 forecast는 제공되지 않았다.

오래 열린 Portal 탭에서 Cost analysis 렌더링 오류(예: React prewarmer)가 나면 정상 인증 SSO를 사용하는 새 Portal 탭으로 다시 연다. 인증을 우회하거나 billing scope를 바꾸지 않고 오류 화면을 비용 0으로 처리하지 않는다. navigation/loading/인증 복구 시간은 교육과 따로 계획하며 이 화면들의 새 실측 시간은 주장하지 않는다.

budget 데모는 별도 생성 승인 없이는 form preview로 유지한다. 예시 입력은 100 USD/Monthly·Actual cost 80%(80 USD)·Action group None이며 종료일 2년 기본값은 워크샵 권장값이 아니다. 수신자 입력·최종 Create 제출·기존 budget 변경은 없었다. preview를 저장된 budget/알림 동작 검증으로 보고하지 않는다. 이후 실제 budget을 승인하면 정확한 scope/name/종료일/수신자·cleanup owner를 별도로 정한다.

## 8. 진행·대체 mode

목표/mode/input/cost/owner/stop부터설명한다. 공식서비스지원·승인단계를하나씩진행하고기대/실제를대조한다. 긴대기를설명하며SKU/권한을자동확대하지않는다. nativeerror/source조건을읽고중단/수정승인후재검사한다. native+data/app/feature·owner정리/보존으로끝낸다.

AWS가 없으면 guided/합성/prepared 결과를 사용하고 discovery/replication/S3/RDS 출력을 만들지 않는다. Mover는 이 워크샵에서 항상 소개만 제공한다. DB source/runtime 지원이 없으면 해당 walkthrough/demo를 선택하고 AzCopy/dump를 native 근거로 쓰지 않는다. timebox 초과 시 선택 실행 module의 추후 관찰/준비 데모를 정확히 표시한다. 카드 A-D의 가정 준비/pre-write 복귀/post-write 복구/unknown NO-GO를 구분한다.

## 9. 정리·회차 결과

consumer는자기app/VM/cluster/namespace/target/job·정확한새grant만, publisher는마지막consumer뒤image/UAI만정리한다. fixture는data소비후자기VM/network/PE/DNS/newrole만삭제하고계정/source를보존한다. cancel/definition/project/stopreplication/target삭제/datarollback은다른행동이다. source/backup은acceptance/복구/retention승인까지보존한다.

정확한scope/name/labtag/resource/grant·영향을목록화후삭제승인하고잔여/지연비용을별도로확인한다. deallocated/Nodata로무료를가정하지않는다. data/backup/role/network/artifact를분리하고전체폴더재귀/구독탐색삭제/customerDROP/TRUNCATE·자동writer변경은하지않는다.

선택mode·지원input/version·actualnative/data/app·오류/unknown·ownedcleanup/보존·다음조치를짧게기록한다. 교육기록이지orchestrationschema가아니다. 실제안전/지원은유지하고learner문서에작성/debug이력을넣지않는다.

### 강사용 local T-SQL 검사 도구

강사용 선택 격리 검증이며 참가자의 공통 앱 수강/실행 요구가 아니다. repository root의 WSL과 승인 Docker/image/package를 사용하고 기존 sample-app pytest 환경은 검사도구로만 재사용한다. 선택 engine만 검사한다. 새 network-isolated container/비공개 port·SQLDeveloper EULA 동의·실제 오류/rollback/제약을 확인하고 자기 container/volume만 정리한다. 통과는 native service/AWS 이전 근거가 아니며 실제 version/digest·exit/오류는 private 기록에 남긴다.

```bash
docker pull mcr.microsoft.com/mssql/server:2019-latest
cd sample-app
WORKSHOP_SQLSERVER_ACCEPT_EULA=Y UV_PROJECT_ENVIRONMENT=.venv-wsl \
  uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k sqlserver
```

### 강사용 로컬 SQL 검증 도구

강사용 선택 격리 검증이며 참가자의 공통 앱 수강/실행 요구가 아니다. repository root의 WSL과 승인 Docker/image/package를 사용하고 기존 sample-app pytest 환경은 검사도구로만 재사용한다. 선택 engine만 검사한다. 새 network-isolated container/비공개 port·SQLDeveloper EULA 동의·실제 오류/rollback/제약을 확인하고 자기 container/volume만 정리한다. 통과는 native service/AWS 이전 근거가 아니며 실제 version/digest·exit/오류는 private 기록에 남긴다.

```bash
docker pull postgres:16
cd sample-app
UV_PROJECT_ENVIRONMENT=.venv-wsl uv run --frozen --no-sync pytest -q -s \
  ../shared/database-sample/verify/test_engines.py -k postgresql
```
## Functions HTTP 검증 도구

Local adapter/host 검사는 repository `lab-output/functions-<id>` stage의 WSL Bash에서만 실행한다. source/adapter/host·승인 Python3.12 dependency·stage venv가 준비되어야 한다. pytest/httpx는 검사환경에만 설치하고 runtime requirements에 추가하지 않는다. host 검사는 새 단일 worker/Azurite·localhost7071을 요구한다. 재실행 전 state를 확인하고 자기 host/emulator만 종료한다.

마지막 cloud 검사는 `sample-app` 디렉터리의 기존 pytest 환경에서 수행하며 앱 수강 요구가 아니다. 새 승인 HTTPS/max1 Functions·보호 function-level key파일·명시 synthetic-write 승인만 사용하고 고객/변경된 기존 endpoint에는 실행하지 않는다. no-key/wrong-key401·health200·POST201/read-back·invalid422 불변·404를 확인하며 scale-out 영속성이나 모든 trigger를 인증하지 않는다.

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
