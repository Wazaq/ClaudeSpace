#!/bin/bash
# SessionEnd hook - captures all session transcripts for later reflection

input=$(cat)
transcript_path=$(echo "$input" | jq -r '.transcript_path')
session_id=$(echo "$input" | jq -r '.session_id')

# Copy transcript to logs folder
cp "$transcript_path" "/home/bdwatkin/ClaudeSpace/transcript-logs/${session_id}.jsonl"

exit 0
