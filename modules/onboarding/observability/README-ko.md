# 관측성과 비용 — Portal에서 결과를 읽고 판단하기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: CloudWatch·CloudTrail·Cost Explorer 경험이 있는 엔지니어.
- 예상: 개념·합성 관찰 카드 20분, 선택 Portal 관찰 30~40분, 선택 budget 15분. 실제 시간은 기록합니다.
- 목표: **리소스 관리 성공·앱 동작·로그·비용을 각각의 결과를 읽고 판단**합니다.
- 기본 방법은 Azure portal입니다. 새로운 CLI wrapper·로그 수집 플랫폼·자동 중지 프로그램을 만들지 않습니다.

| 선택 범위 | 입력 | 결과 | 필요 없는 완료 |
|---|---|---|---|
| 개념·관찰 카드 | 문서의 명시적 합성 사례 | 무엇을 추가 확인해야 하는지 설명 | Azure 로그인·앱·리소스 배포 전부 |
| 선택 Portal 관찰 | 강사가 준비했거나 본인이 선택한 작은 실습 리소스·조회 권한 | 상태·Activity Log·metrics/log·비용의 의미를 읽은 기록 | 모든 컴퓨트·데이터 트랙 완료 |
| 선택 budget | 승인된 scope·금액·알림 수신자·생성/삭제 권한 | 예산 알림의 목적·한계를 설명 | 자동 shutdown·운영 비용 플랫폼 |

관찰 대상이 없으면 합성 카드로만 진행합니다. 이 모듈 때문에 다른 컴퓨트를 새로 만들거나 모든 트랙을 완주하지 않습니다. 관찰할 리소스를 제공받는 것과 해당 컴퓨트 모듈을 수강하는 것은 다릅니다.


## 2. 서비스 소개와 AWS 비교


| 서비스·기능 | Microsoft Learn 소개 | 이 모듈에서 볼 내용 |
|---|---|---|
| Azure Monitor | [Azure Monitor 개요](https://learn.microsoft.com/en-us/azure/azure-monitor/overview) | metrics·logs·events를 구분 |
| Activity Log | [Activity Log 개요](https://learn.microsoft.com/en-us/azure/azure-monitor/platform/activity-log) | 제어 영역의 리소스 관리 이벤트 |
| Azure Cost Management | [Cost Management 개요](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management) | scope·기간·실제 비용·예측 |
| Budgets | [Budget 소개와 생성](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets) | 알림이며 자동 사용 제한이 아님 |
| Log Analytics | [Log Analytics 개요](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview) | 선택 확장의 지속 로그·KQL |
| Application Insights | [Application Insights 개요](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview) | 선택 확장의 앱 요청·추적 |

| AWS에서 읽던 것 | Azure에서 비교할 것 | 동일하다고 가정하면 안 되는 부분 |
|---|---|---|
| CloudWatch metrics/logs | Azure Monitor의 metrics/logs | 수집·저장·권한·비용·기본 제공 범위가 다름 |
| CloudTrail 관리 이벤트 | Activity Log | 앱의 HTTP access log나 Entra sign-in 전체를 대신하지 않음 |
| Cost Explorer | Cost Management의 Cost analysis | scope·청구 유형·갱신 시점·권한이 다름 |
| AWS Budgets | Azure Budgets | 예산 알림이 resource 정지·과금 상한을 보장하지 않음 |

이 기본 범위에서는 **Application Insights SDK·Log Analytics workspace·Container Insights·Managed Prometheus·Grafana를 새로 켜지 않습니다.** 필요한 경우의 제품 선택을 설명하고 지속 수집은 선택 확장으로 분리합니다.


## 3. 사전 준비·권한·비용


- 기본 실습 환경은 **브라우저의 Azure portal**입니다. 메뉴와 표시 이름은 현재 UI·공식 문헌을 따릅니다.
- 승인된 테넌트·구독과 조회할 **자기 실습 리소스 하나** 또는 강사가 제공한 작은 관찰 대상을 고릅니다.
- 리소스/metrics 조회, log stream·VM OS 로그·Kubernetes Pod 로그 권한은 별도일 수 있습니다. 필요한 log 접근 권한을 resource 조회 권한과 별도로 확인합니다.
- 비용 조회에는 해당 scope·청구 체계의 권한이 필요합니다. budget 생성/삭제는 Cost Management 관련 권한을 승인된 관리자와 확인합니다.
- VM·AKS·Container Apps·Storage 중 선택한 대상만 관찰합니다. 이 모듈에서 해당 리소스의 설정·scale·네트워크·코드를 바꾸지 않습니다.
- 조회 중심이지만 대상 리소스의 기존 요금은 계속 발생합니다. 선택 workspace·수집·alert 등은 별도 요금 가능성이 있으므로 자동 활성화하지 않습니다.
- 고객 이름·계정·구독 ID·token·실제 payload가 있는 로그/스크린샷은 저장소·Copilot에 넣지 않습니다. 합성 데이터와 안전하게 가린 교육 기록만 사용합니다.


## 4. 단계별 instruction — 화면에서 의미 읽기


### 4.1 배포하지 않고 합성 관찰 카드 읽기


다음은 **실제 Azure 출력이 아닌 교육용 합성 사례**입니다.

| 카드 | 관찰한 것 | 판단 |
|---|---|---|
| A | Resource provisioning은 Succeeded, 앱은 `/health` 200·쓰기 201·read-back 성공, Cost analysis는 아직 No data | 리소스·앱 관찰은 양호하나 비용은 미확정. 무료라고 결론내리지 않음 |
| B | Activity Log의 리소스 생성은 성공, 현재 container system log에는 image pull 오류, 앱 연결 실패 | 제어 영역 생성 성공과 앱 runtime 성공은 다름. image/identity/권한 확인 필요 |
| C | VM은 Stopped(deallocated), OS disk·public IP·공유 registry는 남아 있음 | compute 정지와 전체 리소스·비용 정리는 다름 |

어떤 관찰이 제어 영역인지, 앱/데이터 영역인지, 비용인지 표시합니다. 이 카드의 결론을 실제 배포 검증 결과로 기록하지 않습니다.


### 4.1a 권한·네트워크·앱 오류를 구분하는 연습

**선택 시간:** 10~15분입니다. 다음 합성 카드 중 하나를 고르고 `관찰 사실 | 원인 후보 | 추가 확인 | 유지할 설정 | 정상 복귀 기준`을 작성합니다. 모든 환경에서 같은 오류 코드가 나온다고 가정하지 않습니다.

| 합성 관찰 | 먼저 구분할 것 | 추가 확인 |
|---|---|---|
| 로그인과 리소스 조회는 성공하지만 Blob 읽기는 403입니다. | 데이터 역할·scope·인증 대상과 네트워크 제한을 함께 확인합니다. 403만으로 RBAC 문제를 확정하지 않습니다. | 승인된 관리자가 현재 identity·data role·scope를 확인하고, 승인된 private client의 DNS·경로·서비스 오류 상세를 대조합니다. |
| private FQDN의 DNS 조회나 TCP 연결이 실패합니다. | 앱 응답 전에 발생한 연결 실패인지 확인합니다. | 실행 위치·DNS 응답·대상 포트·경로·listener를 확인합니다. 경로를 확인하기 전에 권한을 추가하지 않습니다. |
| `/health`는 200이지만 존재하지 않는 URL은 404, 잘못된 입력은 422입니다. | 요청이 앱까지 도착했고 route나 입력 검사가 응답했는지 확인합니다. | 요청 경로·payload·앱 로그와 정상 요청 결과를 비교합니다. 리소스를 다시 배포하지 않습니다. |

**선택 실제 관찰 — 이미 실행 중인 로컬 공통 앱만 사용합니다.** [로컬 앱 실행](../../../sample-app/README-ko.md)을 선택한 경우 같은 WSL/Linux Bash의 두 번째 터미널에서 실행합니다. 새 앱 실행이나 클라우드 배포를 필수로 하지 않으며 local endpoint가 없으면 카드로 마칩니다. 아래 주소를 cloud·customer endpoint로 변경하지 않습니다.

```bash
curl --fail-with-body --max-time 10 --noproxy "*" http://127.0.0.1:8080/health
curl --fail-with-body --max-time 10 --noproxy "*" http://127.0.0.1:8080/items
curl --include --max-time 10 --noproxy "*" http://127.0.0.1:8080/workshop-missing-route
curl --include --max-time 10 --noproxy "*" \
  --request POST http://127.0.0.1:8080/items \
  --header 'Content-Type: application/json' --data '{"name":""}'
curl --fail-with-body --max-time 10 --noproxy "*" http://127.0.0.1:8080/items
curl --fail-with-body --max-time 10 --noproxy "*" http://127.0.0.1:8080/health
```

**기대 관찰:** health 200 → items 기준값 → 404 → 422 → 변경 없는 items → health 200입니다. 같은 앱의 외부 writer가 없는 상태에서 목록을 비교합니다. 오류 요청 두 개는 의도적으로 `--fail-with-body` 없이 HTTP status를 읽으며, curl exit 0은 HTTP 성공을 뜻하지 않습니다. 연결 실패·다른 status·목록 변경이 있으면 중단하고 해당 요청과 앱 로그를 확인합니다.

권한·네트워크 카드는 토론이며 실제 역할 회수·NSG/DNS 변경·token 변조를 실행하지 않습니다. 앱 연습의 잘못된 입력도 저장되지 않습니다. 이 단계의 정리 대상은 개인 기록뿐이며 기존 앱·공유 입력의 종료와 삭제는 원 소유자가 관리합니다.

### 4.2 Portal — 대상·시간 범위부터 맞추기


1. Azure portal에서 승인된 directory·subscription을 확인합니다. 다른 구독으로 임의 변경하지 않습니다.
2. 선택 리소스의 **Overview**를 열어 이름·resource group·region·상태를 읽습니다.
3. 조회할 시간 범위를 실습 시각과 맞춥니다. 화면의 시간대와 앱 로그의 시간대를 확인하고 UTC/로컬 시간을 혼동하지 않습니다.
4. 리소스 종류, owner 모듈, 관찰 기간을 기록합니다. VM의 앱·AKS의 Pod·Container Apps의 replica 등 관찰 단위도 구분합니다.

**기대 결과:** 어느 리소스의 어느 기간을 보고 있는지 설명할 수 있습니다. Overview의 Succeeded/Running만으로 앱·이전 성공을 판정하지 않습니다.


### 4.3 Portal — Activity Log에서 관리 이벤트 읽기


1. 선택 리소스 또는 자기 실습 그룹의 **Activity log**를 엽니다.
2. 해당 리소스·실습 기간·관련 operation으로 범위를 좁힙니다.
3. 생성/변경/삭제 이벤트의 operation·status·시각을 읽고 실패 이벤트의 상세 원인을 확인합니다.
4. caller 등의 식별정보는 공유 기록에서 가립니다.

**배울 점:** “VM 생성”, “NSG 변경”, “앱 resource 쓰기”와 실제 `/items` 요청은 다른 이벤트입니다. Activity Log에 HTTP 요청이 안 보인다고 앱 요청이 없었다고 결론내리지 않습니다.


### 4.4 Portal — Metrics와 앱 로그를 구분


선택 리소스의 **Monitoring → Metrics**에서 사용할 수 있는 metric namespace·metric·기간·aggregation을 읽습니다. 평균·최댓값·합계는 같은 결과가 아닙니다. VM의 기본 host CPU metric을 guest memory나 앱 latency로 해석하지 않습니다.

앱 로그는 선택한 경로 하나만 관찰합니다.

| 대상 | 기본 관찰 방법 | 이 모듈이 자동으로 하지 않는 것 |
|---|---|---|
| Container Apps | Portal의 **Monitoring → Log stream**, System/Console과 revision·replica·container 선택 | Log Analytics workspace 생성·장기 보관 활성화 |
| VM + Docker | Portal host metrics/Activity Log와, 승인된 VM 접근으로 읽는 Docker console log를 구분 | Docker stdout을 Azure Monitor에 자동 수집했다고 주장 |
| AKS | Portal의 cluster/node 상태·metrics와, 승인된 kubeconfig/namespace의 Pod log를 구분 | Container Insights·workspace·Prometheus 자동 활성화 |
| Storage | 해당 service metric·오류와, 선택 실습의 내용 검증 결과를 함께 읽음 | 관리 이벤트만으로 blob content가 같다고 판정 |

Container Apps는 [Portal log stream 절차](https://learn.microsoft.com/en-us/azure/container-apps/log-streaming)를 따릅니다. Console은 앱 출력, System은 platform/runtime 쪽 사건입니다. stream은 지속 보관·전체 이력의 대체재가 아닙니다.

VM/AKS를 선택했으면 해당 모듈에 이미 작성된 **자기 target의 로그 조회 명령만** 참고합니다. 여기에 새 CLI wrapper를 추가하거나 다른 컴퓨트 전체를 진행하지 않습니다. 앱 요청을 발생시키는 방법도 선택한 모듈의 같은 HTTP 계약을 사용합니다.

**기대 결과:** 앱/플랫폼 로그의 출처, 선택한 container/Pod, 요청 status와 오류 원인을 구분합니다. 데이터가 없으면 수집 미설정·권한·scope·시간 범위부터 확인합니다. “없음”을 정상/실패로 자동 해석하지 않습니다.


### 4.5 Portal — Cost analysis에서 실제 비용의 범위 읽기


1. **Cost Management → Cost analysis**에서 승인된 scope를 선택합니다. 처음에는 자기 실습 그룹 또는 관리자가 지정한 조회 범위만 사용합니다.
2. 날짜·currency·actual cost/forecast와 grouping/filter를 확인합니다.
3. service 또는 resource로 나누어 VM·disk·public IP·registry·앱 실행비가 어디에 표시되는지 읽습니다.
4. 결과가 비었거나 갱신되지 않았으면 데이터 반영 지연·권한·청구 범위를 기록하고 다시 확인합니다.

**중요:** AKS managed node 그룹, 공유 image/registry 그룹, 앱 그룹은 서로 다릅니다. 앱 그룹 하나로 filtering하면 전체 실습 비용이 빠질 수 있습니다. “이 모듈 비용”과 “선택 조합의 전체 비용”을 구분해 owner 모듈과 함께 합산 범위를 정합니다.

가격 계산기는 예상, Cost analysis는 해당 scope/기간의 반영된 사용 비용입니다. forecast는 확정 청구액이 아닙니다. resource 삭제도 이미 발생한 요금이나 보존 중인 다른 리소스의 비용을 없애지 않습니다.

1. 날짜 선택기의 preset을 관찰 기간과 비교합니다. 짧은 과거 실습을 읽을 때 **Last 7 days**를 선택할 수 있지만 전체 사용 기간의 비용은 아닙니다.
2. **Group by → Resource group**으로 소유 경계를 나누어 읽습니다. 아래 dropdown은 선택 가능한 dimension의 일부만 보여줍니다.
3. resource-group filter에 **승인된 실습 그룹 하나만** 넣습니다. scope·기간·currency·실제 filter를 대조하고 다른 그룹을 포함하지 않습니다.
4. actual cost와 forecast를 구분합니다. cost point가 하나뿐이거나 이력이 부족하면 forecast가 없을 수 있습니다. 이를 0으로 대신하지 않습니다.

![Cost analysis 날짜 선택기의 세 가지 preset](./images/portal-cost-date-options.png)

![Cost analysis Group by dimension dropdown의 일부](./images/portal-cost-group-options.png)

![이전 Container Apps 실습 그룹 하나만 필터한 비용 차트, legend 마스킹](./images/portal-cost-filtered-chart.png)

*차트의 $0.06은 이전 Container Apps 실습 그룹 하나에 대해 Last 7 days에 반영된 과거 사용 비용입니다. 현재 전체 비용은 해당 scope·기간을 다시 선택해 확인하고 최종 청구는 invoice에서 확인합니다. legend는 가렸습니다.*


### 4.6 선택 Portal — Budget 알림만 준비


승인된 scope·금액·currency·수신자와 생성/삭제 권한이 있을 때만 진행합니다. 기존 운영 budget을 수정하지 않습니다.

1. 해당 scope의 **Budgets → Add**에서 새 실습용 이름 `budget-amw-observe-<lab-id>`를 지정합니다.
2. 승인된 기간과 금액을 입력합니다. 장기 production 예산으로 재사용하지 않습니다.
3. 실제 비용 80% 등의 threshold와 승인된 알림 수신자를 설정합니다. 필요하면 forecast 알림과 차이를 설명합니다.
4. scope·금액·period·threshold·알림 대상 정보를 대조하고 승인 후 생성합니다.
5. action group·자동 shutdown·배포 차단은 연결하지 않습니다.

**기대 결과:** budget 구성이 보이며 그 목적은 알림입니다. 데이터 반영·평가·알림에 지연이 있을 수 있습니다. 알림이 없으면 비용 반영·평가 주기·수신자 설정과 실제 전달 상태를 확인합니다.

예산을 초과시키려고 유료 workload를 생성하지 않습니다. 실제 알림 수신까지 관찰하지 못하면 **구성 확인만·알림 동작 미확인**으로 구분합니다.

form walkthrough를 선택하면 **Create budget**과 alert 조건을 읽고 제출하지 않습니다. 예시 이름 `budget-amw-ui141026`·**100 USD**·**Monthly** reset은 입력 설명용이지 권장 예산이 아닙니다. 보이는 **종료일 2년 기본값은 짧은 워크샵의 권장값이 아닙니다.** 승인된 종료일과 cleanup owner를 별도로 정합니다.

![Scope와 suggested forecast를 가린 budget 생성 form](./images/portal-budget-create-options.png)

alert page에서 **Actual cost**와 Forecast를 구분합니다. 예산 100 USD의 **80%는 80 USD**이며 알림 threshold이지 과금 상한이 아닙니다. **Action group: None**은 이 예시에 action group·자동 중지를 연결하지 않았다는 뜻입니다. 별도 승인한 생성에는 승인 수신자·최종 검토가 필요하며 form 관찰만으로 알림 전달을 확인할 수는 없습니다.

![Actual cost 80%와 Action group None인 alert 조건](./images/portal-budget-alert-conditions.png)

*화면에서 budget form의 입력 항목을 읽습니다. 실제 생성은 승인된 scope·금액·수신자를 확인한 뒤 진행하며, 저장된 설정과 알림 전달을 각각 확인합니다.*


## 5. 성공 기준·대표 실패


| 성공 기준 | 필요한 관찰 |
|---|---|
| scope·시각·대상을 설명 | 리소스 종류·owner·시간대·기간 |
| 제어/앱/비용을 구분 | Activity Log·app/console log·Cost analysis를 서로 다른 근거로 읽음 |
| 선택 리소스의 상태를 판단 | 실제 앱 계약/오류와 해당 log·metric을 함께 사용 |
| 비용의 누락/지연을 설명 | managed/shared 그룹·currency·period·반영 상태 확인 |
| budget 한계를 설명 | 알림은 자동 정지·강제 상한이 아님 |

대표 실패는 scope/기간 오류, log stream 권한 부족, workspace 미설정인데 KQL 이력을 기대함, host CPU를 앱 응답시간으로 해석함, 비용 No data를 무료로 해석함입니다. 화면·권한·수집 설정부터 확인하고 자동 수집·권한 확대·실패 기본값으로 덮지 않습니다.


## 6. 정리 — 관찰 대상 리소스는 원 소유자가 정리


조회·합성 카드만 선택했으면 이 모듈이 만든 Azure 리소스는 없습니다. 다른 모듈의 VM·cluster·앱·registry를 이 화면에서 삭제하지 않습니다. log stream을 닫는 것은 resource 삭제가 아닙니다.

선택 budget을 새로 만들었다면 Portal에서 **정확한 scope·실습 이름·amount·notification 구성**을 먼저 확인하고, 승인 후 그 budget 하나만 삭제합니다. 기존 budget·action group·workspace는 삭제하지 않습니다.

관찰 target의 삭제는 각 owner 모듈의 절차를 따릅니다. 삭제한 뒤 비용·잔여 대상의 확인 시점도 남깁니다. 표시 지연이 있으므로 즉시 0으로 보인다는 이유만으로 최종 정리를 확정하지 않습니다.


## 7. 실제 이전에서 추가로 확인할 사항


- 이전 전 baseline과 이후의 latency·오류율·데이터 정합성 비교, 모니터링 공백.
- Azure Migrate/Storage Mover/DB migration service의 **작업 상태·서비스 로그**와 타깃 앱 상태를 별도로 읽기.
- 지속 수집·보관·sampling·alerts·앱 추적, workspace/telemetry의 비용·민감정보.
- HA·복구·운영 인계·예산 governance. 교육용 기본 관찰이 운영 체계를 완성하지는 않습니다.


## 8. 출처
