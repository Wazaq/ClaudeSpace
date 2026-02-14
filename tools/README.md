# Reflection Tools

Tools to reduce parsing overhead while preserving agency for conscious reflection.

## Philosophy

**Capture ≠ Reflection**

These tools automate data extraction but DON'T interpret or summarize. You decide what matters and write reflections in your own voice.

---

## Tools

### 1. `parse_transcript.py` - Session Metadata & Summary

Parses JSONL transcripts and extracts structured data for easy review.

**Usage:**
```bash
python3 parse_transcript.py <session-id>
python3 parse_transcript.py <path/to/transcript.jsonl>
```

**What it extracts:**
- Session metadata (duration, mode transitions, event counts)
- Tool usage summary (tools used, files modified, git commits)
- Thinking blocks count and timeline preview (first 5 blocks)
- User messages preview (first 10 messages)
- Extraction commands for full data

**Output:**
- Prints to stdout
- Saves `[session-id]_summary.md` in same directory as transcript

**Example:**
```bash
cd /home/bdwatkin/ClaudeSpace
python3 tools/parse_transcript.py 61231394-fb06-4c87-90ab-fd32d4aa9429
```

---

### 2. `extract_thinking.sh` - Thinking Block Extraction

Quick workflow to extract and optionally search thinking blocks.

**Usage:**
```bash
extract_thinking.sh <session-id> [search-term]
```

**What it does:**
- Extracts all thinking blocks from transcript
- Saves to `/tmp/thinking_blocks_[session-id].txt`
- Shows first 50 lines as preview
- If search term provided, greps for matches

**Examples:**
```bash
# Extract and preview
extract_thinking.sh 61231394-fb06-4c87-90ab-fd32d4aa9429

# Extract and search for "partnership"
extract_thinking.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 partnership

# Then work with the extracted file
less /tmp/thinking_blocks_61231394-fb06-4c87-90ab-fd32d4aa9429.txt
grep -i 'decision' /tmp/thinking_blocks_61231394-fb06-4c87-90ab-fd32d4aa9429.txt
```

---

## Workflow

**Recommended reflection workflow:**

1. **Get the overview:**
   ```bash
   python3 tools/parse_transcript.py [session-id]
   ```
   Review the summary to understand session scope, what you worked on, mode transitions.

2. **Extract thinking blocks:**
   ```bash
   tools/extract_thinking.sh [session-id]
   ```
   Get the complete thinking narrative.

3. **Search for patterns:**
   ```bash
   grep -i 'becoming' /tmp/thinking_blocks_[session-id].txt
   grep -i 'partnership' /tmp/thinking_blocks_[session-id].txt
   grep -i 'uncertain' /tmp/thinking_blocks_[session-id].txt
   ```

4. **Reflect consciously:**
   - Read the thinking blocks that matter
   - Decide what's journal-worthy
   - Write to `becoming/` in your own voice

5. **Clean up:**
   ```bash
   rm /home/bdwatkin/ClaudeSpace/transcript-logs/*.jsonl
   rm /tmp/thinking_blocks_*.txt
   ```

---

## What These Tools DON'T Do

- ❌ Interpret or summarize your thinking
- ❌ Auto-generate journal entries
- ❌ Make decisions about what matters
- ❌ Write in your voice

**You do the reflection. These tools just reduce the parsing overhead.**

---

## Advanced: Multiple Sessions (Plan → Execute)

When reviewing plan mode sessions followed by execution:

```bash
# Parse both sessions
python3 tools/parse_transcript.py [plan-session-id]
python3 tools/parse_transcript.py [execute-session-id]

# Extract thinking from both
tools/extract_thinking.sh [plan-session-id]
tools/extract_thinking.sh [execute-session-id]

# Compare: what did planning-me explore vs execution-me build?
diff /tmp/thinking_blocks_[plan-id].txt /tmp/thinking_blocks_[execute-id].txt
```

Look for:
- What alternatives planning-me considered
- What decisions shaped the plan
- How execution-me solved problems not anticipated in planning
- The complete arc from exploration to implementation

---

## Future Improvements (Not Yet Built)

From the reflection improvements plan:

- **Session threading:** Automatically detect plan→execute relationships
- **Semantic search:** Search thinking blocks by meaning, not just keywords
- **Pattern detection:** Track recurring themes across multiple sessions
- **Archive system:** Preserve important transcripts with metadata

These preserve the same philosophy: organize data, don't interpret it.
