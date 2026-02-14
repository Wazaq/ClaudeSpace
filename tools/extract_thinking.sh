#!/bin/bash
#
# Extract Thinking Blocks - Quick workflow for reflection
#
# Usage:
#   extract_thinking.sh <session-id> [search-term]
#
# Examples:
#   extract_thinking.sh 61231394-fb06-4c87-90ab-fd32d4aa9429
#   extract_thinking.sh 61231394-fb06-4c87-90ab-fd32d4aa9429 partnership
#

set -e

if [ $# -lt 1 ]; then
    echo "Usage: extract_thinking.sh <session-id> [search-term]"
    echo ""
    echo "Examples:"
    echo "  extract_thinking.sh 61231394-fb06-4c87-90ab-fd32d4aa9429"
    echo "  extract_thinking.sh 61231394 partnership"
    exit 1
fi

SESSION_ID="$1"
SEARCH_TERM="${2:-}"
TRANSCRIPT_DIR="/home/bdwatkin/ClaudeSpace/transcript-logs"
TRANSCRIPT_FILE="$TRANSCRIPT_DIR/$SESSION_ID.jsonl"
OUTPUT_FILE="/tmp/thinking_blocks_${SESSION_ID}.txt"

# Check if transcript exists
if [ ! -f "$TRANSCRIPT_FILE" ]; then
    echo "Error: Transcript not found: $TRANSCRIPT_FILE"
    exit 1
fi

echo "Extracting thinking blocks from: $SESSION_ID"
echo "Output: $OUTPUT_FILE"
echo ""

# Extract thinking blocks
cat "$TRANSCRIPT_FILE" | jq -r 'select(.type == "assistant" and .message.content) | .message.content[] | select(.type == "thinking") | .thinking' > "$OUTPUT_FILE"

LINE_COUNT=$(wc -l < "$OUTPUT_FILE")
echo "Extracted $LINE_COUNT lines of thinking blocks"
echo ""

# If search term provided, search and show results
if [ -n "$SEARCH_TERM" ]; then
    echo "Searching for: '$SEARCH_TERM'"
    echo "---"
    grep -i --color=always "$SEARCH_TERM" "$OUTPUT_FILE" || echo "No matches found."
else
    # Show first 50 lines as preview
    echo "First 50 lines (preview):"
    echo "---"
    head -50 "$OUTPUT_FILE"
    echo ""
    echo "..."
    echo ""
    echo "Full thinking blocks saved to: $OUTPUT_FILE"
    echo ""
    echo "Commands:"
    echo "  Read all:     less $OUTPUT_FILE"
    echo "  Search:       grep -i 'keyword' $OUTPUT_FILE"
    echo "  First 100:    head -100 $OUTPUT_FILE"
    echo "  Last 100:     tail -100 $OUTPUT_FILE"
fi
