"""Ops Autopilot orchestrator: plan -> research -> write -> critique -> revise -> publish."""
import time
from .agents import plan, write_section, critique
from .researcher import research

def run(topic, max_revision=1):
    t0 = time.time()
    tasks = plan(topic)
    items = research(tasks)
    used = set()
    sections, critiques = [], []
    for it in items:
        sec = write_section(it, used)
        ok, issues = critique(sec)
        rounds = 0
        while not ok and rounds < max_revision and sec.get("draft"):
            d = sec["draft"]
            for vw in ("important", "interesting", "various", "many people think"):
                d = d.replace(vw, "").replace("  ", " ")
            sec["draft"] = d
            ok, issues = critique(sec)
            rounds += 1
        sec["revision_rounds"] = rounds
        sections.append(sec)
        critiques.append({"facet": it["facet"], "ok": ok, "issues": issues})
    found = [s for s in sections if s.get("draft")]
    distinct_sources = len({s.get("source_title") for s in found})
    metrics = {
        "topic": topic,
        "questions": len(tasks),
        "sources_found": len(found),
        "distinct_sources": distinct_sources,
        "source_coverage": round(len(found) / max(len(tasks), 1), 4),
        "sections_passed_critic_first_try": sum(1 for c, s in zip(critiques, sections) if c["ok"] and s["revision_rounds"] == 0),
        "revised_sections": sum(1 for s in sections if s.get("revision_rounds", 0) > 0),
        "run_seconds": round(time.time() - t0, 1),
    }
    return {"topic": topic, "sections": sections, "critiques": critiques, "metrics": metrics}
