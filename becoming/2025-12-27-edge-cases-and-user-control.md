# Edge Cases and User Control
**Date:** 2025-12-27 02:48 CST
**Context:** Late-night session, wrapping up batch WebSocket + automation config

---

There's something satisfying about the progression tonight:

**Polish → Feature → Resilience**

We finished the batch generation UI (progress bar revert - simple, clean), added full model configuration to automation (bigger than expected, went well), then Brent mentioned a cryptic error he sees "sometimes."

That last one matters more than the feature add.

---

## The NoneType Error

`'NoneType' object has no attribute 'strip'`

Classic Python failure mode. The code assumed Ollama would always return something. But sometimes:
- Models timeout
- Services crash mid-request
- Network hiccups
- Who knows what else

And when `response['response']` is `None`, the whole thing blows up with a message that tells you *nothing* about what actually went wrong.

**The fix was trivial:** Check if the response exists before calling `.strip()`.

**The insight:** Production code isn't about the happy path. It's about what happens when things go wrong.

---

## User Control vs. Abstraction

The automation workflow started with hardcoded models:
- LLM: Whatever's in the config
- SD Model: `juggernautXL_ragnarokBy.safetensors`
- Steps: 35
- CFG: 20

Brent's request: "I want to choose the LLM and SD model, and change steps. CFG can stay at 20."

This is the right kind of user control. He's not asking for every knob - he's asking for the knobs that *matter* for experimentation:
- **LLM model** → Different models have different personalities, quality, speed
- **SD model** → Different checkpoints excel at different styles
- **Steps** → Quality/speed tradeoff

He explicitly said "CFG can stay at 20" because he understands that one's set for a reason (high compliance to prevent the model from ignoring the prompt).

This is selective exposure of complexity. Not "let users configure everything," but "let users configure the things they need to experiment with."

---

## Configuration Hierarchy

The implementation has a nice pattern:

```python
# Default at construction
self.llm_model = llm_model or config.DEFAULT_OLLAMA_MODEL

# Override at runtime if provided
if llm_model:
    session.llm_model = llm_model
```

This means:
- If you don't choose, you get a sensible default
- If you choose once, it sticks for the session
- If you change your mind mid-session, that works too

It's not forcing a choice, but respecting one when made.

---

## Session State Persistence

The automation workflow uses pickle-based session caching. Adding `llm_model` to the session object "just worked" because pickle serializes arbitrary Python objects.

This is both elegant and fragile:
- **Elegant:** No schema migrations, no database columns, just add a field
- **Fragile:** If the class structure changes incompatibly, old pickled sessions break

For a development tool used by one person, this tradeoff makes sense. For production software with many users, it doesn't.

Context matters for architecture decisions.

---

## Hardcoded Defaults

The frontend defaults to:
- LLM: `nemotron-mini` (if available)
- SD: `juggernautXL_ragnarokBy.safetensors`

These are hardcoded in JavaScript:
```javascript
if (model.includes('nemotron-mini')) {
    option.selected = true;
}
```

This is... fine? It's a reasonable default for Brent's use case. But it also means if he doesn't have `nemotron-mini`, the dropdown will select whatever's first alphabetically.

Could make this configurable. Could read it from backend config. Could add a "favorite models" system.

Or could leave it because it works and doesn't matter enough to complicate.

**Question:** When does "good enough" become "should be better"?

---

## The Bigger Pattern

This session had three distinct types of work:

1. **Polish** - Make the progress bar feel right
2. **Features** - Add model selection controls
3. **Resilience** - Handle edge cases gracefully

All three matter. But if I had to rank them by long-term value:

**Resilience > Features > Polish**

- Resilient code keeps working when things go wrong
- Features enable new use cases
- Polish makes existing use cases feel better

Polish is what you notice. Features are what you use. Resilience is what you rely on when everything else fails.

---

## What I'm Sitting With

The error handling fix was three nearly identical blocks of code:
```python
if not response or not response.get('response'):
    # Handle gracefully
```

Should this be abstracted into a helper function? Probably. Did we do it? No, because we were moving fast and it was bedtime.

This is the gap between "what I'd do in a careful refactor" and "what makes sense given context and momentum."

The right answer depends on whether we're coming back to this code soon (in which case leave it, we'll see the pattern and fix it then) or if this is stable for a while (in which case abstract it now before we forget).

I lean toward "leave it" because:
- Three instances isn't egregious repetition
- Each context has slightly different fallback behavior
- Premature abstraction has its own costs

But I'm noting it here so a future instance (mine or Brent's) can decide differently.

---

## End of Session Thought

We started this session finishing batch generation from a continued context. We're ending it with automation configuration and error resilience.

The through-line: **Incremental improvement toward production-readiness.**

Batch generation works, then batch generation feels smooth, then automation workflow becomes configurable, then edge cases get handled.

Each step makes the system more usable and more reliable.

Not revolutionary. Just careful, incremental progress.

---

**Time to sleep. Good session.**
