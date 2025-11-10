---
title: "Startup pgAssistant with docker"
date: 2025-01-10
tags: ["Docker"]
draft: false
---

# Before you begin

You must enable the **pg_stat_statements** module on your postgres database. [Here is a documentation]({{< ref "/doc/pg_stat_statments.md" >}}) 

# Using bertrand73/pgassistant docker image

Here is a sample docker-compose.yml file to run pgassistant :

```
services:
  pgassistant:
    image: bertrand73/pgassistant:latest
    restart: always
    environment:
      - OPENAI_API_KEY=nothing
      - OPENAI_API_MODEL=codestral:latest
      - LOCAL_LLM_URI=http://host.docker.internal:11434/v1/
      - LLM_SQL_GUIDELINES=https://raw.githubusercontent.com/beh74/pgassistant-blog/refs/heads/main/content/post/sql-guide.md
      - SECRET_KEY=mySecretKey4PgAssistant
    ports:
      - "8080:5005"
    volumes:
      - ./myqueries.json:/home/pgassistant/myqueries.json
```

The file myqueries.json is not necessary to run pgAssistant, but it should be usefull. Please read the doc [here]({{< ref "/doc/myqueries.md" >}})

### Envrionment variables

| Variable           | Description                                              | Example value                                    |
|--------------------|----------------------------------------------------------|--------------------------------------------------|
| `OPENAI_API_KEY`   | Dummy key (required by clients expecting a token)        | `nothing`                                        |
| `OPENAI_API_MODEL` | Model identifier to use with the API                     | `codestral:latest` or `mistral:latest`           |
| `LOCAL_LLM_URI`    | Local endpoint URL for the OpenAI-compatible API         | `http://host.docker.internal:11434/v1/`          |
| `SECRET_KEY`       | Used to encrypt some htttp session variables.            | `mySecretKey4PgAssistant`                        |
| `LLM_SQL_GUIDELINES`       | An URL pointing on your SQL Guidelines.            | `https://raw.githubusercontent.com/beh74/pgassistant-blog/refs/heads/main/content/post/sql-guide.md`                        |

### Notes

- `OPENAI_API_KEY` is required by most clients but not used when querying local LLMs like **Ollama**. You can set it to any placeholder (e.g. `nothing`).
- `OPENAI_API_MODEL` must match the model name loaded in Ollama (e.g. `codestral`, `llama3`, `mistral`, etc.).
- `LOCAL_LLM_URI` should point to the Ollama server, accessible from inside your Docker container via `host.docker.internal`.
- `LLM_SQL_GUIDELINES` should point to your SQL Guidelines like namings conventions. A markdown format is recommanded.
---

# How to build your docker image

Simply clone the repo and then build your own image like this :

```bash
git clone https://github.com/beh74/pgassistant-community.git
cd pgassistant
docker build . -t mypgassistant:1.0
``` 

# Security Highlights

-	Small attack surface – Lightweight Alpine base with only required packages.
-	Non-root execution – Runs as pgassistant user by default.
-	No caches – Installs packages with --no-cache to prevent stale data.
-	Isolated environment – Uses a dedicated virtualenv inside the container.
-	Regular CVE scans – Automated security scans with Grype & Docker Scout.

