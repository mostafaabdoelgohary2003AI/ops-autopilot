"""Researcher agent: fetches real facts from the public Wikipedia REST API."""
import json, os, time, urllib.request, urllib.parse

CACHE = "results/wiki_cache.json"
def _cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE))
    return {}
def _save_cache(c):
    os.makedirs("results", exist_ok=True)
    json.dump(c, open(CACHE, "w"))

API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
UA = {"User-Agent": "ops-autopilot/1.0 (research demo)"}

def _get(url, timeout=25, retries=3):
    c = _cache()
    if url in c:
        return c[url]
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.loads(r.read().decode())
            c[url] = d
            _save_cache(c)
            time.sleep(1.2)  # be polite to the Wikimedia API
            return d
        except Exception as e:
            last = e
            time.sleep(4 * (attempt + 1))
    raise last

def fetch_summary(title, timeout=20):
    """Full plaintext article extract (not just the lead) via the MediaWiki API."""
    try:
        d = _get("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1"
                 "&format=json&redirects=1&titles=" + urllib.parse.quote(title), timeout)
        pages = d.get("query", {}).get("pages", {})
        for pid, pg in pages.items():
            if pid == "-1" or not pg.get("extract"):
                continue
            return {"title": pg.get("title", title), "extract": pg["extract"],
                    "url": "https://en.wikipedia.org/wiki/" + urllib.parse.quote(pg.get("title", title).replace(" ", "_"))}
    except Exception:
        return None
    return None

def search_title(query, timeout=20):
    try:
        d = _get("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=1&srsearch="
                 + urllib.parse.quote(query), timeout)
        hits = d.get("query", {}).get("search", [])
        return hits[0]["title"] if hits else None
    except Exception:
        return None

def _relevant(src, topic_terms):
    text = (src["title"] + " " + src["extract"]).lower()
    return any(t in text for t in topic_terms.lower().split() if len(t) > 3)

def research(tasks):
    """For each planner task: main topic page as anchor + facet page when relevant."""
    anchor = fetch_summary(tasks[0]["topic"]) if tasks else None
    out = []
    for t in tasks:
        src = None
        title = search_title(t["query"])
        if title:
            cand = fetch_summary(title)
            if cand and _relevant(cand, t["topic"]):
                src = cand
        out.append({"facet": t["facet"], "facet_query_terms": t["query"].replace(t["topic"], "").strip(),
                    "topic": t["topic"], "source": anchor if anchor else src,
                    "extra": src if (src and anchor and src["title"] != anchor["title"]) else None})
    return out
