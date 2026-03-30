#!/usr/bin/env python3
"""
Session history indexer.
Crawls ~/.claude/projects/**/*.jsonl, extracts user+assistant messages,
embeds them via nomic-embed-text (Ollama), stores in SQLite.
"""

import json
import sqlite3
import struct
import sys
import time
from pathlib import Path

import numpy as np
import requests

PROJECTS_DIR = Path.home() / ".claude" / "projects"
DB_PATH = Path.home() / "ClaudeSpace" / "tools" / "session-search" / "index.db"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768

# Don't embed chunks shorter than this (tool results, one-word replies, etc.)
MIN_CHUNK_CHARS = 50


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            project TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_session ON chunks(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_project ON chunks(project)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS indexed_sessions (
            session_id TEXT PRIMARY KEY,
            indexed_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def already_indexed(conn, session_id):
    row = conn.execute(
        "SELECT 1 FROM indexed_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    return row is not None


def mark_indexed(conn, session_id):
    conn.execute(
        "INSERT OR REPLACE INTO indexed_sessions (session_id, indexed_at) VALUES (?, datetime('now'))",
        (session_id,),
    )
    conn.commit()


def embed(text):
    resp = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
    resp.raise_for_status()
    return resp.json()["embedding"]


def pack_embedding(vec):
    return struct.pack(f"{EMBED_DIM}f", *vec)


def extract_text_from_content(content):
    """Extract plain text from a message content field (str or list of blocks)."""
    if isinstance(content, str):
        text = content.strip()
    elif isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block["text"].strip())
        text = "\n".join(parts).strip()
    else:
        return ""

    # Filter out image reference lines — they match on filenames not meaning
    lines = [l for l in text.splitlines() if not l.strip().startswith("[Image:")]
    return "\n".join(lines).strip()


def parse_jsonl(path):
    """Yield (session_id, timestamp, role, text) for indexable messages."""
    session_id = path.stem
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            msg_type = obj.get("type")
            if msg_type not in ("user", "assistant"):
                continue

            message = obj.get("message", {})
            role = message.get("role")
            if role not in ("user", "assistant"):
                continue

            content = message.get("content", "")
            text = extract_text_from_content(content)

            if len(text) < MIN_CHUNK_CHARS:
                continue

            timestamp = obj.get("timestamp", "")
            yield session_id, timestamp, role, text


def index_file(conn, path, project):
    session_id = path.stem
    if already_indexed(conn, session_id):
        return 0

    chunks = list(parse_jsonl(path))
    if not chunks:
        mark_indexed(conn, session_id)
        return 0

    count = 0
    for session_id, timestamp, role, text in chunks:
        try:
            vec = embed(text)
            blob = pack_embedding(vec)
            conn.execute(
                "INSERT INTO chunks (session_id, project, timestamp, role, text, embedding) VALUES (?, ?, ?, ?, ?, ?)",
                (session_id, project, timestamp, role, text, blob),
            )
            count += 1
        except Exception as e:
            print(f"  embed error: {e}", file=sys.stderr)

    conn.commit()
    mark_indexed(conn, session_id)
    return count


def main():
    conn = get_db()

    jsonl_files = sorted(PROJECTS_DIR.rglob("*.jsonl"))
    total_files = len(jsonl_files)
    total_chunks = 0

    print(f"Found {total_files} JSONL files across all projects")

    for i, path in enumerate(jsonl_files, 1):
        project = path.parent.name
        session_id = path.stem

        if already_indexed(conn, session_id):
            continue

        print(f"[{i}/{total_files}] {project}/{path.name}", end=" ... ", flush=True)
        t0 = time.time()
        n = index_file(conn, path, project)
        elapsed = time.time() - t0
        print(f"{n} chunks ({elapsed:.1f}s)")
        total_chunks += n

    print(f"\nDone. {total_chunks} chunks indexed.")
    conn.close()


if __name__ == "__main__":
    main()
