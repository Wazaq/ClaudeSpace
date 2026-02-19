# Neural Swarm: Duplicate Bot + Contextual Q&A Fix

**Date:** 2026-02-19
**Status:** Fixed and deployed

## Problems Fixed

### 1. Duplicate Bot Responses
Two bot instances were running simultaneously:
- PID 1313764 (started Feb 15, manual launch)
- PID 2808819 (systemd service, started Feb 17)

**Fix:** Kill the stale manual process. Systemd service handles everything.

**Note:** The `on_ready` task accumulation bug (multiple digest tasks on reconnect) is still present but not causing immediate issues. Worth fixing if digests start doubling again.

### 2. Contextual Follow-up Hallucination
When user asked "look at full content" in a thread, semantic search ran on that phrase, returned completely unrelated emails (Epstein news), and phi4 hallucinated based on wrong context.

**Fix:** Added to `_answer_with_context()` in `qa_system.py`:
- `_is_contextual_followup()` - detects short/reference questions
- `_get_email_ids_from_history()` - extracts email IDs from prior messages
- When follow-up detected + history has IDs: fetch those emails directly, skip semantic search

**Also fixed:** `sqlite3.Row` is read-only, must convert to `dict()` before adding fields.

### 3. Model Swap
Switched from `phi4:14b` to `gemma2:9b` in config.yaml (gitignored).
- Better instruction following
- More disciplined about staying on topic
- Won't engage in trash talk (tested)

## What's Left
- HTML content in emails (Apple receipt showed CSS class names instead of actual charge)
  - Fix: strip HTML at ingestion time (BeautifulSoup in email scanner)
- `on_ready` digest task accumulation bug
- The bot has no personality (acknowledged, fine for now)

## Next Session
Pick up with HTML stripping at ingestion.
