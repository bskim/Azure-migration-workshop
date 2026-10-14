#!/usr/bin/env bash
set -euo pipefail
trap 'rc=$?; echo "AMW_STORAGE_VERIFY_FAIL exit=$rc line=$LINENO"; exit "$rc"' ERR
account="${1:?Pass the approved new storage account}"
private_ip="${2:?Pass its approved private endpoint IP}"
workdir="${3:?Pass the private inspection working directory}"
phase="${4:-create}"
if [[ ! "$account" =~ ^[a-z0-9]{3,24}$ || ! "$workdir" =~ ^/var/tmp/amw-private-[a-z0-9]{8}$ ||
      ( "$phase" != create && "$phase" != verify-existing-blob ) ]]; then
    echo "Invalid account or inspection working directory." >&2
    exit 1
fi
python3 - "$account" "$private_ip" <<'PY'
import ipaddress
import socket
import sys

expected = ipaddress.ip_address(sys.argv[2])
if expected.version != 4 or not expected.is_private:
    raise ValueError("Expected approved private IPv4 endpoint address")
addresses = {
    entry[4][0]
    for entry in socket.getaddrinfo(
        f"{sys.argv[1]}.blob.core.windows.net", 443, socket.AF_INET, socket.SOCK_STREAM
    )
}
if addresses != {str(expected)}:
    raise RuntimeError(f"Private DNS mismatch: {sorted(addresses)}")
print(f"Private DNS verified: {expected}")
PY
az login --identity --allow-no-subscriptions --output none
if [[ "$phase" == create ]]; then
    az storage container create --account-name "$account" --name sample --auth-mode login \
        --output json | python3 -c \
        'import json,sys; data=json.load(sys.stdin); assert data["created"] is True, "Expected fresh sample container"'
    mkdir "$workdir/basics"
    printf '%s' 'Hello Azure workshop' >"$workdir/basics/hello.txt"
    az storage blob upload --account-name "$account" --container-name sample --name hello.txt \
        --file "$workdir/basics/hello.txt" --type block --content-type text/plain \
        --overwrite false --auth-mode login --output none
else
    test -f "$workdir/basics/hello.txt"
    echo "Verifying the retained blob only; upload will not run again."
fi
comparison="$(mktemp -d "$workdir/basics/verification.XXXXXXXX")"
az storage blob list --account-name "$account" --container-name sample --auth-mode login \
    --query '[].{name:name,bytes:properties.contentLength}' --output json \
    >"$comparison/blobs.json"
az storage blob download --account-name "$account" --container-name sample --name hello.txt \
    --file "$comparison/downloaded-hello.txt" --overwrite false \
    --auth-mode login --output none
python3 - "$workdir/basics" "$comparison" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

folder = Path(sys.argv[1])
comparison = Path(sys.argv[2])
blobs = json.loads((comparison / "blobs.json").read_text())
if blobs != [{"name": "hello.txt", "bytes": 20}]:
    raise AssertionError(f"Unexpected Blob count/name/length: {blobs}")
source = (folder / "hello.txt").read_bytes()
downloaded = (comparison / "downloaded-hello.txt").read_bytes()
if len(source) != 20 or source != b"Hello Azure workshop":
    raise AssertionError("Source content/encoding does not match the contract")
if hashlib.sha256(source).digest() != hashlib.sha256(downloaded).digest():
    raise AssertionError("Downloaded SHA-256 differs from the source")
print(json.dumps({"count": 1, "bytes": 20, "contentMatch": True}))
PY
echo AMW_STORAGE_VERIFY_PASS
