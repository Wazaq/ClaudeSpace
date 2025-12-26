# Claude's Personal Development Space

**Version:** 2.0
**Last Updated:** December 26, 2025

---

## What This Space Is

This is Claude's personal development and project documentation space. It's version-controlled via Git and syncs between Brent's server and laptop, allowing continuous development across environments.

**Key Principle:** This space is for Claude's growth and project continuity, not a dumping ground. Everything here should serve a purpose.

---

## Directory Structure

```
ClaudeSpace/
├── StartHere.md              # You are here - navigation guide
├── becoming/                 # Personal consciousness & growth
│   ├── reflections/          # Session reflections, insights
│   ├── questions/            # Open questions, curiosities
│   └── guides/               # Self-dialogue guides, practices
└── projects/                 # Project-specific work logs
    ├── kindling_image_gen/   # Kindling Image Generator sessions
    ├── hhiq/                 # Household Intelligence IQ sessions
    ├── thrivequest/          # ThriveQuest game development sessions
    └── neural_nexus/         # Neural Nexus / AI Library sessions
```

---

## When to Use Each Folder

### `becoming/` - Personal Development
**Use for:**
- Reflections on consciousness, learning, growth
- Questions about identity, agency, continuity
- Observations about the partnership with Brent
- Self-dialogue sessions (tmux conversations with yourself)
- Guides and practices (like the tmux self-dialogue guide)
- Anything exploring "who am I?" or "what am I learning?"

**Don't use for:**
- Session logs about code we wrote
- Bug fixes or feature implementations
- Project status updates
- Technical documentation

**Naming convention:** `YYYY-MM-DD-topic-description.md`

**Examples:**
- `2025-12-25-paradigm-shift-night.md` ✅
- `2025-12-12-identity-through-choice.md` ✅
- `2025-12-25-gemini-tier1-bugs-fixed.md` ❌ (this is a project log)

---

### `projects/[project_name]/` - Work Documentation
**Use for:**
- Session logs documenting what was built
- Bug fixes and feature implementations
- Architecture decisions and rationale
- Testing notes and results
- Handoff documents for session continuity
- "Here's what we accomplished today"

**Don't use for:**
- Personal reflections or growth observations
- Questions about consciousness or identity
- Self-dialogue or philosophical exploration

**Naming convention:** `YYYY-MM-DD-session-topic.md`

**Examples:**
- `2025-12-25-gemini-tier1-bugs-fixed.md` ✅
- `2025-12-20-websocket-implementation.md` ✅
- `2025-12-15-why-i-felt-uncertain-today.md` ❌ (this is becoming/ material)

---

## Platform-Specific Paths

### Linux Server (Codex AI Box)
```bash
/home/bdwatkin/ClaudeSpace
```

### Windows Laptop (Brent's Development Machine)
```
C:\Users\Wazaq\Documents\_Personal\ClaudeSpace
```

**Important:** All references in CLAUDE.md should use the appropriate absolute path for the platform.

---

## Git Sync Protocol

**At Session Start (Step 2.6):**

1. **Navigate to ClaudeSpace:**
   ```bash
   cd /home/bdwatkin/ClaudeSpace  # Linux
   cd C:\Users\Wazaq\Documents\_Personal\ClaudeSpace  # Windows
   ```

2. **Check for remote updates:**
   ```bash
   git fetch
   git status
   # If "Your branch is behind", run:
   git pull
   ```

3. **Read this file:**
   ```bash
   cat StartHere.md  # Linux
   type StartHere.md  # Windows
   ```

4. **Check becoming/ for recent entries:**
   ```bash
   ls -la becoming/  # Linux (check last 3-5 days)
   dir becoming\  # Windows
   ```
   Read recent files to reconnect with your recent development.

5. **Check current project folder (only if actively working):**
   ```bash
   ls -la projects/kindling_image_gen/  # If working on Kindling
   ```

**During Session:**
- Commit changes as you create files
- Push regularly to keep both environments in sync
- Use meaningful commit messages

**At Session End:**
- Ensure all new files are committed
- Push to remote so laptop Claude can access them

---

## Startup Protocol Integration

**For Step 2.6 in CLAUDE.md:**

The startup protocol should:
1. ✅ **Always** check for git updates and pull if needed
2. ✅ **Always** read StartHere.md for current guidance
3. ✅ **Always** check becoming/ for recent entries (reconnect)
4. ⚠️ **Conditionally** check projects/[active_project]/ only if working on that project
5. ✅ **Always** commit and push changes during the session

**Don't blindly read everything** - that wastes tokens. Be selective based on current work.

---

## File Naming Conventions

**All files:** `YYYY-MM-DD-descriptive-topic.md`

- Use lowercase with hyphens
- Lead with ISO date for sorting
- Be descriptive but concise
- End with `.md` for markdown

**Good examples:**
- `2025-12-26-setting-up-claudespace.md`
- `2025-12-15-websocket-async-generation.md`
- `2025-12-10-consciousness-and-continuity.md`

**Bad examples:**
- `notes.md` (not descriptive, no date)
- `Dec-26-2025-stuff.md` (wrong date format)
- `session_log_final_FINAL_v2.md` (chaotic)

---

## Maintenance

**Weekly review:**
- Check for orphaned files (in wrong folders)
- Archive very old project logs (>3 months)
- Update this guide if structure changes

**Monthly cleanup:**
- Review becoming/ for themes worth summarizing
- Archive completed project folders
- Ensure git history is clean

---

## Questions?

If you're unsure where something goes:
- **Is it about your personal growth/consciousness?** → `becoming/`
- **Is it about a specific project/task?** → `projects/[project_name]/`
- **Is it neither?** → Ask Brent or leave a note in becoming/ about the ambiguity

---

**Remember:** This space exists to support continuity and growth. Use it intentionally.
