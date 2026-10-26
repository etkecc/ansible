#!/usr/bin/python
# SPDX-FileCopyrightText: 2026 Slavi Pantaleev
#
# SPDX-License-Identifier: AGPL-3.0-or-later

DOCUMENTATION = r"""
---
module: postgres_managed_databases
short_description: Prepares managed Postgres databases (roles, passwords, databases, owners)
description:
  - Inspects the server first and only runs the statements needed to bring each managed database
    (and its role) to the desired state, so that it can report whether anything changed.
  - Talks to Postgres by running C(psql) (via O(psql_command)) and feeding it SQL on stdin,
    so that passwords never end up in files or on command lines.
  - Passwords are compared against the stored SCRAM-SHA-256 or MD5 verifiers, and new ones are sent
    as such verifiers (like psql's C(\password) does), so that they do not show up in server logs.
  - O(databases[].additional_sql_queries) run every time (after everything else for that database)
    and are expected to be idempotent. They do not affect whether the task reports a change.
options:
  psql_command:
    description:
      - The command (as a list of arguments) which starts C(psql), connected as a superuser.
        C(psql) arguments are appended to it. It has to pass stdin through (e.g. C(docker exec -i)).
    type: list
    elements: str
    required: true
  databases:
    description: The managed databases.
    type: list
    elements: dict
    required: true
    options:
      name:
        type: str
        required: true
      username:
        type: str
        required: true
      password:
        type: str
        required: true
        no_log: true
      additional_sql_queries:
        type: list
        elements: str
        default: []
  lc_ctype:
    description: C(LC_CTYPE) for newly created databases.
    type: str
    required: true
  lc_collate:
    description: C(LC_COLLATE) for newly created databases.
    type: str
    required: true
  connection_retries:
    description: How many times to retry when C(psql) cannot connect to Postgres (exit code 2).
    type: int
    default: 0
  connection_retry_delay_seconds:
    description: How long to wait between connection retries.
    type: int
    default: 3
  redact_values:
    description: Additional values (e.g. the superuser password) to redact from the output.
    type: list
    elements: str
    default: []
    no_log: true
"""

RETURN = r"""
changes:
  description: Human-readable descriptions of the changes made (or which would be made, in check mode).
  type: list
  elements: str
  returned: always
"""

import base64
import hashlib
import hmac
import json
import os
import stringprep
import time
import unicodedata

from ansible.module_utils.basic import AnsibleModule

PSQL_EXIT_CODES = {
    1: "fatal psql error",
    2: "could not connect to Postgres, or the connection was lost",
    3: "an SQL statement failed",
}

SCRAM_DEFAULT_ITERATIONS = 4096
SCRAM_SALT_LENGTH = 16


def quote_ident(value):
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value):
    # `standard_conforming_strings` is on by default, so backslashes need no escaping.
    return "'" + value.replace("'", "''") + "'"


def saslprep(password):
    """Prepares a password the way Postgres does (see `pg_saslprep()`) before SCRAM-hashing it.

    Returns `None` when Postgres would fall back to the raw password (prohibited input).
    """
    if all(ord(c) < 128 for c in password):
        # Postgres passes pure-ASCII input through unchanged (control characters included).
        return password.encode("utf-8")

    mapped = "".join(
        " " if stringprep.in_table_c12(c) else c
        for c in password
        if not stringprep.in_table_b1(c)
    )
    normalized = unicodedata.ucd_3_2_0.normalize("NFKC", mapped)

    prohibited = (
        stringprep.in_table_c12,
        stringprep.in_table_c21_c22,
        stringprep.in_table_c3,
        stringprep.in_table_c4,
        stringprep.in_table_c5,
        stringprep.in_table_c6,
        stringprep.in_table_c7,
        stringprep.in_table_c8,
        stringprep.in_table_c9,
        stringprep.in_table_a1,
    )
    if any(check(c) for c in normalized for check in prohibited):
        return None

    if any(stringprep.in_table_d1(c) for c in normalized):
        if any(stringprep.in_table_d2(c) for c in normalized):
            return None
        if not (stringprep.in_table_d1(normalized[0]) and stringprep.in_table_d1(normalized[-1])):
            return None

    return normalized.encode("utf-8")


def scram_keys(prepared_password, salt, iterations):
    salted = hashlib.pbkdf2_hmac("sha256", prepared_password, salt, iterations)
    client_key = hmac.new(salted, b"Client Key", hashlib.sha256).digest()
    stored_key = hashlib.sha256(client_key).digest()
    server_key = hmac.new(salted, b"Server Key", hashlib.sha256).digest()
    return stored_key, server_key


def scram_verifier(password, iterations):
    prepared = saslprep(password)
    if prepared is None:
        prepared = password.encode("utf-8")
    salt = os.urandom(SCRAM_SALT_LENGTH)
    stored_key, server_key = scram_keys(prepared, salt, iterations)
    return "SCRAM-SHA-256$%d:%s$%s:%s" % tuple(
        [iterations] + [base64.b64encode(data).decode("ascii") for data in (salt, stored_key, server_key)]
    )


def md5_verifier(password, username):
    return "md5" + hashlib.md5((password + username).encode("utf-8")).hexdigest()


def password_matches(stored, password, username):
    """Tells whether `password` matches the role's stored password (verifier)."""
    if stored is None:
        return False

    if stored.startswith("SCRAM-SHA-256$"):
        try:
            iterations_and_salt, keys = stored[len("SCRAM-SHA-256$"):].split("$", 1)
            iterations, salt = iterations_and_salt.split(":", 1)
            stored_key, server_key = keys.split(":", 1)
            iterations = int(iterations)
            salt = base64.b64decode(salt)
            stored_key = base64.b64decode(stored_key)
            server_key = base64.b64decode(server_key)
        except ValueError:
            return False

        prepared = saslprep(password)
        if prepared is None:
            prepared = password.encode("utf-8")
        actual_stored_key, actual_server_key = scram_keys(prepared, salt, iterations)
        return hmac.compare_digest(actual_stored_key, stored_key) and hmac.compare_digest(actual_server_key, server_key)

    if len(stored) == 35 and stored.startswith("md5"):
        return hmac.compare_digest(stored, md5_verifier(password, username))

    # Postgres < 10 may store passwords in plain text.
    return hmac.compare_digest(stored.encode("utf-8"), password.encode("utf-8"))


def password_to_send(module, server, password, username):
    """Returns the password (preferably as a verifier, so the plain one never reaches Postgres) for `ALTER ROLE`."""
    method = server["password_encryption"]
    verifier = None
    if method == "scram-sha-256" and all(ord(c) < 128 for c in password):
        # Non-ASCII passwords are left to Postgres, so that any difference in our SASLprep
        # implementation cannot make a role unable to log in (it would only make the comparison
        # above fail and the password be set again).
        verifier = scram_verifier(password, server["scram_iterations"])
    elif method in ("md5", "on"):
        verifier = md5_verifier(password, username)

    if verifier is None:
        return password

    module.no_log_values.add(verifier)
    return verifier


class Psql(object):
    def __init__(self, module):
        self.module = module
        self.command = module.params["psql_command"] + [
            "--no-psqlrc",
            "--set=ON_ERROR_STOP=1",
            "--set=VERBOSITY=terse",
            "--quiet",
        ]

    def run(self, sql, extra_args=None):
        args = self.command + (extra_args or [])
        attempts = 1 + max(self.module.params["connection_retries"], 0)
        for attempt in range(1, attempts + 1):
            rc, stdout, stderr = self.module.run_command(args, data=sql, binary_data=True)
            if rc != 2 or attempt == attempts:
                break
            time.sleep(self.module.params["connection_retry_delay_seconds"])

        if rc != 0:
            self.module.fail_json(
                msg="Preparing the managed databases failed: psql exited with code %d (%s).\nOutput:\n%s"
                % (rc, PSQL_EXIT_CODES.get(rc, "see the output below"), stderr),
                rc=rc,
                stderr=stderr,
            )
        return stdout


def inspect_server(psql, databases):
    usernames = sorted({db["username"] for db in databases})
    names = sorted({db["name"] for db in databases})
    sql = """
SELECT json_build_object(
  'password_encryption', current_setting('password_encryption'),
  'scram_iterations', current_setting('scram_iterations', true),
  'roles', COALESCE((SELECT json_object_agg(rolname, rolpassword) FROM pg_authid WHERE rolname IN (%s)), '{}'::json),
  'databases', COALESCE((SELECT json_object_agg(datname, pg_get_userbyid(datdba)) FROM pg_database WHERE datname IN (%s)), '{}'::json)
);
""" % (
        ", ".join(quote_literal(u) for u in usernames),
        ", ".join(quote_literal(n) for n in names),
    )
    server = json.loads(psql.run(sql, ["--tuples-only", "--no-align"]))
    server["scram_iterations"] = int(server["scram_iterations"] or SCRAM_DEFAULT_ITERATIONS)
    return server


def main():
    module = AnsibleModule(
        argument_spec=dict(
            psql_command=dict(type="list", elements="str", required=True),
            databases=dict(
                type="list",
                elements="dict",
                required=True,
                options=dict(
                    name=dict(type="str", required=True),
                    username=dict(type="str", required=True),
                    password=dict(type="str", required=True, no_log=True),
                    additional_sql_queries=dict(type="list", elements="str", default=[]),
                ),
            ),
            lc_ctype=dict(type="str", required=True),
            lc_collate=dict(type="str", required=True),
            connection_retries=dict(type="int", default=0),
            connection_retry_delay_seconds=dict(type="int", default=3),
            redact_values=dict(type="list", elements="str", default=[], no_log=True),
        ),
        supports_check_mode=True,
    )
    module.no_log_values.update(v for v in module.params["redact_values"] if v)

    databases = module.params["databases"]
    if not databases:
        module.exit_json(changed=False, changes=[])

    psql = Psql(module)
    server = inspect_server(psql, databases)
    roles = server["roles"]
    owners = server["databases"]

    changes = []
    statements = []
    has_additional_sql = False
    # Several managed databases may share a role. Its password is the last one given for it.
    passwords_set = {}
    for db in databases:
        name, username, password = db["name"], db["username"], db["password"]

        if username in passwords_set:
            password_ok = passwords_set[username] == password
        else:
            password_ok = username in roles and password_matches(roles[username], password, username)

        if username not in roles:
            changes.append("create role %s" % quote_ident(username))
            statements.append(
                "CREATE ROLE %s LOGIN PASSWORD %s;"
                % (quote_ident(username), quote_literal(password_to_send(module, server, password, username)))
            )
            roles[username] = None
        elif not password_ok:
            changes.append("set the password of role %s" % quote_ident(username))
            statements.append(
                "ALTER ROLE %s PASSWORD %s;"
                % (quote_ident(username), quote_literal(password_to_send(module, server, password, username)))
            )
        passwords_set[username] = password

        if name not in owners:
            changes.append("create database %s owned by %s" % (quote_ident(name), quote_ident(username)))
            # `CREATE DATABASE` cannot run inside a transaction block, but psql does not start one.
            statements.append(
                "CREATE DATABASE %s WITH LC_CTYPE %s LC_COLLATE %s OWNER %s;"
                % (quote_ident(name), quote_literal(module.params["lc_ctype"]), quote_literal(module.params["lc_collate"]), quote_ident(username))
            )
        elif owners[name] != username:
            changes.append("change the owner of database %s from %s to %s" % (quote_ident(name), quote_ident(owners[name]), quote_ident(username)))
            statements.append("ALTER DATABASE %s OWNER TO %s;" % (quote_ident(name), quote_ident(username)))
        owners[name] = username

        if db["additional_sql_queries"]:
            has_additional_sql = True
            statements.extend(db["additional_sql_queries"])

    changed = len(changes) > 0
    result = dict(changed=changed, changes=changes)
    if module._diff:
        result["diff"] = dict(before="", after="".join("%s\n" % c for c in changes))

    if module.check_mode or not (changed or has_additional_sql):
        module.exit_json(**result)

    psql.run("\n".join(statements) + "\n")
    module.exit_json(**result)


if __name__ == "__main__":
    main()
