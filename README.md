<p align="center"><img src="assets/logo.png" width="128" alt="ops-autopilot logo"></p>

# Ops Autopilot — multi-agent research-ops report generator

One topic in, a cited DOCX report out. Five specialized agents run in sequence:
**Planner** decomposes the topic into research facets, **Researcher** fetches real
sources from the live Wikipedia APIs, **Writer** drafts sections strictly from the
fetched text (it cannot invent facts by construction), **Critic** scores each draft
(citation present, substance, no vague wording) and triggers a revise loop, and
**Publisher** exports a formatted `.docx`.

- FastAPI web UI + JSON API; run history persisted in Postgres (Docker Compose) or SQLite locally, with SQL migrations
- Offline-capable: responses are cached, tests stub the network, the pipeline is deterministic given the same sources
- Docker + docker-compose + GitHub Actions CI; 5/5 tests pass

## Run
    pip install -r requirements.txt
    python -m pytest -q
    uvicorn src.api:app --reload            # http://localhost:8000
    # or with Postgres: docker compose up --build

## Design notes
The agents are explicit, inspectable Python rather than black-box LLM calls, so
every number in RUN-RESULTS.md is reproducible and every sentence in a report
traces to a fetched source. The writer can optionally use a hosted LLM (see below); the default run stays
offline and extractive.

Built with AI pair-programming; all runs and metrics are real.


## Real LLM writer (Gemini API free tier)
Set `LLM_API_KEY` (environment only, never committed; optional `LLM_BASE_URL`, `LLM_MODEL`, default `gemini-3.1-flash-lite`) and the Writer rewrites each section from the fetched Wikipedia text. It may use only facts in that text: a draft that introduces a number not in the source is rejected and the extractive text is used instead. The Critic runs on every draft as before.

Measured Nov 26, 2026 on the topic "Retrieval-augmented generation" (live Wikipedia + hosted LLM, one run): 5 of 5 sections written by the LLM, 5 of 5 passed the Critic first try, 31.5 s end to end (an earlier run took 45.6 s; free-tier latency varies). Limits: the Critic checks length, citation and vague wording, not factual accuracy, and the number guard only catches invented digits. In this run all 5 sections came from a single Wikipedia article (distinct_sources = 1), so coverage is shallow. The first run echoed section headings into two drafts, which is why the writer now strips them.
