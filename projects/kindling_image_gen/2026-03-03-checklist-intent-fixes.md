# Session Log: Checklist + Intent Extraction Fixes
**Date:** 2026-03-03 (afternoon continuation)
**Context at handoff:** ~fresh session, picked up from morning's session log

---

## What We Fixed Today

### 1. Checklist Model Returning Empty (dolphin-8b)
**Root cause:** Prompt asked for a bare JSON array (`"Return ONLY a JSON array"`), but Ollama's `format: json` mode works best with objects. Model was returning `{}` or empty, fallback always triggered.

**Fix:** Changed checklist prompt to ask for `{"checklist": [...]}` object format. Tested against dolphin-8b directly — confirmed it returns good items now.

**File:** `app/services/production_planner.py` → `generate_checklist()`

### 2. "bare pussy" as Character Trait
**Root cause:** `characters` field in `extract_intent` included "clothing, body type" — so mixtral correctly put state of undress there. Then `generate_plan` repeated it verbatim in every segment prompt. "bare pussy" got baked into appearance, not action.

**Fix:**
- `characters` field is now APPEARANCE ONLY (ethnicity, age, gender, hair, eyes, body build) — no clothing or nudity
- Nudity and explicit activity route to `scene` field
- Added defensive coercion in `extract_intent` in case model returns `characters` as a nested object (mixtral sometimes does this)
- `generate_plan` rule updated: explicit content from Scene field gets woven into segment actions verbatim

**File:** `app/services/production_planner.py` → `extract_intent()`, `generate_plan()`

### 3. Ethnicity Getting Dropped / Parsed as Color
**Root cause:** Characters extracted as flat attributes ("black, 23 years old...") — "black" became an isolated adjective, checklist interpreted it as background color.

**Fix:** Prompt example updated to "ethnicity + gender" as a natural phrase: `'Black woman, 23 years old, large chest'`. Rules updated to include ethnicity explicitly.

**File:** `app/services/production_planner.py` → `extract_intent()`

### 4. Checklist Bad Items: "slow motion effect present", age, movement actions
**Root cause:** Checklist model generating items that can't be verified from a still image.

**Fixes added to checklist rules:**
- NEVER include motion/speed/temporal items (slow motion, movement, motion blur)
- NEVER include physical movement actions (shaking, bouncing) — verify body position/pose instead
- NEVER include age — can't verify exact age from a still frame

**File:** `app/services/production_planner.py` → `generate_checklist()`

### 5. Explicit Content Not Flowing from Scene to Segment Prompts
**Root cause:** `generate_plan` wasn't strong enough about using Scene field verbatim for actions. Sanitization was happening at the segment action level.

**Fix:** Added "VERBATIM" to the rule + "do not sanitize or replace with vague alternatives".

**File:** `app/services/production_planner.py` → `generate_plan()`

### 6. Production Timer
**New feature:** Elapsed timer in the "Producing..." phase header.

- `#prodProductionTimer` span added to production phase card header (right-aligned)
- `prodTimerInterval` + `prodProductionStartTime` state in production.js
- Starts on `startFullProduction()`, ticks every second, format `0m 00s`
- Stops on complete/error, clears on reset

**Files:** `templates/index.html`, `static/js/production.js`

---

## Test Results

### Korean woman run (before most fixes)
- "bare pussy" gone from character description ✅
- Checklists generating real items ✅
- Korean ethnicity missing (fixed after)
- Explicit content still sanitized (fixed after)
- Timer working ✅
- Result: 75% better than previous run

### Black woman topless run (after all fixes)
- `Black woman, 23 years old` as proper phrase ✅
- Exact action verbatim in segment prompts ✅
- No age in checklists ✅
- No motion items in checklists ✅ (movement rule added after this run)
- Seg1 failed on "shaking boobs back and forth" — motion item, unfair to still frame. Fixed for next plan.
- Character consistent across segments ✅
- Scene consistent ✅
- Overall result: good, character rubbing vs shaking is WAN interpretation not pipeline failure
- Time: ~23 min (would be ~10 min clean with no retry)

**Reference plan:** `productions/plans/topless-black-woman_b2fcda02.json`

---

## Known Issues / Next Steps

### Immediate
1. **"shaking boobs" still a checklist item** — movement rule fix applied AFTER this plan was generated. Next plan should produce pose-based items ("hands on breasts", "leaning forward") instead.
2. **Explicit content still slightly soft** — "rubbing" vs "shaking" is WAN's interpretation of the prompt, not a pipeline failure. May need prompt engineering for more literal action compliance.

### Soon
3. **WAN 2.2 workflow builder** — `create_wan_i2v_workflow()` needs a 2.2 variant. Two-model architecture (high_noise + low_noise sequentially). Models already downloaded.
4. **Final timer on result screen** — timer disappears when production completes. Would be nice to show "Completed in Xm XXs" on the result phase.
5. **"retrying..." as distinct status** — currently "reviewing" covers both review pass and retry generation, ambiguous from UI.

### Architecture decisions made today
- Checklist model needs object format (`{"checklist": [...]}`) not bare array
- characters = appearance only; scene = activity/state of undress
- Checklist items must be static visual facts only — no motion, no age, no sound

---

## Key Files Modified Today
- `app/services/production_planner.py` — checklist prompt, intent extraction, plan generation rules
- `templates/index.html` — timer element in production phase
- `static/js/production.js` — timer state + logic
