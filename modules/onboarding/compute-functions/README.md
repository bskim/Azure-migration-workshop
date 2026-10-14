# Functions — connect the same app to an HTTP trigger

English | [한국어](./README-ko.md)

**Sample configuration:** the provided Blob examples use private endpoints/DNS, public network Disabled, Entra data authentication, Shared Key/anonymous access disabled, bypass None and no resource-instance exceptions. Use the selected lab's approved identity/network inputs and check applicable policies with the administrator. Keep the supplied configuration and TLS checks unchanged; an alternative needs its own supported scenario and approval. Authentication and network access are independent.


An optional extension for Lambda/API Gateway users: learn triggers, bindings, host and the thin ASGI adapter while keeping the same business logic. Source packaging differs from running the shared Docker image.

## 1. Learning objectives and module boundaries

Choose concept/source reading (30 minutes), local HTTP host (45–60 minutes), or approved Linux Flex cloud deployment (45–60 minutes plus setup). Use existing app.py with the adapter, host and Python requirements in a fresh stage. No other compute course or ACR image is required. HTTP is the only implemented trigger; Timer/Queue/Blob are concepts, not automatically provisioned functions. The shared API is an unauthenticated learning sample with process-local memory, two seed items and a maximum of 100 items. It has no DB adapter. Multiple workers or replicas do not share state, and a restart loses added data. Do not use customer data or describe an app redeployment as a real AWS server or database migration.

**Resources for this step**

- [Shared FastAPI application](../../../sample-app/app.py)

## 2. Service introductions and selection

Open the Microsoft Learn introductions below before choosing a deployment or migration tool. Compare responsibilities, identity, network boundaries and lifecycle rather than treating AWS and Azure product names as one-to-one equivalents. A service resource, a running job and a verified application or dataset are separate outcomes.

**Resources for this step**

- [Functions overview](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview)
- [Functions triggers bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)
- [Functions bindings http webhook trigger](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger)
- [Functions reference python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure.functions.asgifunctionapp](https://learn.microsoft.com/en-us/python/api/azure-functions/azure.functions.asgifunctionapp?view=azure-python)
- [Flex consumption plan](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview)
- [Functions app settings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-app-settings#azurewebjobsstorage)

## 3. Prerequisites, permissions and cost

Local development uses Python 3.12, supported Linux Core Tools v4 and Azurite in WSL Bash; staging examples use local PowerShell. Confirm actual executable paths and working versions, not Windows npm launchers on WSL PATH. Use approved package sources and supported OS install paths, not a forced APT release alias. Cloud needs current Linux Flex region/runtime/quota, host/deployment storage, identity/data roles, deployment method, costs and function-key rights. local.settings.json is local-only and never published. AuthLevel.FUNCTION in Azure needs a protected function-level key, not a master key; it is not per-user Entra authorization. Local Core Tools auth behavior differs. Host storage is not persistence for /items. Use only an approved sandbox, synthetic data and the selected module's minimum inputs. Do not place credentials, account identifiers, real customer inventory or sensitive output in Git, prompts or shared screenshots. Confirm tenant, subscription, region, quota, cost and the resource owner; do not change the participant's default subscription or broaden access to make an error disappear.

**Resources for this step**

- [Functions run local](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools)
- [Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)

## 4. Step-by-step lab

Choose only the mode that matches your objective and available inputs. Read the full step, its execution environment and expected observation before running its commands. Use approved synthetic sandbox inputs. Obtain approval for resource creation, role assignments, writes and destructive actions separately.

### 4.1. Read the adapter and configuration changes

function_app.py uses azure.functions AsgiFunctionApp to invoke the shared FastAPI object. host.json has config version 2.0 and an empty HTTP routePrefix, preserving /health and /items. Functions runtime 4, Python programming model v2 and host.json version 2.0 are distinct numbering systems. requirements replace the Docker Uvicorn entry; .funcignore excludes venv/tests/local settings/secrets. Lambda event JSON is not automatically an HTTP request.

**Resources for this step**

- [Function app.py](./lab/function_app.py)
- [Host.json](./lab/host.json)
- [Requirements.txt](./lab/requirements.txt)
- [Local.settings.example.json](./lab/local.settings.example.json)
- [Functions publication exclusions](./lab/.funcignore)

### 4.2. Prepare a fresh source staging directory

Run local PowerShell from the repository root. Copy the existing adapter/host/requirements/ignore and same app.py into only the generated stage; do not modify the original app or create a duplicate business app. Copy the emulator settings example only for local mode. Do not publish local settings or use development-storage values in Azure.

```powershell
$ErrorActionPreference = "Stop"
$LabId = [guid]::NewGuid().ToString("N").Substring(0, 8)
$StagePath = Join-Path (Join-Path $PWD "lab-output") "functions-$LabId"
$TemplatePath = Join-Path $PWD "modules\onboarding\compute-functions\lab"
if (Test-Path -LiteralPath $StagePath) { throw "Use a fresh Functions staging folder." }
New-Item -ItemType Directory -Path $StagePath -ErrorAction Stop | Out-Null
foreach ($Name in @("function_app.py", "host.json", "requirements.txt", ".funcignore")) {
    Copy-Item -LiteralPath (Join-Path $TemplatePath $Name) -Destination (Join-Path $StagePath $Name)
}
Copy-Item -LiteralPath .\sample-app\app.py -Destination (Join-Path $StagePath "app.py")
$StagePath
```

```powershell
Copy-Item -LiteralPath (Join-Path $TemplatePath "local.settings.example.json") -Destination (Join-Path $StagePath "local.settings.json")
```

### 4.3. Local mode: start the host and verify the contract

Run the first commands in the stage's WSL Bash with approved dependencies and a separately started Azurite instance. Activate only this stage venv and keep func start running. Request localhost:7071 from another WSL terminal. For a fresh single-process application, expect GET /health to return 200 with status ok, two initial items, POST /items to return 201, and the new item to appear on read-back. Invalid input returns 422 without changing the data. Restarting resets the in-memory dataset. A running resource or container is not enough: observe the actual HTTP responses and relevant logs. Host function-list output alone is insufficient. Optional adapter/host tests require pytest/httpx only in the local test environment, not cloud runtime requirements. The test paths assume a repository lab-output/functions-<id> stage. Use a fresh single-worker host for write tests and stop only the host/emulator you started. After local HTTP checks, test the deployed Azure function's key enforcement separately.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv --requirements requirements.txt
source .venv/bin/activate
func start --port 7071
```

```bash
curl --fail-with-body http://127.0.0.1:7071/health
curl --fail-with-body http://127.0.0.1:7071/items
curl --fail-with-body --request POST http://127.0.0.1:7071/items \
  --header 'Content-Type: application/json' \
  --data '{"name":"functions-workshop-item"}'
curl --fail-with-body http://127.0.0.1:7071/items
```


**Resources for this step**

- [Test adapter.py](./verify/test_adapter.py)
- [Test host.py](./verify/test_host.py)

### 4.4. Cloud mode: hosting, storage and source deployment

Approve a fresh Function App/group with supported Linux Flex/Python 3.12, memory, maximum instances, concurrency and always-ready choices. Review default telemetry/workspace cost rather than assuming it is free. Configure supported identity-based private host/deployment storage separately from app data access; keep keys and emulator settings out of source. Core Tools publish below is one supported candidate and depends on current hosting/build support. A prebuilt-zip alternative follows separately; do not run both deployments blindly.

```bash
: "${FUNCTION_APP_NAME:?Set this lab's approved Function App name}"
func azure functionapp publish "$FUNCTION_APP_NAME"
```

#### Alternative: prebuilt zip with private Managed Identity storage

For a prebuilt package, use approved Linux CPython 3.12 dependencies under .python_packages/lib/site-packages with app.py/adapter/host/requirements at zip root. Exclude local.settings, venv, tests and secrets. Deploy with build-remote false from local management PowerShell to only the approved fresh app. Any package-feed exception is specific to the approved build environment, not authorization for cloud remote build. Configure the hosting-supported UAI for host and deployment storage, required Blob/Queue data roles and Blob/Queue/Table private endpoints/DNS with VNet outbound. Keep storage public Disabled/Deny/bypass None and Shared Key/anonymous off. Public HTTPS app access, if approved, is separate from private storage access. Inspect deployed route/auth and HTTP after deployment; an accepted deployment ID or null filtered field is not app success.

```powershell
if (-not $env:FUNCTION_APP_NAME -or -not $env:FUNCTION_APP_RESOURCE_GROUP -or -not $env:FUNCTION_PREBUILT_ZIP -or -not $env:FUNCTION_APP_SUBSCRIPTION_ID) {
    throw "Set the approved subscription, app, group and prebuilt zip."
}
if (-not (Test-Path -LiteralPath $env:FUNCTION_PREBUILT_ZIP -PathType Leaf)) { throw "The deployment zip does not exist." }
az functionapp deployment source config-zip --name $env:FUNCTION_APP_NAME --resource-group $env:FUNCTION_APP_RESOURCE_GROUP --src $env:FUNCTION_PREBUILT_ZIP --subscription $env:FUNCTION_APP_SUBSCRIPTION_ID --build-remote false --timeout 600
if ($LASTEXITCODE -ne 0) { throw "Functions prebuilt zip deployment failed" }
```

### 4.5. Observe Azure HTTP authentication and state limits

Confirm the actual app endpoint and FUNCTION auth. Expect no-key and wrong-key requests to fail with 401, and an approved function-level key in x-functions-key header to permit health 200, POST 201/read-back, invalid 422 and 404. Keep the key in a protected file/client, never URL/history/argv/logs/Git/prompts. The optional linked test runs from sample-app WSL and requires a fresh max-one-instance app plus explicit synthetic-write approval. Do not generalize two-to-three item state to multiple workers/instances, durability or HA. A function key and storage MI are different authentication paths.


**Resources for this step**

- [Test cloud.py](./verify/test_cloud.py)

The optional adapter/host/cloud pytest commands are in the [instructor validation tooling](../../../guides/instructor-guide.md#functions-http-validation-tooling), not prerequisites for the learner's HTTP exercise.

## 5. Verification and common failures

For a read-only inventory check, open the approved **Function App Overview → Functions** tab. The example lists **`http_app_func` / HTTP / Enabled**.

![Flex Function App inventory showing the enabled HTTP function](./images/portal-flex-http-function.png)

*Enabled describes the registered function, while invocation behavior is checked through the HTTP/auth steps above. Keep function keys and connection strings private. Compare the actual no-key/wrong-key rejection, authorized health/write/read-back, invalid-input and missing-route responses rather than treating an inventory row as a data test.*

Check staged source/root, Python/SDK/build support and approved feeds for import errors; routePrefix/ASGI entry for 404; emulator settings for local storage issues; actual host/deployment identity, roles and private DNS for Azure storage failures. Investigate 401/403 without changing auth to anonymous. State resets/differences follow workers, restart and scale; do not hide them with fallback output. Cloud Core Tools/remote build, other triggers and scale-out require their own support validation.

## 6. Cleanup and ownership

Reading creates no Azure resources. Local mode stops only this stage's host/emulator and removes its own verified files/venv/settings, preserving original source/templates and other stages. Cloud mode lists exact app/group/storage/telemetry/identity/new grants and obtains deletion approval. Revoke the specific key/grants and preserve shared DNS/storage or externally provided identity. App deletion, hosting cessation and storage deletion are different actions/cost boundaries.

## 7. Additional considerations for a real migration

Real Lambda migration needs event/payload/path/auth mapping, batches, retry/duplicate/idempotency/DLQ, binding support and connection identity, timeout/cold start/concurrency, durable shared data, monitoring and cutover/rollback. This HTTP adapter does not convert all Lambda triggers.

## 8. Sources and reuse

The workshop instructions and synthetic inputs were written for learning. Consult the official introductions and procedures linked here for the current support matrix, versions and regional availability. Documentation and illustrative screenshots are not a compatibility guarantee for a different source, target or topology. Keep third-party dependency licenses and notices intact.
