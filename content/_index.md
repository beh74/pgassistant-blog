---
title: "Welcome to pgAssistant"
description: "Analyze one PostgreSQL database or prioritize improvements across a fleet of hundreds or thousands."
---

![logo](images/logo.png)

**pgAssistant** helps developers, DBAs, and operations teams understand and improve PostgreSQL databases.

It can be used interactively to analyze a single database, or combined with **pgAssistant Collector** and **pgAssistant Grafana** to identify and prioritize actions across hundreds or thousands of databases.

> **Analyze one PostgreSQL database. Prioritize a fleet of thousands.**

---

## One Database or an Entire PostgreSQL Fleet

### Analyze a Single Database

The main **pgAssistant** application provides an interactive interface for:

- understanding a database schema and its workload;
- detecting structural and configuration issues;
- analyzing expensive SQL queries and execution plans;
- identifying indexing opportunities;
- reviewing autovacuum, statistics, and maintenance;
- producing prioritized recommendations and an implementation plan.

This is useful for a developer investigating one application database, as well as for a DBA performing a detailed PostgreSQL assessment.

### Manage Hundreds or Thousands of Databases

For larger PostgreSQL estates, two companion projects automate and centralize pgAssistant analyses:

| Project | Role |
| --- | --- |
| **[pgAssistant Collector](https://github.com/beh74/pgassistant-collector)** | Runs selected pgAssistant analyses across declared databases and stores historical results in a central PostgreSQL repository. |
| **[pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)** | Provides fleet-wide dashboards showing priorities, trends, advisor findings, and the databases requiring attention first. |

Together, the three projects make it possible to:

1. collect consistent diagnostics across applications and environments;
2. identify which databases require action first;
3. drill down from a fleet overview to a database, query, or recommendation;
4. assign remediation work to development and operations teams;
5. track whether priority findings are resolved over time.

```text
PostgreSQL fleet → Collector → pgAssistant analyses → Central repository → Grafana
                                      ↓
                         Diagnosis and action plan
```

---

## Deterministic First, AI When Needed

pgAssistant is built on a simple principle:

> **Start with deterministic database analysis.  
> Use AI only when it adds value.**

### Deterministic Analysis

pgAssistant queries PostgreSQL system catalogs and statistics to produce **reliable and reproducible diagnostics**.

The **Global Advisor** provides:

- one-click database analysis;
- recommendations ranked by priority, confidence, impact, and effort;
- detection of missing indexes on foreign keys;
- datatype inconsistencies;
- redundant, invalid, or unused indexes;
- tables without primary keys;
- stale statistics and maintenance issues;
- table bloat and dead-tuple pressure;
- long-running transactions;
- unsupported PostgreSQL versions and available upgrades;
- important configuration issues.

The **Executive Plan** consolidates findings from the Global, Index, Parameter, Autovacuum, and Fillfactor advisors into ordered work packages for DEV and OPS teams.

No AI is required for these analyses.

---

## Query and Workload Analysis

pgAssistant can analyze an individual SQL statement or the workload collected by `pg_stat_statements`:

- `EXPLAIN ANALYZE` insights;
- expensive-query ranking;
- join, scan, sort, and aggregate analysis;
- index recommendations;
- row-estimation and statistics issues;
- query rewrite opportunities;
- PostgreSQL parameter recommendations;
- relational visualization of the tables involved.

> `EXPLAIN ANALYZE` executes the statement. Review queries carefully and use a suitable database role.

---

## Optional AI Assistance

AI is an augmentation layer, not a dependency.

When an LLM is configured, pgAssistant can provide:

- SQL rewrite suggestions;
- contextual explanations of execution plans;
- advanced optimization reasoning;
- database-design feedback based on schema and workload;
- naming convention and RFC checks.

**pgAssistant remains fully usable without AI.**

---

## Try It Online

Database analysis interface:  
[https://ov-004f8b.infomaniak.ch/](https://ov-004f8b.infomaniak.ch/)

Demo connection:

```text
postgresql://postgres:demo@demo-db:5432/northwind
```

Fleet dashboards:  
[pgAssistant Grafana demo](https://ov-004f8b.infomaniak.ch/grafana/)

The Grafana demo credentials are documented in the  
[pgAssistant Grafana repository](https://github.com/beh74/pgassistant-grafana).

> The public demo does not use an LLM.  
> Do not provide personal API keys.

---

## Why pgAssistant?

- Open source and built specifically for PostgreSQL;
- useful for both a single database and a large PostgreSQL estate;
- deterministic and reproducible analysis;
- optional AI assistance;
- recommendations prioritized by impact and effort;
- focused on actionable improvements, not just metrics;
- implementation planning for development and operations teams;
- historical fleet-level visibility with Collector and Grafana.

Explore the documentation, blog posts, and project repositories:

- [pgAssistant Community](https://github.com/beh74/pgassistant-community)
- [pgAssistant Collector](https://github.com/beh74/pgassistant-collector)
- [pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)

---

## Before You Begin

- [Enable pg_stat_statements](doc/pg_stat_statments)
- [Quick start with Docker](doc/startup_docker)

---

## Monitoring and pgAssistant

pgAssistant is not intended to replace a real-time monitoring and alerting platform.

For PostgreSQL observability, **[pgWatch](https://github.com/cybertec-postgresql/pgwatch)** provides:

- real-time metric collection;
- Grafana dashboards;
- Prometheus integration;
- visualization and alerting.

> **Monitoring shows what is happening.**  
> **pgAssistant helps decide what to improve next and how to implement it.**
