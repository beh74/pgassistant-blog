---
title: "What’s New in pgAssistant Since Version 2.8 !"
date: 2026-06-06
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)


# What’s New in pgAssistant Since Version 2.8

Since version 2.8, pgAssistant has evolved significantly.

The initial goal was to introduce a **Global Advisor** capable of combining multiple PostgreSQL signals—schema design, indexes, maintenance statistics, configuration, and workload activity—to provide higher-level recommendations.

Several releases later, this experimental feature has become a much more mature expert system. At the same time, the Query Advisor, Index Advisor, ranking engine, collector integrations, and developer-facing maintenance views have also improved.

This article summarizes the main changes introduced between **pgAssistant 2.8.0 and 2.9.2**.

---

## Global Advisor: from an experiment to a broader expert system

Version 2.8 introduced the first version of the Global Advisor.

Its purpose was to move beyond isolated query analysis and evaluate the database as a whole. Instead of looking only at a single execution plan, pgAssistant started correlating signals from:

- database schemas;
- foreign keys;
- indexes;
- table statistics;
- vacuum and analyze activity;
- configuration settings;
- storage usage.

The first release was intentionally experimental, but the advisor quickly expanded.

By version 2.8.2, the Global Advisor included **14 different recommendations**, together with:

- a summary of the detected findings;
- clearer recommendation grouping;
- a button to display all generated SQL suggestions;
- one-click copying of all suggested commands.

This made the advisor more useful as both a diagnostic tool and a review checklist.

---

## Better foreign-key diagnostics

Foreign keys were one of the first areas improved after the initial Global Advisor release.

### Data type mismatches

pgAssistant now detects foreign-key columns whose data types differ from the referenced columns.

The detection logic was refined to reduce false positives and provide clearer remediation guidance.

The recommendation also takes into account that changing a column type can:

- rewrite the table;
- rebuild dependent indexes;
- acquire an `ACCESS EXCLUSIVE` lock;
- require additional disk space;
- require a maintenance window.

The suggested SQL includes both the type change and a subsequent `ANALYZE`.

### Missing foreign-key indexes

The advisor also detects useful indexes missing from foreign-key columns.

The logic now considers the size of both the child and referenced tables, reducing noise for very small tables and prioritizing cases where the index is more likely to improve:

- joins;
- lookups;
- parent-table `UPDATE` operations;
- parent-table `DELETE` operations.

---

## Stronger index diagnostics

Index analysis has received several important improvements.

### Better index recommendations from execution plans

The Index Advisor can now identify a potentially better index even when an execution-plan node already uses an existing index.

Previously, the presence of an index scan could hide opportunities for a more selective or better-aligned index. The new logic evaluates whether the existing index is actually the best available access path.

### Duplicate and redundant indexes

The Global Advisor now identifies:

- strictly duplicate indexes;
- unused indexes;
- non-unique indexes fully covered by equivalent unique indexes;
- tables with an unusually high index-to-table size ratio.

For strictly duplicate indexes, pgAssistant now keeps the **most-used equivalent index** rather than selecting one only by object identifier.

This is important because identical index definitions do not necessarily have identical operational value.

### Safer unused-index detection

An index with `idx_scan = 0` is not automatically useless.

The counter may have been reset recently, or the observed workload may not yet be representative.

The unused-index checks now expose:

- the database statistics reset timestamp;
- the observation age;
- table scan activity;
- table write activity.

A generic unused index is reported only when:

- at least 24 hours of statistics are available; and
- the table has experienced meaningful activity.

The current thresholds require at least:

- 100 table scans; or
- 1,000 row modifications.

For structurally redundant indexes, the statistics age remains informational rather than blocking the recommendation, because the redundancy can already be proven from PostgreSQL system catalogs.

### Invalid index handling

The invalid-index recommendation has also been redesigned.

Instead of always suggesting a drop and manual recreation, pgAssistant now prefers:

```sql
REINDEX INDEX schema.index_name;
```

This preserves the index definition and is generally safer for indexes supporting constraints.

The advisor also recognizes common artifacts left by failed concurrent rebuilds:

- `_ccnew`;
- `_ccold`.

These cases receive specific guidance, because blindly rebuilding or dropping such indexes could leave duplicates or remove the wrong object.

---

## PostgreSQL release and support checks

Version 2.9.1 introduced PostgreSQL release checks in the Global Advisor.

pgAssistant retrieves the official release information from:

https://www.postgresql.org/versions.json

It can now detect two different situations.

### A newer minor release is available

For example:

> PostgreSQL 17.6 is not the latest minor release available for branch 17. Upgrade to PostgreSQL 17.10, released on 2026-05-14, to benefit from the latest bug, security, reliability, and data-integrity fixes.

The recommendation includes:

- the installed release;
- the latest release in the same major branch;
- the publication date of that release;
- a recommendation to review intermediate release notes.

### The PostgreSQL branch is no longer supported

The advisor also reports end-of-life versions, even if the final minor release is already installed.

For example:

> PostgreSQL 13.23 is the latest minor release of the 13 branch, but this branch is no longer supported. Plan a major upgrade to a supported PostgreSQL version. End-of-life date: 2025-11-13.

This distinction matters because installing the latest minor release does not restore support for an obsolete major branch.

---

## More accurate maintenance recommendations

Maintenance recommendations were refined to reduce unnecessary findings.

### Tables never vacuumed

The previous implementation could report very small tables simply because no vacuum timestamp was available.

The rule now requires stronger evidence, combining:

- table size;
- an absolute number of dead tuples;
- dead tuple percentage;
- absence of recorded vacuum activity.

This prevents pgAssistant from recommending maintenance for insignificant tables containing only a few rows or dead tuples.

### Stale statistics

The stale-statistics check considers:

- the age of the last manual or automatic analyze;
- the amount of data modified since the last analyze;
- the table size;
- the modification ratio.

The recommendation is therefore based on workload and table significance rather than only on a timestamp.

### Vacuum recommendations

Starting with version 2.8.4, pgAssistant recommends `ANALYZE` or `VACUUM` only when the latest relevant maintenance operation is older than six days.

This reduces repetitive advice for tables that were maintained recently.

### Autovacuum urgency

A dedicated recommendation calculates whether a table has exceeded its effective autovacuum threshold.

The calculation considers:

- global autovacuum settings;
- table-specific reloptions;
- estimated row count;
- dead tuple count;
- configured maximum thresholds.

This gives a more meaningful signal than a simple dead tuple percentage.

---

## Version-aware PostgreSQL configuration checks

Configuration recommendations now consider the installed PostgreSQL version.

This is necessary because default values have changed between major releases.

The advisor checks settings such as:

- `autovacuum`;
- `track_counts`;
- `track_activities`;
- `log_checkpoints`;
- `log_autovacuum_min_duration`;
- `checkpoint_completion_target`;
- `checkpoint_timeout`.

For example, `checkpoint_completion_target` used a lower default in older PostgreSQL releases, while logging defaults also changed in more recent versions.

The recommendation text now explains whether a value was historically normal for that PostgreSQL version or differs from a modern default.

---

## Sequence exhaustion detection

Version 2.8.3 introduced a recommendation for sequences approaching their maximum value.

pgAssistant calculates the percentage of the available sequence range already consumed and reports:

- a medium-level warning above 75%;
- a high-level warning above 90%.

This helps identify future insert failures before the sequence is exhausted.

---

## Better workload prioritization

The query ranking algorithm was improved in version 2.8.4.

Sorting queries only by mean execution time or total execution time often produces misleading priorities.

A query executed once may be slow but have little overall impact, while a moderately slow query executed thousands of times can consume much more of the workload.

The updated ranking gives more weight to:

- execution frequency;
- total workload impact;
- repeatability;
- technical signals.

At the same time, it reduces the influence of low-impact one-off queries.

The result is a more practical answer to the question:

> Which PostgreSQL queries should I optimize first?

---

## Richer context for AI-assisted query analysis

The query-analysis prompt is now enriched with column statistics collected by pgAssistant.

Execution plans alone rarely provide enough context for accurate recommendations.

The additional statistics help the AI reason about:

- cardinality;
- null fractions;
- common values;
- data distributions;
- selectivity;
- correlations.

This reinforces pgAssistant’s hybrid approach:

- deterministic expert-system rules for reliable technical diagnostics;
- AI for explanation, synthesis, and contextual analysis.

---

## Table Definition Helper redesign

The Table Definition Helper interface was redesigned to provide a clearer view of:

- table size;
- index footprint;
- row estimates;
- dead tuples;
- estimated bloat;
- schema information.

The new card-based interface includes:

- summary indicators;
- immediate search while typing;
- client-side filters;
- sorting;
- pagination;
- visual severity levels.

This makes it easier to navigate large databases without repeatedly submitting server-side searches.

---

## New Table Health view

Version 2.9.2 introduces a new **Table Health** page in the DBA Corner.

Despite its location, the goal is not to turn pgAssistant into a general-purpose DBA console.

The purpose remains developer-oriented:

> Help developers understand the state of a table before escalating the issue to a DBA.

For every schema and table, the view displays:

- table size;
- index size;
- estimated row count;
- dead tuple count and percentage;
- tuples modified since the last analyze;
- update activity;
- HOT update percentage;
- latest manual vacuum;
- latest autovacuum;
- latest manual analyze;
- latest autoanalyze;
- vacuum age;
- analyze age;
- database statistics reset timestamp.

Tables are classified using statuses such as:

- `HEALTHY`;
- `ANALYZE_DUE`;
- `NEVER_ANALYZED`;
- `HIGH_DEAD_TUPLES`.

Users can filter, search, sort, and inspect tables immediately.

They can also launch:

```sql
ANALYZE schema.table;
```

or:

```sql
VACUUM (ANALYZE) schema.table;
```

through the existing SQL execution endpoint, with a confirmation dialog showing the exact command and execution result.

---

## Collector and Grafana integration

Version 2.9.0 added two API endpoints used by:

- [pgAssistant Collector](https://github.com/beh74/pgassistant-collector)
- [pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)

This allows pgAssistant findings to be collected over time and visualized across multiple PostgreSQL instances.

The integration makes it possible to build fleet-level views such as:

- recommendation evolution;
- database design issues;
- maintenance risks;
- corrected findings;
- PostgreSQL version exposure;
- environment-level comparisons.

---

## Broader schema coverage

Several Global Advisor rules were unintentionally limited to:

```sql
n.nspname = 'public'
```

This meant that databases using application-specific schemas could be only partially analyzed.

The rules now inspect all user schemas while excluding:

- `pg_catalog`;
- `information_schema`;
- `pg_toast`;
- temporary schemas;
- temporary TOAST schemas.

This bug fix affects several important checks, including:

- foreign-key type mismatches;
- missing foreign-key indexes;
- duplicate indexes;
- redundant indexes;
- unused indexes.

---

## Additional fixes and compatibility improvements

Other changes since version 2.8 include:

- support for the Qwen 3.6 model;
- a fix for a missing `re` import during parameter extraction;
- improved connection-form behavior when using a PostgreSQL connection URI;
- automatic parsing of URI fields before browser validation.

These fixes improve both model compatibility and the initial connection experience.

---

## A clearer direction for pgAssistant

The releases since version 2.8 reflect a broader direction for the project.

pgAssistant is not intended to replace PostgreSQL DBAs.

Instead, it aims to help developers:

- understand PostgreSQL behavior;
- identify the most important problems;
- distinguish strong evidence from weak signals;
- generate safer remediation commands;
- collect the context required before involving a DBA.

The product increasingly combines two complementary approaches:

1. **A deterministic expert system**, based on PostgreSQL catalogs, statistics, configuration, and execution plans.
2. **AI-assisted explanations**, used to summarize findings and make complex PostgreSQL behavior easier to understand.

The goal is not to automate every database decision.

The goal is to make PostgreSQL diagnostics more transparent, more explainable, and more actionable.

---

## Links

- [pgAssistant Community on GitHub](https://github.com/beh74/pgassistant-community)
- [pgAssistant Collector](https://github.com/beh74/pgassistant-collector)
- [pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)