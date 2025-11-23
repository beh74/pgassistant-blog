---
title: "pgAssistant 2.1 is released !"
date: 2025-11-23
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

- **Code Suggestions Section**  
  When pgAssistant generates recommendations, the form now includes a dedicated **“Code suggestions”** section grouping all actionable statements.  
  A convenient **“Copy”** button lets users export them instantly.  
  *(Thank you Manon for the great idea!)*

- **Bgwriter & Checkpointer Insights**  
  The reporting API now exposes **pg_stat_bgwriter** (and pg_stat_checkpointer for PG17+) metrics along with detailed recommendations to improve checkpoint and background writer performance.

- **Database Uptime on Dashboard**  
  The main dashboard now displays the database uptime, with a clean human-readable format.

- **Shared Buffers Display + pgTune Link**  
  The dashboard shows the current `shared_buffers` value and provides a quick link to **pgTune** to help tune memory settings.

- **DDL & Utility Queries on Profile Page**  
  The main dashboard (database profile) now includes a curated set of **DDL and maintenance queries** to help assess and understand a database instance quickly.

- **Support for Standard PostgreSQL Connection URI**  
  The connection form now accepts **PostgreSQL URI strings**  
  (e.g. `postgresql://user:password@host:port/dbname`)  
  and automatically fills all connection fields.

- **Unused Index Detection Improved**  
  The “unused indexes” analysis now **excludes indexes supporting primary keys or unique constraints**, preventing false positives.

- **New Statistics Reset Endpoint**  
  The API includes a new endpoint to **reset PostgreSQL statistics**, useful for baselining or performance tests. POST end point : /api/v1/pg_stat_statements_reset


## New docker image is available on dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/bertrand73/pgassistant/tags)

```bash
docker pull bertrand73/pgassistant:latest
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.