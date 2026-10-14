# 참가자 준비 — 선택한 모듈에 필요한 것만

[English](./participant-preparation.md) | 한국어

[workload 선택표](../Readme-ko.md)에서 목표·모듈·mode를 고릅니다. 읽기·Portal walkthrough·준비된 강사 데모·승인 합성 실습은 준비가 다르며 모든 도구 설치·트랙 배포가 필요하지 않습니다.

**AWS 안내:** AWS Terraform 분석과 Azure 합성 파일/DB/앱을 사용해 학습합니다. 실제 AWS 환경 구축·이전은 실습 범위에서 제외합니다.

## 1. 범위 선택

1. 해당 module의 입력·결과·제외·cleanup owner를 읽습니다.
2. 목적에 필요한 compute 하나 또는 DB engine 하나만 고릅니다. Blob/IaC/계획에는 앱 서버가 필요 없습니다.
3. 읽기/walkthrough/demo/합성 live 범위를 강사와 합의합니다.
4. 아래 선택 행과 module의 실제 version/환경 요구만 준비합니다.

[모듈 조합](./module-combinations-ko.md)을 참고합니다. 시간은 계획용이며 배포·권한·job 대기는 환경에 따라 다릅니다.

## 2. 민감한 값 없이 요구 공유

source 종류(EC2/EKS/S3/DB engine), 목표·Azure/CLI/SQL/Kubernetes 경험·mode·Windows/WSL/client·정책 제약을 알려줍니다. sandbox·권한·region/quota·비용 승인 준비 여부만 공유합니다.

customer 이름·실제 inventory/data·subscription/tenant ID·credential/token·내부 문서를 공개 설문/Git/prompt/screenshot에 넣지 않습니다. 실제 값은 승인 private 경로로 준비하며 MFA 코드 공유·인증 우회를 하지 않습니다.

## 3. 필요한 도구만 준비

| 선택 mode | 준비 | 자동 추가하지 않는 것 |
|---|---|---|
| 계획/카드/source 읽기 | browser/text/CSV/SQL 읽기 | cloud login/배포 |
| Portal 소개/관찰 | 승인 user·해당 조회/관리 scope | 전체 CLI/Terraform |
| Migrate 합성 CSV assessment | browser·승인 전용 project/assessment 권한·[가상1행 CSV](../modules/migration/servers/lab/synthetic-inventory.csv), import 후 대기 고려 | 실제 AWS/source VM·복제 appliance·새 target VM |
| Identity/network CLI | PowerShell7.4+·Azure CLI | 앱/compute/DB |
| Blob data | private endpoint/DNS/client·실제 data identity, 선택 CLI/MI | Docker/ACR/앱/다른 compute 수강 |
| local 앱 | WSL Bash·uv·Python3.12 | Azure login/DB/SDK |
| local container | Docker daemon·승인 image/package | 필수 Azure registry |
| VM+Docker | image/registry/VM/MI, SSH면 키/tunnel 또는 private Run Command/outbound | private 경로 public IP/SSH·다른 compute |
| AKS | 지원 kubectl/kubelogin·image/cluster/network/role, private API면 private client/DNS | public API 개방·다른 compute |
| Container Apps | 지원 core CLI·image·UAI pull/assign | 필요 없는 extension·VM/AKS |
| Functions HTTP | 읽기 source, local Python/CoreTools v4/Azurite, cloud hosting/storage/auth/deploy | 같은 ACR image·모든 event trigger |
| Terraform 정적 | Terraform·승인 provider/module 다운로드 | AWS login/plan/apply·유료 Azure |
| DB 하나 | 지원 SQL client/source/빈 target·native 연결/권한 | 다른 engine·앱 DB adapter |
| SQL B2 | 공식 SqlPackage/private Windows client·보호 BACPAC·source TLS/Windows auth·target MI/빈DB·Import/권한복구 승인 | DMS/SHIR/Blob/target SQL password |
| AzCopy 오브젝트 실습 | 공식 utility·source Reader/target Contributor·양쪽 private path·지원 topology | Mover 실행·자체 copy code |

PowerShell·local WSL Bash·VM Bash를 구분하고 Windows .venv/WSL .venv-wsl을 공유하지 않습니다. [PowerShell 설치](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell)·[CLI 설치](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)를 참고합니다. 승인 source를 사용하고 TLS/서명 검사 해제·fallback feed를 추가하지 않습니다.

**샘플 설정:** 제공 Blob 예제는 private endpoint/DNS·public Disabled·Entra data 인증·Shared Key/익명 금지·bypass None·resource-instance 예외 없음으로 구성합니다. 선택 lab의 승인 identity/network 입력과 관리자에게 적용 정책을 확인합니다. 제공 설정/TLS 검사는 유지하며 대안은 별도 지원 시나리오·승인을 따릅니다. 인증과 network는 다른 통제입니다.

## 4. Network·identity 입력 확인

login은 management/data/engine/Kubernetes 권한을 자동 부여하지 않습니다. Contributor는 role assignment 권한이나 DB superuser가 아닙니다. local user·VM MI·kubelet·CAA UAI는 다릅니다. 필요하면 [Identity](../modules/onboarding/identity/README-ko.md) 개념만 참고합니다.

Blob 기본은 public Disabled/Deny/bypassNone·익명/SharedKey 금지와 승인 private endpoint/DNS/client입니다. 실제 실행 위치의 canonical hostname/route를 확인합니다. WSL/CloudShell/Portal 관리가 private data 접근을 보장하지 않습니다. [private 입력](../shared/storage-private-access/README-ko.md)을 재사용하거나 강사 fixture/walkthrough를 선택하고 public을 켜지 않습니다.

native migration은 source/tool/target 실제 연결·version 지원·engine 권한을 별도로 확인합니다. Mover는 소개만 제공하므로 참가자는 선택 AzCopy Reader/Contributor만 준비합니다. CSV assessment는 복제 source가 아닙니다. 참가자에게 적용되는 정책이 SQL Entra-only를 요구할 때 해당 도구 인증 지원을 확인합니다. generic target Entra 지원만으로 충분하지 않으며 모든 Azure의 공통 인증 조건도 아닙니다.

Functions local settings는 emulator용이며 Git/publish에서 제외합니다. cloud storage MI·HTTP key·사용자 app 인증은 별개입니다. prebuilt package와 CoreTools remote publish는 다른 경로이고 local 공급 예외를 cloud builder에 확대하지 않습니다.

승인 image/identity/source/client가 제공되면 생성 준비를 생략합니다. [image 준비](../shared/container-image/README-ko.md)는 app/cluster를 배포하지 않습니다.

## 5. 비용·안전 합의

directory/subscription/region/group/owner/mode·지원/quota·최소권한·비용·stop/cleanup을 확인합니다. [계산기](https://azure.microsoft.com/en-us/pricing/calculator/)는 견적이며 budget은 알림이지 강제 상한이 아닙니다. AKS node/disk/outbound·PremiumDMS·SQL runtime/MI/VM·fixture/storage/backup/egress 비용을 승인합니다.

source readonly/writer·target truncate/overwrite·Complete migration·role·삭제는 해당 별도 승인 없이 실행하지 않습니다. live 조건이 없으면 읽기/데모로 학습합니다. source/backup은 보존/복구 결정까지 유지합니다.

## 6. 중단 조건

예상과 다른 target/owner·미지원 source/version/mode·source/network/권한/비용 승인 없음·공개 credential 요청·target 기존 data·기대와 다른 결과·job 성공에도 미확인 schema/기능·unknown writer/rollback 책임이면 중단합니다.

오류를 default·권한 확대·data 삭제·새 migration 코드로 덮지 않고 실제 오류와 승인 경로를 강사/관리자와 해결합니다.

## 7. 소유자별 정리

consumer 자기 resource/정확한 새 grant를 먼저, 공유 publisher는 마지막 consumer 이후 정리합니다. 외부 source/backup/강사 입력·키·다른 group·전체 작업 폴더는 삭제하지 않습니다. actual resource/data/grant와 지연 비용을 확인합니다. 준비·시간·diagnostic fixture는 [강사 가이드](./instructor-guide-ko.md)를 따릅니다.
