#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "AMW_OBJECT_PREPARE_FAIL exit=$rc line=$LINENO"; exit "$rc"' ERR
source="${1:?Pass the approved source account}"
source_ip="${2:?Pass the source private endpoint IP}"
target="${3:?Pass the approved target account}"
target_ip="${4:?Pass the target private endpoint IP}"
workdir="${5:?Pass the private inspection working directory}"
catalog="${6:?Pass the original catalog.csv bytes as base64}"
info="${7:?Pass the original info.json bytes as base64}"
notes="${8:?Pass the original notes.txt bytes as base64}"
if [[ ! "$source" =~ ^[a-z0-9]{3,24}$ || ! "$target" =~ ^[a-z0-9]{3,24}$ ||
      "$source" == "$target" || ! "$workdir" =~ ^/var/tmp/amw-private-[a-z0-9]{8}$ ]]; then
    echo "Invalid source, target or inspection working directory." >&2
    exit 1
fi
python3 - "$source" "$source_ip" "$target" "$target_ip" <<'PY'
import ipaddress
import socket
import sys

for account, raw_address in ((sys.argv[1], sys.argv[2]), (sys.argv[3], sys.argv[4])):
    expected = ipaddress.ip_address(raw_address)
    if expected.version != 4 or not expected.is_private:
        raise ValueError("Expected approved private IPv4 endpoint")
    addresses = {
        entry[4][0]
        for entry in socket.getaddrinfo(
            f"{account}.blob.core.windows.net", 443, socket.AF_INET, socket.SOCK_STREAM
        )
    }
    if addresses != {str(expected)}:
        raise RuntimeError(f"{account}: private DNS mismatch {sorted(addresses)}")
    print(f"Private DNS verified: {account} -> {expected}")
PY
az login --identity --allow-no-subscriptions --output none
az storage container create --account-name "$source" --name source --auth-mode login \
    --output json | python3 -c \
    'import json,sys; assert json.load(sys.stdin)["created"] is True, "Expected new source container"'
az storage container create --account-name "$target" --name target --auth-mode login \
    --output json | python3 -c \
    'import json,sys; assert json.load(sys.stdin)["created"] is True, "Expected new target container"'
mkdir "$workdir/objects"
mkdir "$workdir/objects/original" "$workdir/objects/source" "$workdir/objects/target"
python3 - "$workdir/objects/original" "$catalog" "$info" "$notes" <<'PY'
import base64
import sys
from pathlib import Path

folder = Path(sys.argv[1])
for name, value in zip(("catalog.csv", "info.json", "notes.txt"), sys.argv[2:], strict=True):
    data = base64.b64decode(value, validate=True)
    with (folder / name).open("xb") as output:
        output.write(data)
PY
for name in catalog.csv info.json notes.txt; do
    case "$name" in
        catalog.csv) content_type=text/csv ;;
        info.json) content_type=application/json ;;
        notes.txt) content_type=text/plain ;;
    esac
    az storage blob upload --account-name "$source" --container-name source --name "$name" \
        --file "$workdir/objects/original/$name" --type block --content-type "$content_type" \
        --metadata workshop=amw-objects --overwrite false --auth-mode login --output none
    az storage blob download --account-name "$source" --container-name source --name "$name" \
        --file "$workdir/objects/source/$name" --overwrite false --auth-mode login --output none
done
az storage blob list --account-name "$source" --container-name source --include m \
    --auth-mode login --output json >"$workdir/objects/source-list.json"
az storage blob list --account-name "$target" --container-name target --include m \
    --auth-mode login --output json >"$workdir/objects/target-before.json"
python3 - "$workdir/objects" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

folder = Path(sys.argv[1])
expected = {"catalog.csv": "text/csv", "info.json": "application/json", "notes.txt": "text/plain"}
blobs = json.loads((folder / "source-list.json").read_text())
if len(blobs) != 3 or {blob["name"] for blob in blobs} != set(expected):
    raise AssertionError("Expected exactly three named source blobs")
if json.loads((folder / "target-before.json").read_text()) != []:
    raise AssertionError("Target must be empty before the copy")
total = 0
for blob in blobs:
    name = blob["name"]
    original = (folder / "original" / name).read_bytes()
    downloaded = (folder / "source" / name).read_bytes()
    if blob["properties"]["contentLength"] != len(original):
        raise AssertionError(f"Source length mismatch: {name}")
    if blob["properties"]["contentSettings"]["contentType"] != expected[name]:
        raise AssertionError(f"Source content type mismatch: {name}")
    if blob["metadata"] != {"workshop": "amw-objects"}:
        raise AssertionError(f"Source metadata mismatch: {name}")
    if hashlib.sha256(original).digest() != hashlib.sha256(downloaded).digest():
        raise AssertionError(f"Source SHA-256 mismatch: {name}")
    total += len(original)
print(json.dumps({"sourceFiles": 3, "totalBytes": total, "targetEmpty": True, "sourceMatch": True}))
PY
echo AMW_OBJECT_PREPARE_PASS
