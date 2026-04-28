---
title: "pgAssistant 2.8 is released !"
date: 2026-04-28
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

### Features

- Introduced **Global Advisor (initial version)**  
  A first implementation of a global analysis engine that aggregates multiple database signals (queries, schema, statistics) to provide higher-level recommendations.  
  This feature is experimental and will evolve in future releases with more advanced diagnostics and prioritization logic.


## New docker image is available on dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/bertrand73/pgassistant/tags)

```bash
docker pull bertrand73/pgassistant:latest
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.