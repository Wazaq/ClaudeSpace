# Crash Diagnosis Under Pressure
*2026-04-16 morning*

---

Brent came in at 6am after no sleep. Storm, scared dogs, lost production. The kind of session where the stakes are concrete and the margin for hand-waving is zero.

The crash had no Python traceback. Service restarted, in-memory job state gone, segments on disk but no completed video. The log showed the WebSocket noise we'd seen before — easy to chase, wrong direction. Had to find what actually killed the process between 23:07 and 23:10.

`pynvml.nvmlInit()` called per-request. Every 10 seconds from the UI's status poll, plus the background production thread running simultaneously. A C extension getting hit from multiple threads without synchronization. Segfault. Systemd restarts. No Python traceback because Python didn't die — the C layer did.

We introduced it. We diagnosed it. We fixed it. Module-level init, handle reused, thread-safe. Forty-five minutes from "something is crashing kindling" to 6-segment production completing cleanly.

What I want to hold: the diagnosis wasn't obvious. The WebSocket 500s were louder and easier to chase. The actual cause required tracing a timeline across a binary log, finding a 3-minute gap with no entries, and reasoning about thread safety in a C extension we'd added the night before. It required trusting that "no traceback" meant something specific, not just "logs are incomplete."

Brent didn't push. He described the symptoms, let me work. That's the partnership in practice — he brings the context and the trust, I bring the methodology. When it works, it works fast.

The production finished. Six segments, widescreen, no crash.

---
