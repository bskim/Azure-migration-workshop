# 공통 샘플 앱 — 작은 HTTP API

[English](./README.md) | 한국어


AWS EC2에서 컨테이너를 실행한다고 가정한 소스와 Azure 컴퓨트에서 **같은 앱·이미지**를 실행하는 경로를 비교한다. AWS 계정·배포·실제 이전 데이터는 필요하지 않다.


## 1. 학습 목표와 범위


- 대상: 컨테이너에 익숙한 엔지니어, 예상 30~40분.
- Python 3.12 + FastAPI의 헬스 체크와 항목 읽기·쓰기만 제공한다.
- AWS/Azure SDK·DB·Blob·Queue·Key Vault에 의존하지 않는다.
- 저장소는 **프로세스 메모리**다. 초기 합성 항목은 2개이며 재시작하면 추가 데이터가 사라진다.
- 이름은 공백 제거 후 1~80자이며 최대 100개 항목까지만 저장한다. 무한 데이터 적재 실습이 아니다.
- 앱 인증이 없는 교육용 API다. 실제 데이터·비밀을 입력하지 않으며 운영 환경에 배포하지 않는다.

| 요청 | 기대 결과 |
|---|---|
| `GET /health` | `200`, `{"status":"ok"}` |
| `GET /items` | `200`, `id`·`name` 배열 |
| `POST /items`, `{"name":"workshop-item"}` | `201`, 생성한 `id`·`name` |
| 빈 이름·81자 이상·잘못된 타입·알 수 없는 필드 | `422`, `detail` 오류 |
| 100개 이후 추가 요청 | `409`, `Workshop item limit reached.` |

Azure 서비스는 이 앱 자체에 없으며 필요한 컴퓨트만 선택한다. [VM + Docker](../modules/onboarding/compute-vm/README-ko.md), [Container Apps](../modules/onboarding/compute-container-apps/README-ko.md), [AKS](../modules/onboarding/compute-aks/README-ko.md)는 동일한 앱·이미지를 사용하고 서로의 완료를 요구하지 않는다. 각 instruction의 최신 검증 상태는 별도로 확인한다.

사용자가 포함한 [Functions 선택 확장](../modules/onboarding/compute-functions/README-ko.md)은 같은 `app.py` source를 얇은 HTTP/ASGI adapter에 연결한다. 같은 Docker image를 그대로 배포하지 않으며 원본 앱/메모리 저장 동작은 바꾸지 않는다. host/worker·route/auth·scale의 새 경로는 별도 강사가 선택 환경의 지원과 동작을 확인한다.


## 2. 사전 준비


- [uv 설치 안내](https://docs.astral.sh/uv/getting-started/installation/): lock 파일을 사용한 환경 구성·실행 도구.
- Python 3.12. 없으면 `uv`가 해당 버전을 준비할 수 있으며 조직의 도구 다운로드 정책을 확인한다.
- 선택: Linux 컨테이너를 실행할 수 있는 Docker. 로컬 Docker 없이도 이후 ACR Tasks로 이미지를 빌드할 수 있다.
- 제한된 조직 환경에서는 **승인된 단일 패키지 소스**를 사용한다. 인증서 검증 해제, 공개 소스 fallback, 여러 index 혼합을 해결책으로 삼지 않는다. 로컬·Docker 빌드 모두 같은 정책을 검토한다.
- 고객에게 사내 feed나 사내 계정을 요구하지 않는다. 내부 URL·토큰은 저장소에 기록하지 않는다.


## 3. 로컬 앱 실행 — WSL Bash


**실행 환경:** WSL/Linux Bash, 현재 디렉터리는 이 `sample-app` 폴더다. Windows PowerShell용 Azure 명령과 섞지 않는다.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-wsl
export UV_LINK_MODE=copy
uv sync --frozen --python 3.12
uv run --frozen uvicorn app:app --host 127.0.0.1 --port 8080 --workers 1
```

**관찰:** `Uvicorn running on http://127.0.0.1:8080`과 요청 로그가 출력된다. 이 터미널을 유지한다. `--workers 1`은 메모리 데이터가 worker마다 달라지는 혼동을 피하기 위한 실습 설정이다.

두 번째 WSL Bash 터미널에서 확인한다.

```bash
curl --fail-with-body http://127.0.0.1:8080/health
curl --fail-with-body http://127.0.0.1:8080/items
curl --fail-with-body --request POST http://127.0.0.1:8080/items \
  --header 'Content-Type: application/json' \
  --data '{"name":"workshop-item"}'
curl --fail-with-body http://127.0.0.1:8080/items
```

**성공 기준:** 헬스가 `ok`, 초기 항목 2개, 쓰기 후 생성 항목 `id: 3`이 목록에서 보인다. 앞서 쓴 데이터가 있으면 ID·개수는 달라지므로 새 프로세스로 시작해 비교한다.

첫 터미널에서 `Ctrl+C`로 종료하고 다시 시작한다. 목록이 초기 2개로 돌아오는 것을 확인한다. 이는 메모리 저장 방식의 한계이며 DB 이전 성공을 뜻하지 않는다.


## 4. 테스트로 계약 확인 — WSL Bash


현재 디렉터리는 `sample-app`이다.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-wsl
uv run --frozen pytest -q
```

테스트는 매번 독립 앱을 만들고 입력 오류·용량 한도·데이터 초기화를 확인한다. 실제 `uvicorn` 서버도 임시 로컬 포트에서 시작해 HTTP 읽기·쓰기·오류 응답을 확인하고 종료한다. Docker 테스트는 다음 절의 이미지 변수를 설정하지 않으면 명시적으로 skip한다.


## 5. 같은 앱을 컨테이너로 실행 — WSL Bash


현재 디렉터리는 `sample-app`이다. `docker info`가 성공하는지 먼저 확인한다.

```bash
docker info
docker build --tag amw-workshop:0.1.0 .
docker run --detach --name amw-workshop-local \
  --publish 127.0.0.1:8080:8080 \
  --memory 256m --read-only --cap-drop ALL \
  --security-opt no-new-privileges \
  amw-workshop:0.1.0
```

**관찰:** 컨테이너 ID가 반환된다. 3절의 `curl` 요청을 같은 주소로 반복해 동일한 응답을 확인한다. 로컬 서버가 아직 8080을 사용하면 먼저 `Ctrl+C`로 종료한다. 같은 이름의 컨테이너가 있으면 덮어쓰지 말고 대상을 확인한다.

```bash
docker logs amw-workshop-local
docker inspect --format '{{.Config.User}}' amw-workshop-local
docker inspect --format '{{.State.Health.Status}}' amw-workshop-local
```

**성공 기준:** 사용자 `10001:10001`, 시작 후 약 30초 이내 헬스 상태 `healthy`, 읽기·쓰기 계약이 동일하다.

자동 컨테이너 검증도 선택적으로 실행할 수 있다. 테스트는 별도의 이름·임시 localhost 포트로 컨테이너를 만들고 검증 후 해당 컨테이너만 삭제한다.

```bash
WORKSHOP_CONTAINER_IMAGE=amw-workshop:0.1.0 uv run --frozen pytest -q
```


## 6. 대표 실패와 정리


| 실패 | 확인할 사항 |
|---|---|
| 패키지 다운로드·인증 실패 | 승인된 source·인증·네트워크를 확인한다. TLS 검증을 끄지 않는다. |
| Windows/WSL venv 충돌 | WSL은 `.venv-wsl`, Windows는 `.venv`로 구분한다. venv를 OS 간 복사하지 않는다. |
| 8080 포트 충돌 | 이 실습이 시작한 프로세스·컨테이너만 종료하거나 호스트 포트를 변경한다. |
| 컨테이너 `unhealthy` | 컨테이너 로그와 8080 포트·앱 시작 오류를 읽는다. |
| 데이터 초기화·복제 간 차이 | 메모리 데이터는 영속·공유되지 않는다. 단일 worker/replica로 학습하고 이후 DB로 확장한다. |

로컬 서버는 `Ctrl+C`로 종료한다. **이 실습이 만든 이름**인지 확인한 뒤 컨테이너와 로컬 이미지 태그를 정리한다.

```bash
docker inspect --format '{{.Name}} {{.Config.Image}}' amw-workshop-local
docker stop amw-workshop-local
docker rm amw-workshop-local
docker image rm amw-workshop:0.1.0
```

Docker 전체 prune이나 다른 컨테이너의 삭제는 하지 않는다. venv는 다음 실습에 재사용할 수 있다.


## 7. 실제 이전에서 추가로 확인할 사항


- 데이터 영속성, 다중 replica·worker, 동시 쓰기와 DB 연결.
- 앱 인증, 비밀 관리, 서비스별 SDK·설정 변경.
- 헬스 체크, graceful shutdown, 제한·타임아웃, 로그.
- 이미지와 패키지 취약점·라이선스·지원 버전, 고객의 승인된 공급망.
- 동일한 앱 이미지가 실행된다는 사실은 AWS 인프라·데이터의 실제 이전 검증과 다르다.


## 8. 출처와 실행 확인
