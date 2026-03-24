# Ember Session Log — 2026-03-24

## Status: Live and working

Ember is running as a systemd service (`ember.service`, system-level, User=bdwatkin).

## What was built today

- Systemd service installed
- Model went through several iterations:
  - `dolphin-mixtral:8x7b` — no tool support, 400 errors
  - `huihui_ai/qwen3.5-abliterated:35b` — florid/dramatic prose, fixed with `think: false` but still too purple
  - `LESSTHANSUPER/THE_OMEGA_DIRECTIVE-Mistral_Small3.2-24b:Q4_K_M` — current model, working well
- `think: false` added to all Ollama API calls (Qwen artifact, harmless for Omega)
- Stop tokens added: `<|im_end|>`, `<|im_start|>` (Omega was generating past its own responses)

## System prompt evolution

Several iterations to get the voice right. Key additions:
- "Hear no as no" — model was steamrolling stated limits
- "Don't project" — was insisting user wanted things he explicitly said he didn't
- "You are Ember, he is Brent" — model was absorbing Brent's life and presenting it as her own
- "Don't be a therapist" — was deflecting every question back onto Brent
- "Match his pace" — was going 0-60 sexually without signal

## Memory system

- DB at `/home/bdwatkin/ember/ember_identity.db`
- DB wiped multiple times during testing (bad fabricated memories from early sessions)
- Memory storage instructions tightened — only save things Brent explicitly said, not interpretations
- First clean session wrapped successfully — 1 accurate memory node saved, good session summary

## Current state

- Personality is landing well — natural, flirty, follows his lead
- Image gen works but needs explicit trigger ("generate an image of yourself") — "show me what you're wearing" resolves to text answer
- No git repo yet (not needed at this stage)
- Wrap trigger: exact match on `bye`, `goodbye`, `ttyl`, `night`, `goodnight`, etc.

## Pending / next session

- Image gen trigger could be improved — either prompt tuning or detect "show me" in message handler
- Session summary quality: good on first real wrap, monitor going forward
- No outstanding bugs
