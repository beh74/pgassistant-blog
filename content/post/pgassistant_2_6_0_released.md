---
title: "pgAssistant 2.6 is released !"
date: 2026-03-29
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

### Features

- Introduced **SQL Advisor**, a new **safe-by-design** advisor focused on SQL query analysis and guidance.
  It is designed to provide helpful recommendations while staying conservative and avoiding risky automated actions.

### Improved

- Top queries are now displayed as **cards**, making them easier to scan, compare, and review visually.

## New docker image is available on dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/bertrand73/pgassistant/tags)

```bash
docker pull bertrand73/pgassistant:latest
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.