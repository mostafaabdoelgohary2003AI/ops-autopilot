"""Persistence: Postgres when DATABASE_URL is set (Docker), SQLite otherwise."""
import json, os, sqlite3, time

DB_URL = os.environ.get("DATABASE_URL", "")
SQLITE = os.environ.get("SQLITE_PATH", "results/ops_autopilot.db")

def _pg():
    import psycopg2
    return psycopg2.connect(DB_URL)

def init():
    if DB_URL:
        con = _pg(); cur = con.cursor()
        cur.execute(open("migrations/001_init.sql").read())
        con.commit(); con.close()
    else:
        con = sqlite3.connect(SQLITE)
        con.executescript(open("migrations/001_init.sqlite.sql").read())
        con.commit(); con.close()

def save_run(result):
    init()
    if DB_URL:
        con = _pg(); cur = con.cursor()
        cur.execute("INSERT INTO runs (topic, metrics, result) VALUES (%s, %s, %s)",
                    (result["topic"], json.dumps(result["metrics"]), json.dumps(result)))
        con.commit(); con.close()
    else:
        con = sqlite3.connect(SQLITE)
        con.execute("INSERT INTO runs (topic, metrics, result) VALUES (?, ?, ?)",
                    (result["topic"], json.dumps(result["metrics"]), json.dumps(result)))
        con.commit(); con.close()

def history(limit=20):
    init()
    if DB_URL:
        con = _pg(); cur = con.cursor()
        cur.execute("SELECT id, topic, metrics, created_at FROM runs ORDER BY id DESC LIMIT %s", (limit,))
        rows = cur.fetchall(); con.close()
    else:
        con = sqlite3.connect(SQLITE)
        rows = con.execute("SELECT id, topic, metrics, created_at FROM runs ORDER BY id DESC LIMIT ?",
                           (limit,)).fetchall(); con.close()
    return [{"id": r[0], "topic": r[1], "metrics": json.loads(r[2]), "created_at": str(r[3])} for r in rows]
