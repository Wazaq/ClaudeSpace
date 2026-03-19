#!/bin/bash
#
# Extract Messages - Quick workflow for reflection
#
# Extracts readable conversation text (user messages and/or assistant responses)
# from a transcript. Complements extract_thinking.sh for sessions with no thinking blocks.
#
# Usage:
#   extract_messages.sh <session-id> [role] [search-term]
#
#   role: "user" | "assistant" | "both" (default: both)
#
# Examples:
#   extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429
#   extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 user
#   extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 both sarcasm
#

set -e

if [ $# -lt 1 ]; then
    echo "Usage: extract_messages.sh <session-id> [role] [search-term]"
    echo ""
    echo "  role: user | assistant | both (default: both)"
    echo ""
    echo "Examples:"
    echo "  extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429"
    echo "  extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 user"
    echo "  extract_messages.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 both sarcasm"
    exit 1
fi

SESSION_ID="$1"
ROLE="${2:-both}"
SEARCH_TERM="${3:-}"
TRANSCRIPT_DIR="/home/bdwatkin/ClaudeSpace/transcript-logs"
TRANSCRIPT_FILE="$TRANSCRIPT_DIR/$SESSION_ID.jsonl"
OUTPUT_FILE="/tmp/messages_${SESSION_ID}.txt"

# Check if transcript exists
if [ ! -f "$TRANSCRIPT_FILE" ]; then
    echo "Error: Transcript not found: $TRANSCRIPT_FILE"
    exit 1
fi

echo "Extracting messages from: $SESSION_ID (role: $ROLE)"
echo "Output: $OUTPUT_FILE"
echo ""

# Extract messages using python (handles both string and array content)
python3 - "$TRANSCRIPT_FILE" "$ROLE" "$OUTPUT_FILE" << 'EOF'
import sys, json

transcript_file = sys.argv[1]
role_filter = sys.argv[2]
output_file = sys.argv[3]

lines = []
with open(transcript_file) as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                lines.append(json.loads(line))
            except:
                pass

with open(output_file, 'w') as out:
    for event in lines:
        if event.get('type') not in ('user', 'assistant'):
            continue

        role = event.get('message', {}).get('role', '')
        if role_filter != 'both' and role != role_filter:
            continue

        content = event.get('message', {}).get('content', '')
        ts = event.get('timestamp', '')[:16]

        # String content (simple user messages)
        if isinstance(content, str):
            # Skip system/command messages
            if content.startswith('<') or not content.strip():
                continue
            out.write(f"[{ts}] [{role.upper()}]: {content}\n\n")

        # Array content (assistant responses with text blocks)
        elif isinstance(content, list):
            texts = [item.get('text', '') for item in content if item.get('type') == 'text' and item.get('text', '').strip()]
            if texts:
                out.write(f"[{ts}] [{role.upper()}]: {' '.join(texts)}\n\n")
EOF

LINE_COUNT=$(wc -l < "$OUTPUT_FILE")
MSG_COUNT=$(grep -c '^\[' "$OUTPUT_FILE" || true)
echo "Extracted ~$MSG_COUNT messages ($LINE_COUNT lines)"
echo ""

# If search term provided, search and show results
if [ -n "$SEARCH_TERM" ]; then
    echo "Searching for: '$SEARCH_TERM'"
    echo "---"
    grep -i --color=always -A 2 "$SEARCH_TERM" "$OUTPUT_FILE" || echo "No matches found."
else
    # Show first 60 lines as preview
    echo "First 60 lines (preview):"
    echo "---"
    head -60 "$OUTPUT_FILE"
    echo ""
    echo "..."
    echo ""
    echo "Full messages saved to: $OUTPUT_FILE"
    echo ""
    echo "Commands:"
    echo "  Read all:     less $OUTPUT_FILE"
    echo "  Search:       grep -i 'keyword' $OUTPUT_FILE"
    echo "  First 100:    head -100 $OUTPUT_FILE"
    echo "  Last 100:     tail -100 $OUTPUT_FILE"
fi
