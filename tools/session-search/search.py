#!/usr/bin/env python3
"""
Search indexed session history by semantic similarity.
Usage: python3 search.py "your query here" [--top 5] [--project kindling-image-gen]
"""

import argparse
import json
import sqlite3
import struct
import sys
from pathlib import Path

import numpy as np
import requests

DB_PATH = Path.home() / "ClaudeSpace" / "tools" / "session-search" / "index.db"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768


def embed(text):
    resp = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
    resp.raise_for_status()
    return np.array(resp.json()["embedding"], dtype=np.float32)


def unpack_embedding(blob):
    return np.array(struct.unpack(f"{EMBED_DIM}f", blob), dtype=np.float32)


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def search(query, top_k=5, project=None):
    if not DB_PATH.exists():
        print("Index not found. Run indexer.py first.", file=sys.stderr)
        sys.exit(1)

    query_vec = embed(query)

    conn = sqlite3.connect(DB_PATH)

    if project:
        rows = conn.execute(
            "SELECT id, session_id, project, timestamp, role, text, embedding FROM chunks WHERE project = ?",
            (project,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, session_id, project, timestamp, role, text, embedding FROM chunks"
        ).fetchall()

    conn.close()

    if not rows:
        return []

    scored = []
    for row in rows:
        _, session_id, proj, timestamp, role, text, blob = row
        vec = unpack_embedding(blob)
        score = cosine_similarity(query_vec, vec)
        scored.append((score, session_id, proj, timestamp, role, text))

    scored.sort(reverse=True)
    return scored[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Search Claude session history")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--project", help="Filter to a specific project")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = search(args.query, top_k=args.top, project=args.project)

    if args.json:
        out = [
            {
                "score": round(score, 4),
                "session_id": session_id,
                "project": proj,
                "timestamp": timestamp,
                "role": role,
                "text": text[:500],
            }
            for score, session_id, proj, timestamp, role, text in results
        ]
        print(json.dumps(out, indent=2))
    else:
        for i, (score, session_id, proj, timestamp, role, text) in enumerate(results, 1):
            print(f"\n--- Result {i} (score: {score:.4f}) ---")
            print(f"Project: {proj}  |  Session: {session_id[:8]}...  |  {timestamp[:10]}")
            print(f"Role: {role}")
            print(text[:400] + ("..." if len(text) > 400 else ""))


if __name__ == "__main__":
    main()
