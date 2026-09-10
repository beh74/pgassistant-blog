# pgAssistant Documentation and Blog

This [Hugo](https://gohugo.io/) static site hosts the official documentation and blog for **pgAssistant — a continuous PostgreSQL improvement platform**.

pgAssistant turns PostgreSQL evidence into prioritized action: it helps teams analyze databases and workloads, build an actionable remediation plan, track changes over time, and measure whether the workload actually improved. It can be used for a single database or extended with the pgAssistant Collector and Grafana projects to support a fleet of thousands.

AI assistance is optional. The core advisors are deterministic and can be used without an LLM.

📍 **Live site**: [https://beh74.github.io/pgassistant-blog/](https://beh74.github.io/pgassistant-blog/)

---

## About This Site

The site documents the continuous improvement loop supported by pgAssistant:

```text
Observe → Diagnose → Prioritize → Plan → Implement → Collect again → Measure
   ↑                                                                  │
   └────────────────────────── Repeat continuously ────────────────────┘
```

It includes:

- installation and configuration guides;
- tutorials for analyzing SQL, schemas, indexes, PostgreSQL parameters, and maintenance;
- guidance for turning advisor findings into an ordered Executive Plan;
- articles about workload prioritization, historical comparison, and result measurement;
- documentation for single-database and fleet-wide workflows;
- optional AI-assisted analysis and explanations.

pgAssistant complements real-time monitoring platforms: it uses periodic database and workload evidence to drive a repeatable improvement process.

---

## Built With

- [Hugo](https://gohugo.io/) — Static site generator
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) — Clean, responsive Hugo theme
- [GitHub Pages](https://pages.github.com/) — Hosting
- [GitHub Actions](https://github.com/features/actions) — CI/CD for deployment

---

## Run Locally

Make sure you have [Docker](https://docs.docker.com/get-docker/) installed.

```bash
git clone https://github.com/beh74/pgassistant-blog.git
cd pgassistant-blog
docker compose up
```

## Edit or Contribute

Feel free to open an issue or submit a pull request if you’d like to suggest changes or improvements.
Each blog post provides a “Suggest Changes” link that takes you directly to the GitHub source.

## Deployment

The site is automatically deployed to GitHub Pages using a GitHub Actions workflow.
Any push to the main branch triggers a rebuild and redeploy.
