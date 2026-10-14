# DB 모듈의 작은 공통 합성 데이터

[English](./README.md) | 한국어


PostgreSQL·MySQL 두 실제 모듈만 재사용하는 SQL 입력과 비교 기준입니다. 이전 서비스·CDC·copy engine을 구현한 것이 아니며 새 business app·앱 DB adapter도 아닙니다.


## 사용 순서와 범위


1. 승인된 새 합성 **source DB `workshop`**만 준비합니다. 실제 customer/운영 DB나 migration target에 seed하지 않습니다.
2. 선택 엔진의 `schema.sql`로 `items`, `batches`, `batch_items`를 준비합니다.
3. 이 폴더의 [seed.sql](./seed.sql)을 **한 번만 source에** 실행합니다. 이미 데이터가 있으면 중단하며 `DROP/TRUNCATE/IF NOT EXISTS`로 덮지 않습니다.
4. [verify.sql](./verify.sql)은 읽기 전용 결과 비교입니다. 동일한 script를 source와 migration이 완료된 target에 각각 실행합니다.

각 엔진의 승인된 DB/session을 명시적으로 선택하고 오류 중단을 켭니다. PostgreSQL은 새 `workshop` DB의 `public` schema, MySQL은 새 `workshop` DB를 명시합니다. 사용자·grant·DB 생성·접속 비밀은 이 SQL에 넣지 않습니다.


## 작성한 기대값


| 결과 | 의도한 값 |
---|---|
| 테이블 | 3개: items·batches·batch_items |
| 각 테이블 행 수 | 각각 10 |
| 전체 행 | 30 |
| join 결과 행 수 | 10 |
| quantity 합계 | 55 |
| 대표 첫 행 | 1, batch-01, item-01, 1 |
| 대표 마지막 행 | 10, batch-10, item-10, 10 |


## 엔진별 차이


- PostgreSQL schema는 DDL transaction을 사용합니다. source load는 오류 중단을 켜고 완료/rollback을 확인합니다.
- MySQL schema는 InnoDB를 명시하며 DDL implicit commit 때문에 중간 실패 후 일부 table이 남을 수 있습니다. 이때 자동 삭제·재seed하지 말고 실제 만든 대상과 승인된 초기화 방법을 확인합니다.
- MySQL의 CHECK enforcement는 해당 버전 지원을 확인합니다. 기본 source 사례는 승인된 8.0.16 이상 8.0 계열을 후보로 두되 migration service의 현재 지원도 별도로 검토합니다.
- `seed.sql`의 data insert는 transaction으로 묶었습니다. 오류를 무시하고 COMMIT·재실행하지 않습니다.


## 선택 경로


- [PostgreSQL migration service](../../modules/migration/database-postgresql/README-ko.md)
- [MySQL DMS](../../modules/migration/database-mysql/README-ko.md)

다른 엔진 모듈을 완료할 필요 없습니다. source owner·data 보호·cleanup은 선택 모듈을 따릅니다. 공통 앱은 현재 메모리 API이므로 이 데이터를 앱이 자동 사용한다고 주장하지 않습니다.

Native MySQL target에는 workload3개 외에 빈 `dms_persistent_objects` metadata table도 관찰됐습니다. mapped workload의 30행/DDL 비교와 physical target 전체의 차이는 별도로 기록합니다. [MySQL 검증](../../modules/migration/database-mysql/README-ko.md)은 이 정확한 service artifact를 명시하고 미확인 extra table을 조용히 제외하지 않습니다.
