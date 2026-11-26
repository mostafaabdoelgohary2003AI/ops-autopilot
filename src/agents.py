"""Planner / Writer / Critic agents - deterministic, honest, offline-capable.

No fake LLM calls: each agent is explicit, inspectable logic operating on the
real fetched sources. An optional external LLM can be plugged into the writer,
but the default pipeline runs fully offline so results are reproducible."""
import re

STOP = {"the","a","an","of","in","on","and","or","to","for","with","is","are","was","were",
        "what","how","why","which","who","whom","does","do","did","it","its","their","his","her"}

FACETS = [("Overview", "definition overview"),
          ("History", "history development origin"),
          ("Methods", "methods techniques how it works"),
          ("Applications", "applications uses adoption industry"),
          ("Limitations", "limitations criticism challenges risks")]
FACET_TERMS = {
    "Overview": "technique model models system approach defined combines",
    "History": "introduced developed first proposed history originally researchers paper",
    "Methods": "works uses retrieves documents query embedding vector database combine generation",
    "Applications": "used applications chatbots companies adoption industry deployed products",
    "Limitations": "however limitations criticism challenges risks may can fail hallucination cost latency",
}

def keywords(text, k=8):
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text)]
    freq = {}
    for w in words:
        if w not in STOP:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: -kv[1])[:k]]

def plan(topic, n_questions=5):
    """Planner: turn a topic into focused research tasks (deterministic facets)."""
    return [{"facet": f, "query": f"{topic} {q}", "topic": topic} for f, q in FACETS[:n_questions]]

def split_sentences(text):
    text = re.sub(r"==+[^=]*==+", " ", text)  # strip wiki section headers
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if 4 < len(s.split()) < 60]

def extract_key_sentences(text, facet, topic_terms, used, k=2):
    """Pick sentences relevant to THIS facet (not just the topic), skipping
    sentences already used by another section."""
    fw = set(FACET_TERMS.get(facet, "").split())
    tw = set(w.lower() for w in topic_terms.split() if len(w) > 3)
    sents = split_sentences(text)
    def score(s):
        ws = set(w.lower().strip('.,();') for w in s.split())
        return 2 * len(fw & ws) + len(tw & ws)
    ranked = sorted(sents, key=lambda s: -score(s))
    picked = []
    for s in ranked:
        if s not in used and score(s) > 0:
            picked.append(s); used.add(s)
        if len(picked) == k:
            break
    return picked

def write_section(item, used_sentences):
    """Writer: draft a section strictly from the fetched source; never invent facts."""
    src = item["source"]
    if not src:
        return {"facet": item["facet"], "draft": None, "note": "no source found"}
    texts = [src["extract"]] + ([item["extra"]["extract"]] if item.get("extra") else [])
    sents = []
    for tx in texts:
        sents = extract_key_sentences(tx, item["facet"], item["topic"], used_sentences)
        if len(sents) >= 2:
            break
    if not sents:
        sents = split_sentences(src["extract"])[:1]
    draft = " ".join(sents) + f" (Source: {src['title']}, Wikipedia.)"
    return {"facet": item["facet"], "draft": draft, "source_title": src["title"], "url": src["url"]}

def critique(section):
    """Critic: score a draft on grounding signals; returns (ok, issues)."""
    issues = []
    d = section.get("draft")
    if not d:
        return False, ["empty draft"]
    if len(d.split()) < 12:
        issues.append("too thin (<12 words)")
    if "(Source:" not in d:
        issues.append("missing citation")
    vague = [w for w in ("important", "interesting", "various", "many people think") if w in d.lower()]
    if vague:
        issues.append("vague wording: " + ", ".join(vague))
    return not issues, issues
