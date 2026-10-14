# Azure Migrate — 서버 평가와 실제 이전을 구분해서 읽기

[English](./README.md) | 한국어


## 1. 학습 목표·모듈 경계


- 대상: 기존 EC2/서버의 OS·disk·service를 유지하는 이전 접근법을 배우려는 엔지니어.
- 목표: Azure Migrate가 맡는 discovery·assessment·replication·test migration·cutover와 각각의 근거를 읽습니다.
- 방법: **Portal/native service가 기본**입니다. 평가/복제 engine이나 CLI wrapper를 구현하지 않습니다.
- 예상: 개념·합성 카드 30~45분, 선택 CSV assessment 45~60분, 준비된 복제/test migration 데모 60~90분 + 환경 준비 별도. 시간은 회차 설계용 추정치입니다.

| 교육 모드 | 입력·수행 범위 | 하지 않는 것 |
|---|---|---|
| A: 개념·guided walkthrough | 합성 카드·공식 화면/절차, 4.1과 실제 이전 흐름 읽기 | Azure/AWS 로그인·resource/job 생성 전부 |
| B: 합성 CSV assessment | 현재 공식 template·고유 실습 project·approved planning 권한, 4.2~4.4 | 실제 source discovery·복제·AWS 변경·타깃 VM 생성 |
| C: 강사 준비 복제 데모 | 지원되는 실제 sandbox source·전용 appliance·권한/network가 따로 준비된 경우에만 4.5~4.7 | 참가자의 운영 source·production DNS/connection 변경 |

다른 컴퓨트·Docker·AKS·Container Apps·Terraform·DB 모듈의 완료를 요구하지 않습니다. 필요하면 [이전 계획](../planning/README-ko.md)의 `server-sample` 선택 기준만 참고합니다.

**CSV import로 assessment한 서버는 그 항목만으로 migration할 수 없습니다.** B를 완료했다고 C의 source·appliance·replication이 준비된 것은 아닙니다. AWS 환경이 없는 현재 기본 범위는 A이며 B는 통합 검증에서 승인할 선택 후보, C는 준비 조건이 충족된 강사 데모/설명입니다.


## 2. 서비스 소개와 구조


### 2.1 실제 Portal에서 Migrate의 단계부터 소개하기

![Azure Migrate 실제 Get started의 Explore, Decide and plan, Execute](./images/portal-migrate-stages.png)

- **Explore:** discovery·inventory의 근거를 수집합니다. 현재 source가 없는 카드의 unknown을 임의 측정값으로 바꾸지 않습니다.
- **Decide and plan:** business case·assessment·wave planning을 구분합니다. CPU/memory/OS 가정만으로 앱/부팅·운영 호환성까지 확정하지 않습니다.
- **Execute:** 지원되는 실제 source·별도 replication 준비·격리된 test migration·cutover가 필요합니다. **VM+Docker 새 배포와 서버 OS/disk 이전은 다릅니다.**

선택 소개 mode에서는 **Create project**의 Project/Geography/Advanced 필드를 읽고 제출하지 않습니다. 실제 project/assessment 생성은 4.2의 별도 승인 범위입니다.

![Migrate project 폼의 Project와 Geography 입력, 구독 마스킹](./images/portal-migrate-project-options.png)

*Portal 소개/설정 예시. 보이는 기본값을 승인 입력으로 사용하지 않고 실제 job 결과와 구분합니다.*

| 서비스·기능 | Microsoft Learn 소개 | 이 모듈에서 볼 내용 |
|---|---|---|
| Azure Migrate | [Azure Migrate 개요](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview) | project·inventory·assessment·migration 흐름 |
| Discovery and Assessment | [CSV import/assessment 소개](https://learn.microsoft.com/en-us/azure/migrate/tutorial-discover-import) | source appliance 없는 초기 평가와 한계 |
| AWS VM의 서버 이전 | [AWS 공식 경로](https://learn.microsoft.com/en-us/azure/migrate/tutorial-migrate-aws-virtual-machines) | EC2를 physical-server 경로로 다룸 |
| Azure VM | [VM 개요](https://learn.microsoft.com/en-us/azure/virtual-machines/overview) | test/final target와 별도 app/data 확인 |
| Virtual Network | [VNet 개요](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-networks-overview) | test 격리 network와 최종 연결 |
| Azure RBAC | [RBAC 개요](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview), [Migrate 역할](https://learn.microsoft.com/en-us/azure/migrate/prepare-azure-accounts) | Decide/Plan과 Execute 권한 분리 |

```text
CSV import → 합성 inventory의 assessment
             └─ 실제 서버·성능·replication을 발견했다는 뜻은 아님

실제 source → discovery/assessment 준비 → 평가 근거
실제 source + 별도 replication appliance/Mobility service → 복제
  → 격리 network의 test migration → 실제 앱/데이터 확인
  → 승인된 cutover → 최종 확인·rollback/운영 인계
```

AWS의 이 경로는 EC2 resource 이름을 Azure VM으로 치환하는 것이 아닙니다. source OS·boot/disk·설정·identity·network·service의 지원을 확인해야 합니다. [VM + Docker](../../onboarding/compute-vm/README-ko.md)의 새 Ubuntu VM 앱 배포와도 다른 학습 목표입니다.


## 3. 사전 준비·권한·비용·안전


- A는 로그인·도구 설치 없이 문서로 진행합니다. B/C의 환경은 **브라우저의 Azure portal**이며 메뉴·경험은 현재 화면·공식 문헌으로 확인합니다.
- B는 승인된 tenant/subscription·Migrate project geography·실습 전용 그룹·고유 project·지원되는 template을 준비합니다.
- 현재 공식 built-in 역할을 우선 검토합니다. `Azure Migrate Owner`는 project 생성/관리, `Azure Migrate Decide and Plan Expert`는 import/assessment, `Azure Migrate Execute Expert`는 migration 단계의 범위입니다. 정확한 scope·추가 권한은 관리자와 현재 문서로 대조합니다.
- 광범위한 subscription Owner나 tenant의 app registration 허용을 참가자 기본값으로 자동 변경하지 않습니다. appliance 등록에는 추가 Entra 권한이 필요할 수 있고 B의 CSV-only 준비와 구분합니다.
- C는 실제 지원 source·별도 replication appliance·Mobility service·source admin/읽기 권한·필요 network를 강사가 준비합니다. **discovery appliance를 physical/AWS replication appliance로 재사용하지 않습니다.**
- AWS 문헌의 source 인증·WinRM/SSH 설정 변경은 실제 source 환경의 보안 승인 대상입니다. public root/password 로그인이나 전체 port 개방을 이 워크샵의 자동 준비 명령으로 복사하지 않습니다.
- source/target credentials·project registration key·실제 customer inventory·agent 설정은 저장소·Copilot·공유 screenshot에 넣지 않습니다.
- assessment는 가상 입력에 따른 sizing/cost 추정입니다. 무료 관리 기능이 있더라도 appliance·replica·storage·test/target VM·network·egress는 별도 비용일 수 있습니다.
- GPU·HA·대규모 disk/data·별도 OS upgrade는 기본 데모에 추가하지 않습니다. test/final source와 target, temporary resource의 owner·삭제 승인·보존 기간을 미리 정합니다.


## 4. 단계별 instruction — 모드를 먼저 고르기


### 4.1 합성 server 요구와 evidence 읽기


[사례 카드](./lab/assessment-case-ko.md)를 읽습니다. OS/service/local state를 유지하는 요구와, CPU·memory·disk가 **추가한 가상 capacity**라는 점을 구분합니다.

아래 네 질문에 답합니다.

1. 보존할 OS·disk·service를 정리하고 새 Container Apps 배포로 충족되는 범위를 비교합니다.
2. source dependency·boot type·쓰기량·기능에서 추가 확인할 항목을 정리합니다.
3. CSV/assessment의 확인 항목과 실제 replication/test VM의 확인 항목을 나눕니다.
4. A/B/C 중 선택할 모드와 실제 source가 필요한 단계를 구분합니다.

기존 [workloads.csv](../planning/lab/workloads.csv)는 선택 사례표이지 Migrate 공식 import 형식이 아닙니다. 그대로 업로드하지 않습니다. A만 선택하면 아래 실제 Portal 행동은 하지 않고 흐름을 읽습니다.


### 4.2 선택 B — Portal에서 새 assessment project만 준비


실습 대상·권한·비용·관리 geography를 승인한 뒤에만 수행합니다.

1. Portal에서 **Azure Migrate**를 찾고 현재 경험의 **Create project** 경로를 엽니다.
2. 승인된 subscription·실습 전용 새 group `rg-amw-migrate-<lab-id>`·고유 project `migrate-amw-<lab-id>`를 정합니다.
3. group/project에 `Workshop=azure-migration-servers`, `LabId=<lab-id>` 등 실습 식별 정보를 적용/기록합니다. Portal에서 지원되는 적용 위치는 검증 때 확인합니다.
4. project geography와 이후 assessment target region이 같은 설정 항목이라고 가정하지 않습니다.
5. 기존 운영/공유 project를 가져오지 않고 source discovery/appliance 등록이나 **Replicate/Migrate**는 선택하지 않습니다.
6. project·owner·교육 모드 B·생성한 관련 resource를 기록합니다.

**관찰할 결과:** 이 실습의 Migrate project와 assessment 도구 진입점입니다. 아직 실제 source를 발견하거나 VM을 복제한 결과가 아닙니다.

현재 Portal이 문헌의 경험과 다르면 관리자와 공식 경로를 확인하고 중단합니다. 메뉴가 없다고 Terraform/자체 API로 같은 기능을 만들지 않습니다.

현재 project 흐름은 **All projects → Create project**에서 form을 검토하는 것입니다. 전용 project 생성 승인 후 **Start discovery → Using import → Server inventory (CSV)**로 진입합니다. 이때 “Start discovery”는 import 진입 메뉴 이름이며 합성 CSV 업로드를 실제 source discovery로 표현하지 않습니다.


### 4.3 공식 CSV template에 한 합성 서버만 입력


1. Discovery and Assessment 쪽의 **Discover / Import using CSV** 또는 현재 이에 해당하는 import 경험을 엽니다.
2. **Download template**로 현재 공식 CSV와 필드/OS 인식 목록을 확보합니다. 이 저장소의 카드나 계획 CSV를 대신 업로드하지 않습니다.
3. [사례 카드](./lab/assessment-case-ko.md)의 가상 capacity를 그 template에 **한 서버만** 입력합니다.
4. `Server name`은 실습 전용 고유 이름, cores `4`, memory 필드는 후보 `8192`, OS name은 현재 지원 목록에 맞는 `Windows Server 2019`, architecture는 가정한 x64로 표시합니다.
5. disk size 등은 현재 template이 지원하는 위치에 가상 값으로 넣고 performance/history·boot/source IP 등 unknown은 지원 규칙에 맞춰 미확인으로 남깁니다. 정확도를 높이려고 실제 측정값인 것처럼 임의 사용률/IOPS를 채우지 않습니다.
6. 단위·필수 필드·인코딩·OS 표현은 공식 template과 대조합니다. CSV가 업로드 가능하다는 것과 실제 source 지원은 다릅니다.
7. 입력을 검토하고 승인한 뒤 **Import**합니다. 상태·warning/error details를 읽어 필요한 입력을 수정합니다.

**관찰할 결과:** import 상태와 import-based 항목 1개입니다. `Completed`는 입력 inventory 수용의 결과이며 실제 OS·app discovery/호환성 검증은 아닙니다.

같은 Server name의 재import는 기존 항목을 갱신할 수 있습니다. 고유 실습 이름을 사용하고 공유 project의 데이터를 덮어쓰지 않습니다. 오류·unknown·warning을 삭제해 성공처럼 만들지 말고 근거를 기록합니다.

현재 화면의 **Download .CSV file**로 공식 template을 확보하고 검토한 파일을 **Browse → Import**로 올립니다. 제공된 [synthetic-inventory.csv](./lab/synthetic-inventory.csv)는 Portal 공식 template의 **27개 column**을 유지한 **가상 서버 1개**입니다. 실제 AWS inventory나 측정 성능값이 아닙니다.

| 입력 | 합성 값 |
|---|---|
| 필수 server name | `synthetic-srv-01.example.invalid` |
| 필수 cores / memory MB | `4` / `8192` |
| 필수 OS name | `Microsoft Windows Server 2019 (64-bit)` |
| OS version / architecture | `2019` / `x64` |
| Disk 수 / disk 1 GB | `1` / `64` |
| IP·사용률·throughput·IOPS·boot 근거 | 빈 값 / unknown, 측정한 0이 아님 |

별표 필드는 최소 필수 입력이며 전체 column 구조를 유지하고 현재 다운로드한 template과 비교합니다. 다른 전용 실습에서는 필요하면 고유 합성 이름을 사용하고 다른 참가자의 같은 이름 항목을 갱신하지 않습니다. [계획 workloads.csv](../planning/lab/workloads.csv)와 달리 이 파일은 **Azure Migrate CSV import용**이며 실제 discovery·복제·test migration·AWS transfer용이 아닙니다.

![Completed·Rows processed 1인 Azure Migrate 합성 CSV import details](./images/portal-synthetic-csv-import.png)

*Completed / Rows processed 1은 가상 inventory 1행을 수용했다는 뜻입니다. assessment·readiness 추천·서버 이전 결과가 아닙니다.*

project inventory에서 imported 항목을 읽고 제공 입력과 없는 근거를 구분합니다.

![Azure Migrate inventory의 가상 imported server 1개](./images/portal-synthetic-inventory.png)

*잘라낸 화면은 imported 항목 1개·Windows Server 2019·unknown IP·Dependencies: Not supported를 보여줍니다. column 폭 때문에 이름/OS 문장이 잘려 있으므로 전체 입력은 연결된 합성 CSV를 읽고 화면에 전부 보인다고 하지 않습니다. “Not supported”는 이 imported inventory 화면의 dependency 정보 경계이지 Azure Migrate 전반의 미지원이나 실제 앱 dependency의 판단이 아닙니다.*


### 4.4 Assessment에서 readiness·sizing·비용 읽기

import 후 Portal이 안내하는 **15분 대기**를 고려한 뒤 assessment로 진행합니다. inventory 수용을 확인한 다음 아래 절차로 assessment를 생성하고 계산 결과를 읽습니다.

1. 기존 승인 **Migrate project → Overview → Create assessment**를 엽니다.
2. **Basics**에서 `synthetic-vm-<lab-id>`처럼 고유 합성 이름을 정합니다. **Add workloads**에서 `synthetic-srv-01.example.invalid`의 checkbox 하나만 선택하고 **Add selection**으로 확정합니다. 다른 참가자의 inventory를 포함하지 않습니다.
3. **General**에서 target region·environment·currency·가격/savings/discount·시간·license를 읽습니다. 예시 계산은 **Korea Central / Production / USD / Pay as you go / savings 없음 / discount0% / 월31일 / 하루24시간**입니다. Production은 견적 설정이지 운영 workload 배포 승인이 아닙니다.
4. hardware-only 입력에는 **Sizing: As on-premises**를 선택합니다. 예시 견적은 **Windows Azure Hybrid Benefit: No / Linux Azure Hybrid Benefit: No / Include Defender cost: No**입니다. 계산에서 Defender 비용을 제외해도 기존 Defender 설정을 끄는 것은 아닙니다.

![합성 Azure VM 견적의 Assessment General 설정](./images/portal-assessment-settings.png)

5. 필요한 경우에만 **Advanced** 기본값을 확인하고 target은 **Azure VM**으로 유지합니다. form을 채우려고 다른 workload를 추가하지 않습니다.
6. **Review**에서 **server1개·Azure VM·As on-premises·Korea Central·AHB No·선택 security cost 가정**을 대조합니다. owner 확인 후 **assessment 생성만** 승인합니다.

![합성 서버1개와 선택 가정을 보여주는 Assessment Review](./images/portal-assessment-review.png)

7. **Decide and plan → Assessments**에서 자기 assessment의 status/readiness·source·target 추천을 읽습니다. 예시는 가상 imported server1개의 완료 assessment이며 VM/replication을 생성한 결과가 아닙니다.

![Ready·Extended support를 보여주는 가상 서버 Assessment summary](./images/portal-assessed-server-summary.png)

![Source hardware와 수집된 performance metric이 없음을 보여주는 화면](./images/portal-assessed-source-properties.png)

**없는 성능값을 올바르게 해석합니다.** CSV 입력은4core·8192MB·64GBdisk1개이며 utilization/IOPS 이력이 없습니다. UI/API의 CPU/memory/IOPS 기본0은 **측정한 idle 사용률이 아닙니다.** As on-premises 설정을 읽고 성능 수집 여부와 추천 계산 가정을 각각 확인합니다. hardware 입력·저장 설정·추천 설명을 함께 읽고 누락/default·상충 가정을 확인한 뒤 고객 설계에 활용합니다. 측정값을 만들어 넣거나 native field를 다시 이름 붙이지 않습니다.

![Azure VM/storage 추천과 월 비용 breakdown](./images/portal-assessed-target-recommendations.png)

| 예시 출력 | 해석 |
|---|---|
| Source Ready·Windows Server2019 Extended support | 적합성과 lifecycle은 별개입니다. Mainstream은2024-01-09 종료, Extended는2029-01-09 종료입니다. Extended를 이미 지원 종료로 읽지 않습니다. |
| `Standard_D4as_v5`·4vCPU/16GB | 합성 입력의 추천이지 측정 rightsizing·quota/가용성·부팅 검증·배포 capacity가 아닙니다. |
| `StandardSSD_E6`·64GB | 추천 disk이지 생성된 disk가 아닙니다. |
| Compute294.62+storage4.80=월299.42USD | retail/noAHB/no예약·31×24시간·Defender 제외 견적입니다. invoice·가격 견적 보장·전체 운영비·새 배포 요금이 아닙니다. |

예시를 활용할 때 [Windows Server2019 lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/windows-server-2019)·현재 서비스 지원을 다시 확인합니다.

**B는 assessment 해석에서 끝나며 migration이 아닙니다.** Ready/Suitable·추천 Server Migration 도구도 실제 boot/dependency/network/replication/app/data 호환성을 증명하지 않습니다. [CSV-imported 서버는 해당 inventory에서 바로 migration할 수 없으며](https://learn.microsoft.com/en-us/azure/migrate/tutorial-discover-import?view=migrate), 실제 지원 source·별도 복제 준비가 필요합니다. Replicate/Migrate를 누르거나 AWS source를 생성해 실습을 확대하지 않습니다.


### 4.5 A/C — 실제 AWS/physical replication 준비의 흐름 읽기


AWS가 없는 참가자는 다음을 **설명/강사 준비 자료**로 읽습니다. 강사 데모라도 필요한 환경이 없다면 live replication으로 표시하지 않습니다.

| 준비 대상 | 역할·읽을 것 | 혼동하면 안 되는 것 |
|---|---|---|
| 실제 source | OS/kernel·boot/disk·service 지원·쓰기 변화·접근/변경 승인 | 합성 imported 항목이 실제 EC2 source는 아님 |
| Discovery/assessment appliance | source 정보를 수집하는 선택 경로 | CSV import에는 appliance가 필수 아님 |
| 별도 replication appliance | AWS/physical agent-based 경로의 복제 준비·등록·연결 | discovery appliance나 복제할 source 자체에 설치하는 것으로 대체하지 않음 |
| Mobility service | source 측 복제 agent의 지원·등록·상태 | Dockerfile/AMI 이름만 변환하는 것이 아님 |
| Network/권한 | source↔appliance·appliance→Azure, URL/TLS·scope | broad inbound·권한 확대를 기본 해결책으로 하지 않음 |
| Target 설정 | region·compute/disk·NIC/subnet·test/final network·quota·비용 | assessment 값이 physical 경로에 자동 적용됐다고 가정하지 않음 |

AWS 공식 문헌은 별도 replication appliance의 현재 OS/하드웨어 조건과 source/appliance의 연결을 요구합니다. 구체 port·appliance size·agent 설치·인증 방식은 해당 경로의 최신 문헌과 보안 승인을 따르며 지금 배포하지 않습니다.

지원 검토 사례로 기존 AWS Terraform의 **Amazon Linux 가정**도 읽을 수 있습니다. 그 샘플은 실제 발견/복제한 source가 아닙니다. AWS 공식 문헌의 Amazon Linux as-is 이전 제약을 검토하고 필요하면 앱을 지원 OS/플랫폼에 재배포하는 다른 접근법을 택합니다. 임의 disk/image 변환 코드로 지원을 보장하지 않습니다.


### 4.6 준비된 강사 C — Portal 복제·test migration·결과 해석


현재 기본 범위에서는 실제 실행하지 않습니다. **지원 source와 모든 준비·생성/변경·비용 승인이 확보된 별도 데모만** 다음을 수행할 수 있습니다.

1. 현재 Azure Migration and modernization의 migration 경험에서 준비된 실제 source를 선택합니다. CSV 항목과 실제 replication inventory를 구분합니다.
2. source 범위·target compute/storage/network를 검토하고 승인 후 replication을 시작합니다.
3. 초기/변경 복제 상태·health·지연·error와 service가 요구하는 조치를 읽습니다. 진행률이 보인다는 이유로 데이터 일관성·앱 준비를 확정하지 않습니다.
4. 준비된 서버에 **Start test migration**을 선택하고 운영과 분리한 test VNet·subnet·임시 VM/disk·비용을 확인합니다.
5. test target이 운영 DNS·DB·queue·mail/payment 등의 외부 dependency에 쓰지 않도록 endpoint/config·경로를 검토합니다. VNet 이름에 test라고 쓴 것만으로 격리가 보장되지 않습니다.
6. service job status와 별도로 test VM의 boot·선택 service·대표 data·실제 앱 동작을 확인합니다. source 기능이 unknown이면 테스트 기준도 먼저 보완합니다.
7. 결과·오류·확인하지 못한 기능을 기록하고 Portal의 **Clean up test migration** 경로로 test 자원을 정리합니다.

**기대 결과:** 서비스 job과 실제 target의 결과를 함께 설명하고 test 정리를 확인합니다. 원래 source가 계속 운영될 수 있더라도 복제/데모의 부하·연결 영향은 별도로 관리합니다.


### 4.7 Cutover·완료와 rollback 경계


공통 판단이 필요하면 [컷오버·롤백](../cutover/README-ko.md)의 카드/runbook을 사용합니다. 이 서버의 native source/replication·test evidence가 없으면 실제 전환이 아니라 tabletop으로 기록합니다.

1. [계획 모듈](../planning/README-ko.md)의 go/no-go·backup·데이터 기준·전환 책임자를 다시 확인합니다.
2. source 쓰기 정지·최종 sync·migration 승인·connection/DNS 전환 순서를 **source에 맞게** 확인합니다.
3. Portal의 planned migration 옵션을 읽습니다. AWS/physical source의 실제 중지 책임·방법을 확인하지 않고 “옵션을 선택하면 AWS가 자동 정지됐다”고 가정하지 않습니다.
4. 승인된 경우에만 final migration을 진행하고 service 결과·target boot/app/data·network/identity·관측을 확인합니다.
5. **Complete migration / stop replication**은 복제 상태·임시 resource의 정리와 연결해 읽습니다. 실제 버튼의 영향·되돌릴 수 없는 시점은 source·운영·복구 승인과 대조합니다.
6. target에 새 쓰기가 있으면 source connection 복귀만으로 data rollback이 되지 않습니다. rollback 조건·data 처리·보존 기간을 별도로 적용합니다.
7. source·backup 삭제/해지는 acceptance·보존 기간·소유자 승인 이후이며 기본 자동 정리 명령에 넣지 않습니다.

Online·동기화·최종 migration 선택은 무중단 보장이 아닙니다. 서비스의 migration 완료와 운영 cutover 수용을 구분합니다.


## 5. 성공 기준·대표 실패


| 범위·관찰 | 판단·대응 |
|---|---|
| A의 학습 완료 | imported evidence·실제 discovery·assessment·replication/test/cutover를 구분하고 source가 없는 범위는 사례·공식 절차로 설명 |
| B의 import/assessment | 공식 입력과 고유 합성 항목, warning/unknown·as-is 입력·출력 한계를 읽음 |
| Import OS/형식 오류 | 현재 template·인식 목록·단위 확인. 이름 치환으로 지원된 것처럼 만들지 않음 |
| 역할·Portal 메뉴 없음 | 현재 Migrate 역할/경험·scope·관리자 준비 확인. subscription Owner/tenant 설정을 자동 확대하지 않음 |
| C에서 source가 안 보임 | 실제 replication appliance·Mobility service·등록·연결·OS 지원을 확인. assessment/CSV 항목이 있다는 것으로 대체하지 않음 |
| 복제 지연·실패 | service health/error·appliance/source/network·data 변화량을 읽고 중단/조치. retry 플랫폼을 새로 만들지 않음 |
| test VM boot/app 실패 | OS/boot/disk·service dependency·config·network·identity를 검토. job 성공만으로 accept하지 않음 |
| 정리 후 비용 남음 | target·disk·storage·appliance·test resource·복제 상태·보존 범위를 확인 |

실패를 우회해 `Ready`·job 성공·전환 완료로 쓰지 않습니다. 기록은 합성 입력/준비된 데모/실제 확인 범위를 구분합니다.


## 6. 정리 — 교육 모드별로 다르게


### A: 읽기만 수행


Azure 삭제 대상이 없습니다. 개인 기록은 합성 요구·기준만 보관합니다.


### B: 생성한 import/assessment 전용 project


1. project/group 이름·lab ID·owner와 관련 resource 목록을 Portal에서 확인합니다.
2. 다른 참가자의 data·discovery appliance·replication·운영 source/target이 없는 **전용 project**인지 확인합니다.
3. 필요한 합성 assessment 기록은 식별정보/비밀 없이 보관합니다.
4. 승인 후 해당 project·전용 group의 현재 Portal 삭제 경로를 따릅니다.
5. 관련 storage·management resource·비용/잔여 상태를 확인합니다.

imported 서버의 개별 삭제가 제공된다고 가정하지 않습니다. 같은 이름 reimport/공유 project 삭제로 정리하지 않습니다. 생성 전부터 전용 project를 써야 하는 이유입니다.


### C: 강사가 소유한 복제 데모


- **Clean up test migration**과 **Complete migration/stop replication**, project 삭제, 실제 target 삭제는 서로 다른 작업입니다.
- 먼저 각 service 동작이 정리하는 resource를 확인하고 source 보호·rollback/보존 조건을 대조합니다.
- test VM·disk·NIC, 복제 관련 storage/state, appliance, 최종 target의 owner·필요성을 각각 확인합니다. project 삭제만으로 모두 없어졌다고 하지 않습니다.
- 이 모듈이 만들지 않은 기존 source·backup·network·다른 트랙 resource는 삭제하지 않습니다.
- 삭제는 영향·보존 조건을 승인한 뒤 수행하고 실제 잔여 목록·비용을 확인합니다.


## 7. 실제 이전에서 추가로 고려할 사항


- 실제 inventory/dependency·성능 관찰 기간·license·app/OS 지원·sizing 정확도.
- source 인증·agent 설치·appliance 규모/보안·bandwidth/egress·대규모 disk/change rate.
- test 격리·RPO/RTO·source 쓰기 중지·복구·DNS/connection·운영 인계.
- 관측·backup·보존·보안/규제. 관련 전문가 검토 없이 작은 합성 assessment를 production 이전 승인으로 쓰지 않습니다.


## 8. 출처


- 사례 카드·instruction은 직접 작성했고 실제 AWS inventory·service 결과·외부 screenshot을 복사하지 않았습니다.
