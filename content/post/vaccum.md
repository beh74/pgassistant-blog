---
title: "PostgreSQL Autovacuum Tuning Based on Table Size"
date: 2025-07-27
tags: ["PostgreSQL", "vacuum"]
draft: false
---

# Object 

This post provides a SQL query that analyzes PostgreSQL tables and suggests optimized `autovacuum` settings on a **per-table basis**. It aims to improve database health and performance by adapting vacuum/analyze thresholds according to **table size** and **usage patterns**.

## Goal

PostgreSQL uses `autovacuum` to automatically clean up dead tuples and refresh planner statistics. However, the default settings may be too aggressive for small tables or too lax for large ones, leading to:

- **Table bloat** (too much dead data)
- **Poor query planning** (outdated statistics)
- **Unnecessary I/O overhead** (frequent vacuums on small tables)

This script identifies tables with suboptimal autovacuum settings and suggests tailored values using industry recommendations.

---

## Logic Used

The query calculates optimal values for four key autovacuum parameters:

- `autovacuum_vacuum_scale_factor`
- `autovacuum_vacuum_threshold`
- `autovacuum_analyze_scale_factor`
- `autovacuum_analyze_threshold`

These are determined based on the estimated number of rows in each table (`pg_class.reltuples`).

### Dynamic Threshold Logic

| Estimated Row Count (`reltuples`) | `vacuum_scale_factor` | `vacuum_threshold` | `analyze_scale_factor` | `analyze_threshold` |
|-----------------------------------|------------------------|--------------------|-------------------------|----------------------|
| > 1,000,000                       | 0.0                    | 400,000            | 0.0                     | 100,000              |
| 100,000 – 1,000,000               | 0.005                  | 10,000             | 0.01                    | 10,000               |
| 10,000 – 100,000                  | 0.02                   | 1,000              | 0.01                    | 1,000                |
| < 10,000                          | 0.01                   | 1,000              | 0.005                   | 500                  |

These values are based on community best practices from sources like:

- [EnterpriseDB](https://www.enterprisedb.com/blog/autovacuum-tuning-basics)
- [Percona](https://www.percona.com/blog/tuning-autovacuum-in-postgresql-and-autovacuum-internals)
- [pganalyze](https://pganalyze.com/blog/introducing-vacuum-advisor-postgres)
- [Keith Fiske](https://www.keithf4.com/per-table-autovacuum-tuning/)

---

## Special Cases

- **If `reltuples = -1`**, it means the table has never been analyzed.
  - → The script will suggest: `ANALYZE schema.table;`
- **If a table already has optimal settings**, no action is suggested.

---

## Output

The query returns:

- Table name
- Current and suggested autovacuum values
- A SQL command: either `ANALYZE` or `ALTER TABLE ... SET (...)`

You can filter on `suggested_action IS NOT NULL` to extract only actionable commands.

---

## How to Use

1. Run the [query](/post/vaccum/#the-query) in a PostgreSQL-compatible tool (e.g. `psql`, DBeaver, pgAdmin).
2. Review the `suggested_action` column.
3. Apply the `ALTER TABLE` and `ANALYZE` commands where appropriate.

** Always test configuration changes in staging environments before deploying to production.**

---

## Notes

- The script assumes default PostgreSQL configuration as baseline (`scale_factor = 0.2`, `threshold = 50`).
- It is designed for PostgreSQL 12+.
- It ignores `pg_catalog` and `information_schema` namespaces.

---

## Feedback

Feel free to contribute improvements or report issues if your workload requires more specialized tuning (e.g. append-only tables, partitioned workloads, etc.).

## The query
```
WITH table_info AS (
  SELECT
    n.nspname,
    c.relname,
    c.oid,
    COALESCE(c.reltuples, -1) AS reltuples,
    c.reloptions,
    (
      SELECT regexp_replace(opt, 'autovacuum_vacuum_scale_factor=', '')
      FROM unnest(c.reloptions) opt
      WHERE opt LIKE 'autovacuum_vacuum_scale_factor=%'
    )::float AS current_vacuum_scale,
    (
      SELECT regexp_replace(opt, 'autovacuum_vacuum_threshold=', '')
      FROM unnest(c.reloptions) opt
      WHERE opt LIKE 'autovacuum_vacuum_threshold=%'
    )::int AS current_vacuum_threshold,
    (
      SELECT regexp_replace(opt, 'autovacuum_analyze_scale_factor=', '')
      FROM unnest(c.reloptions) opt
      WHERE opt LIKE 'autovacuum_analyze_scale_factor=%'
    )::float AS current_analyze_scale,
    (
      SELECT regexp_replace(opt, 'autovacuum_analyze_threshold=', '')
      FROM unnest(c.reloptions) opt
      WHERE opt LIKE 'autovacuum_analyze_threshold=%'
    )::int AS current_analyze_threshold
  FROM
    pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
  WHERE
    c.relkind = 'r'
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
),
computed_autovacuum AS (
  SELECT
    *,
    CASE
      WHEN reltuples > 1000000 THEN 0.0
      WHEN reltuples > 100000 THEN 0.005
      WHEN reltuples > 10000 THEN 0.02
      WHEN reltuples >= 0 THEN 0.01
      ELSE NULL
    END AS new_vacuum_scale,
    CASE
      WHEN reltuples > 1000000 THEN 400000
      WHEN reltuples > 100000 THEN 10000
      WHEN reltuples > 10000 THEN 1000
      WHEN reltuples >= 0 THEN 1000
      ELSE NULL
    END AS new_vacuum_threshold,
    CASE
      WHEN reltuples > 1000000 THEN 0.0
      WHEN reltuples > 100000 THEN 0.01
      WHEN reltuples > 10000 THEN 0.01
      WHEN reltuples >= 0 THEN 0.005
      ELSE NULL
    END AS new_analyze_scale,
    CASE
      WHEN reltuples > 1000000 THEN 100000
      WHEN reltuples > 100000 THEN 10000
      WHEN reltuples > 10000 THEN 1000
      WHEN reltuples >= 0 THEN 500
      ELSE NULL
    END AS new_analyze_threshold
  FROM table_info
)
SELECT
  nspname || '.' || relname AS table_name,
  reltuples AS estimated_rows,
  COALESCE(current_vacuum_scale, 0.2) AS current_vacuum_scale,
  COALESCE(current_vacuum_threshold, 50) AS current_vacuum_threshold,
  COALESCE(current_analyze_scale, 0.1) AS current_analyze_scale,
  COALESCE(current_analyze_threshold, 50) AS current_analyze_threshold,
  new_vacuum_scale,
  new_vacuum_threshold,
  new_analyze_scale,
  new_analyze_threshold,
  CASE
    WHEN reltuples = -1 THEN 
      'ANALYZE ' || quote_ident(nspname) || '.' || quote_ident(relname) || ';'
    WHEN COALESCE(current_vacuum_scale, 0.2) != new_vacuum_scale
      OR COALESCE(current_vacuum_threshold, 50) != new_vacuum_threshold
      OR COALESCE(current_analyze_scale, 0.1) != new_analyze_scale
      OR COALESCE(current_analyze_threshold, 50) != new_analyze_threshold
    THEN 'ALTER TABLE ' || quote_ident(nspname) || '.' || quote_ident(relname) || ' SET (' ||
         'autovacuum_vacuum_scale_factor = ' || new_vacuum_scale || ', ' ||
         'autovacuum_vacuum_threshold = ' || new_vacuum_threshold || ', ' ||
         'autovacuum_analyze_scale_factor = ' || new_analyze_scale || ', ' ||
         'autovacuum_analyze_threshold = ' || new_analyze_threshold || ');'
    ELSE NULL
  END AS suggested_action
FROM computed_autovacuum
ORDER BY reltuples DESC NULLS LAST;
```

