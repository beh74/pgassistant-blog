---
title: "Introducing pgAssistant Auto-Tune: From Recommendations to Action"
date: 2026-10-25
tags: ["pgAssistant", "Release", "PostgreSQL", "Auto-Tune"]
description: "Apply selected pgAssistant recommendations across your PostgreSQL fleet with YAML policies, dry-run previews, and execution history."
draft: false
---

**pgAssistant Auto-Tune is now available.** It turns selected pgAssistant recommendations into controlled actions, for a single PostgreSQL database or an entire fleet.

pgAssistant advises, **Collector** stores recommendation snapshots, **Grafana** makes fleet priorities visible, and **Auto-Tune** executes the actions you authorize.

## Choose, preview, execute

Define a **YAML policy** to select recommendations by team, advisor, action type, schema, table, or confidence. Apply a common policy across the fleet, with overrides for individual databases.

Start in **dry-run mode** to inspect the proposed SQL without connecting to target databases or executing changes. When ready, switch to execution mode and submit a new run. Starting the services alone does not trigger tuning.

Supported actions include:

- **Indexes:** concurrent creation and removal through supported advisor recommendations.
- **Maintenance:** `ANALYZE` and `VACUUM`.
- **Autovacuum configuration:** supported changes that do not require a restart.

The Parameter Advisor does not yet have an executor. All profiles in the default policy are initially disabled.

## Keep execution visible

The API retains policies, source snapshots, SQL, step results, and durations. Failed or uncertain attempts require review before retrying; multi-step scripts have no automatic rollback.

To get started, you need **Docker Compose** and a **pgAssistant Collector** collecting the `executive_plan` job.

[Explore pgAssistant Auto-Tune and follow the quick start →](https://github.com/beh74/pgassistant-autotune)
