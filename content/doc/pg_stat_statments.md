---
title: "Enable pg_stat_statements module"
date: 2025-07-24
tags: ["Docker","Postgres"]
draft: false
---

# How to do it

pg_stat_statements is required by pgAssistant. If you are not familiar with this module, you can find [here](https://www.postgresql.org/docs/current/pgstatstatements.html) the official Postgres documentation.

To enable this module, add this option on the command that runs Posgres : 

```
shared_preload_libraries='pg_stat_statements'
```
Then, connect to the database and run this command :
```
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

(When you run pgAssistant, he will execute this SQL Statements)

# If you run Postgresql in a docker environment

Here is a sample docker-compose file that enables the module : 

```
services:
  demo-db:
    restart: always
    image: postgres:17
    environment:
      - POSTGRES_USER=demo
      - POSTGRES_PASSWORD=demo
      - POSTGRES_DB=demo
    command: >
        postgres
        -c shared_preload_libraries='pg_stat_statements'
        -c max_connections=200
        -c shared_buffers='512MB'
        -c effective_cache_size='1536MB'
        -c maintenance_work_mem='128MB'
        -c checkpoint_completion_target=0.9
        -c wal_buffers='16MB'
        -c default_statistics_target=100
        -c random_page_cost=1.1
        -c effective_io_concurrency=200
        -c work_mem='1310kB'
        -c huge_pages='off'
        -c min_wal_size='1GB'
        -c max_wal_size='4GB'
        -c max_worker_processes=4
        -c max_parallel_workers_per_gather=2
        -c max_parallel_workers=4
        -c max_parallel_maintenance_workers=2
     
    ports:
      - 5432:5432
```

