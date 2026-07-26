---
title: "PostgreSQL Roles for pgAssistant"
date: 2026-07-25
tags: ["security", "roles"]
draft: false
---


## Purpose

pgAssistant inspects PostgreSQL configuration, system catalogs, statistics,
schemas, relations, sequences, and query plans. Some optional features can also
run maintenance operations or reset statistics.

This document recommends separating these capabilities between two login roles:

- `pgassistant_analyze`: the default, read-only account used for dashboards,
  reports, advisors, query ranking, query plans, and database design analysis.
- `pgassistant_maintain`: a privileged account used only when an operator
  explicitly requests maintenance, such as `VACUUM`, `ANALYZE`, or a statistics
  reset.

The maintenance role inherits the analysis role, so it can perform the same
diagnostic work in addition to its explicitly granted maintenance operations.

> [!IMPORTANT]
> Use `pgassistant_analyze` for normal pgAssistant sessions. Store the
> `pgassistant_maintain` credentials separately and expose them only to trusted
> operators.

## Capabilities

| Capability | `pgassistant_analyze` | `pgassistant_maintain` |
|---|---:|---:|
| Dashboard and database report | Yes | Yes |
| Global Advisor | Yes | Yes |
| Query Ranking | Yes | Yes |
| Index Advisor | Yes | Yes |
| Database Design analysis | Yes | Yes |
| Read `pg_stat_statements` for other users | Yes | Yes |
| `VACUUM` and `ANALYZE` on PostgreSQL 17+ | No | Optional |
| Reset PostgreSQL statistics | No | Optional |
| Terminate non-superuser sessions | No | Optional |
| `CREATE INDEX`, `DROP INDEX`, or `ALTER TABLE` | No | No |
| `ALTER SYSTEM` | No | No |

## Prerequisites

The PostgreSQL administrator must configure `pg_stat_statements` before using
the workload-related pgAssistant features. The extension requires the module to
be present in `shared_preload_libraries`, followed by a PostgreSQL restart when
that setting is changed.

Install the extension in every database analyzed by pgAssistant:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Do not grant extension installation privileges to the pgAssistant roles. Treat
extension installation as a database administration operation.

## Create the roles

Run the following commands as a PostgreSQL administrator. Replace the example
passwords with secrets generated and stored outside source control.

```sql
CREATE ROLE pgassistant_analyze
    LOGIN
    PASSWORD 'CHANGE_ANALYZE_PASSWORD'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    NOBYPASSRLS
    CONNECTION LIMIT 5;

CREATE ROLE pgassistant_maintain
    LOGIN
    PASSWORD 'CHANGE_MAINTAIN_PASSWORD'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    NOBYPASSRLS
    CONNECTION LIMIT 2;

GRANT pgassistant_analyze TO pgassistant_maintain;
```

PostgreSQL roles are cluster-wide. Object privileges and default role settings
must still be configured in each target database.

## Configure the analysis role

### Monitoring privileges

Grant the predefined `pg_monitor` role:

```sql
GRANT pg_monitor TO pgassistant_analyze;
```

`pg_monitor` includes the capabilities of `pg_read_all_settings`,
`pg_read_all_stats`, and `pg_stat_scan_tables`. In particular, it allows
pgAssistant to inspect server settings and see query text and query identifiers
for statements executed by other users in `pg_stat_statements`.

### Database connection

Repeat this grant for every database that pgAssistant is allowed to analyze:

```sql
GRANT CONNECT ON DATABASE my_database TO pgassistant_analyze;
```

PostgreSQL commonly grants `CONNECT` to `PUBLIC` by default. If strict database
isolation is required, review the existing database privileges and `pg_hba.conf`
rules rather than assuming the preceding grant prevents access to other
databases.

### Application schemas

Connect to the target database and grant read access to each application schema:

```sql
GRANT USAGE
ON SCHEMA public, application_schema
TO pgassistant_analyze;

GRANT SELECT
ON ALL TABLES IN SCHEMA public, application_schema
TO pgassistant_analyze;

GRANT SELECT
ON ALL SEQUENCES IN SCHEMA public, application_schema
TO pgassistant_analyze;
```

Sequence access is required for checks that compare sequence values with their
data type limits. Table access is also required when pgAssistant obtains generic
plans for workload queries or samples column values for database design
analysis.

Repeat these grants for every user schema that pgAssistant must inspect.

### Future objects

Default privileges are defined by the role that creates objects. Run the
following commands for every relevant application owner and schema:

```sql
ALTER DEFAULT PRIVILEGES
FOR ROLE application_owner
IN SCHEMA application_schema
GRANT SELECT ON TABLES TO pgassistant_analyze;

ALTER DEFAULT PRIVILEGES
FOR ROLE application_owner
IN SCHEMA application_schema
GRANT SELECT ON SEQUENCES TO pgassistant_analyze;
```

If workload queries reference application functions whose `EXECUTE` privilege
has been revoked from `PUBLIC`, grant only the functions required to plan those
queries:

```sql
GRANT EXECUTE
ON FUNCTION application_schema.some_function(integer)
TO pgassistant_analyze;
```

Avoid granting `EXECUTE ON ALL FUNCTIONS` unless all functions in the schema
have been reviewed for side effects and sensitive behavior.

### Optional session safeguards

The following settings provide useful safeguards for the normal analysis
account. They must be applied separately in each target database:

```sql
ALTER ROLE pgassistant_analyze
IN DATABASE my_database
SET default_transaction_read_only = on;

ALTER ROLE pgassistant_analyze
IN DATABASE my_database
SET statement_timeout = '5min';

ALTER ROLE pgassistant_analyze
IN DATABASE my_database
SET lock_timeout = '5s';

ALTER ROLE pgassistant_analyze
IN DATABASE my_database
SET idle_in_transaction_session_timeout = '1min';
```

These settings are safeguards, not replacements for PostgreSQL privileges. A
role can normally change user-settable parameters within its own session.

## Broader read-only alternative

Instead of granting access schema by schema, an administrator can use the
predefined `pg_read_all_data` role:

```sql
GRANT pg_read_all_data TO pgassistant_analyze;
```

This is easier to maintain because it covers current and future tables, views,
sequences, and schemas. However, it applies across the PostgreSQL cluster for
every database the role can connect to. It also does not bypass row-level
security policies.

Explicit per-schema grants are recommended when database isolation and least
privilege are important.

## Configure the maintenance role

### `VACUUM` and `ANALYZE` on PostgreSQL 17 or newer

PostgreSQL 17 introduced the `MAINTAIN` table privilege and the predefined
`pg_maintain` role.

The recommended approach is to scope maintenance to the application schemas:

```sql
GRANT MAINTAIN
ON ALL TABLES IN SCHEMA public, application_schema
TO pgassistant_maintain;
```

Configure future tables for each application owner:

```sql
ALTER DEFAULT PRIVILEGES
FOR ROLE application_owner
IN SCHEMA application_schema
GRANT MAINTAIN ON TABLES TO pgassistant_maintain;
```

`MAINTAIN` permits operations including `VACUUM`, `ANALYZE`, `REINDEX`,
`CLUSTER`, `REFRESH MATERIALIZED VIEW`, and `LOCK TABLE`. Grant it only on
relations that pgAssistant is expected to maintain.

If pgAssistant must maintain every relation in every accessible database, the
broader predefined role can be used instead:

```sql
GRANT pg_maintain TO pgassistant_maintain;
```

The per-schema `MAINTAIN` grants are preferred.

### PostgreSQL 16 and older

PostgreSQL 16 and older do not provide the `MAINTAIN` privilege. Maintenance
commands generally require relation ownership or superuser access on those
versions.

Do not make `pgassistant_maintain` the owner of application objects solely to
work around this restriction. Run maintenance through the application owner or
a database administrator instead.

## Reset statistics

Statistics resets erase diagnostic history used by the Dashboard, Query
Ranking, Global Advisor, Index Advisor, and database reports. Keep these grants
exclusive to the maintenance role.

Grant access to the core PostgreSQL statistics reset:

```sql
GRANT EXECUTE
ON FUNCTION pg_catalog.pg_stat_reset()
TO pgassistant_maintain;
```

The signature of `pg_stat_statements_reset` varies between PostgreSQL versions.
The following block grants access to every installed signature with that exact
function name:

```sql
DO $grant$
DECLARE
    function_record record;
BEGIN
    FOR function_record IN
        SELECT
            n.nspname AS schema_name,
            p.proname AS function_name,
            pg_get_function_identity_arguments(p.oid) AS arguments
        FROM pg_proc AS p
        JOIN pg_namespace AS n
          ON n.oid = p.pronamespace
        WHERE p.proname = 'pg_stat_statements_reset'
    LOOP
        EXECUTE format(
            'GRANT EXECUTE ON FUNCTION %I.%I(%s) TO pgassistant_maintain',
            function_record.schema_name,
            function_record.function_name,
            function_record.arguments
        );
    END LOOP;
END
$grant$;
```

Run this block in every database where `pg_stat_statements` is installed and
pgAssistant is allowed to reset its statistics.


## Deliberately excluded privileges

The two roles intentionally do not receive privileges for:

- installing extensions;
- creating or dropping indexes;
- altering tables, columns, constraints, or object definitions;
- changing cluster configuration with `ALTER SYSTEM`;
- changing settings for arbitrary PostgreSQL roles;
- creating databases or roles;
- bypassing row-level security;
- reading or writing server files.

PostgreSQL treats the ability to alter or drop an object as an ownership
capability rather than an independently grantable privilege. Making the
maintenance account a member of every application owner role would provide
broad DDL control and is not recommended.

pgAssistant should display generated DDL as a recommendation for review. A
database owner or administrator should execute that DDL through the normal
change-management process.

## Verification queries

Connect as `pgassistant_analyze` and verify the effective roles:

```sql
SELECT
    current_user,
    pg_has_role(current_user, 'pg_monitor', 'MEMBER') AS has_monitor,
    pg_has_role(current_user, 'pgassistant_analyze', 'MEMBER') AS has_analyze;
```

Verify that workload statistics are visible:

```sql
SELECT queryid, query, calls, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 5;
```

Verify application relation access:

```sql
SELECT has_table_privilege(
    current_user,
    'application_schema.example_table',
    'SELECT'
);
```

On PostgreSQL 17 or newer, connect as `pgassistant_maintain` and verify scoped
maintenance access:

```sql
SELECT has_table_privilege(
    current_user,
    'application_schema.example_table',
    'MAINTAIN'
);
```

Check the reset function privileges without resetting statistics:

```sql
SELECT has_function_privilege(
    current_user,
    'pg_catalog.pg_stat_reset()',
    'EXECUTE'
);
```

## Operational recommendation

1. Configure pgAssistant with `pgassistant_analyze` by default.
2. Keep `pgassistant_maintain` credentials in a separate secret.
3. Require an explicit operator action before using the maintenance account.
4. Review generated SQL before execution.
5. Record the operator, target database, SQL command, start time, result, and
   error for every maintenance action.
6. Revoke optional capabilities when they are no longer required.

Example revocations:

```sql
REVOKE pg_signal_backend FROM pgassistant_maintain;

REVOKE EXECUTE
ON FUNCTION pg_catalog.pg_stat_reset()
FROM pgassistant_maintain;

REVOKE MAINTAIN
ON ALL TABLES IN SCHEMA application_schema
FROM pgassistant_maintain;
```

## PostgreSQL documentation

- [Predefined roles](https://www.postgresql.org/docs/current/predefined-roles.html)
- [`GRANT`](https://www.postgresql.org/docs/current/sql-grant.html)
- [`pg_stat_statements`](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [System administration functions](https://www.postgresql.org/docs/current/functions-admin.html)
- [`VACUUM`](https://www.postgresql.org/docs/current/sql-vacuum.html)
- [`ANALYZE`](https://www.postgresql.org/docs/current/sql-analyze.html)
