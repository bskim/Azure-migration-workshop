import argparse
import hashlib
import ipaddress
import json
import os
import re
import socket
import stat
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source_host")
    parser.add_argument("target_host")
    parser.add_argument("protected_directory")
    parser.add_argument("subscription")
    parser.add_argument("group")
    parser.add_argument("server")
    parser.add_argument("migration")
    args = parser.parse_args()
    directory = Path(args.protected_directory)
    if not re.fullmatch(r"/var/tmp/amw-pg-[a-z0-9]{8}", str(directory)):
        raise ValueError("Use the approved synthetic PostgreSQL working directory.")
    if not args.target_host.startswith("pg-amw-") or not args.target_host.endswith(".postgres.database.azure.com"):
        raise ValueError("Use the approved synthetic Flexible Server hostname.")
    for hostname in (args.source_host, args.target_host):
        addresses = {
            item[4][0] for item in socket.getaddrinfo(
                hostname, 5432, socket.AF_INET, socket.SOCK_STREAM
            )
        }
        if not addresses or any(not ipaddress.ip_address(value).is_private for value in addresses):
            raise ValueError(f"Endpoint is not private: {hostname}")
    credential_file = directory / "credentials.json"
    details = credential_file.stat()
    if not stat.S_ISREG(details.st_mode) or details.st_uid != os.geteuid() or details.st_mode & 0o077:
        raise ValueError("Credential file must be owned by this user and private.")
    credentials = json.loads(credential_file.read_text())

    def execute(command, *, input=None, env=None):
        result = subprocess.run(command, input=input, env=env, text=True, capture_output=True, timeout=120)
        if result.returncode:
            error = result.stderr
            for value in credentials.values():
                error = error.replace(value, "<redacted>")
            raise RuntimeError(f"Read-only comparison exit {result.returncode}: {error}")
        return result.stdout

    job = json.loads(execute([
        "az", "postgres", "flexible-server", "migration", "show",
        "--name", args.migration, "--server-name", args.server,
        "--resource-group", args.group, "--subscription", args.subscription,
        "--query", "{option:migrationOption,mode:migrationMode,overwrite:overwriteDbsInTarget,"
        "roles:migrateRoles,status:currentStatus}", "--output", "json",
    ]))
    if job["option"] != "Migrate" or job["mode"] != "Offline":
        raise AssertionError("Expected an actual native offline migration, not validation.")
    if job["overwrite"] != "False" or job["roles"] != "False":
        raise AssertionError("Native migration safety settings differ from the approved scope.")
    status = job["status"]
    if status["state"] != "Succeeded" or status["error"] is not None:
        raise AssertionError("Native migration did not succeed.")
    databases = status["currentSubStateDetails"]["dbDetails"]
    if set(databases) != {"workshop"}:
        raise AssertionError("Native job has unexpected database scope.")
    database = databases["workshop"]
    if (database["migrationState"] != "Succeeded"
            or database["fullLoadCompletedTables"] != 3
            or any(database[name] != 0 for name in (
                "fullLoadErroredTables", "fullLoadQueuedTables", "fullLoadLoadingTables"))):
        raise AssertionError("Native table completion/error counts differ.")

    connections = {
        "source": (
            f"host={args.source_host} port=5432 dbname=workshop user=workshopadmin "
            f"sslmode=verify-full sslrootcert={directory / 'source-ca.crt'}",
            credentials["sourcePassword"],
        ),
        "target": (
            f"host={args.target_host} port=5432 dbname=workshop user=workshopadmin "
            "sslmode=verify-full sslrootcert=/etc/ssl/certs/ca-certificates.crt",
            credentials["targetPassword"],
        ),
    }

    def query(side, sql):
        connection, password = connections[side]
        environment = os.environ.copy()
        environment["PGPASSWORD"] = password
        environment["PGOPTIONS"] = "-c search_path=public"
        output = execute([
            "psql", "--no-psqlrc", "--set=ON_ERROR_STOP=1", "--tuples-only",
            "--no-align", "--field-separator=\t", connection,
        ], input=sql, env=environment)
        return [line.strip() for line in output.splitlines() if line.strip()]

    tables = (
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;"
    )
    columns = """
SELECT c.relname, a.attnum, a.attname, format_type(a.atttypid,a.atttypmod), a.attnotnull
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
JOIN pg_attribute a ON a.attrelid=c.oid
WHERE n.nspname='public' AND c.relkind='r' AND a.attnum>0 AND NOT a.attisdropped
ORDER BY c.relname,a.attnum;
"""
    constraints = """
SELECT c.relname, k.conname, k.contype, pg_get_constraintdef(k.oid,true)
FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='public' AND k.contype IN ('p','f','c','u')
ORDER BY c.relname,k.conname;
"""
    expected_rows = ["10\t55"] + [
        f"{i}\tbatch-{i:02}\titem-{i:02}\t{i}" for i in range(1, 11)
    ]
    snapshots = {}
    for side in connections:
        names = query(side, tables)
        if len(names) != 3 or set(names) != {"items", "batches", "batch_items"}:
            raise AssertionError(f"{side}: unexpected public tables")
        rows = query(side, (directory / "verify.sql").read_text())
        if (len(rows) != 14 or set(rows[:3]) != {"items\t10", "batches\t10", "batch_items\t10"}
                or rows[3:] != expected_rows):
            raise AssertionError(f"{side}: count/sum/full ordered data differs")
        column_rows = query(side, columns)
        constraint_rows = query(side, constraints)
        if len(column_rows) != 8 or len(constraint_rows) != 7:
            raise AssertionError(f"{side}: column/PK/FK/CHECK/unique shape differs")
        if query(side, "SELECT ssl FROM pg_stat_ssl WHERE pid=pg_backend_pid();") != ["t"]:
            raise AssertionError(f"{side}: current connection is not TLS")
        snapshots[side] = {
            "data": sorted(rows[:3]) + rows[3:],
            "columns": sorted(column_rows),
            "constraints": sorted(constraint_rows),
        }
    if snapshots["source"] != snapshots["target"]:
        raise AssertionError("Source and target data/schema do not match.")
    if query("source", "SHOW default_transaction_read_only;") != ["on"]:
        raise AssertionError("Source default read-only state was not retained.")
    original = (directory / "source-baseline.txt").read_text().splitlines()
    normalized_original = sorted(original[:3]) + original[3:]
    if snapshots["source"]["data"] != normalized_original:
        raise AssertionError("Source changed from its pre-migration baseline.")
    with (directory / "comparison.json").open("w") as output:
        json.dump(snapshots, output)
    versions = {side: query(side, "SELECT version();")[0] for side in connections}
    print(json.dumps({
        "nativeJob": "Succeeded", "nativeCompletedTables": 3, "nativeErroredTables": 0,
        "versions": versions, "tables": 3, "rows": 30, "joinedRows": 10, "quantitySum": 55,
        "columns": 8, "constraints": 7, "schemaMatch": True, "allOrderedDataMatch": True,
        "clientsTls": "verify-full", "sourceUnchanged": True,
        "dataSha256": hashlib.sha256("\n".join(snapshots["source"]["data"]).encode()).hexdigest(),
    }))
    print("AMW_PG_NATIVE_COMPARE_PASS")


if __name__ == "__main__":
    main()
