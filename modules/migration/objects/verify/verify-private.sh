#!/usr/bin/env bash
set -euo pipefail
source="${1:?Pass the approved source account}"
target="${2:?Pass the approved target account}"
workdir="${3:?Pass the private inspection working directory}"
phase="${4:-copy}"
if [[ ! "$source" =~ ^[a-z0-9]{3,24}$ || ! "$target" =~ ^[a-z0-9]{3,24}$ ||
      "$source" == "$target" || ! "$workdir" =~ ^/var/tmp/amw-private-[a-z0-9]{8}$ ||
      ( "$phase" != copy && "$phase" != verify-existing-job ) ]]; then
    echo "Invalid source, target or inspection working directory." >&2
    exit 1
fi
folder="$workdir/objects"
trap 'rc=$?; echo "AMW_OBJECT_VERIFY_FAIL exit=$rc line=$LINENO"; if test -f "$folder/copy.jsonl"; then tail -n 5 "$folder/copy.jsonl"; fi; exit "$rc"' ERR
az login --identity --allow-no-subscriptions --output none
if [[ "$phase" == copy ]]; then
    az storage blob list --account-name "$target" --container-name target --auth-mode login \
        --output json | python3 -c \
        'import json,sys; assert json.load(sys.stdin) == [], "Expected empty target before copy"'
    mkdir "$folder/azcopy-logs" "$folder/azcopy-plans"
    export AZCOPY_AUTO_LOGIN_TYPE=MSI
    export AZCOPY_LOG_LOCATION="$folder/azcopy-logs"
    export AZCOPY_JOB_PLAN_LOCATION="$folder/azcopy-plans"
    "$workdir/azcopy" copy "https://$source.blob.core.windows.net/source/*" \
        "https://$target.blob.core.windows.net/target" --from-to=BlobBlob \
        --recursive=false --overwrite=false --s2s-preserve-properties=true \
        --output-type json >"$folder/copy.jsonl"
else
    test -f "$folder/copy.jsonl"
    echo "Verifying the recorded job only; copy will not run again."
fi
python3 - "$folder/copy.jsonl" <<'PY'
import json
import sys
from pathlib import Path

events = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
summaries = [event for event in events if event.get("MessageType") == "EndOfJob"]
if len(summaries) != 1:
    raise AssertionError("Expected exactly one official AzCopy EndOfJob event")
summary = summaries[0]["MessageContent"]
if isinstance(summary, str):
    summary = json.loads(summary)
if (summary["JobStatus"] != "Completed" or summary["ErrorMsg"] != ""
        or summary["CompleteJobOrdered"] is not True):
    raise AssertionError(f"AzCopy job did not complete: {summary['JobStatus']}")
for name, expected in {
    "TotalTransfers": 3,
    "TransfersCompleted": 3,
    "TransfersFailed": 0,
    "TransfersSkipped": 0,
    "TotalBytesTransferred": sum(
        (Path(sys.argv[1]).parent / "original" / name).stat().st_size
        for name in ("catalog.csv", "info.json", "notes.txt")
    ),
}.items():
    value = summary[name]
    if not isinstance(value, str) or not value.isdigit() or int(value) != expected:
        raise AssertionError(f"AzCopy {name}: expected numeric string {expected}, got {value!r}")
print(json.dumps({name: summary[name] for name in (
    "JobID", "JobStatus", "TotalTransfers", "TransfersCompleted",
    "TransfersFailed", "TransfersSkipped", "TotalBytesTransferred",
)}))
PY
comparison="$(mktemp -d "$folder/verification.XXXXXXXX")"
mkdir "$comparison/source" "$comparison/target"
for name in catalog.csv info.json notes.txt; do
    az storage blob download --account-name "$source" --container-name source --name "$name" \
        --file "$comparison/source/$name" --overwrite false --auth-mode login --output none
    az storage blob download --account-name "$target" --container-name target --name "$name" \
        --file "$comparison/target/$name" --overwrite false --auth-mode login --output none
done
az storage blob list --account-name "$source" --container-name source --include m \
    --auth-mode login --output json >"$comparison/source.json"
az storage blob list --account-name "$target" --container-name target --include m \
    --auth-mode login --output json >"$comparison/target.json"
python3 - "$folder" "$comparison" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

folder = Path(sys.argv[1])
comparison = Path(sys.argv[2])
types = {"catalog.csv": "text/csv", "info.json": "application/json", "notes.txt": "text/plain"}
for filename in ("source.json", "target.json"):
    blobs = json.loads((comparison / filename).read_text())
    if len(blobs) != 3 or {blob["name"] for blob in blobs} != set(types):
        raise AssertionError(f"Expected exact three root names: {filename}")
    for blob in blobs:
        name = blob["name"]
        expected = (folder / "original" / name).read_bytes()
        if blob["properties"]["contentLength"] != len(expected):
            raise AssertionError(f"Length mismatch: {filename}, {name}")
        if blob["properties"]["contentSettings"]["contentType"] != types[name]:
            raise AssertionError(f"Content type mismatch: {filename}, {name}")
        if blob["metadata"] != {"workshop": "amw-objects"}:
            raise AssertionError(f"Metadata mismatch: {filename}, {name}")
total = 0
for name in types:
    original = (folder / "original" / name).read_bytes()
    expected_hash = hashlib.sha256(original).digest()
    for side in ("source", "target"):
        if hashlib.sha256((comparison / side / name).read_bytes()).digest() != expected_hash:
            raise AssertionError(f"SHA-256 mismatch: {side}, {name}")
    total += len(original)
print(json.dumps({"sourceFiles": 3, "targetFiles": 3, "totalBytes": total,
                  "hashMatch": True, "contentTypesMatch": True, "metadataMatch": True}))
PY
echo AMW_OBJECT_VERIFY_PASS
