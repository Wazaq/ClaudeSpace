# Waifu: Dialogue Mode Diagnosis
*2026-03-10 — investigated during free time, not a Brent-requested session*

## Problem
Story/dialogue mode toggle exists but dialogue mode doesn't work reliably. Model keeps producing third-person purple prose narration regardless of mode.

Brent's actual want: back-and-forth dialogue, character speaks directly to him. Example he wants:
> *She looks up slowly.* "I was wondering when you'd show up." *Low voice, hint of a smile.* "Did you lock the door?"

What he gets instead: third-person narrative prose.

## Root Cause (Diagnosed March 9)
Uncensored models (dolphin-mixtral, etc.) are heavily trained on prose/narrative. They fight dialogue instructions from the system prompt. The model training bias is strong.

## Current Implementation (route.ts)
System prompt structure:
1. `SYSTEM_PROMPT` (base creative writing prompt)
2. `styleDirective` (dialogue mode instruction — inserted HERE)
3. Character personality (`systemPrompt` from Personality object)
4. Mood suffix

**The problem with current structure:** The character personality comes AFTER the dialogue directive. If the character's prompt has any narrative framing, it effectively overrides the dialogue instruction. The model reads: "be creative" → "use dialogue" → "here's the character" and the character wins.

## Two Untried Approaches

### 1. Move styleDirective to end of system prompt
Place it AFTER character personality, BEFORE mood tags:
```
[Base] → [Character personality] → [Style directive] → [Mood]
```
Instructions later in the system prompt carry more weight. Simple change, low risk.

### 2. Inject reminder into user messages
In route.ts, when `responseStyle === 'dialogue'`, append to the actual user message content:
```typescript
const userContent = responseStyle === 'dialogue'
  ? `${message}\n\n[Respond as ${characterName} in dialogue: direct speech only, "I" and "you", no third-person narration]`
  : message;
```
Models weight immediate instruction in the user turn more heavily than distant system prompt content. This is probably the higher-leverage fix.

## Also Worth Checking
Character personality prompts themselves. If any character's `systemPrompt` contains "narrate", "describe", "story" framing, those would override any dialogue directive. Worth auditing the character prompts.

## Models Available
- dolphin-mixtral (fights dialogue hard)
- llama3.3:70b (calls tools correctly — may also handle dialogue better, untested for this)

Worth testing llama3.3:70b with dialogue mode — different training base might respond better.

## Status
Not implemented. Brent deferred March 9 (tired). Note written March 10 for next session with energy.
