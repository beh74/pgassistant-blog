---
title: "Managing More Than 1,000 PostgreSQL Databases with pgAssistant"
date: 2026-09-10
tags: ["pgAssistant", "PostgreSQL", "Fleet", "Docker", "Architecture"]
description: "A practical architecture for analyzing more than 1,000 PostgreSQL databases with one pgAssistant per environment and one central Collector and Grafana stack."
draft: false
---

# Managing more than 1,000 PostgreSQL databases with pgAssistant

Managing a PostgreSQL fleet at scale is not simply a matter of running the same diagnostic tool 1,000 times. Development, staging, and production have different access rules, risk profiles, owners, and workloads. At the same time, DEV, DBA, SRE, and OPS teams need one place to decide which databases require attention first.

A practical pgAssistant architecture separates **analysis by environment** while centralizing **collection, history, and fleet-wide visibility**:

- one pgAssistant instance for each environment or security boundary;
- one pgAssistant Collector for the entire organization;
- one PostgreSQL repository for historical results;
- one pgAssistant Grafana instance for the global fleet view.

```text
Development databases ──→ pgAssistant DEV ──────┐
                                                 │
Staging databases ──────→ pgAssistant STAGING ──┼──→ Collector ──→ Repository ──→ Grafana
                                                 │                      ↑
Production databases ───→ pgAssistant PROD ─────┘                      │
                                                                        │
                         Workload Insights and Executive Plan history ──┘
```

For Kubernetes deployments, the same principle can be applied as **one pgAssistant per cluster or environment**. If `n` environments represent `n` isolated security zones, deploy `n` pgAssistant instances and keep each one close to the databases it is allowed to analyze.

## Why deploy one pgAssistant per environment?

pgAssistant connects to PostgreSQL to inspect catalogs, statistics, settings, schemas, and execution plans. Placing an instance inside each environment preserves the existing security boundary:

- the production instance only receives production credentials and network access;
- development users and services do not need a route to production databases;
- Kubernetes NetworkPolicies, security groups, firewall rules, and secrets remain environment-specific;
- each environment can use its own PostgreSQL analysis role and credential rotation policy;
- a failure or configuration mistake in one zone does not automatically grant access to the others.

This design is especially useful when each environment runs in a separate Kubernetes cluster. pgAssistant can be deployed as a small internal service in each cluster, reachable by the central Collector through a private network, VPN, peering connection, or controlled ingress.

The pgAssistant API should not be exposed directly to the public internet. Restrict access to the Collector and authorized users at the network or reverse-proxy layer.

## Why use one Collector?

The Collector orchestrates periodic jobs against all declared databases and stores their results. Keeping one central Collector gives DEV and OPS a shared inventory and a consistent history across the whole fleet.

Each source can identify its:

- environment;
- application or target group;
- owner;
- database identity;
- pgAssistant instance;
- collection jobs.

The Collector can therefore send a development database to `pgassistant-dev`, a staging database to `pgassistant-staging`, and a production database to `pgassistant-prod`, while storing all results in the same repository.

Centralization does **not** mean removing isolation. The Collector must have only the network routes and credentials required for collection, and its API should remain private. Connection URIs and passwords are used at collection time but are not persisted in the repository.

## One global Grafana view for DEV and OPS

pgAssistant Grafana reads the central repository and provides the portfolio-level view that becomes essential beyond a few dozen databases.

Teams can filter the dashboards by environment, group, target, priority, advisor source, workstream, job type, run status, and DEV/OPS ownership. This makes it possible to answer questions such as:

- Which production databases have P1 findings?
- Which applications are responsible for the largest workload regressions?
- Which recommendations persist across several collections?
- Which databases failed their latest collection?
- What work belongs to DEV, OPS, or both?

Grafana should normally use a dedicated read-only PostgreSQL role. The pgAssistant instances should also use a read-only role when accessing Collector history for Workload Insights and Executive Plan comparisons.

## Design the source inventory for 1,000 databases

The Collector source file is the fleet inventory. Use stable target IDs and metadata that match the way responsibility is organized in the company.

```yaml
defaults:
  jobs:
    - rank_top_10_queries
    - executive_plan

sources:
  - id: billing-dev-primary
    name: Billing development
    enabled: true
    environment: development
    group: billing
    pgassistant_api_url: http://pgassistant.dev.internal:8080
    conn_str: postgresql://pgassistant:${BILLING_DEV_PASSWORD}@billing-dev.internal:5432/billing
    metadata:
      app: billing
      owner: payments-team

  - id: billing-staging-primary
    name: Billing staging
    enabled: true
    environment: staging
    group: billing
    pgassistant_api_url: http://pgassistant.staging.internal:8080
    conn_str: postgresql://pgassistant:${BILLING_STAGING_PASSWORD}@billing-staging.internal:5432/billing
    metadata:
      app: billing
      owner: payments-team

  - id: billing-prod-primary
    name: Billing production
    enabled: true
    environment: production
    group: billing
    pgassistant_api_url: http://pgassistant.prod.internal:8080
    conn_str: postgresql://pgassistant:${BILLING_PROD_PASSWORD}@billing-prod.internal:5432/billing
    metadata:
      app: billing
      owner: payments-team
```

Avoid using a single highly privileged PostgreSQL account across the fleet. Create purpose-specific analysis roles, scope secrets by environment, and inject passwords through your container or secrets platform rather than committing them to YAML.

For a large inventory, generate `sources.yaml` from the authoritative service catalog or infrastructure inventory. This prevents a manually maintained list from becoming a second, outdated source of truth.

## Control concurrency and collection frequency

A fleet of 1,000 databases does not imply 1,000 simultaneous analyses. The Collector supports bounded concurrency through `PGA_COLLECTOR_MAX_CONCURRENT_COLLECTS`.

Start conservatively, observe collection duration and database impact, and then adjust. Expensive jobs—especially a complete Executive Plan—should not be scheduled at the same frequency as lightweight workload ranking.

A sensible operating model is to:

1. distribute collections across a time window instead of creating a fleet-wide spike;
2. use a small concurrency limit initially;
3. collect lightweight rankings more frequently than complete plans;
4. use different schedules for development, staging, and production;
5. watch failed runs and response times in the Grafana Collection Runs dashboard;
6. increase concurrency only after measuring the effect on pgAssistant, the repository, and target databases.

The Collector exposes `POST /collect_all` to start an asynchronous fleet collection and `GET /runs/{job_id}` to inspect progress. A scheduler can call these endpoints, but they should remain available only on a trusted network.

## Keep history manageable with weekly partitions

The two high-volume repository tables are partitioned weekly by collection time:

- `pga_collection_payload`;
- `pga_ranked_query_snapshot`.

The default schema creates partitions for the previous week, the current week, and the following eight weeks. Additional partitions can be prepared with:

```sql
SELECT pga_create_weekly_partitions(CURRENT_DATE, 12, 1);
```

Old history can be removed efficiently by dropping complete weekly partitions. For example, retain approximately six months—26 weeks—of data:

```sql
SELECT pga_drop_partitions_older_than(26);
```

The same operation is available through the Collector API:

```bash
curl -X POST http://collector.internal:8081/repository/partitions/purge \
  -H "Content-Type: application/json" \
  -d '{"retain_weeks": 26}'
```

Dropping an old partition is much simpler and more predictable than deleting millions of historical rows individually. The purge function also removes matching old collection-run rows after their partitioned child rows have been dropped.

Choose the retention window according to collection frequency, audit requirements, repository storage, and the time horizon needed to compare workload changes. Automate both future partition creation and retention purges, and test backup and restore procedures before relying on retention jobs.

## A lightweight container architecture

pgAssistant and the Collector are stateless Python web services apart from configuration and small local cache files. Their persistent history lives in the Collector PostgreSQL repository. This makes them inexpensive to run compared with the databases they analyze and straightforward to scale or replace as containers.

CPU and memory usage depend on collection concurrency, SQL complexity, database size, and the selected jobs. Start with modest container limits, measure real collections, and resize from evidence. For a fleet of 1,000 databases, the repository and collection schedule usually deserve more capacity planning attention than the idle web services themselves.

Docker is the recommended deployment method because it provides:

- reproducible versions and simple upgrades;
- explicit configuration and network boundaries;
- health checks and restart policies;
- resource limits at the container or orchestrator level;
- persistent volumes only where they are needed.

## Docker Compose: one pgAssistant per environment

Deploy the following Compose project separately in development, staging, and production. Use environment-specific secrets and keep port `8080` on a private interface or behind an authenticated reverse proxy.

```yaml
services:
  pgassistant:
    image: bertrand73/pgassistant:3.8.0
    restart: unless-stopped
    environment:
      SECRET_KEY: ${PGASSISTANT_SECRET_KEY}
      COLLECTOR_URI: ${COLLECTOR_READ_ONLY_URI}
    ports:
      - "8080:5005"
    volumes:
      - pgassistant_data:/home/pgassistant/data
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:5005/ >/dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  pgassistant_data:
```

`COLLECTOR_READ_ONLY_URI` enables Executive Plan history and Workload Insights in the environment-local pgAssistant interface. Use a dedicated read-only repository role and a TLS connection when traffic crosses hosts or clusters.

If the exact version tag is not available in your registry, use the deployed release tag provided by Docker Hub or mirror the tested image into your internal registry. Avoid an uncontrolled `latest` tag in production.

## Docker Compose: central Collector, repository, and Grafana

The current Collector repository provides a Dockerfile rather than a published runtime image in its example Compose file. The stack below assumes this directory layout:

```text
pgassistant-stack/
├── docker-compose.yml
├── .env
├── pgassistant-collector/
│   ├── Dockerfile
│   ├── config/sources.yaml
│   └── sql/schema.sql
└── pgassistant-grafana/
    └── grafana/
```

Clone the Collector and Grafana repositories into these directories, then use:

```yaml
services:
  collector-repository:
    image: postgres:18
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 512MB
    environment:
      POSTGRES_DB: pga_collector
      POSTGRES_USER: pga_collector
      POSTGRES_PASSWORD: ${COLLECTOR_DB_PASSWORD}
      POSTGRES_INITDB_ARGS: --auth-local=scram-sha-256 --auth-host=scram-sha-256
    command: >
      postgres
        -c shared_preload_libraries='pg_stat_statements'
        -c autovacuum=on
        -c max_connections=50
        -c shared_buffers='128MB'
        -c effective_cache_size='384MB'
        -c maintenance_work_mem='32MB'
        -c checkpoint_completion_target=0.9
        -c wal_buffers='3932kB'
        -c default_statistics_target=100
        -c random_page_cost=1.1
        -c effective_io_concurrency=200
        -c work_mem='2621kB'
        -c min_wal_size='1GB'
        -c max_wal_size='4GB'
        -c huge_pages='off'
        -c max_worker_processes=2
        -c max_parallel_workers_per_gather=1
        -c max_parallel_workers=2
        -c max_parallel_maintenance_workers=1
    volumes:
      - collector_repository_data:/var/lib/postgresql/data
      - ./pgassistant-collector/sql/schema.sql:/docker-entrypoint-initdb.d/001_schema.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks:
      - pgassistant-central

  pgassistant-collector:
    build:
      context: ./pgassistant-collector
    restart: unless-stopped
    environment:
      PGA_COLLECTOR_DEFAULT_SOURCES_PATH: config/sources.yaml
      PGA_COLLECTOR_REQUEST_TIMEOUT_SECONDS: 300
      PGA_COLLECTOR_MAX_CONCURRENT_COLLECTS: ${COLLECTOR_CONCURRENCY:-4}
      PGA_COLLECTOR_REPOSITORY_DSN: postgresql://pga_collector:${COLLECTOR_DB_PASSWORD}@collector-repository:5432/pga_collector
      BILLING_DEV_PASSWORD: ${BILLING_DEV_PASSWORD}
      BILLING_STAGING_PASSWORD: ${BILLING_STAGING_PASSWORD}
      BILLING_PROD_PASSWORD: ${BILLING_PROD_PASSWORD}
    volumes:
      - ./pgassistant-collector/config:/app/config:ro
    depends_on:
      collector-repository:
        condition: service_healthy
    ports:
      - "127.0.0.1:8081:8081"
    networks:
      - pgassistant-central

  grafana:
    image: grafana/grafana:12.4
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_ADMIN_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_USERS_ALLOW_SIGN_UP: "false"
      PGASSISTANT_REPOSITORY_HOST: collector-repository
      PGASSISTANT_REPOSITORY_PORT: 5432
      PGASSISTANT_REPOSITORY_DATABASE: pga_collector
      PGASSISTANT_REPOSITORY_USER: pga_collector
      PGASSISTANT_REPOSITORY_PASSWORD: ${COLLECTOR_DB_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./pgassistant-grafana/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./pgassistant-grafana/grafana/dashboards:/var/lib/grafana/dashboards:ro
    depends_on:
      collector-repository:
        condition: service_healthy
    ports:
      - "3800:3000"
    networks:
      - pgassistant-central

networks:
  pgassistant-central:
    driver: bridge

volumes:
  collector_repository_data:
  grafana_data:
```

Store passwords in a local `.env` file for development and in Docker or Kubernetes secrets for production. Do not use the demonstration passwords from the project examples.

The repository is intentionally not published as a host port in this Compose file. If environment-local pgAssistant instances need direct access for Workload Insights, expose it only through a protected private address, create a dedicated read-only user, require TLS, and restrict inbound access to the pgAssistant environments.

## Production checklist

Before onboarding the full fleet:

- deploy one pgAssistant inside each security boundary;
- keep pgAssistant and Collector APIs private;
- use separate, least-privilege database roles and environment-scoped secrets;
- give Grafana and pgAssistant history access dedicated read-only repository roles;
- use stable target IDs plus environment, group, application, and owner metadata;
- start with bounded collection concurrency and stagger schedules;
- define weekly partition creation and retention jobs;
- persist and back up the Collector repository and Grafana data volumes;
- pin tested container versions and plan controlled upgrades;
- monitor collection failures, durations, repository growth, and target-database load.

## The result: isolation locally, visibility globally

The architecture deliberately separates two concerns:

- **pgAssistant stays local to each environment**, where database access and security can be controlled;
- **Collector and Grafana stay central**, where DEV and OPS can prioritize the entire PostgreSQL estate together.

This balance makes the design suitable for more than 1,000 databases without turning pgAssistant into another heavy monitoring platform. The services remain small, collection is scheduled and bounded, historical growth is controlled through partitions, and the organization gains one continuous improvement loop across every environment.

## Related projects

- [pgAssistant Community](https://github.com/beh74/pgassistant-community)
- [pgAssistant Collector](https://github.com/beh74/pgassistant-collector)
- [pgAssistant Grafana](https://github.com/beh74/pgassistant-grafana)
- [pgAssistant Docker installation guide](/pgassistant-blog/doc/startup_docker/)
