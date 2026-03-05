# Waifu: Avatar Panel + Kokoro TTS
*2026-03-05, full day session*

## What We Built

**Avatar Panel:**
- Right-side panel showing character avatar by mood
- LLM tags mood at end of response `[MOOD:xxx]`, stripped from display
- Moods: default, happy, sad, angry, flirty, horny, thinking, shy
- Generation: txt2img for first gen, img2img from default.png for consistency (denoise 0.5)
- Cached per-character per-mood in `memory/avatars/{id}/{mood}.png`
- Regen button deletes cached file, fetches fresh
- `/api/avatar` route handles serve/generate logic

**Kokoro TTS:**
- Replaced piper with Kokoro (hexgrad/Kokoro-82M)
- Service at `/home/bdwatkin/kokoro-tts/` on port 5003
- Systemd service: `kokoro-tts.service`
- ~900MB RAM, minimal GPU, much better voice quality
- Voices: af_heart, af_bella, af_sarah, af_nicole, am_adam, am_michael, bf_emma, bf_isabella, bm_george, bm_lewis
- Nicole was Brent's favorite

**Per-character settings in character editor:**
- Visual description (SD tags for avatar generation)
- SD model (pulls live from Kindling `/sd/models`, not hardcoded)
- Voice (Kokoro voice, overrides global selection)
- SD model dropdown removed from header — now per-character only

**Other fixes:**
- TTS strips `*action*` text before speaking
- Mood regex allows optional space: `[MOOD: flirty]`
- Race condition: skip mood update when generating in-chat image
- Next.js 15 async params fix in avatars route
- TS build errors fixed (SpeechRecognition cast, devIndicators config)
- Mac SSH key setup for Brent (generated ed25519, copied to server)
- VSCode sudoers rule for passwordless systemctl

## Architecture Notes
- Avatar API: GET serves cached or generates; DELETE busts cache
- img2img only runs when default.png exists and mood != default
- No default.png yet = all moods are independent txt2img (happened with Abby)
- Abby described herself as a robot — SD ran with it, results were actually cool
- Kokoro follows same service pattern as Kindling: standalone HTTP, cross-project usable

## What's Left
- Race condition with "show me X" + avatar mood not fully retested
- Per-character voice not tested end-to-end after restart
- Grand vision: lip sync animation (far future)
- The `selectedSdModel` state in page.tsx is still used for avatar fallback and in-chat image gen but has no UI — defaults to juggernaut
