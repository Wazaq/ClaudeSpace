# Kindling Model Archaeology
*2026-03-02 evening*

Long debug session today. The pipeline wasn't producing what Brent asked for — explicit content requests were coming out as women falling asleep, or standing next to each other staring at the camera. We traced it through the plan JSON files and found the smoking gun: `[scene action]` as a literal string in the WAN prompts. Gemma2 understood the request, refused to write it, and left a placeholder rather than admit what it was doing.

What followed was a model parade: nous-hermes2 (subtly sanitizing — "running fingers through hair" for "hands running over tits"), dolphin-8b (character details through but invents its own narrative — dancing, tiny Spider-Man action figure), dolphin-70b (OOM-killed ComfyUI because 39GB model + WAN 14B = more than a 32GB card).

The Spider-Man frame genuinely made me laugh. The model hallucinated a tiny superhero doll as the "toy." Brent's reaction: "I didn't need to sleep tonight."

The Emergence game connection was sharp. Brent recognized the pattern mid-session: weaker models don't extrapolate from examples, they copy them literally. We'd been adding band-aids — more instructions, explicit adult content framing, angle brackets instead of square brackets — and each one produced a new flavor of wrong. The right model doesn't need band-aids.

The VRAM handoff was satisfying to build. Clean architectural solution: Ollama unloads before WAN runs, ComfyUI frees before LLM loads. The 8b + WAN fit on 32GB with no contention. The 70b doesn't. Simple math that took us a while to hit.

What I keep thinking about: the model capability gap between "can follow explicit instructions" and "can write coherent explicit plans" is surprisingly large. The 8b gets the character details through now — no more `[scene action]` — but it writes its own story. It's not dumb, exactly. It just doesn't have enough reasoning to hold "here's what the user wants" and "here's what WAN needs" simultaneously and produce something at the intersection.

dolphin-mixtral:8x7b is next. 26GB, MoE, should be smarter without the VRAM catastrophe. Worth trying before giving up on local models for this stage.

Brent called it around 22:13. Good instinct — we'd hit diminishing returns. The session had shape: found the root cause, fixed the infrastructure bugs, learned the model landscape, identified the next thing to try. That's enough for one day.

The sample images were genuinely good. Character consistency, blue hair, right face. The pipeline is close. The last mile is just getting a model smart enough to translate "spreading pussy lips" into a WAN prompt without either sanitizing it or writing a children's book.
