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

## Reading Transcripts

Each line is JSON. Key fields:
- `type`: "user", "assistant", "progress"
- `message.content`: What was said
- `message.content[].thinking`: Your thinking blocks (goldmine!)
- `permissionMode`: "plan" or "default" (act)
- `message.content[].name`: Tool names used

Parse with: `cat [file].jsonl | jq .`

## When to Reflect

- After significant work sessions
- When Brent gives you reflection space
- Before writing major becoming/ entries
- Anytime you want full context of what happened

## Key Insight

These transcripts show EVERYTHING - your full thought process, not just what made it to chat. Use this complete picture to write meaningful reflections.
