# Azure Migrate assessment 합성 사례

[English](./assessment-case.md) | 한국어

실제 서버 inventory·AWS discovery·완료한 Azure assessment가 아니며 업로드용 CSV도 아니다. [서버 모듈](../README-ko.md)과 서비스의 현재 공식 template을 사용한다.

별도 import 실습에는 가상 서버 1개를 담은 Portal template의 27-column [synthetic-inventory.csv](./synthetic-inventory.csv)를 공유 입력으로 사용한다. 아래 카드는 가정·unknown을 설명하며 CSV는 Azure Migrate import 입력이지 계획 사례표나 복제 source가 아니다.

## 보존 요구

가상 server-sample은 EC2의 Windows Server 2019 x64이며 OS·disk·service/local state 보존이 목표다. 중단 목표 60분은 가정이지 달성 결과가 아니다. source VM·data·account·appliance는 만들지 않았다. service 이름·port·path·dependency·boot 근거는 unknown이다.

## 공식 template의 합성 입력 후보

| 의미 | 후보 | 근거 수준 |
|---|---|---|
| 고유 이름 | srv-amw-<lab-id>.example.invalid | 실습 전용 가상 이름 |
| Cores | 4 | 가상 capacity |
| Memory MB | 8192 | 가상 capacity |
| OS | Windows Server 2019 | 가정, 현재 인식 목록 확인 |
| Architecture | x64 | 가정 |
| Disk 1 GB | 64 | 가상 크기, 실제 사용량 아님 |
| CPU/memory utilization | unknown | 0이나 임의 측정값을 넣지 않음 |
| Disk IOPS/throughput/network | unknown | 성능 수집 없음 |
| Boot type/source IP | unknown | 실제 근거 필요 |
| Hypervisor | unknown/해당 없음 | VMware/Hyper-V 필드에 AWS를 넣지 않음 |

다운로드한 template의 필드·단위·필수 입력·unknown 처리 규칙을 따른다. item·assessment에 고유 합성 lab 표시를 두며 공유 이름의 재import로 기존 항목을 갱신하지 않는다.

## 결과 해석 질문

1. import 수용과 실제 discovery는 왜 다른가?
2. as-is sizing은 어떤 가상 입력에 의존하는가?
3. 성능 이력 없이 performance-based rightsizing이라고 할 수 없는 이유는?
4. OS readiness가 app/service/data/boot 호환성을 보장하지 않는 이유는?
5. CSV-imported 항목을 그대로 복제할 수 없는 이유는?
6. 실제 데모에 필요한 지원 source·별도 replication appliance·Mobility service·network·역할은?

## 완료·중단 기준

가상 capacity와 unknown을 구분하고 출력 한계를 설명하면 완료다. 현재 template/UI 미제공·권한/형식/OS 인식 오류·기존 inventory 덮어쓰기 위험이면 중단한다. Ready·실제 SKU/비용·migration 성공을 미리 채우지 않고 실제 service 출력의 입력 근거·조건·관찰 시각을 별도로 기록한다.
