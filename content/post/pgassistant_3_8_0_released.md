---
title: "pgAssistant 3.8.0: Closing the Continuous Improvement Loop"
date: 2026-09-09
tags: ["pgAssistant", "Release", "PostgreSQL", "Workload Insights"]
description: "pgAssistant 3.8.0 introduces Workload Insights to connect PostgreSQL changes, recommendation history, and measured workload results."
draft: false
---

![pgAssistant 3.8.0 release](/pgassistant-blog/images/release.png)

# pgAssistant 3.8.0 is released

pgAssistant 3.8.0 marks an important step in the product's evolution into **a continuous PostgreSQL improvement platform**.

The release introduces **Workload Insights**, improves Executive Plan history, and records PostgreSQL environment changes alongside workload measurements. pgAssistant can now help teams move beyond producing recommendations: it connects what was observed, what changed, and what happened to the workload afterward.

```text
Observe → Diagnose → Prioritize → Plan → Implement → Collect again → Measure
   ↑                                                                  │
   └────────────────────────── Repeat continuously ────────────────────┘
```

## Workload Insights

Workload Insights explores the periodic measurements stored by **pgAssistant Collector** and compares each collection with its predecessor.

It brings several signals into one historical view:

- total execution time and call-volume evolution;
- changes in workload and query mix;
- the queries responsible for the largest gains and regressions;
- Executive Plan recommendation changes;
- PostgreSQL version upgrades;
- changes to important tuning settings.

The goal is not to replace real-time monitoring. Workload Insights is designed for comparison and decision-making: after a team implements an improvement, the next collection provides evidence of whether the workload became faster, shifted elsewhere, or needs further investigation.

## A more useful Executive Plan history

Executive Plan history now makes collection-to-collection changes easier to inspect. Selecting a point in the history displays the differences from the preceding collection.

Teams can distinguish between:

- **new findings**, which appeared in the latest evidence;
- **persistent findings**, which still require attention;
- **no-longer-detected findings**, which disappeared from the latest analysis.

This wording is deliberate. A finding that is no longer detected may indicate a successful implementation, but it may also result from a workload or environment change. Deployment confirmation remains explicit rather than inferred.

## PostgreSQL changes are part of the evidence

Executive Plan payloads now persist the detected PostgreSQL version and important tuning settings. Collector-backed comparisons can therefore show when an upgrade or configuration change occurred between two workload measurements.

This additional context matters when interpreting performance changes. A query improvement may coincide with an index deployment, a PostgreSQL upgrade, or a parameter change; Workload Insights helps make those relationships visible without claiming causation automatically.

## Safer pgTune recommendations on small instances

pgTune now clamps worker and parallel-worker settings to the CPU count supplied to the calculation. This is especially relevant for PostgreSQL instances limited to one or two CPUs, where generic recommendations could otherwise exceed the resources actually available.

## Ready for PostgreSQL pre-release versions

Version parsing and pgTune now accept PostgreSQL beta, release-candidate, and development version strings such as `19beta3`.

The release also adds PostgreSQL 19 parameter generation. Unreleased branches are treated as review-only: pgAssistant can analyze them without presenting their lifecycle status as if they were already production releases.

## The product direction

Earlier versions built the individual parts of the improvement workflow: deterministic advisors, workload ranking, the Executive Plan, Collector-backed recommendation history, and per-query execution history.

Version 3.8.0 connects those capabilities into a continuous loop:

1. collect PostgreSQL and workload evidence;
2. diagnose and prioritize improvements;
3. build an ordered plan for DEV and OPS;
4. implement selected changes;
5. collect again;
6. compare the result and decide what to improve next.

That is the new pgAssistant promise: not simply finding PostgreSQL issues, but helping teams manage a repeatable, evidence-based improvement process.

## Get pgAssistant 3.8.0

Pull the latest Docker image:

```bash
docker pull bertrand73/pgassistant:latest
```

Then follow the [Docker quick-start guide](/pgassistant-blog/doc/startup_docker/) or explore the source in the [pgAssistant Community repository](https://github.com/beh74/pgassistant-community).

