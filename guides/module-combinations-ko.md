# 모듈 조합 — 필요한 경로만 구성

[English](./module-combinations.md) | 한국어

[workload 선택표](../Readme-ko.md)와 [참가자 준비](./participant-preparation-ko.md)로 주된 목표 하나를 고릅니다. 필요한 기초만 추가하고 모든 조합에 compute·DB를 넣지 않습니다. 세부 setup·실측·diagnostic fixture는 [강사 가이드](./instructor-guide-ko.md)에 둡니다.

## 1. 추천 경로

| 목표 | 선택 자료 | 기본 제외 |
|---|---|---|
| 작은 HTTP 앱/서버 관리 축소 | 필요한 Identity/network+ContainerApps+관측성 | VM/AKS/DB/migration |
| EC2+Docker 운영 | VM+Docker+필요 identity/network+관측성 | AKS/CAA/DB 필수 수강 |
| EKS/Kubernetes | AKS manifest/cluster+identity/network 차이 | 다른 compute·모든 DB |
| Lambda/HTTP | Functions adapter/host/auth+관측 | ACR image·모든 trigger·다른 compute |
| S3/objects 우선 | 필요 Blob기초+Mover 소개/private AzCopy+계획/컷오버 | 앱/compute/DB/Terraform |
| DB 하나 | PG전용 OR MySQLDMS OR SQL타깃/DMS/SqlPackage+계획/컷오버 | 다른 engine·앱 adapter |
| 기존 OS/service 유지 | Migrate 합성 CSV/Portal assessment+계획/컷오버, 실제 복제는 별도 준비 범위 | 앱 재배포로 대체·assessment 중 target VM 배포 |
| IaC 분석만 | Terraform 읽기/정적+관련 개념 | AWS 실행·필수 Azure |
| 의사결정만 | 계획+컷오버 카드 | resource/live job |

각 module 링크·최소 입력은 root 선택표에 있습니다. 기존 승인 image/identity/source/private client는 생성 준비를 대체하지만 의미·scope·owner 설명은 생략하지 않습니다. Blob에는 승인 private endpoint/DNS/client가 필요하며 VM+Docker 수강/public 예외를 강제하지 않습니다.

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성합니다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인합니다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따릅니다. 인증과 network는 다른 통제입니다.

## 2. 온보딩 하루 예시

교육360분+점심/휴식/환경대응120분의 계획 가설이며 실제 참가자 시간이나 필수 코스가 아닙니다.

| 내용 | 계획 분 |
|---|---:|
| scope/resource 계층 | 30 |
| Identity/RBAC·관리/data | 50 |
| Network 개념/구성, probeVM 제외 | 35 |
| 선택 private Blob 기초 | 45 |
| Image/digest·publisher/consumer | 30 |
| 선택 ContainerApps·기대 결과 | 65 |
| Portal 관측/비용 | 45 |
| owner cleanup/미확인 | 30 |
| compute 비교/회고/선택 Copilot | 30 |
| 합계 | 360 |

AKS/VM을65분에 맞추려고 지원/안전을 낮추지 않습니다. 선택 내용을 줄이거나 승인 입력을 준비하거나 별도 회차로 나눕니다. live 입력이 없으면 walkthrough/demo를 정확히 선택합니다.

## 3. 이전 하루 예시

지원 합성 object/DB 하나 또는 준비된 서버 데모를 선택하며 없는 AWS job을 기본으로 하지 않습니다. 같은360+120분 가설은 다음처럼 구성할 수 있습니다.

| 내용 | 계획 분 |
|---|---:|
| 보존 요구/native 도구 | 50 |
| source/target·권한/network/비용 | 45 |
| Portal/native validation/assessment·영향 gate | 50 |
| 승인 도구 하나 실행 또는 준비 데모 | 70 |
| native 상태/오류/지원 해석 | 35 |
| data/schema/필요 기능 | 30 |
| cutover 카드 또는 개인 읽기client | 40 |
| owner/보존/정리 | 20 |
| 실제 이전 checklist/회고 | 20 |
| 합계 | 360 |

Objects는Mover 소개만·private AzCopy 실행, DB는engine/native 하나, Migrate는CSV와실제복제/test를 구분합니다. MI/runtime/appliance 비용·준비가 크면 준비 데모를 선택하고 참가자 source 성공으로 표현하지 않습니다.

## 4. 반일/셀프 가이드

독립 목표 하나와 관찰 기준으로 끝냅니다. 승인 입력을 재사용하고 준비/job 대기는 교육과 구분하며 필요한 개념만 추가합니다. IaC가 목표일 때만 실행 segment를Terraform으로 바꾸고 이전서비스 소개는 유지합니다.

실제 AWS 환경은 만들지 않았으며 Azure합성 결과는AWS인증/discovery/transfer가 아닙니다. online은무중단 보장이 아니고 target새쓰기 이후는접속복귀와data복구가 다릅니다. 강사는설명/질문/setup/대기/cleanup을실측해 다음회차를 조정합니다.
