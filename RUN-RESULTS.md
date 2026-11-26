# Run Results (real)

End-to-end live run, topic "Retrieval-augmented generation"
(Wikipedia APIs, full plaintext articles):

- research facets planned: 5 (overview, history, methods, applications, limitations)
- sources found: 5/5 (100% coverage), live fetch run 13.4s; cached reruns <1s
- critic first-try pass: 5/5 on the final recipe (an earlier recipe needed 1 revision; the loop works and is exercised in tests)
- output: results/sample_report.docx (real export, 5 cited sections)
- tests: 5/5 passing (offline, researcher stubbed; writer abstention, critic flags, pipeline metrics)

Honest limits: English Wikipedia only; extractive summaries (sentences quoted
from sources, not free generation) - chosen deliberately so no claim in a
report is ungrounded. Rate-limited politely (1.2s pacing, backoff, local cache).

Reproduce: python -m src.api, POST /run {"topic": "..."}, or
    python -c "from src import pipeline; print(pipeline.run('your topic')['metrics'])"
