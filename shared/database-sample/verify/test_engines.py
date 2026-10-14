import os
import secrets
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest


ROOT = Path(__file__).resolve().parents[3]
SAMPLE = ROOT / "shared" / "database-sample"
MIGRATION = ROOT / "modules" / "migration"
EXPECTED = (
    ["10\t55"]
    + [f"{i}\tbatch-{i:02}\titem-{i:02}\t{i}" for i in range(1, 11)]
)
IMAGES = {
    "postgresql": "postgres:16",
    "mysql": "mysql:8.0",
    "sqlserver": "mcr.microsoft.com/mssql/server:2019-latest",
}


def docker(*args, input=None, env=None):
    return subprocess.run(
        ["docker", *args], input=input, env=env, text=True, capture_output=True,
        timeout=180,
    )


def require_success(result):
    if result.returncode:
        raise AssertionError(
            f"Docker/client exit {result.returncode}:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout


@contextmanager
def database(engine):
    name = f"amw-sql-{engine}-{uuid4().hex[:8]}"
    variable = {
        "postgresql": "POSTGRES_PASSWORD",
        "mysql": "MYSQL_ROOT_PASSWORD",
        "sqlserver": "MSSQL_SA_PASSWORD",
    }[engine]
    environment = os.environ.copy()
    environment[variable] = "Amw1!" + secrets.token_urlsafe(32)
    image = IMAGES[engine]
    options = ["--env", variable]
    if engine == "postgresql":
        options += ["--env", "POSTGRES_DB=workshop"]
    elif engine == "mysql":
        options += ["--env", "MYSQL_DATABASE=workshop"]
    else:
        options += ["--env", "ACCEPT_EULA=Y", "--env", "MSSQL_PID=Developer"]
    require_success(docker(
        "run", "--detach", "--pull=never", "--name", name,
        "--network", "none", "--memory", "3g" if engine == "sqlserver" else "1g",
        *options, image, env=environment,
    ))
    try:
        if engine == "sqlserver":
            wait_for_sqlserver(name)
            configure_local_tls(name)
            require_success(docker("restart", name))
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            result = query(
                engine, name, "SELECT 1;",
                db="master" if engine == "sqlserver" else "workshop",
            )
            if result.returncode == 0:
                break
            state = require_success(docker(
                "inspect", "--format", "{{.State.Running}}", name
            )).strip()
            if state != "true":
                pytest.fail(require_success(docker("logs", name)))
            time.sleep(1)
        else:
            pytest.fail(
                f"DB readiness timeout; last client exit {result.returncode}:\n"
                f"{result.stdout}\n{result.stderr}\n"
                + require_success(docker("logs", name))
            )
        if engine == "sqlserver":
            require_success(query(engine, name, "CREATE DATABASE workshop;", db="master"))
        yield name
    finally:
        require_success(docker("rm", "--force", "--volumes", name))


def wait_for_sqlserver(name):
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        result = docker("logs", name)
        logs = require_success(result) + result.stderr
        if "SQL Server is now ready for client connections" in logs:
            return
        if require_success(docker(
            "inspect", "--format", "{{.State.Running}}", name
        )).strip() != "true":
            pytest.fail("SQL Server stopped:\n" + logs)
        time.sleep(1)
    pytest.fail("SQL Server startup timeout:\n" + logs)


def configure_local_tls(name):
    require_success(docker(
        "exec", "--user", "0", name, "sh", "-c",
        "openssl req -x509 -newkey rsa:2048 -nodes -days 1 "
        "-subj /CN=127.0.0.1 -addext subjectAltName=DNS:127.0.0.1,IP:127.0.0.1 "
        "-keyout /var/opt/mssql/amw-local.key "
        "-out /usr/local/share/ca-certificates/amw-local.crt "
        "&& chown 10001:0 /var/opt/mssql/amw-local.key "
        "&& chmod 600 /var/opt/mssql/amw-local.key "
        "&& update-ca-certificates "
        "&& /opt/mssql/bin/mssql-conf set network.tlscert "
        "/usr/local/share/ca-certificates/amw-local.crt "
        "&& /opt/mssql/bin/mssql-conf set network.tlskey /var/opt/mssql/amw-local.key "
        "&& /opt/mssql/bin/mssql-conf set network.forceencryption 1",
    ))


def query(engine, name, sql, db="workshop"):
    if engine == "postgresql":
        command = [
            "psql", "--username=postgres", "--dbname=workshop",
            "--no-psqlrc", "--set=ON_ERROR_STOP=1", "--tuples-only", "--no-align",
            "--field-separator=\t",
        ]
    elif engine == "mysql":
        command = [
            "sh", "-c",
            'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" exec mysql --protocol=tcp --host=127.0.0.1 '
            '--user=root --database=workshop --batch --skip-column-names',
        ]
    else:
        command = [
            "sh", "-c",
            'SQLCMDPASSWORD="$MSSQL_SA_PASSWORD" exec /opt/mssql-tools18/bin/sqlcmd '
            '-S tcp:127.0.0.1,1433 -U sa -N '
            '-l 5 -b -r 1 -h -1 -W -s "\t" -d "$1"',
            "sql-client", db,
        ]
    return docker("exec", "--interactive", name, *command, input=sql)


def rows(output):
    return [line.strip() for line in output.splitlines() if line.strip()]


@pytest.mark.parametrize("engine", ["postgresql", "mysql", "sqlserver"])
def test_schema_seed_queries_constraints_and_rollback(engine):
    if engine == "sqlserver" and os.environ.get("WORKSHOP_SQLSERVER_ACCEPT_EULA") != "Y":
        pytest.skip("Explicit Developer EULA approval required: WORKSHOP_SQLSERVER_ACCEPT_EULA=Y.")
    with database(engine) as name:
        version_sql = "SELECT @@VERSION;" if engine == "sqlserver" else "SELECT version();"
        version = require_success(query(engine, name, version_sql)).strip()
        print(f"\n{engine} engine: {version}")
        schema = (MIGRATION / f"database-{engine}" / "lab" / "schema.sql").read_text()
        data_folder = MIGRATION / "database-sqlserver" / "lab" if engine == "sqlserver" else SAMPLE
        seed = (data_folder / "seed.sql").read_text()
        verify = (data_folder / "verify.sql").read_text()
        require_success(query(engine, name, schema))
        require_success(query(engine, name, seed))
        read_sql = ("SET NOCOUNT ON;\n" if engine == "sqlserver" else "") + verify
        baseline = rows(require_success(query(engine, name, read_sql)))
        assert len(baseline) == 14
        assert set(baseline[:3]) == {"batch_items\t10", "batches\t10", "items\t10"}
        assert baseline[3:] == EXPECTED

        rejected = [
            "INSERT INTO items (id, name) VALUES (1, 'duplicate');",
            "INSERT INTO items (id, name) VALUES (11, NULL);",
            "INSERT INTO batch_items VALUES (11, 999, 1, 1);",
            "INSERT INTO batch_items VALUES (11, 1, 999, 1);",
            "INSERT INTO batch_items VALUES (11, 1, 2, 0);",
            "INSERT INTO batch_items VALUES (11, 1, 2, -1);",
            "INSERT INTO batch_items VALUES (11, 1, 1, 1);",
        ]
        for sql in rejected:
            result = query(engine, name, sql)
            assert result.returncode != 0, f"Constraint did not reject: {sql}"
            assert rows(require_success(query(engine, name, read_sql))) == baseline

        assert query(engine, name, seed).returncode != 0
        assert rows(require_success(query(engine, name, read_sql))) == baseline
        broken_transaction = (
            ("SET XACT_ABORT ON;\nBEGIN TRANSACTION;\n"
             if engine == "sqlserver" else "START TRANSACTION;\n")
            +
            "INSERT INTO items VALUES (11, 'must-rollback');\n"
            "INSERT INTO items VALUES (1, 'duplicate');\n"
            "COMMIT;\n"
        )
        assert query(engine, name, broken_transaction).returncode != 0
        assert rows(require_success(query(engine, name, read_sql))) == baseline
        assert query(engine, name, schema).returncode != 0
        assert rows(require_success(query(engine, name, read_sql))) == baseline
        if engine == "sqlserver":
            for script in (schema, seed, verify):
                assert query(engine, name, script, db="master").returncode != 0
            encryption = rows(require_success(query(
                engine, name,
                "SET NOCOUNT ON; SELECT encrypt_option FROM sys.dm_exec_connections "
                "WHERE session_id = @@SPID;",
            )))
            assert encryption == ["TRUE"]
        digest = require_success(docker(
            "image", "inspect", "--format", "{{index .RepoDigests 0}}",
            IMAGES[engine],
        )).strip()
        print(f"{engine} image: {digest}")
        print("PASS: 30 rows, 10 joined rows, sum 55, all 10 sorted rows; "
              "7 constraint failures, reseed/schema rejection and partial transaction rollback.")
