---
title: "pgAssistant 1.9.6 is released !"
date: 2025-07-30
tags: ["pgAssistant", "Release"]
draft: false
---

![Result](/pgassistant-blog/images/release.png)

This release is coming with this news features :

- Prefix all queries performed by pgAssistant with : /* launched by pgAssistant */ 
- Optimizing the issue "Indexe missing on foreign keys" by giving recommandations, depending on the size of the referenced table [documentation here](https://beh74.github.io/pgassistant-blog/doc/issue_index_fk/).
- Experimental : Add a vacuum query to try to optimize the default vacuum parameters for each table. See : [documentation here](https://beh74.github.io/pgassistant-blog/post/vaccum/)


## New docker image is available on Nexsol dockerhub

Take a look at DockerHub [image tag](https://hub.docker.com/r/nexsoltech/pgassistant/tags)

```bash
docker pull nexsoltech/pgassistant:1.9.6
```

Enjoy !

## Docker image security advices

No any security advice from github or docker scouts or Grype.

