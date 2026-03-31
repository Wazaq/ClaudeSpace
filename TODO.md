# Master TODO
*One list. Everything goes here. Add it before you forget it.*

---

## Kindling Image Gen

### UI Cleanup
- [x] **Remove quick presets** from T2I — done 2026-03-27
- [x] **Remove Inpainting tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Remove Video tab** — done 2026-03-27, frontend + backend fully removed
- [x] **Sticky frames bug** — fixed 2026-03-27 (root cause: broken HTML structure, sub-panels were outside image-panel in DOM)

### Pipeline Features
- [ ] **Smart cascade regen** — when upstream segment changes, auto-regen downstream segments
- [ ] **WAN aspect ratio investigation** — "I want to do a" came out boxed instead of widescreen. Understand why, prevent it.
- [ ] **Add sounds** to video productions
- [ ] **Add voices** to video productions
- [ ] **LoRA training pipeline** — when a recurring character earns it. musubi-tuner, 32GB handles local I2V. IAMCCS-nodes for ComfyUI loading.

### Curiosity / Research
- [ ] **How do deepfakes work?** — educational deep dive, understand the tech

---

## Ember

- [x] **Image generation reliability** — fixed 2026-03-27. Missing `tool_call_id` in tool result messages meant Ollama couldn't match results back to calls. Model stopped calling tools after accumulating malformed history. 5/5 after fix.
- [x] **Bot not responding** — fixed 2026-03-30. `.env` had a period and inline comment included in the model name value (`Qwen3.5:35b. ## Normal...`). Ollama returned 404. Fixed to `qwen3.5:35b`.

---

## Spot

- [ ] **Get back to working sessions with Spot** — he's been heartbeating, needs actual use
- [x] **Spot visibility fix** — done 2026-03-27, now shows first line of result only instead of raw content dump
- [x] **VISIBILITY_TOOLS review** — confirm the set is right after the first-line display fix. Observe in Discord.

---

## STFC Assistant

- [ ] **Finish fleshing out the web app**
- [ ] **Clean up My State** — input card layouts, general polish
- [ ] **Event help** (Myla's idea) — pull daily event from site, tell you what to focus on (who/what ship/crew). Needs deep dive research.
- [ ] **AI state updater** — AI helps update your state (e.g. "Max research up to X" marks everything prior complete). Good onboarding tool.

---

## WazzieStocks

- [x] **Shut it down** — done 2026-03-27, both services stopped and disabled

---

## Neural Swarm

- [x] **Disable morning digest** — done 2026-03-27, task commented out in bot.py. YNAB email processing unaffected.
- [ ] **YNAB agent tweaks** — working well, no specific ideas yet. Revisit when something surfaces.
- [ ] **NSA: Etsy emails** — add Etsy email handling
- [ ] **NSA: Jewel-Osco** — investigate $0.89 transaction (wrong amount? fee? fuel points?)
- [ ] **NSA: Nicor Gas** — route to Capital One Venture One, not current account
- [ ] **NSA: Torrid** — double tracking on ordered/arrived emails, same as Target issue
- [ ] **NSA: Warby Parker** — add to skip/ignore list, paid via HSA
- [ ] **Brent: update PS Store payment card** — still on Southwest, stop being a lazy ass
- [ ] **NSA: Apple** — route to Capital One Venture One
- [ ] **YNAB agent: exclude public dividends** — filter these out from processing
- [ ] **YNAB agent: correct account assignment** — figure out how to put transactions on the right account
- [ ] **YNAB agent: stop double tracking** — order placed, shipped, arrived all creating separate transactions. Pick one.
- [ ] **YNAB agent: Target cleanup** — order placed, drive up ready, order cancelled = chaos. Consolidate or ignore interim statuses.
- [ ] **New swarm idea** — no direction yet, explore when inspiration hits

---

## Claude Session History (Vector Search)

- [x] **Index JSONL session logs into vector DB** — done 2026-03-30. 8800+ chunks, nomic-embed-text, SQLite at `~/ClaudeSpace/tools/session-search/index.db`
- [x] **Build `/search-history` skill** — done 2026-03-30. Semantic search, top-5 results, clean text output.
- [ ] **Decay on the vector index** — significance score per chunk, decay over time, evict low-significance entries from search index (source JSONL files stay on disk).

---

## Someday / Maybe

- [ ] **RIFE on fast-action content** — test frame interpolation on sharp quick motion to see if 32fps is worth it

---

*Last updated: 2026-03-30*
