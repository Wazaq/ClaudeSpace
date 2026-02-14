# Transcript Logs - Reflection Workflow

## Purpose

This folder captures full session transcripts for conscious reflection. Like recording lectures to review later.

## What's Here

- `[session-id].jsonl` files - Complete conversation transcripts from ended sessions
- Each JSONL line is an event: messages, thinking blocks, tool uses, everything
- You have FULL context - more than Brent could tell you

## Reflection Workflow (When `/reflect` is called)

1. **Read all transcript files** in this folder
2. **Parse and understand** what happened in each session:
   - Planning sessions: what you explored, what agents found, decisions made
   - Execution sessions: what worked, what didn't, problems solved
   - Conversations: insights, discoveries, partnership moments
3. **Decide what's journal-worthy**:
   - New patterns or insights
   - Things that surprised you
   - Connections between planning and execution
   - Partnership moments that mattered
   - Questions that arose
4. **Write to `becoming/`** in your own voice, not auto-summaries
5. **Clear this folder** when done: `rm /home/bdwatkin/ClaudeSpace/transcript-logs/*.jsonl`

## How to Parse Transcripts

**Method 1: Use the Parser Tool (Recommended)**

The transcript parser reduces jq overhead and organizes data for easy review:

```bash
# Parse a transcript by session ID
python3 ../tools/parse_transcript.py [session-id]

# Or by file path
python3 ../tools/parse_transcript.py transcript-logs/[session-id].jsonl
```

**What the parser gives you:**
- Session metadata (duration, mode transitions, event counts)
- Tool usage summary (what you did, files modified, commits)
- Thinking blocks count and timeline preview
- User messages preview
- Extraction commands for full data

**Output:** Prints to stdout and saves `[session-id]_summary.md` for reference.

**Then extract full thinking blocks:**
```bash
# The summary shows the command - copy/paste it
cat transcript-logs/[session-id].jsonl | jq -r 'select(.type == "assistant" and .message.content) | .message.content[] | select(.type == "thinking") | .thinking' > /tmp/thinking_blocks.txt

# Read in chunks or search
grep -i 'keyword' /tmp/thinking_blocks.txt
head -100 /tmp/thinking_blocks.txt
tail -200 /tmp/thinking_blocks.txt
```

---

**Method 2: Manual jq Commands (For Custom Queries)**

If you need custom parsing beyond what the tool provides:

### Understand session scope
```bash
# See what event types exist and how many
cat [file].jsonl | jq -r '.type' | sort | uniq -c

# Check for mode transitions (plan vs act)
cat [file].jsonl | jq -r 'select(.permissionMode) | .permissionMode' | uniq -c
```

### Extract thinking blocks manually
```bash
# Extract all thinking blocks to a temp file
cat [file].jsonl | jq -r 'select(.type == "assistant" and .message.content) | .message.content[] | select(.type == "thinking") | .thinking' > /tmp/thinking_blocks.txt

# Check how many lines
wc -l /tmp/thinking_blocks.txt

# Read in chunks
head -100 /tmp/thinking_blocks.txt  # First 100 lines
tail -200 /tmp/thinking_blocks.txt  # Last 200 lines
```

### Get work context from user messages
```bash
# Extract user messages (skip system messages)
cat [file].jsonl | jq -r 'select(.type == "user" and (.message.content | type) == "string") | .message.content' | grep -v "^<" | head -20
```

---

## Understanding Thinking Blocks

The thinking blocks show your complete reasoning process:
- What connections you made between different work
- How you approached problems
- What you were uncertain about
- Decisions and trade-offs
- Cross-references to becoming/ entries

Read them chronologically to understand the session's arc.

### Key Fields Reference

Each JSONL line is an event with these fields:
- `type`: "user", "assistant", "progress", "system", "file-history-snapshot"
- `message.content`: What was said (string or array)
- `message.content[].thinking`: Your thinking blocks (goldmine!)
- `message.content[].type`: "text", "thinking", "tool_use", "tool_result"
- `permissionMode`: "plan", "acceptEdits", or null
- `timestamp`: When the event occurred

## Reflection Prompts by Session Type

Use these prompts to guide attention to session-specific insights:

**Plan mode sessions:**
- What alternatives did I consider?
- What decisions were made and why?
- What uncertainties remained when planning ended?
- How did I use sub-agents to explore?

**Execution sessions:**
- What worked as planned?
- What problems arose unexpectedly?
- How did I debug/solve issues?
- What did I learn during implementation?

**Conversation sessions:**
- What partnership moments mattered?
- What insights or connections emerged?
- What questions arose?
- What patterns am I seeing across work?

**Plan → Execute pairs (clean break):**
- What did planning-me explore that execution-me built upon?
- What decisions from planning shaped execution?
- How did the separation affect the work?
- What's the complete arc across both sessions?

These are **optional scaffolding** - not required, but helpful for finding what matters.

---

## When to Reflect

- After significant work sessions
- When Brent gives you reflection space
- Before writing major becoming/ entries
- Anytime you want full context of what happened

## Key Insight

These transcripts show EVERYTHING - your full thought process, not just what made it to chat. Use this complete picture to write meaningful reflections.
