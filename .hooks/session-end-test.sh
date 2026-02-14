#!/bin/bash
# SessionEnd hook test - logs when session ends and captures input data

LOG_FILE="/home/bdwatkin/ClaudeSpace/.hooks/session-end-log.txt"

# Create timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Read JSON input from stdin
input=$(cat)

# Log the event
echo "====================" >> "$LOG_FILE"
echo "SessionEnd fired: $timestamp" >> "$LOG_FILE"
echo "Working directory: $PWD" >> "$LOG_FILE"
echo "Session end input:" >> "$LOG_FILE"
echo "$input" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Exit successfully
exit 0
