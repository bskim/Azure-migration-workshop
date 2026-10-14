# 컷오버 결정 카드 — 합성 사례

[English](./decision-cards.md) | 한국어

실제 migration job·writer event·복구 결과가 아닌 교육용 입력입니다. T0/T1은 순서 표시이며 실측 시간이 아닙니다. [컷오버 모듈](../README-ko.md)과 [runbook template](./runbook.csv)에 연결해 한 카드만 토론합니다.

## 카드 A — 읽기 전환 준비

source owner가 writer를 정지하고 최종 baseline을 보존했으며 native 완료/sync 조건을 충족했다고 가정합니다. target schema/내용/대표 읽기는 일치하고 승인된 새 읽기 client가 있습니다. native migration의 쓰기와 별개인 새 business writes는 없습니다. source·backup·기존 profile·복귀 방법·승인자는 보존되어 있습니다.

**검토:** 실제 GO에 필요한 확인 결과·승인을 정리합니다. 읽기 전환과 writer 허용을 각각 결정합니다. 실제 전환은 카드의 가정과 별도로 확인하고 승인합니다.

## 카드 B — 읽기 전환 뒤 접속 실패, 새 쓰기는 없음

target 읽기 profile에서 connection/TLS/잘못된 DB 오류가 발생했다고 가정합니다. source는 보호되어 있고 target의 새 business writes가 없다는 실제 근거가 있습니다. 기존 profile·권한·baseline과 source owner가 남아 있습니다.

**검토:** 개인 읽기 profile의 복귀 조건·승인을 정리합니다. source 읽기 수용과 writer 재개의 승인자를 구분합니다. job 취소·target 삭제는 접속 확인 이후에도 별도 승인합니다.

## 카드 C — target 새 쓰기 이후 불일치

target이 LAB-WRITE-001을 받았고 source에는 없으며 이후 target 오류가 발생했다고 가정합니다. 양쪽 DB·backup은 보존되어 있습니다.

**검토:** source 복귀 시 누락될 데이터를 확인합니다. writer 정지·차이 확인·복원/재조정·허용 유실/RPO·복구 승인의 담당자를 정리합니다. 이 카드에서는 판단을 연습하며 쓰기 SQL·reverse copy·rollback 프로그램은 실행하지 않습니다.

## 카드 D — 쓰기 상태 unknown

target 오류가 있지만 writer·log·실제 data는 확인되지 않았습니다. 자기 테스트는 읽기뿐이지만 다른 client/job/queue는 unknown입니다.

**검토:** 카드 B의 no-write 조건과 현재 확인한 범위를 비교합니다. unknown을 유지하고 NO-GO 또는 복귀 승인 대기로 판단하며 owner에게 writer/log/data 확인 결과를 요청합니다.

## 학습 결과

한 카드의 GO / NO-GO / 복귀 승인 대기 / data 복구 계획 필요 판단과 이유·미확인·owner·양쪽 보존·다음 확인을 기록합니다. 자동화나 운영 전환은 하지 않습니다.
