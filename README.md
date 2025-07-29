# pgAssistant Blog

This is the [Hugo](https://gohugo.io/) static site that powers the official blog of **pgAssistant**, a PostgreSQL-first assistant designed to improve query performance using LLMs.

📍 **Live site**: [https://beh74.github.io/pgassistant-blog/](https://beh74.github.io/pgassistant-blog/)

---

## About the Blog

This blog shares use cases, tutorials, and articles around:

- `pgAssistant` and how to use it effectively
- PostgreSQL optimization techniques
- LLM Models

---

##  Built With

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