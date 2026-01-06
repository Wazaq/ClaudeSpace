# Waifu Chat - Image Generation & Personalities

**Date:** January 5, 2026
**Session Focus:** Adding image generation integration and character personality system

## What We Built

### 1. Clear/Reset Button
- Added to header next to model selectors
- Disabled when no messages or loading

### 2. Image Generation Integration
- **Trigger detection:** "show me [something specific]", "send a pic of [x]"
- Smart trigger logic - requires enough specificity (won't fire on just "show me" alone)
- Calls Kindling API at localhost:5000
- Flow: User triggers → Ollama generates SD prompt from context → Kindling generates image → displays inline
- Added SD model selector dropdown (Juggernaut XL, Dreamshaper, Pony Diffusion, RealVis, Animagine, SDXL Base, Qwen)
- Updated prompt generator to be uncensored for NSFW content

**Files created:**
- `app/api/generate-image/route.ts` - handles prompt generation + Kindling API call

### 3. Character Personality System
- Personalities stored in `memory/personalities/` as JSON files
- AI-assisted character creation:
  - User describes character in natural language
  - LLM generates: name, avatar emoji, description, system prompt, greeting
  - User can review/edit before saving
- Character selector dropdown in header
- Messages show character name instead of "Assistant"
- Greeting auto-displays when selecting character (if chat empty)

**Files created:**
- `app/api/personalities/route.ts` - list and save personalities
- `app/api/personalities/generate/route.ts` - AI-assisted generation
- `memory/personalities/default.json` - default unrestricted persona

**API updated:**
- `app/api/chat/route.ts` - now accepts custom `systemPrompt` parameter

## Technical Notes

- Image generation uses 768x1024 portrait orientation, 25 steps
- Prompt generator system prompt explicitly uncensored for adult content
- Personality generator outputs JSON with specific structure
- Chat history preserved when switching personalities (per Brent's preference)

## Known Issues / Future Work

- Personality AI generation can be hit-or-miss - may need prompt tuning
- Brent noted some "strange" behavior with generated personalities - needs investigation
- Could add: personality deletion, editing existing personalities from UI

## Status

Working but personality system needs real-world testing to refine the generation prompts.
