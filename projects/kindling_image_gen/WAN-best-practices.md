# WAN Video Generation: Community Best Practices
*Researched 2026-03-26 — sources at bottom*

---

## 1. Prompt Structure for Smooth Motion

**Formula:** `Subject + Scene + Motion + Camera + Atmosphere/Style`

Keep prompts 80-120 words. Under-specifying = random model defaults. Over-specifying (multiple competing actions) = confusion about what to execute.

**Lead with visible state, then describe the motion.** Tell the model what it sees at frame 1, then what changes.

**Motion descriptions need physics words.** Amplitude, direction, speed. "Walks forward" is worse than "walks slowly forward through shallow water, each step lifting a small splash."

**One action per clip.** This is the #1 community rule. Don't pack two distinct beats into one 5-second generation. A character who stands up, walks to the window, and looks out = 3 clips, not 1. Trying to pack it into one generation produces temporal smearing or the model executes the first action and ignores the rest.

**Describe what shouldn't be static.** Fire crackling, flag waving, hair moving in wind — say it explicitly. The model won't animate background elements by default.

---

## 2. Frame Counts and Duration

**Frame count formula: `4n + 1`** (25, 49, 65, 81, 97, 113, 129...)

**81 frames @ 16fps = ~5 seconds** is the native sweet spot. Quality degrades and glitching appears above 97 frames on the 14B model.

**Minimum usable: 25 frames.** Below this, character identity consistency breaks down in I2V.

| Action Type | Recommended Frames | Duration |
|-------------|-------------------|----------|
| Simple ambient motion (wind, candle flicker, gentle drift) | 49 | 3s |
| Single physical action (sit down, door opens) | 81 | 5s |
| Slow cinematic shot (dolly in, contemplative pan) | 81-97 | 5-6s |
| Fast action (running, jumping, fight move) | 49 max | 3s |

**Fast actions should be shorter, not longer.** Fast actions over long clips loop or degrade.

**Generate at 16 FPS, interpolate to 24/30 FPS afterward** using Flowframes (RIFE). Don't generate at higher FPS natively — costs VRAM without improving quality. RIFE interpolation produces smoother output than native high-FPS generation.

---

## 3. I2V Chaining and Anchor Frames

**The core loop:**
1. Generate Clip 1 (T2V or from seed image)
2. Extract last frame
3. Use that last frame as I2V input for Clip 2
4. Prompt describes what happens from that new starting state
5. Repeat

**The last frame IS the anchor.** Model sees it as "where we are now" and uses text prompt to describe motion forward.

**Upscaling anchor frames (optional):** Lanczos 2x scale on extracted last frame before passing to next I2V. Mitigates detail loss from repeated compression. Avoid AI upscaler between every clip — artifacts compound.

**FLF2V (First-Last Frame to Video):** Wan2.1 workflow where you provide both start AND end image. Model interpolates between them.
- Start and end frames must be spatially coherent
- Text prompt guides HOW the transition happens
- Midpoint artifacts = spatial mismatch between frames
- Best for: controlled camera paths, scene transitions with known endpoints
- Avoid: sharp direction changes, physically discontinuous motion

**Character drift:** Two strategies needed together:
1. Last-frame anchor (visual consistency)
2. Character LoRA trained on subject (identity consistency)

Prompt engineering alone is insufficient for maintaining facial identity across many chained clips.

---

## 4. Multi-Segment Production Planning

**Plan before generating.** Storyboard-first: break full video into 4-6 second beats before touching ComfyUI. Each beat = one generation = one scene state + one camera move + one action.

**Beginning-Middle-End at the beat level.** Even within a single 5-second clip, something needs to change. Standing still is not a video; standing then slowly looking up is.

**Lock seed + resolution before iterating.** Same prompt at 480p vs 720p produces meaningfully different motion and framing. Pick one resolution for a project and commit.

**Upscaling strategy:** Generate at 480p or 720p, upscale ONCE at the end using latent video upscaler. Don't upscale per-clip. WAN 2.2 5B latent upscaler is community-preferred.

**Motion vocabulary that works reliably:**
- `slow dolly in` ✅
- `pan left/right` ✅ (direction sometimes non-deterministic)
- `tilt up/down` ✅
- `orbital arc` ✅
- `crane up` ✅
- `tracking shot` ✅
- `close-up`, `wide shot`, `medium shot` ✅
- `whip pan` ❌
- Extremely fast camera moves ❌
- `dolly out` ⚠️ (less reliable than dolly in)

Pan direction is often non-deterministic — design storyboards that can tolerate either direction, or budget for retries.

---

## 5. Common Mistakes

1. **Static description instead of action description.** Beautiful scene, no motion instruction = nearly static output. Video prompts require motion language.

2. **Too many actions in one clip.** #1 failure mode.

3. **Vague camera language.** "Camera moves closer" is weak. "Slow dolly in, center-framed, steady" is actionable.

4. **CFG/guidance scale too high.** Community range: **5-7 for Wan2.1**. Above 7 causes flickering between frames. If seeing frame-to-frame inconsistency, lower CFG to 5 first.

5. **Relying on prompts alone for character consistency.** LoRAs are necessary for longer productions.

6. **Not standardizing resolution.** Same prompt at different resolutions = different video.

7. **Fighting native FPS.** WAN generates at 16 FPS. Generate at 16, interpolate in post.

8. **LoRA weights too high.** Use minimum weight that produces desired effect. High weights cause "laggy" motion — LoRA fights motion generation.

9. **Expecting direction-specific camera compliance on first try.** Budget for retries on pan direction.

---

## Community Baseline Negative Prompt

```
blurry, distorted face, deformed eyes, extra limbs, bad anatomy, artifacts, glitch, motion blur, watermark, text, flickering, duplicate body parts, low resolution, grainy, inconsistent character, identity drift
```

---

## Implications for Kindling

- **ScriptMaster** should know the "one action per beat" rule when planning segments. Each segment = one action, one camera state.
- **Default negative prompt** in plan should include the community baseline above.
- **LoRA training pipeline** is the real fix for long-production character consistency drift.
- **FLF2V** is what the bridge system is doing — the validation and prompting should align with FLF2V best practices (spatially coherent anchors, no impossible motion paths).
- **CFG 5-7** — worth checking what the current ComfyUI workflows are set to.
- **RIFE interpolation** post-production step worth adding to the pipeline.

---

## Sources
- [Ambience AI — WAN 2.1 Prompting Guide](https://www.ambienceai.com/tutorials/wan-prompting-guide)
- [InstASD — Camera Movements in WAN](https://www.instasd.com/post/mastering-prompt-writing-for-wan-2-1-in-comfyui-a-comprehensive-guide)
- [Hugging Face — How to Prompt WAN Models](https://huggingface.co/blog/MonsterMMORPG/how-to-prompt-wan-models-full-tutorial-and-guide)
- [Civitai — I Spent 300 Hours on WAN 2.2](https://civitai.com/articles/23629/i-spent-300-hours-on-wan-22-so-you-dont-have-to)
- [GitHub Issue #32 — Frame count and FPS](https://github.com/Wan-Video/Wan2.1/issues/32)
- [GitHub PR #100 — I2V frame count fix](https://github.com/Wan-Video/Wan2.1/pull/100/files)
- [Next Diffusion — FLF2V in ComfyUI](https://www.nextdiffusion.ai/tutorials/wan-22-first-last-frame-video-generation-in-comfyui)
- [Civitai — WAN 2.2 Long Video Workflow](https://civitai.com/models/2285457/wan-22-long-video-via-multi-step-actions)
- [Civitai — All-in-One I2V Workflow](https://civitai.com/models/2404513/i2v-first-last-frame-loop-upscale-and-interpolate-or-all-in-one-wan-22-workflow)
- [Apatero — CFG Scheduling Guide](https://apatero.com/blog/wan-2-2-cfg-scheduling-hidden-optimization-guide-2025)
- [RunComfy — Character Consistency LoRA Training](https://www.runcomfy.com/trainer/ai-toolkit/wan-2-2-i2v-character-consistency-lora)
- [SimaLabs — Motion Quality Tips](https://www.simalabs.ai/resources/best-tricks-improve-motion-quality-wan2-2-outputs-october-2025)
