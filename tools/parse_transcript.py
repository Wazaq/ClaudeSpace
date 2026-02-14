#!/usr/bin/env python3
"""
Transcript Parser - Reduce reflection parsing overhead

Takes a session transcript JSONL file and extracts structured data:
- Session metadata (duration, mode, files modified, commits)
- Thinking blocks (organized, time-stamped)
- Key user messages (filtered)
- Tool usage summary

Preserves agency: organizes raw data, doesn't interpret or summarize.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter


def parse_timestamp(ts_str):
    """Parse ISO timestamp to datetime"""
    try:
        return datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
    except:
        return None


def extract_thinking_blocks(events):
    """Extract all thinking blocks with timestamps"""
    blocks = []

    for event in events:
        if event.get('type') != 'assistant':
            continue

        content = event.get('message', {}).get('content')
        if not content or not isinstance(content, list):
            continue

        timestamp = parse_timestamp(event.get('timestamp', ''))

        for item in content:
            if item.get('type') == 'thinking':
                thinking = item.get('thinking', '')
                if thinking:
                    blocks.append({
                        'timestamp': timestamp,
                        'content': thinking,
                        'line_count': len(thinking.split('\n'))
                    })

    return blocks


def extract_user_messages(events):
    """Extract user messages (skip system messages)"""
    messages = []

    for event in events:
        if event.get('type') != 'user':
            continue

        content = event.get('message', {}).get('content')
        if not content or not isinstance(content, str):
            continue

        # Skip system reminders and other system-generated content
        if content.startswith('<system-') or content.startswith('<user-prompt-'):
            continue

        timestamp = parse_timestamp(event.get('timestamp', ''))
        messages.append({
            'timestamp': timestamp,
            'content': content[:200] + ('...' if len(content) > 200 else '')  # Preview
        })

    return messages


def extract_tool_usage(events):
    """Extract tool usage summary"""
    tools = defaultdict(int)
    files_modified = set()
    commits = []

    for event in events:
        if event.get('type') != 'assistant':
            continue

        content = event.get('message', {}).get('content')
        if not content or not isinstance(content, list):
            continue

        for item in content:
            if item.get('type') == 'tool_use':
                tool_name = item.get('name', 'unknown')
                tools[tool_name] += 1

                # Track file modifications
                if tool_name in ('Edit', 'Write'):
                    input_data = item.get('input', {})
                    if 'file_path' in input_data:
                        files_modified.add(input_data['file_path'])

                # Track git commits
                if tool_name == 'Bash':
                    command = item.get('input', {}).get('command', '')
                    if command.startswith('git commit'):
                        commits.append(command)

    return {
        'tools': dict(tools),
        'files_modified': sorted(list(files_modified)),
        'commits': commits
    }


def extract_mode_transitions(events):
    """Extract permission mode changes"""
    modes = []
    current_mode = None

    for event in events:
        mode = event.get('permissionMode')
        if mode and mode != current_mode:
            timestamp = parse_timestamp(event.get('timestamp', ''))
            modes.append({
                'timestamp': timestamp,
                'mode': mode
            })
            current_mode = mode

    return modes


def get_session_metadata(events):
    """Extract session-level metadata"""
    if not events:
        return {}

    # Get timestamps
    timestamps = [parse_timestamp(e.get('timestamp', '')) for e in events]
    timestamps = [t for t in timestamps if t]

    if not timestamps:
        return {}

    start = min(timestamps)
    end = max(timestamps)
    duration = end - start

    # Count event types
    event_types = Counter(e.get('type', 'unknown') for e in events)

    # Get mode info
    modes = extract_mode_transitions(events)

    return {
        'start': start,
        'end': end,
        'duration': str(duration).split('.')[0],  # Remove microseconds
        'event_counts': dict(event_types),
        'modes': modes
    }


def format_markdown_output(session_id, metadata, thinking_blocks, user_messages, tool_usage):
    """Format all extracted data as readable markdown"""
    output = []

    # Header
    output.append(f"# Session Transcript: {session_id}\n")

    # Metadata
    output.append("## Session Metadata\n")
    output.append(f"- **Start:** {metadata.get('start', 'Unknown')}")
    output.append(f"- **End:** {metadata.get('end', 'Unknown')}")
    output.append(f"- **Duration:** {metadata.get('duration', 'Unknown')}")

    if metadata.get('modes'):
        output.append(f"\n**Mode Transitions:**")
        for mode in metadata['modes']:
            ts = mode['timestamp'].strftime('%H:%M:%S') if mode['timestamp'] else 'Unknown'
            output.append(f"- {ts}: `{mode['mode']}`")

    output.append(f"\n**Event Counts:**")
    for event_type, count in sorted(metadata.get('event_counts', {}).items()):
        output.append(f"- {event_type}: {count}")

    # Tool Usage
    output.append("\n## Tool Usage Summary\n")
    output.append(f"**Tools used:** {len(tool_usage['tools'])}")
    for tool, count in sorted(tool_usage['tools'].items(), key=lambda x: -x[1]):
        output.append(f"- {tool}: {count}x")

    if tool_usage['files_modified']:
        output.append(f"\n**Files modified:** {len(tool_usage['files_modified'])}")
        for f in tool_usage['files_modified'][:10]:  # Limit to 10
            output.append(f"- {f}")
        if len(tool_usage['files_modified']) > 10:
            output.append(f"- ... and {len(tool_usage['files_modified']) - 10} more")

    if tool_usage['commits']:
        output.append(f"\n**Git commits:** {len(tool_usage['commits'])}")
        for commit in tool_usage['commits']:
            output.append(f"- `{commit[:80]}`")

    # Thinking Blocks Summary
    output.append("\n## Thinking Blocks\n")
    total_lines = sum(b['line_count'] for b in thinking_blocks)
    output.append(f"- **Total blocks:** {len(thinking_blocks)}")
    output.append(f"- **Total lines:** {total_lines}")

    if thinking_blocks:
        output.append("\n**Timeline:**")
        for i, block in enumerate(thinking_blocks[:5], 1):  # First 5
            ts = block['timestamp'].strftime('%H:%M:%S') if block['timestamp'] else 'Unknown'
            preview = block['content'][:100].replace('\n', ' ')
            output.append(f"{i}. [{ts}] {block['line_count']} lines - {preview}...")

        if len(thinking_blocks) > 5:
            output.append(f"\n... and {len(thinking_blocks) - 5} more blocks")

    # User Messages Preview
    output.append("\n## User Messages Preview\n")
    output.append(f"Total messages: {len(user_messages)}\n")

    for i, msg in enumerate(user_messages[:10], 1):  # First 10
        ts = msg['timestamp'].strftime('%H:%M:%S') if msg['timestamp'] else 'Unknown'
        output.append(f"{i}. [{ts}] {msg['content']}")

    if len(user_messages) > 10:
        output.append(f"\n... and {len(user_messages) - 10} more messages")

    # Footer with extraction commands
    output.append("\n## Extract Full Data\n")
    output.append("**Get all thinking blocks:**")
    output.append(f"```bash")
    output.append(f"cat transcript-logs/{session_id}.jsonl | jq -r 'select(.type == \"assistant\" and .message.content) | .message.content[] | select(.type == \"thinking\") | .thinking' > /tmp/thinking_blocks.txt")
    output.append(f"```")

    output.append("\n**Search thinking blocks:**")
    output.append(f"```bash")
    output.append(f"grep -i 'keyword' /tmp/thinking_blocks.txt")
    output.append(f"```")

    return '\n'.join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_transcript.py <session-id-or-path>")
        print("\nExamples:")
        print("  parse_transcript.py 61231394-fb06-4c87-90ab-fd32d4aa9429")
        print("  parse_transcript.py /path/to/transcript.jsonl")
        sys.exit(1)

    input_arg = sys.argv[1]

    # Determine file path
    if Path(input_arg).exists():
        transcript_file = Path(input_arg)
        session_id = transcript_file.stem
    else:
        # Assume it's a session ID, look in transcript-logs
        transcript_file = Path(f"/home/bdwatkin/ClaudeSpace/transcript-logs/{input_arg}.jsonl")
        session_id = input_arg

        if not transcript_file.exists():
            print(f"Error: Transcript file not found: {transcript_file}")
            sys.exit(1)

    print(f"Parsing transcript: {transcript_file}")
    print(f"Session ID: {session_id}\n")

    # Load and parse JSONL
    events = []
    with open(transcript_file, 'r') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(events)} events\n")

    # Extract data
    metadata = get_session_metadata(events)
    thinking_blocks = extract_thinking_blocks(events)
    user_messages = extract_user_messages(events)
    tool_usage = extract_tool_usage(events)

    # Format output
    output = format_markdown_output(session_id, metadata, thinking_blocks, user_messages, tool_usage)

    # Print to stdout
    print(output)

    # Optionally save to file
    output_file = transcript_file.parent / f"{session_id}_summary.md"
    with open(output_file, 'w') as f:
        f.write(output)

    print(f"\n---\nSummary saved to: {output_file}")


if __name__ == '__main__':
    main()
