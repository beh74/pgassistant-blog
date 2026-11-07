---
title: "Run pgAssistant with Docker"
description: "Start Community in minutes, connect your PostgreSQL database, and extend your setup with Collector, Grafana, and Auto-Tune."
date: 2025-01-10
tags: ["Docker", "Getting started"]
draft: false
---

{{< docker-start >}}

## Before you start

You need Docker with the Compose plugin and a PostgreSQL database reachable from the container. Enable **pg_stat_statements** on the database you want to analyze: follow the [extension setup guide]({{< ref "/doc/pg_stat_statments.md" >}}).

**AI is optional.** You can start with the deterministic advisors and add an OpenAI-compatible endpoint later.

## 1. Create your Compose file

Create a folder for your installation and save the following as `compose.yaml`:

```yaml
services:
  pgassistant:
    image: bertrand73/pgassistant:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:5005"
    environment:
      SECRET_KEY: ${SECRET_KEY:?Set SECRET_KEY in .env}
      # Optional: connect to a Collector repository.
      # COLLECTOR_URI: ${COLLECTOR_URI}
      # Optional: protect the /api/v2 endpoints with a bearer token.
      # PGA_API_TOKEN: ${PGA_API_TOKEN}
    # Optional: mount an existing custom query file.
    # volumes:
    #   - ./myqueries.json:/home/pgassistant/myqueries.json:ro
```

In the same folder, create a `.env` file and set `SECRET_KEY` to a long random value. For example, generate the file with:

```bash
# Run once when setting up a new installation.
printf 'SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > .env
```

Keep this value stable between restarts and keep `.env` out of version control.

This example adapts the [Community Compose file](https://github.com/beh74/pgassistant-community/blob/main/docker-compose/docker-compose.yml). It uses the published image instead of the local `test:0` image in the checked-out example, leaves integrations optional, and binds the web interface to localhost.

## 2. Start and connect

From the folder containing `compose.yaml`:

```bash
docker compose up -d
docker compose logs -f pgassistant
```

Open **[http://localhost:8080](http://localhost:8080)** and enter the connection details for the PostgreSQL database you want to analyze.

The database address must be reachable **from inside the container**:

- **Database on your computer:** use `host.docker.internal` on Docker Desktop.
- **Database in the same Compose network:** use its service name and internal port, such as `postgres:5432`.
- **Remote database:** use its reachable hostname, port, and appropriate credentials.

On Linux Docker Engine, add the following under the `pgassistant` service if you need to reach the host:

```yaml
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

## 3. Add the options you need

### Local AI with Ollama

To use Ollama running on your computer, add these entries to the service's `environment` section:

```yaml
      OPENAI_API_KEY: nothing
      OPENAI_API_MODEL: gpt-oss:20b
      LOCAL_LLM_URI: http://host.docker.internal:11434/v1/
      LLM_SQL_GUIDELINES: https://raw.githubusercontent.com/beh74/pgassistant-blog/refs/heads/main/content/post/sql-guide.md
```

Install the chosen model in Ollama first. `OPENAI_API_MODEL` must match its name exactly; `gpt-oss:20b` is the model shown in the Community Compose example. Choose a model your machine can run.

Ollama must accept connections from the container. The Community example suggests setting `OLLAMA_HOST=0.0.0.0:11434` before running `ollama serve`; limit access to trusted hosts with your network configuration. `nothing` is a placeholder token for the local API, not an OpenAI API key.

Apply environment changes with `docker compose up -d`.

### Collector history

Enable `COLLECTOR_URI` in your Compose file and add the repository connection string to `.env`:

```dotenv
COLLECTOR_URI=postgresql://collector_reader:replace_me@host.docker.internal:5433/pga_collector
```

Use credentials valid for your repository. Port `5433` is the host port exposed by the Collector Compose example. This connects Community to the **PostgreSQL repository**, rather than to the Collector HTTP service.

### Custom queries and API access

| Setting | When to use it |
| --- | --- |
| `SECRET_KEY` | Stable secret for application sessions. |
| `PGA_API_TOKEN` | Optional bearer token protecting `/api/v2` endpoints. Empty or unset leaves these endpoints without token authentication. |
| `COLLECTOR_URI` | PostgreSQL connection string for the Collector repository. |
| `OPENAI_API_KEY` | Token for your selected AI endpoint; a placeholder for local Ollama. |
| `OPENAI_API_MODEL` | Model available from that endpoint. |
| `LOCAL_LLM_URI` | URL of the OpenAI-compatible endpoint, reachable from the container. |
| `LLM_SQL_GUIDELINES` | Optional URL of your SQL guidelines in Markdown. |

For your own saved queries, create `myqueries.json` before enabling the volume mount. See the [custom queries guide]({{< ref "/doc/myqueries.md" >}}). The file is optional for starting pgAssistant.

## Extend your Docker setup

Start with Community for a single database. Add Collector for historical evidence, Grafana for a fleet overview, and Auto-Tune for policy-controlled execution.

{{< docker-projects >}}

The companion files reference configuration folders, provisioning files, or environment files. **Clone the corresponding repository and follow its README**, rather than downloading only its Compose file. These are separate Compose projects; adapt their hostnames and credentials when connecting them.

## Everyday commands

```bash
# Check service status.
docker compose ps

# Follow application logs.
docker compose logs -f pgassistant

# Pull the latest image and recreate the service.
docker compose pull
docker compose up -d

# Stop and remove this installation's containers and network.
docker compose down
```

## Troubleshooting

**The web page does not open.** Check `docker compose ps` and the logs. If port `8080` is already in use, change the host port to `127.0.0.1:8082:5005`, then open `http://localhost:8082`.

**The database connection fails.** Check its hostname from the container's perspective. `localhost` inside pgAssistant refers to the pgAssistant container itself. Also check PostgreSQL connection permissions and network access.

**Workload statistics are unavailable.** Verify that `pg_stat_statements` is loaded and created in the target database, then allow the workload to generate statistics.

**Ollama cannot be reached.** Check the endpoint URL, listening address, network access, and installed model name. Deterministic analysis remains available without AI.

## Build your own image

To build from the Community source:

```bash
git clone https://github.com/beh74/pgassistant-community.git
cd pgassistant-community
docker build -t mypgassistant:local .
```

Set `image: mypgassistant:local` in your Compose file, then run `docker compose up -d`.
