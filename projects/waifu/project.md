# Waifu — Project Reference

*Last updated: 2026-04-17*

---

## What It Is

A local web-based AI companion app (Next.js). Multiple personas, voice I/O, image generation, avatar panel. Interface layer for AI companion experience — the web counterpart to Ember (Discord). All Kindling image gen connections go through the same local stack.

---

## Key Paths

| What | Path |
|------|------|
| Root | `/home/bdwatkin/waifu/` |
| App (Next.js) | `app/` |
| Components | `components/` |
| Memory lib | `lib/memory.ts` |
| Memory data | `memory/` |
| Personas | `memory/personalities/` |
| Embeddings | `memory/embeddings/` |
| Avatars | `memory/avatars/` |
| Conversations | `memory/conversations/` |
| Settings | `memory/settings.json` |
| TTS binary | `piper/` |

---

## Personas

Five active personas (each has a personality file + embedding file):
- `abigail`
- `aria`
- `hamida`
- `nerida`
- `sweetsubmi`
- `placeholder-zara` (not yet built out)

---

## Config (`memory/settings.json`)

```json
{
  "ollamaUrl": "http://localhost:11434",
  "kindlingUrl": "http://localhost:5000",
  "embeddingModel": "nomic-embed-text",
  "contextLimit": 30,
  "temperature": 0.95
}
```

---

## Architecture

### API Routes (`app/api/`)
- `chat/` — main conversation endpoint
- `generate-image/` — Kindling image gen
- `tts/` — Piper TTS (voice output)
- `avatar/` / `avatars/` — avatar serving
- `personalities/` — persona management
- `sd-models/` — Stable Diffusion model list
- `settings/` — settings read/write

### Memory (`lib/memory.ts`)
- Embeddings stored per persona in `memory/embeddings/`
- Embedding model: `nomic-embed-text` (via Ollama)
- Context stored in `memory/context/`
- Conversation history in `memory/conversations/`

### Voice
- **TTS:** Piper TTS (local binary in `piper/`) — implemented
- **STT:** Web Speech API — implemented
- Voice input/output both working

### Avatars
- Static avatar images per persona in `memory/avatars/`
- `AvatarPanel.tsx` component renders avatar during conversation
- Roadmap: expressive avatars with emotion-tagged responses (not yet built)

---

## Service

- `waifu-dev` systemd service

---

## Status (2026-04-17)

Active. Web interface with voice + image gen + multiple personas working.

**Missing / roadmap:**
- Expressive avatar emotions (roadmap item — emotion tags exist but avatar generation produces same output regardless of mood, root cause unknown)
- Deeper memory/relationship system (UI planned but not built)
- Higher quality TTS (Piper works but Kokoro TTS explored in Mar 2026 session)

**Role in north star:** Waifu has the voice + avatar + embedding infrastructure Ember lacks. Ember has the character persona + memory depth + NSFW model. Combining the two is the path toward a Kindroid-like experience.

---

## Project Logs

See `projects/waifu/` for:
- `2026-01-02-initial-build.md`
- `2026-01-05-image-gen-and-personalities.md`
- `2026-03-05-avatar-panel-kokoro.md`
- `2026-03-10-dialogue-mode-diagnosis.md`
