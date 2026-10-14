# Azure Migration Workshop — contribution guidance / 작성 안내

## English

- Public documentation is paired: root `Readme.md`/`Readme-ko.md`, directory `README.md`/`README-ko.md`, and guide/lab `name.md`/`name-ko.md`. Every audience document has a reciprocal language switch. English links route to English Markdown; Korean links route to Korean Markdown. Executable code and images are shared.
- Start with the learner's workload and selected mode. Keep modules independent, use minimum inputs and avoid mandatory completion of unrelated tracks. Reuse approved image, identity, database and private-client inputs.
- Explain why each step is chosen, its execution environment, expected observations, verification and owner-specific cleanup. Include Microsoft Learn service introductions, not just command references. Keep instructor setup, timing and diagnostic fixture notes in instructor guides, not learner status reports.
- Introduce Azure Migrate with server migration, Storage Mover with AzCopy, and DMS with engine-specific DB tools. Preserve native/private/Entra distinctions and current support constraints. Do not rebuild managed replication, CDC, copy, scheduling or retry platforms.
- Do not create AWS environments, query AWS credentials/AMI or run AWS plan/apply. Illustrative AWS source and synthetic Azure samples are learning inputs, not actual AWS migration evidence.
- Use only synthetic sandbox data. Never include customer data, secrets, identifiers, internal documents or sensitive outputs in files, prompts or shared screenshots. Respect approved package/image supply sources and distinguish Windows/WSL/guest shells and virtual environments.
- The provided Blob samples use public network Disabled with approved Private Endpoint/DNS/client and Entra/RBAC, no anonymous or Shared Key access. Identity permissions do not replace network isolation. Do not weaken policy, TLS or access boundaries to resolve errors.
- Display exact scope, costs and effects before Azure queries/plans, paid creation, assignments, apply, destructive migration actions or deletion; execute only within explicit approval. Consumers preserve shared inputs; source/backups remain until acceptance/retention/recovery approval.
- Report actual results and unresolved support/evidence accurately. Proposed commands, screenshots, static checks and prepared demos are not interchangeable with live native/app/data verification. Do not commit, create remotes or push without a separate request.

- Storage Mover is service introduction only in this workshop; do not generate native endpoint/job/Start/role labs, failed-run evidence or execution schedules. The separate private AzCopy lab remains available. Future customer execution follows supported official scenarios and their administrator's policies/approval.

## 한국어

- 공개 문서는 root `Readme.md`/`Readme-ko.md`, 디렉터리 `README.md`/`README-ko.md`, guide/lab `name.md`/`name-ko.md`로 짝을 만든다. 상호 언어 전환을 제공하고 영어 문서는 영어 Markdown, 한국어 문서는 한국어 Markdown으로 연결한다. 실행 코드·이미지는 공유한다.
- 학습자의 workload·선택 mode부터 정하고 module을 독립적으로 구성한다. 최소 입력과 기존 승인 image/identity/DB/private client를 재사용하며 다른 트랙 수강을 강제하지 않는다.
- 선택 이유·명령 환경·기대 관찰·검증·owner별 정리를 설명하고 Microsoft Learn 서비스 소개를 둔다. 강사 준비·시간·fixture 진단은 강사 가이드에 두고 학습자 문서에 작성/상태 이력을 넣지 않는다.
- 서버에는 Migrate, AzCopy에는 Mover, DB 도구에는 DMS/engine 선택을 함께 소개한다. native/private/Entra·지원 경계를 유지하고 관리형 복제/CDC/copy/scheduler/retry를 재구현하지 않는다.
- AWS 환경·credential/AMI 조회·plan/apply는 하지 않는다. AWS 소스 분석과 Azure 합성 실습은 실제 AWS 이전 성공 근거가 아니다.
- 합성 sandbox data만 사용한다. customer data·secret·식별정보·내부 문서·민감 출력을 파일/prompt/screenshot에 넣지 않는다. 승인 package/image source와 Windows/WSL/guest shell·venv 구분을 따른다.
- 제공 Blob 샘플은 public Disabled·승인 Private Endpoint/DNS/client·Entra/RBAC·익명/Shared Key 금지다. identity가 network 격리를 대신하지 않으며 정책/TLS/접근 경계를 낮춰 오류를 해결하지 않는다.
- Azure 조회/plan·유료 생성·role·apply·파괴적 이전·삭제는 정확한 scope/비용/영향을 표시하고 명시적 승인 범위만 실행한다. consumer는 공유 입력을 보존하고 source/backup은 acceptance/retention/복구 승인까지 유지한다.
- 실제 결과·미확인 지원/근거를 정직하게 기록한다. 제안 명령·screenshot·정적 검사·준비 데모를 live native/app/data 검증으로 바꾸지 않는다. 별도 요청 없이 commit/remote 생성/push를 하지 않는다.

- 이 워크샵의 Storage Mover는 서비스 소개만 제공하며 native endpoint/job/Start/role 실습·실패 run 근거·실행 시간표를 만들지 않는다. 별도 private AzCopy는 유지한다. 미래 고객 실행은 공식 지원 시나리오와 고객 정책/관리자 승인을 따른다.
