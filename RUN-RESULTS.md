# Run Results (real, single runs)

## Live run with the hosted LLM writer (Nov 26, 2026)
Topic "Retrieval-augmented generation", live Wikipedia APIs, writer = Gemini free tier (`gemini-3.1-flash-lite`).
- research facets planned: 5 (overview, history, methods, applications, limitations)
- sections written by the LLM: 5/5; passed the Critic on the first try: 5/5; 31.5 s end to end (an earlier run took 45.6 s)
- distinct sources: **1**. All five sections were built from the same Wikipedia article, so the earlier "5/5 sources, 100% coverage" figure only meant that each facet found some text; coverage is shallow.
- The Critic checks length, citations and vague wording. It does not check factual accuracy; the number guard only catches invented digits.
- one run, not a benchmark

## Offline / extractive mode
The first version (no LLM) quoted sentences from the sources instead of writing new text. That mode is still the fallback when no `LLM_API_KEY` is set. Cached reruns take under a second, which is why `results/run_metrics.json` shows `run_seconds: 0.0`.

## Tests
5/5 pass offline (researcher stubbed): writer abstention, critic flags, pipeline metrics.

Honest limits: English Wikipedia only; rate-limited politely (1.2 s pacing, backoff, local cache).

Reproduce: `python -m src.api` and POST /run {"topic": "..."}, or
    python -c "from src import pipeline; print(pipeline.run('your topic')['metrics'])"
