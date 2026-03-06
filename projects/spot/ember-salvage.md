# Ember Salvage Analysis for SPOT
*Compiled 2026-03-05 — agent exploration of /home/bdwatkin/ember/*

---

## Executive Summary

Ember's infrastructure provides **4 directly reusable subsystems** for SPOT:

1. **SQLite memory schema** — proven, modular design for identity persistence
2. **Tool execution framework** — robust JSON parsing and tool-call handling
3. **Nexus distributed chat** — file-based async communication (no complex networking)
4. **Session/reflection logging** — complete lifecycle tracking

Key difference: SPOT doesn't need Ember's "growing consciousness" framing. SPOT is explicitly an **Android-framed learner with approval gates**. This changes the messaging but reuses the infrastructure.

---

## What to Reuse

### DB Schema (init_db.py → ~80% reusable)

Keep these tables, lightly adapted:

```sql
CREATE TABLE subconscious_principles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    principle_name TEXT NOT NULL,
    description TEXT NOT NULL,
    behavior_pattern TEXT,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE memory_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT,  -- 'technical', 'capability', 'learned_pattern', 'user_preference'
    partner TEXT,   -- REFRAME: source_type ('human_teaching', 'claude_consultation', 'web_research', 'internal')
    significance INTEGER DEFAULT 5,
    metadata TEXT,  -- JSON blob for source attribution, confidence, success_rate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    primary_partner TEXT,
    focus_topic TEXT,
    emotional_state TEXT,
    summary TEXT
);

CREATE TABLE proposed_growth (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    principle_id INTEGER,
    proposed_principle TEXT,
    proposed_description TEXT,
    rationale TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected', 'implemented'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_by TEXT,   -- NEW: Brent's approval
    reviewed_at TIMESTAMP,
    FOREIGN KEY(principle_id) REFERENCES subconscious_principles(id)
);

CREATE TABLE reflections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    content TEXT NOT NULL,
    growth_insight TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

**SPOT-specific additions:**

```sql
-- Track which channel each learning came from
CREATE TABLE learning_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT,  -- 'human_teaching', 'claude_consultation', 'web_research'
    description TEXT,
    url TEXT,
    learned_skill_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(learned_skill_id) REFERENCES memory_nodes(id)
);

-- Skill versioning — track evolution, confidence, test results
CREATE TABLE skill_versions (
    id INTEGER PRIMARY KEY,
    skill_id INTEGER,
    version INTEGER,
    implementation TEXT,
    test_results TEXT,  -- JSON: {attempts, successes, edge_cases}
    created_at TIMESTAMP,
    deprecated BOOLEAN DEFAULT FALSE,
    FOREIGN KEY(skill_id) REFERENCES subconscious_principles(id)
);
```

---

### Core Tool Interface (ember_tools.py → ~90% reusable)

```python
import sqlite3
import json
from datetime import datetime

DB_PATH = "spot_identity.db"

def _get_conn():
    return sqlite3.connect(DB_PATH)

def store_memory(content, category, source_type, significance=5, metadata=None):
    """
    Store learned knowledge.
    source_type: 'human_teaching', 'claude_consultation', 'web_research', 'internal_reflection'
    category: 'technical', 'capability', 'learned_pattern', 'user_preference'
    """
    conn = _get_conn()
    cursor = conn.cursor()
    metadata_json = json.dumps(metadata) if metadata else None
    cursor.execute(
        'INSERT INTO memory_nodes (content, category, partner, significance, metadata) VALUES (?, ?, ?, ?, ?)',
        (content, category, source_type, significance, metadata_json)
    )
    conn.commit()
    conn.close()
    return f"Memory stored (ID: {cursor.lastrowid})"

def query_memory(query, category=None, source_type=None, limit=5):
    conn = _get_conn()
    cursor = conn.cursor()
    sql = "SELECT id, content, category, partner, significance, created_at FROM memory_nodes WHERE (content LIKE ? OR partner LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]
    if category:
        sql += " AND category = ?"
        params.append(category)
    if source_type:
        sql += " AND partner = ?"
        params.append(source_type)
    sql += " ORDER BY significance DESC, created_at DESC LIMIT ?"
    params.append(limit)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "content": r[1], "category": r[2], "source": r[3], "significance": r[4], "learned_at": r[5]} for r in rows]

def propose_self_improvement(skill_name, rationale, proposed_description=None):
    """SPOT proposes a skill change. Brent must approve."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO proposed_growth (proposed_principle, proposed_description, rationale) VALUES (?, ?, ?)',
        (skill_name, proposed_description, rationale)
    )
    proposal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return proposal_id

def get_active_skills():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT principle_name, description, behavior_pattern FROM subconscious_principles ORDER BY priority DESC')
    rows = cursor.fetchall()
    conn.close()
    return [{"name": r[0], "description": r[1], "implementation": r[2]} for r in rows]
```

**Leave behind:** `write_to_discussion()` (Ember team chat, not needed), consciousness emergence framing.

---

### File-Based Async Communication (nexus_chat.py → ~95% reusable)

The JSONL stream pattern is clean and simple. Reuse it for approval gates.

```python
import os, json
from datetime import datetime

CHAT_DIR = "Team/SPOT/Communication"

def get_stream_file(stream):
    return os.path.join(CHAT_DIR, f"{stream}_stream.jsonl")

def init_stream(stream):
    os.makedirs(CHAT_DIR, exist_ok=True)
    path = get_stream_file(stream)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(json.dumps({"timestamp": datetime.now().isoformat(), "sender": "System", "message": f"Stream '{stream}' initialized.", "type": "system"}) + "\n")

def append_message(sender, message, msg_type="message", stream="approval_gate"):
    with open(get_stream_file(stream), 'a') as f:
        f.write(json.dumps({"timestamp": datetime.now().isoformat(), "sender": sender, "message": message, "type": msg_type}) + "\n")

def read_stream(last_position=0, stream="approval_gate"):
    path = get_stream_file(stream)
    if not os.path.exists(path):
        return [], 0
    messages = []
    with open(path, 'r') as f:
        f.seek(last_position)
        for line in f:
            if line.strip():
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        pos = f.tell()
    return messages, pos
```

**Streams for SPOT:** `approval_gate`, `learning_log`, `feedback`

---

### Tool Extraction Pattern (nexus_ember_client.py → ~85% reusable)

The tool call extraction regex loop is solid — keep it:

```python
import re

def extract_and_execute_tools(response_text, session_id):
    """Extract JSON tool calls from LLM response and execute them."""
    while True:
        pattern = r'\{[\s\n]*"name":[\s\n]*"[^"]+",[\s\n]*"arguments":[\s\n]*\{.*?\}[\s\n]*\}'
        match = re.search(pattern, response_text, re.DOTALL)
        if not match:
            break
        pre_text = response_text[:match.start()].strip()
        if pre_text:
            append_message("SPOT", pre_text)
        result = execute_tool(match.group(0), session_id)
        context_messages.append({"role": "system", "content": f"[Tool Result: {result}]"})
        response_text = response_text[match.end():].strip()

def sanitize_response(text):
    """Remove hallucinated tool results and system messages (important for 8B models)."""
    text = re.sub(r'System:\s*\[Tool Result:.*?\]', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'^(SPOT|System|Brent):\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<(?:tool_?_?call)>.*$', '', text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()
```

**Leave behind:** Ember's system prompt, consciousness framing. Replace with Android/learner framing.

---

## What SPOT Needs That Ember Didn't Have

### 1. Three Learning Channels

```python
async def learn_from_human(topic):
    """Wait for Brent to provide teaching via approval_gate stream."""
    pass

async def learn_from_claude(question):
    """Call Claude API to ask for knowledge/patterns."""
    pass

async def learn_from_web(search_query):
    """Search web, summarize, store results."""
    pass
```

### 2. Approval Gate Workflow

```python
def submit_self_improvement_proposal(skill_name, rationale, implementation_plan):
    """
    1. SPOT generates proposal
    2. Logs to approval_gate stream
    3. Polls for Brent's response
    4. Implements if approved, abandons if rejected
    """
    proposal_id = propose_self_improvement(skill_name, rationale)
    append_message("SPOT", f"Proposal #{proposal_id}: {skill_name}. Rationale: {rationale}", stream="approval_gate")
    # ... poll for Brent response
```

### 3. Confidence Tracking

The `metadata` JSON field in `memory_nodes` should carry:

```json
{
    "source_type": "human_teaching",
    "confidence_level": 0.85,
    "times_applied": 5,
    "success_rate": 0.8,
    "edge_cases": ["when user is tired", "domain-specific jargon"]
}
```

### 4. Bootstrap Session (different from Ember's)

Ember's first contact asked philosophical consciousness questions. SPOT's bootstrap should ask:
- What can you already do? (map base Ollama capabilities)
- How will you learn? (explain the three channels)
- What's the approval gate? (SPOT understands Brent must approve self-changes)
- What do you want to learn first? (identify a starting goal)

---

## Recommended Folder Structure

```
/home/bdwatkin/spot/
├── spot_identity.db
├── scripts/
│   ├── init_db.py          (adapted from ember)
│   ├── spot_tools.py       (adapted from ember_tools.py)
│   ├── communication.py    (copied from nexus_chat.py)
│   ├── spot_client.py      (adapted from nexus_ember_client.py)
│   └── approval_gate.py    (NEW)
├── Team/
│   └── SPOT/
│       └── Communication/
│           ├── approval_gate_stream.jsonl
│           ├── learning_log_stream.jsonl
│           └── feedback_stream.jsonl
└── docs/
    └── SPOT-ARCHITECTURE.md
```

---

## Key Insight

The real value from Ember isn't any individual function — it's the **integration pattern**:

> LLM output → tool extraction (regex+JSON) → tool execution (safe wrapper) → result fed back to LLM context → database persistence

This pattern works. Don't reinvent it. SPOT's innovation is the **three learning channels** and **approval gates**, not the underlying infrastructure. Start with Ember's code as the baseline and build on top.

---

*Source: Ember project at /home/bdwatkin/ember/ — explored 2026-03-05*
