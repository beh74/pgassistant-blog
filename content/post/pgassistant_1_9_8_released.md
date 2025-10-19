---
title: "pgAssistant 1.9.9 is released !"
date: 2025-10-13
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

This release is coming with this news features :

- pgTune : docker-compose yaml file is using a healthcheck and the shm_size parameter
- pgTune : a Kubernetes deployment descriptor has been added


## New docker image is available on dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/bertrand73/pgassistant/tags)

```bash
docker pull bertrand73/pgassistant:1.9.8
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.