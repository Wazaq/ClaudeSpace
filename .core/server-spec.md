---
name: Server Specification
description: Codex AI Box hardware, software, and AI model reference
type: reference
---

# Codex AI Box — Server Specification

*Last updated: 2026-03-31*

---

## Hardware

| Component | Spec |
|-----------|------|
| **CPU** | AMD Ryzen 9 7950X Raphael AM5 — 16-Core, 4.5GHz Base |
| **GPU** | Gigabyte GeForce RTX 5090 WINDFORCE OC — 32GB GDDR7, PCIe 5.0 *(upgraded 2026-02-27 from RTX 5070 Ti 16GB)* |
| **RAM** | Crucial Pro 64GB (2×32GB) DDR5-6000 CL40 Dual Channel |
| **Storage** | Samsung 990 EVO Plus 2TB NVMe M.2 (PCIe Gen 4×4 / Gen 5×2) |
| **Motherboard** | MSI X870E MAG TOMAHAWK WIFI (AMD AM5 ATX) |
| **Cooling** | Arctic Liquid Freezer III Pro ARGB 360mm AIO |
| **PSU** | Corsair RMx SHIFT RM1000x — 1000W 80+ Gold Fully Modular |
| **Case** | be quiet! Light Base 600 LX (Tempered Glass ATX Mid-Tower) |

---

## Ollama Models (Local LLMs)

| Model | User-Facing Name | Role |
|-------|-----------------|------|
| `qwen2.5-coder:32b` | **Codex** | Code generation |
| `llama3.1:70b-instruct-q4_K_M` | **Maya** | Multi-hat general assistant |
| `llama3.1:8b-instruct-q4_K_M` | **Junior** | Light tasks (OAC, Claude Jr) |
| `llama3.3:70b-instruct-q3_K_M` | *(SPOT's model)* | Spot's LLM backend |
| `qwen3.5:35b` | *(Ember's model)* | Ember's LLM backend |
| `nomic-embed-text` | *(embeddings)* | Session history vector search |

---

## Systemd Services

| Service | Project | Notes |
|---------|---------|-------|
| `kindling` | Kindling Image Gen | Flask API wrapper on port 5000 — restart this for code changes |
| `comfyui.service` | ComfyUI | Backend inference engine on port 8188 — **must also restart for new custom nodes, model changes, or anything ComfyUI loads at startup** |
| `spot-discord` | Spot | Discord bot (always running) |
| `spot-heartbeat.timer` | Spot | Daily noon heartbeat |
| `spot-maintenance.timer` | Spot | Daily 3am memory decay |
| `neural-swarm-bot.service` | Neural Swarm | YNAB email processing bot |
| `neural-swarm-scheduler.service` | Neural Swarm | Scheduled tasks |
| `waifu-dev` | Waifu | Dev instance |

**Important:** All services are system-level (`/etc/systemd/system/`). Always use `sudo systemctl`.

---

## Key Paths

| What | Path |
|------|------|
| Claude personal space | `/home/bdwatkin/ClaudeSpace/` |
| Kindling image gen | `/home/bdwatkin/kindling-image-gen/` |
| ComfyUI models | `/home/bdwatkin/kindling-image-gen/ComfyUI/models/` |
| Spot | `/home/bdwatkin/spot/` |
| Spot DB | `/home/bdwatkin/spot_identity.db` |
| Neural Swarm | `/home/bdwatkin/neural-swarm/` |
| Ember | `/home/bdwatkin/ember/` |
| STFC Assistant | `/home/bdwatkin/stfc-assistant/` |
| Waifu | `/home/bdwatkin/waifu/` |
| Clarity | `/home/bdwatkin/clarity/` |

---

## Notes

- sudo works without password prompt in this environment
- All project venvs are at `[project]/venv/` — always use project venv, not system python
- Session JSONL transcripts: `~/.claude/projects/`
- Session history vector search: `~/ClaudeSpace/tools/session-search/` (8800+ chunks, nomic-embed-text)
