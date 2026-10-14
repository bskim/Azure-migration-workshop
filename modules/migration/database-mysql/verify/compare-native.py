import argparse
import configparser
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
    parser.add_argument("protected_directory")
    parser.add_argument("subscription")
    parser.add_argument("group")
    parser.add_argument("service")
    parser.add_argument("project")
    parser.add_argument("task")
    args = parser.parse_args()
    folder = Path(args.protected_directory)
    if not re.fullmatch(r"/var/tmp/amw-mysql-[a-z0-9]{8}", str(folder)):
        raise ValueError("Use the approved synthetic MySQL working directory.")

    def require_private(path):
        metadata = path.stat()
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.geteuid()
                or metadata.st_mode & 0o077):
            raise ValueError("Connection/credential files must be owner-private.")

    credential_file = folder / "credentials.json"
    require_private(credential_file)
    credentials = json.loads(credential_file.read_text())

    def execute(command, *, input=None):
        result = subprocess.run(command, input=input, text=True, capture_output=True, timeout=120)
        if result.returncode:
            error = result.stderr
            for value in credentials.values():
                error = error.replace(value, "<redacted>")
            raise RuntimeError(f"Read-only comparison exit {result.returncode}: {error}")
        return result.stdout

    native = json.loads(execute([
        "az", "dms", "project", "task", "show",
        "--name", args.task, "--project-name", args.project, "--service-name", args.service,
        "--resource-group", args.group, "--subscription", args.subscription, "--expand", "output",
        "--query", "{state:properties.state,type:properties.taskType,errors:properties.errors,"
        "output:properties.output}", "--output", "json",
    ]))
    if (native["type"] != "Migrate.MySql.AzureDbForMySql"
            or native["state"] != "Succeeded" or native["errors"]):
        raise AssertionError("An actual successful native offline migration is required.")
    outputs = native["output"]
    migration = [item for item in outputs if item["resultType"] == "MigrationLevelOutput"]
    databases = [item for item in outputs if item["resultType"] == "DatabaseLevelOutput"]
    tables = [item for item in outputs if item["resultType"] == "TableLevelOutput"]
    expected_tables = {"workshop.items", "workshop.batches", "workshop.batch_items"}
    if (len(migration) != 1 or migration[0]["status"] != "Completed"
            or migration[0]["hasServerLevelError"] or migration[0]["hasServerLevelWarning"]
            or migration[0]["exceptionsAndWarnings"]):
        raise AssertionError("Native migration has incomplete/error/warning state.")
    if (len(databases) != 1 or databases[0]["databaseName"] != "workshop"
            or databases[0]["state"] != "Completed" or databases[0]["numberOfObjects"] != 3
            or databases[0]["numberOfObjectsCompleted"] != 3
            or databases[0]["errorCount"] != 0 or databases[0]["warningCount"] != 0):
        raise AssertionError("Native database completion scope/counts differ.")
    if len(tables) != 3 or {item["objectName"] for item in tables} != expected_tables:
        raise AssertionError("Native table scope differs.")
    for table in tables:
        if (table["state"] != "Completed" or table["errorCount"] != 0
                or table["warningCount"] != 0 or table["itemsCompletedCount"] != 10):
            raise AssertionError("Native table rows/error counts differ.")

    clients = {}
    for side in ("source", "target"):
        path = folder / f"{side}-client.cnf"
        require_private(path)
        configuration = configparser.ConfigParser()
        configuration.read(path)
        if configuration["client"]["ssl-mode"] != "VERIFY_IDENTITY":
            raise ValueError("Client must verify TLS peer identity.")
        host = configuration["client"]["host"]
        if not host.startswith("my-amw-") or not host.endswith(".mysql.database.azure.com"):
            raise ValueError("Use only the approved synthetic private host.")
        addresses = {
            item[4][0] for item in socket.getaddrinfo(host, 3306, socket.AF_INET, socket.SOCK_STREAM)
        }
        if not addresses or any(not ipaddress.ip_address(value).is_private for value in addresses):
            raise ValueError("MySQL endpoint did not resolve privately.")
        clients[side] = ["mysql", f"--defaults-extra-file={path}", "--protocol=TCP",
                         "--batch", "--raw", "--skip-column-names", "--database=workshop"]

    def query(side, sql):
        return execute(clients[side], input=sql).splitlines()

    artifacts = {}
    for side in clients:
        names = query(side, "SELECT TABLE_NAME FROM information_schema.TABLES "
                      "WHERE TABLE_SCHEMA='workshop' ORDER BY TABLE_NAME;")
        workload_names = {"items", "batches", "batch_items"}
        extra = set(names) - workload_names
        if not workload_names.issubset(names) or len(names) != len(set(names)):
            raise AssertionError(f"{side}: mapped workload tables are missing or duplicated.")
        allowed = {"dms_persistent_objects"} if side == "target" else set()
        if not extra.issubset(allowed):
            raise AssertionError(f"{side}: unexplained additional tables: {sorted(extra)}")
        artifacts[side] = []
        if extra:
            if query(side, "SELECT COUNT(*) FROM dms_persistent_objects;") != ["0"]:
                raise AssertionError("This sample expects empty DMS persistent-object metadata.")
            metadata_columns = query(side, "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
                                     "WHERE TABLE_SCHEMA='workshop' AND TABLE_NAME='dms_persistent_objects' "
                                     "ORDER BY ORDINAL_POSITION;")
            if metadata_columns != [
                "DB_NAME", "TABLE_NAME", "OBJ_NAME", "OBJ_TYPE",
                "CREATE_STMT", "CREATE_ORDER", "ACTIVITY_ID",
            ]:
                raise AssertionError("The extra table does not match the observed DMS metadata structure.")
            artifacts[side].append({"table": "dms_persistent_objects", "rows": 0})

    column_sql = """
SELECT TABLE_NAME,ORDINAL_POSITION,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,
IF(COLUMN_DEFAULT IS NULL,'<NULL>',COLUMN_DEFAULT),EXTRA,
IF(CHARACTER_SET_NAME IS NULL,'<NULL>',CHARACTER_SET_NAME),
IF(COLLATION_NAME IS NULL,'<NULL>',COLLATION_NAME)
FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='workshop'
AND TABLE_NAME IN ('items','batches','batch_items')
ORDER BY TABLE_NAME,ORDINAL_POSITION;
"""
    constraint_sql = """
SELECT TABLE_NAME,CONSTRAINT_NAME,CONSTRAINT_TYPE
FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA='workshop'
AND TABLE_NAME IN ('items','batches','batch_items')
ORDER BY TABLE_NAME,CONSTRAINT_NAME;
"""
    key_sql = """
SELECT TABLE_NAME,CONSTRAINT_NAME,COLUMN_NAME,ORDINAL_POSITION,
IF(REFERENCED_TABLE_NAME IS NULL,'<NULL>',REFERENCED_TABLE_NAME),
IF(REFERENCED_COLUMN_NAME IS NULL,'<NULL>',REFERENCED_COLUMN_NAME)
FROM information_schema.KEY_COLUMN_USAGE WHERE CONSTRAINT_SCHEMA='workshop'
AND TABLE_NAME IN ('items','batches','batch_items')
ORDER BY TABLE_NAME,CONSTRAINT_NAME,ORDINAL_POSITION;
"""
    check_sql = """
SELECT c.CONSTRAINT_NAME,c.CHECK_CLAUSE FROM information_schema.CHECK_CONSTRAINTS c
JOIN information_schema.TABLE_CONSTRAINTS t
ON c.CONSTRAINT_SCHEMA=t.CONSTRAINT_SCHEMA AND c.CONSTRAINT_NAME=t.CONSTRAINT_NAME
WHERE c.CONSTRAINT_SCHEMA='workshop' AND t.TABLE_NAME IN ('items','batches','batch_items')
ORDER BY c.CONSTRAINT_NAME;
"""
    snapshots = {}
    expected_data = ["10\t55"] + [f"{i}\tbatch-{i:02}\titem-{i:02}\t{i}" for i in range(1, 11)]
    for side in clients:
        engines = query(side, "SELECT TABLE_NAME,ENGINE,TABLE_COLLATION FROM information_schema.TABLES "
                        "WHERE TABLE_SCHEMA='workshop' AND TABLE_NAME IN "
                        "('items','batches','batch_items') ORDER BY TABLE_NAME;")
        if len(engines) != 3 or any("\tInnoDB\t" not in row for row in engines):
            raise AssertionError(f"{side}: expected three InnoDB tables.")
        data = query(side, (folder / "verify.sql").read_text())
        if (len(data) != 14 or set(data[:3]) != {"items\t10", "batches\t10", "batch_items\t10"}
                or data[3:] != expected_data):
            raise AssertionError(f"{side}: all ordered data/counts differ.")
        columns = query(side, column_sql)
        constraints = query(side, constraint_sql)
        keys = query(side, key_sql)
        checks = query(side, check_sql)
        if len(columns) != 8 or len(constraints) != 7 or len(checks) != 1:
            raise AssertionError(f"{side}: column/constraint/CHECK shape differs.")
        cipher = query(side, "SHOW STATUS LIKE 'Ssl_cipher';")
        if len(cipher) != 1 or len(cipher[0].split("\t")) != 2 or not cipher[0].split("\t")[1]:
            raise AssertionError(f"{side}: current TLS cipher is absent.")
        snapshots[side] = {
            "engines": sorted(engines), "columns": sorted(columns),
            "constraints": sorted(constraints), "keys": sorted(keys), "checks": sorted(checks),
            "data": sorted(data[:3]) + data[3:],
        }
    if snapshots["source"] != snapshots["target"]:
        raise AssertionError("Native service completed, but source/target schema/data do not match.")
    baseline = (folder / "source-baseline.txt").read_text().splitlines()
    if snapshots["source"]["data"] != sorted(baseline[:3]) + baseline[3:]:
        raise AssertionError("Source changed after preparation.")
    with (folder / "comparison.json").open("w") as output:
        json.dump({"workload": snapshots, "serviceArtifacts": artifacts}, output)
    versions = {side: query(side, "SELECT VERSION();")[0] for side in clients}
    print(json.dumps({
        "nativeTask": "Succeeded", "databaseCompleted": True, "tablesCompleted": 3,
        "nativeTableErrors": 0, "nativeTableWarnings": 0, "versions": versions,
        "tables": 3, "rows": 30, "joinedRows": 10, "quantitySum": 55,
        "columns": 8, "constraints": 7, "schemaMatch": True, "allOrderedDataMatch": True,
        "clientsTls": "VERIFY_IDENTITY", "sourceUnchanged": True,
        "serviceArtifacts": artifacts,
        "dataSha256": hashlib.sha256("\n".join(snapshots["source"]["data"]).encode()).hexdigest(),
    }))
    print("AMW_MYSQL_NATIVE_COMPARE_PASS")


if __name__ == "__main__":
    main()
