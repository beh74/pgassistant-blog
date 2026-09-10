---
title: "pgAssistant — Continuous PostgreSQL Improvement"
description: "Turn PostgreSQL evidence into a prioritized remediation plan, track what changed, and measure whether the workload improved."
---

![pgAssistant logo](images/logo.png)

# A continuous PostgreSQL improvement platform

**pgAssistant** turns PostgreSQL evidence into prioritized action. Analyze a database and its workload, decide what to improve, organize the work, collect new evidence, and measure the result.

Use it for one database or extend the same approach across a fleet of hundreds or thousands.

> **Observe. Diagnose. Prioritize. Plan. Implement. Measure. Repeat.**

---

## The continuous improvement loop

pgAssistant connects diagnosis, implementation planning, and historical evidence in one repeatable process:

```text
Observe → Diagnose → Prioritize → Plan → Implement → Collect again → Measure
   ↑                                                                  │
   └────────────────────────── Repeat continuously ────────────────────┘
```

1. **Observe** — collect repeatable database, workload, and environment evidence.
2. **Diagnose** — use deterministic advisors to identify SQL, schema, index, configuration, and maintenance issues.
3. **Prioritize** — rank findings by urgency, confidence, effort, and workload impact.
4. **Plan** — turn related recommendations into ordered work packages owned by DEV, OPS, or both.
5. **Implement** — apply each change with its dependencies, SQL guidance, and maintenance requirements in view.
6. **Measure** — compare the next collection with the previous one to understand what changed and whether the workload improved.

pgAssistant is not a real-time monitoring or alerting system. Monitoring tells you what is happening now; pgAssistant helps you decide what to improve next and verify the result over time.

---

## From findings to an Executive Plan

The **Global, Index, Parameter, Autovacuum, and Fillfactor advisors** produce reproducible findings from PostgreSQL catalogs, statistics, settings, and execution plans.

The **Executive Plan** consolidates those findings into an ordered remediation plan instead of leaving teams with a disconnected list of recommendations. It provides:

- priorities, dependencies, confidence, impact, and estimated effort;
- work packages assigned to DEV, OPS, or DEV/OPS;
- implementation guidance, maintenance constraints, and executable SQL;
- PDF reports filtered for development and operations audiences;
- historical comparison of new, persistent, and no-longer-detected findings.

A finding that disappears from a later collection is reported as no longer detected—not automatically treated as proof that a change was deployed.

---

## Measure results with Workload Insights

Introduced in **pgAssistant 3.8.0**, **Workload Insights** compares consecutive Collector measurements and shows:

- execution time, call volume, and query-mix changes;
- the queries driving the largest gains or regressions;
- changes in PostgreSQL versions and important tuning settings;
- the evolution of Executive Plan recommendations;
- workload impact before and after an intervention.

This historical view closes the improvement loop: teams can connect a decision to observed PostgreSQL changes, evaluate the outcome, and choose the next action using fresh evidence.

[Read what is new in pgAssistant 3.8.0](post/pgassistant_3_8_0_released/)

---

## One database or a PostgreSQL fleet

### One database

Use the pgAssistant web interface for a deep analysis of:

- SQL statements and execution plans;
- workload impact and expensive-query ranking;
- schema design, relationships, indexes, and table health;
- PostgreSQL configuration and pgTune baselines;
- autovacuum, statistics, bloat indicators, and maintenance;
- prioritized remediation for developers and DBAs.

### A fleet of hundreds or thousands

Two companion projects automate and centralize the same improvement process:

| Project | Role |
| --- | --- |
| **[pgAssistant Collector](https://github.com/beh74/pgassistant-collector)** | Runs selected jobs across declared databases and stores historical workload, environment, and advisor snapshots in a central PostgreSQL repository. |
| **[pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)** | Displays fleet-wide priorities and trends so teams can identify the databases, queries, and recommendations requiring attention first. |

```text
PostgreSQL fleet → Collector → Repository → pgAssistant → Executive Plan
       ↑                           ↓             ↓              ↓
       └──────────── Collect again ← Measure results ← Implement changes
                                   ↓
                          Grafana fleet overview
```

---

## Deterministic first, AI when useful

The core pgAssistant advisors are deterministic and work without an LLM. They query PostgreSQL system catalogs, statistics, configuration, and execution plans to produce reproducible recommendations.

AI is an optional augmentation layer for tasks such as:

- SQL rewrite suggestions;
- contextual execution-plan explanations;
- schema-design feedback;
- naming convention and RFC checks.

**pgAssistant remains fully usable without AI.**

---

## Try pgAssistant

Open the [pgAssistant live demo](https://ov-004f8b.infomaniak.ch/) and use:

```text
postgresql://postgres:demo@demo-db:5432/northwind
```

Explore fleet-wide priorities in the [pgAssistant Grafana demo](https://ov-004f8b.infomaniak.ch/grafana/). Credentials are documented in the [pgAssistant Grafana repository](https://github.com/beh74/pgassistant-grafana).

> The demo database is reset daily. AI features are disabled; do not enter personal API keys.

---

## Get started

- [Quick start with Docker](doc/startup_docker/)
- [Install from Python sources](doc/startup_python/)
- [Enable pg_stat_statements](doc/pg_stat_statments/)
- [Explore pgAssistant Community](https://github.com/beh74/pgassistant-community)
- [Read the latest release notes](post/pgassistant_3_8_0_released/)
- [Manage a fleet of more than 1,000 PostgreSQL databases](post/managing_1000_postgresql_databases/)
