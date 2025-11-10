---
title: "pgAssistant 2.0 is released !"
date: 2025-11-09
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

I’m excited to announce the release of **pgAssistant 2.0**, a major milestone for the project.
This new version marks a strategic shift toward API-first integration, making it easier to embed pgAssistant into existing workflows — from code review pipelines to production compliance checks.

The first available API in this release focuses on automated database health reporting.
It generates a Markdown report that provides :

	•	A global health overview of your PostgreSQL database
	•	Key performance and metrics
	•	Identified issues and improvement suggestions

Since its beginning, pgAssistant’s mission has been to help developers design better, faster, and more maintainable databases — while also providing educational insights, references, and explanations for every metric.

With version 2.0, the focus extends to operational integration:
you can now generate automated reports for all your PostgreSQL databases and, for example, store them in Git to track historical changes in your database design and health.

This release is a big step toward making pgAssistant a fully integrable AI assistant for PostgreSQL — not just a tool, but a collaborator in your database lifecycle.

The idea behind this new direction came after inspiring discussions during the [SwissPGDay](https://www.pgday.ch/2025/) and [PGConf Europe](https://wiki.postgresql.org/wiki/PGConf.EU_2025_PostgreSQL_AI_Summit)  events, where I had the chance to present pgAssistant and exchange with many passionate members of the PostgreSQL community.
This community is incredibly open, supportive, and full of ideas — I highly encourage everyone to join and take part in future events!

If you want to try the new database report API coming with v2.0 :
```
curl -X POST https://ov-004f8b.infomaniak.ch/api/v1/report \
  -H "Content-Type: application/json" \
  -d '{
    "db_config": {
      "db_host": "demo-db",
      "db_port": 5432,
      "db_name": "northwind",
      "db_user": "postgres",
      "db_password": "demo"
    }
  }'
```

## New docker image is available on dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/bertrand73/pgassistant/tags)

```bash
docker pull bertrand73/pgassistant:latest
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.