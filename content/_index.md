---
title: "Welcome to pgAssistant"
description: "A PostgreSQL assistant combining deterministic analysis and optional AI to understand and optimize database performance."
---

![logo](images/logo.png)

**pgAssistant** helps you design your schema, understand and optimize PostgreSQL database performance.

---

## Deterministic First, AI When Needed

pgAssistant is built on a simple principle:

> **Start with deterministic database analysis.  
> Use AI only when it adds value.**

### Deterministic Analysis (Core Engine)

pgAssistant directly queries PostgreSQL system catalogs to produce **reliable and reproducible diagnostics**.

With **pgAssistant v2.8**, this is now unified into the **Global Advisor**:

- **One-click full database analysis**
- Prioritized recommendations with:
  - Ranking  
  - Confidence  
  - Impact  
  - Effort  
- Detection of structural issues:
  - Missing indexes on foreign keys  
  - Datatype inconsistencies  
  - Redundant / unused indexes  
  - Index coverage gaps  
  - Schema design problems  

No AI. No guesswork. Just PostgreSQL truth.

---

### Query-Level Analysis

For deeper performance tuning, pgAssistant analyzes real execution plans:

- `EXPLAIN ANALYZE` insights  
- Index recommendations  
- Join and scan optimization  
- Query rewrite hints  

---

### AI (Optional Layer)

AI is available as an **augmentation layer**, not a dependency:

- Query rewrite suggestions  
- Advanced optimization reasoning  
- Naming conventions & RFC checks  

You can use pgAssistant **fully without AI**.

---

## Try It Online

Live demo:  
https://ov-004f8b.infomaniak.ch/

Demo connection: postgresql://postgres:demo@demo-db:5432/northwind

⚠️ The public demo does NOT use an LLM  
⚠️ Do not provide personal API keys  

---

## Why pgAssistant?

- Open-source  
- Built specifically for PostgreSQL  
- Combines deterministic analysis with optional AI  
- Focused on **actionable performance improvements**, not just metrics  

Explore the documentation, blog posts, or the  
[GitHub repository](https://github.com/beh74/pgassistant-community)

---

## Before you begin

Read this documentation:

- [Enable pg_stat_statements](doc/pg_stat_statments)  
- [Quick start with docker](doc/startup_docker)  

---

## Complementary Tools for Working with pgAssistant

While **pgAssistant** focuses on query optimization and schema analysis, it is **not a monitoring tool**.

For real-time metrics and observability, we recommend:

- **[pgWatch](https://github.com/cybertec-postgresql/pgwatch)**  

Why pgWatch?

- Built with **Go** → fast and efficient  
- **Docker-based** deployment → easy setup  
- Uses **Grafana** and **Prometheus** for visualization and alerting  

> pgWatch monitors your database.  
> pgAssistant helps you fix it.