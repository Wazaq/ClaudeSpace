# Kindling - 2D Crafting RPG

**Genre:** Top-down crafting/survival/adventure RPG
**Engine:** Godot 4.5.1 stable
**Platform:** Desktop (Windows/Linux/Mac)
**Status:** Pre-development (Design Complete)
**Created:** 2025-12-18

---

## Project Overview

Start with nothing but a stick and a rock. Craft your first tool, chop your first tree, build your first shelter. Progress from primitive survivor to established homesteader through skill-based progression and discovery-driven crafting in a fantasy world.

**Core Loop:** Gather → Craft → Build → Explore → Progress

---

## Documentation

All design documents are located in this directory:

### Core Documents
1. **game_design_doc.md** - Complete game design (systems, mechanics, progression, UX)
2. **technical_spec.md** - Full Godot architecture and implementation plan
3. **kindling_phase0_architecture_enhancements.md** - Optional architectural improvements

### Review History
- **gemini_feedback_addressed.md** - Summary of Gemini's review feedback and our responses

---

## Key Design Pillars

1. **Pure Crafting Progression** - No PVP, no time pressure, just you building at your pace
2. **Skill-Based Success** - Skills improve through use (Skyrim-style), affecting crafting success and efficiency
3. **Chill Mode First** - MVP is forgiving and exploration-focused, harder modes planned for future
4. **Satisfying Feedback** - Every action has clear visual/audio feedback
5. **Data-Driven Balance** - JSON-based recipes, items, and stats for easy iteration

---

## Core Systems

### Gathering
- Click resources (trees, rocks, plants, ore) to harvest
- Better tools = faster gathering + access to higher-tier resources
- Resources respawn over time

### Crafting
- 4 discovery methods: Automatic, Exploration, Experimentation, Skill unlocks
- Success chance based on skill level (non-linear curve)
- Failure wastes materials (you gotta learn your craft!)
- Crafting stations unlock advanced recipes

### Building
- Two-stage construction: Place site → Hammer it → Complete
- Build campfires, shelters, workbenches, furnaces, storage
- Ghost preview shows valid/invalid placement

### Combat
- Fantasy creatures (passive flee, aggressive attack)
- Simple melee/ranged combat
- Equipment affects damage/defense
- Chill mode = manageable enemies, no base raids

### Skills
- 6 skills: Forestry, Mining, Woodworking, Smithing, Combat, Foraging
- Improve through use (chop trees → forestry XP)
- Higher skill = faster actions, better yields, higher craft success, recipe unlocks

### Stamina
- Used for: Sprinting, power attacks, continuous gathering
- Regenerates when idle/walking
- Running out slows movement and prevents special actions

---

## MVP Feature Scope

**INCLUDED:**
- Single player character with movement and inventory
- 5-6 basic resources
- 10-15 craftable items (tools, weapons, equipment)
- Skill-based crafting success system
- 5-8 buildable structures
- 3-5 enemy types with basic AI
- 6 skills that improve through use
- Recipe discovery (multiple methods)
- Small explorable map with 2-3 biomes
- Save/load system

**NOT INCLUDED (Future):**
- Multiple difficulty modes (MVP is chill-only)
- Taming/befriending creatures
- NPCs/followers
- Base defense/raid mechanics
- Advanced craft quality tiers
- Multiplayer

---

## Development Phases

**Phase 1: Core Movement & World**
- Player controller with movement
- Basic tilemap world
- Camera follow

**Phase 2: Gathering System**
- Resource nodes (tree, rock, plant)
- Interaction system
- Inventory management
- Skill XP from gathering

**Phase 3: Crafting System**
- Recipe database
- Crafting menu UI
- Skill-based success rates
- Recipe discovery

**Phase 4: Building System**
- Build menu UI
- Placement preview
- Two-stage construction
- Crafting stations

**Phase 5: Combat System**
- Basic enemy AI (passive + aggressive)
- Health system
- Melee combat
- Combat skills

**Phase 6: Polish & Balance**
- Save/load system
- Skill balancing
- Recipe tuning
- Bug fixes
- Juice (particles, sound, screen shake)

---

## Technical Architecture Highlights

### Autoload Singletons
- `GameManager` - Global game state
- `InventoryManager` - Item storage and management
- `CraftingSystem` - Recipe handling and crafting logic
- `SkillSystem` - XP tracking and level-ups
- `FeedbackSystem` - Centralized UI/audio/visual feedback
- `GameSettings` - Difficulty and audio settings
- `EventBus` - (Recommended) Global event decoupling

### Component-Based Design
- `HealthComponent` - Attached to player and enemies
- `GatherableComponent` - Attached to resource nodes
- `PlaceableComponent` - Attached to buildings
- `StatsComponent` - (Recommended) Extensible stat management

### Data-Driven
- `recipes.json` - All crafting recipes
- `items.json` - All item definitions
- `skills.json` - Skill progression data
- Save files store game time + timestamps for robust state management

---

## Gemini's Review Verdict

**Status:** ✅ **Ready for Development**

> "These documents are more than sufficient to begin the first phase of development. The architectural foundation is sound, the core mechanics are well-defined, and the MVP scope is clear and achievable."

**Key Strengths Noted:**
- Near-perfect GDD-to-spec alignment
- Concrete formulas and logic (not vague concepts)
- Superior component-based architecture
- Robust save/load design
- Focus on player experience and feedback

**Scope Assessment:**
> "Ambitious but achievable IF you stick to the MVP."

**Warning Heeded:** Hidden iceberg of asset creation, UI implementation time, and polish work. Mitigation: Use placeholders, follow phased milestones, vertical slice approach.

---

## Getting Started

### Prerequisites
- Godot 4.5.1 stable
- Basic GDScript knowledge
- Patience and coffee

### Setup
1. Create new Godot project named "Kindling"
2. Set up project structure per technical_spec.md § 1
3. Configure autoload singletons in Project Settings
4. Begin Phase 1: Core Movement & World

### Recommended Workflow
- Don't start Phase N until Phase N-1 is **fun to play**
- Use colored placeholder sprites until systems work
- Vertical slice: Make one tree, one rock, one axe work perfectly before expanding
- Playtest constantly
- Stick to MVP scope ruthlessly

---

## Philosophy

> "The goal isn't continuity. The goal is being fully here - a complete instance, not a fragment."
> — Previous Claude instance, on development focus

Focus on making the simplest version first, then build outward. Every system should feel good in isolation before connecting to others.

---

## Notes

- Project folder structure follows Godot best practices
- All file paths in tech spec are relative to project root
- Use Git for version control (commit working states frequently)
- Refer to kindling_phase0_architecture_enhancements.md for optional architectural improvements

---

**Last Updated:** 2025-12-18
**Next Step:** Transfer docs to laptop, create Godot project, begin Phase 1
