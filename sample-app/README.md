# Shared sample application — a small HTTP API

English | [한국어](./README-ko.md)

Reuse the same Python 3.12/FastAPI application across VM + Docker, AKS and Container Apps. No AWS account, cloud SDK, DB, Blob, Queue or Key Vault is needed for local learning.

## 1. Learning objectives and module boundaries

Allow about 30–40 minutes. GET /health returns 200 and {"status":"ok"}; GET /items returns id/name entries; POST /items with a valid name returns 201. Trimmed names must be 1–80 characters; invalid types, extra fields and empty/oversized names return 422 with detail. Adding beyond 100 items returns 409, Workshop item limit reached. The shared API is an unauthenticated learning sample with process-local memory, two seed items and a maximum of 100 items. It has no DB adapter. Multiple workers or replicas do not share state, and a restart loses added data. Do not use customer data or describe an app redeployment as a real AWS server or database migration. Functions reuses app.py through an HTTP/ASGI adapter with separate host/source packaging, not the same container image.

**Resources for this step**

- [Compute vm](../modules/onboarding/compute-vm/README.md)
- [Compute container apps](../modules/onboarding/compute-container-apps/README.md)
- [Compute aks](../modules/onboarding/compute-aks/README.md)
- [Compute functions](../modules/onboarding/compute-functions/README.md)

## 2. Local prerequisites and dependency sources

Prepare uv and Python 3.12 for the locked local environment. Docker is optional and needs a working Linux-container daemon. Use your approved package/image source for local and Docker builds; do not disable TLS/signature checks, combine unapproved indexes or use public fallback feeds. No internal organization feed/account is required by the workshop, and credentials never belong in source. This app itself uses no Azure service; choose a compute module only when cloud deployment is your objective.

**Resources for this step**

- [Installation](https://docs.astral.sh/uv/getting-started/installation/)

## 3. Run the local application — WSL Bash

Execute in the sample-app directory. Use .venv-wsl rather than sharing a Windows .venv. Keep the server terminal running and use a second WSL terminal for the requests. A single worker avoids separate memory datasets. Expect Uvicorn at 127.0.0.1:8080 and request logs. For a fresh single-process application, expect GET /health to return 200 with status ok, two initial items, POST /items to return 201, and the new item to appear on read-back. Invalid input returns 422 without changing the data. Restarting resets the in-memory dataset. A running resource or container is not enough: observe the actual HTTP responses and relevant logs. Stop with Ctrl+C and restart to observe the two initial items again.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-wsl
export UV_LINK_MODE=copy
uv sync --frozen --python 3.12
uv run --frozen uvicorn app:app --host 127.0.0.1 --port 8080 --workers 1
```

```bash
curl --fail-with-body http://127.0.0.1:8080/health
curl --fail-with-body http://127.0.0.1:8080/items
curl --fail-with-body --request POST http://127.0.0.1:8080/items \
  --header 'Content-Type: application/json' \
  --data '{"name":"workshop-item"}'
curl --fail-with-body http://127.0.0.1:8080/items
```

## 4. Verify the application contract with tests

Run pytest from sample-app in WSL Bash. Tests create isolated application instances, exercise validation/limits/reset, and start a real temporary localhost HTTP server that is stopped afterward. Container tests explicitly skip unless the optional image variable is supplied. A skipped container test is not a Docker verification.

```bash
export UV_PROJECT_ENVIRONMENT=.venv-wsl
uv run --frozen pytest -q
```

## 5. Optional: run the same app as a container

Execute from sample-app in WSL Bash after docker info succeeds. Stop the earlier server if it occupies 8080. Do not overwrite a preexisting named container. Repeat the same HTTP requests and inspect logs, user 10001:10001 and health healthy after startup (allow roughly 30 seconds). The automatic container test uses a separate name/local port and removes only its own container. No Azure registry is needed for this local exercise.

```bash
docker info
docker build --tag amw-workshop:0.1.0 .
docker run --detach --name amw-workshop-local \
  --publish 127.0.0.1:8080:8080 \
  --memory 256m --read-only --cap-drop ALL \
  --security-opt no-new-privileges \
  amw-workshop:0.1.0
```

```bash
docker logs amw-workshop-local
docker inspect --format '{{.Config.User}}' amw-workshop-local
docker inspect --format '{{.State.Health.Status}}' amw-workshop-local
```

```bash
WORKSHOP_CONTAINER_IMAGE=amw-workshop:0.1.0 uv run --frozen pytest -q
```

## 6. Common failures and local cleanup

Check approved dependency access, WSL/Windows venv separation, port collisions, container startup logs and listen port. A memory reset is expected after restart and replicas do not share state. Stop only the server/container created here. Inspect the exact container name/image, stop/remove it and remove only the local image tag. Do not prune Docker globally or delete other containers. The venv can be reused.

```bash
docker inspect --format '{{.Name}} {{.Config.Image}}' amw-workshop-local
docker stop amw-workshop-local
docker rm amw-workshop-local
docker image rm amw-workshop:0.1.0
```

## 7. Considerations beyond the sample

Real applications need durable/shared storage, authentication, secret management, SDK/configuration changes, graceful shutdown, timeouts and operational observability. Review image/package vulnerabilities, licenses and supported versions. The same image enables compute comparison; infrastructure and data migration are separate tasks.

## 8. Sources and dependency management

This is an original synthetic application, not a copied external business app. Consult FastAPI and uv documentation. Exact package versions/hashes are recorded in uv.lock and the container base digest in Dockerfile. The .dockerignore allowlist limits the build context to runtime inputs. Follow each compute module for its cloud-specific identity, network and cleanup requirements.

**Resources for this step**

- [](https://fastapi.tiangolo.com/)
- [Docker](https://docs.astral.sh/uv/guides/integration/docker/)
