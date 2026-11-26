"""Offline tests: planner/writer/critic logic + pipeline with a stubbed researcher."""
from src import pipeline
from src.agents import plan, write_section, critique

FAKE = {"title": "Test Page", "url": "https://en.wikipedia.org/wiki/Test",
        "extract": "Retrieval augmented generation combines search with language models. "
                   "It grounds answers in retrieved documents to reduce hallucination. "
                   "The method was introduced by Facebook AI Research in 2020."}

def _item():
    return {"facet": "Methods", "facet_query_terms": "methods techniques", "topic": "RAG",
            "source": FAKE}

def test_planner_returns_five_facets():
    tasks = plan("any topic")
    assert len(tasks) == 5 and all(t["topic"] == "any topic" for t in tasks)
    assert tasks[0]["facet"] == "Overview"

def test_writer_uses_only_source_text():
    sec = write_section(_item(), set())
    assert sec["draft"] and "(Source:" in sec["draft"]
    assert "search" in sec["draft"].lower() or "model" in sec["draft"].lower()

def test_writer_abstains_without_source():
    it = _item(); it["source"] = None
    assert write_section(it, set())["draft"] is None

def test_critic_flags_uncited_and_thin():
    ok, issues = critique({"draft": "short"})
    assert not ok and issues
    ok, _ = critique({"draft": " ".join(["word"] * 20) + " (Source: X.)"})
    assert ok

def test_pipeline_with_stubbed_research(monkeypatch):
    monkeypatch.setattr(pipeline, "research",
                        lambda tasks: [dict(_item(), facet=t["facet"], topic=t["topic"]) for t in tasks])
    res = pipeline.run("retrieval-augmented generation")
    m = res["metrics"]
    assert m["sources_found"] == m["questions"] == 5
    assert m["source_coverage"] == 1.0
    assert all(s.get("draft") for s in res["sections"])
