# 컷오버 결정 카드 — 합성 사례

[English](./decision-cards.md) | 한국어

실제 migration job·writer event·복구 결과가 아닌 교육용 입력이다. T0/T1은 순서 표시이며 실측 시간이 아니다. [컷오버 모듈](../README-ko.md)과 [runbook template](./runbook.csv)에 연결해 한 카드만 토론한다.

## 카드 A — 읽기 전환 준비

source owner가 writer를 정지하고 최종 baseline을 보존했으며 native 완료/sync 조건을 충족했다고 가정한다. target schema/내용/대표 읽기는 일치하고 승인된 새 읽기 client가 있다. native migration의 쓰기와 별개인 새 business writes는 없다. source·backup·기존 profile·복귀 방법·승인자는 보존되어 있다.

**질문:** 실제 GO에 필요한 근거·승인은 무엇인가? 읽기 전환과 writer 허용은 왜 별도 결정인가? 카드의 가정만으로 실제 전환을 승인하지 않는다.

## 카드 B — 읽기 전환 뒤 접속 실패, 새 쓰기는 없음

target 읽기 profile에서 connection/TLS/잘못된 DB 오류가 발생했다고 가정한다. source는 보호되어 있고 target의 새 business writes가 없다는 실제 근거가 있다. 기존 profile·권한·baseline과 source owner가 남아 있다.

**질문:** 개인 읽기 profile은 어떤 승인 후 복귀할 수 있는가? source 읽기 수용과 writer 재개는 누가 별도로 승인하는가? 접속 성공만으로 job 취소·target 삭제를 승인할 수는 없다.

## 카드 C — target 새 쓰기 이후 불일치

target이 LAB-WRITE-001을 받았고 source에는 없으며 이후 target 오류가 발생했다고 가정한다. 양쪽 DB·backup은 보존되어 있다.

**질문:** source로 접속만 되돌리면 어떤 데이터가 빠지는가? writer 정지·차이 확인·복원/재조정·허용 유실/RPO·복구 승인 책임은 누구에게 있는가? 이 카드는 쓰기 SQL·reverse copy·rollback 프로그램 실행 지시가 아니다.

## 카드 D — 쓰기 상태 unknown

target 오류가 있지만 writer·log·실제 data는 확인되지 않았다. 자기 테스트는 읽기뿐이지만 다른 client/job/queue는 unknown이다.

**질문:** 카드 B처럼 취급할 수 없는 이유는? unknown을 유지하고 NO-GO 또는 복귀 승인 대기로 판단하며 owner에게 실제 writer/log/data 근거를 요청한다.

## 학습 결과

한 카드의 GO / NO-GO / 복귀 승인 대기 / data 복구 계획 필요 판단과 이유·미확인·owner·양쪽 보존·다음 확인을 기록한다. 자동화나 운영 전환은 하지 않는다.
