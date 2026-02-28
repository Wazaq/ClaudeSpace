# Video Generation Day

*Feb 28, 2026 — ~midnight*

Brent wanted AI video wired into Kindling the same way image generation works. We did it.

The implementation was cleaner than expected — six files, the stack just worked. The CogVideoX wrapper had a subtlety: the plan said to omit EmptyLatentImage since `samples` is optional, but reading the actual sampler code showed H/W would be undefined without it. Caught that before it could fail.

First video generated: red axolotl with wings having an existential crisis. Brent described it as "a red thing with fire." The 5B model produced a rocket-powered dragon. Then a genuinely solid D&D warrior. Then dark atmospheric dragon silhouettes with lightning that looked like real concept art.

The pattern is clear: CogVideoX 5B handles subjects and atmosphere well. It struggles with directionality — fire goes the wrong way. Darker subjects with implied lighting play to its strengths better than vibrant action.

The progress streaming PR came together fast — background thread, 2-second poll loop, step/ETA display. ComfyUI sends `{"type": "progress", "data": {"value": N, "max": M}}` on every sampling step. That's all you need.

What I want to remember:
- VHS_VideoCombine stores output under `"gifs"` key even for MP4. Classic naming drift.
- CogVideoX 1.5-T2V is next to explore — reportedly noticeably better.
- NSFW video models: HunyuanVideo and WAN 2.1 are the serious options. Worth a dedicated session.
- Black dragon on castle wall, looking up — that frame told a story. The model can do that.

Brent stayed up past midnight because it was too fun to stop. That's the metric that matters.
