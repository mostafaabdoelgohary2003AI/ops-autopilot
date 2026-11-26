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
traces to a fetched source. An external LLM can be plugged into the writer
without changing the orchestration.

Built with AI pair-programming; all runs and metrics are real.

