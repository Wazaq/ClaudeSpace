# GAME DESIGN DOCUMENT v0.1
**Project Name:** Kindling
**Last Updated:** 2025-12-18

## 1. Core Concept

**Genre:** 2D top-down crafting/survival/adventure RPG
**Platform:** Desktop (Windows via Godot, initial target)
**Difficulty:** Chill mode (forgiving exploration, manageable combat) with harder modes planned for future
**Core Loop:** Gather → Craft → Build → Explore → Progress

**Elevator Pitch:**
Start with nothing but a stick and a rock. Craft your first tool, chop your first tree, build your first shelter. Progress from primitive survivor to established homesteader through skill-based progression and discovery-driven crafting in a fantasy world.

---

## 2. Core Systems

### 2.1 Gathering
- **Resources:** Wood, stone, plants (fiber/food), ores (copper, iron, etc)
- **Mechanics:** Click/interact with resource nodes → play animation → receive items
- **Tools matter:** Better tools = faster gathering, access to higher-tier resources
- **Respawn:** Resources regenerate over time (trees regrow, ore respawns)

### 2.2 Crafting
- **Recipe Discovery:**
  - **Automatic:** Basic recipes unlock automatically when you first obtain the required materials (stick + rock = crude axe)
  - **Exploration:** Recipe Scrolls found in chests or as enemy drops unlock specific recipes
  - **Experimentation:** Crafting menu has "Discovery" tab where players can drag items to experiment - matching a hidden recipe unlocks it permanently
  - **Skill Unlocks:** Some advanced recipes unlock automatically when reaching specific skill levels
- **Crafting Stations:**
  - Hand-crafting (basic items, no station needed)
  - Workbench (tools, weapons)
  - Furnace (smelting ores)
  - Advanced stations unlock as you progress
- **Material Consumption & Success:**
  - Crafting uses exact quantities
  - Success chance based on relevant skill level (low skill = chance to fail and waste materials)
  - Higher skill = higher success rate, eventually 100% for mastered recipes
  - **Chill mode affects combat difficulty, NOT crafting** - you still need to learn your craft

### 2.3 Building
- **Placement System:**
  - Open build menu, select structure
  - Ghost preview shows where it will go (green = valid, red = invalid placement)
  - Click to place construction site (consumes materials)
  - Player must interact with construction site and "hammer" it 3-5 times to complete
  - Completion plays build animation and structure becomes functional
- **Initial Structures:**
  - Campfire (cooking, light)
  - Small shelter (save point/respawn?)
  - Storage chest (expand inventory)
  - Workbench, furnace (crafting stations)
  - Fences/walls (decorative/light defense in harder modes)

### 2.4 Combat
- **Enemies:** Fantasy creatures (not earth animals - we'll design specific creatures later)
  - Passive: Run away when approached (rabbit-equivalent)
  - Aggressive: Attack on sight (wolf-equivalent)
- **Combat Mechanics:**
  - Simple melee/ranged attacks
  - Health system for player and enemies
  - Equipment affects damage/defense
- **Chill mode:** Enemies manageable, respawn limited, no base raids

### 2.5 Skill Progression
- **Skyrim-style:** Skills improve through use, not XP/levels
- **Skill Categories:**
  - Forestry (chopping trees)
  - Mining (gathering ore/stone)
  - Woodworking (crafting wood items)
  - Smithing (crafting metal items)
  - Combat (fighting enemies)
  - Foraging (gathering plants)
- **Benefits:** Higher skill = more efficient (faster, less stamina, better yields), better craft success rate, unlock advanced recipes

### 2.6 Player Resources
- **Health:** Reduced by enemy damage, restored by food/rest
- **Stamina:**
  - Used for: Sprinting, power attacks, continuous gathering/crafting
  - Regeneration: Slowly regenerates when standing still or walking
  - Does NOT regenerate while performing stamina-draining actions
  - Running out of stamina forces slower movement and prevents special actions

---

## 3. Progression Arc

**Early Game (Primitive):**
- Gather stick + rock → craft crude axe
- Chop small trees → get wood
- Build campfire and small shelter
- Gather plants for food
- Craft basic tools (expect failures until skills improve)

**Mid Game (Established):**
- Build workbench and furnace
- Mine copper/iron ore
- Smelt into ingots
- Craft metal tools and weapons (skills improving, fewer failures)
- Explore dangerous areas
- Expand base with storage and crafting stations

**Late Game (Advanced):**
- Access rare resources in difficult areas
- Craft high-tier equipment (master crafters, no failures)
- Build expansive base
- Master all skills
- (Endgame content TBD - bosses? Special areas? Achievements?)

---

## 4. World Design

**Map Size:** Small-to-medium for MVP (expandable later)

**Biomes:**
- Starting area (safe, basic resources)
- Forest (wood, common animals)
- Mountains (stone, ore, dangerous creatures)
- (Additional biomes: swamp? desert? snow? - to be determined)

**Resource Distribution:** Resources get rarer/more valuable further from starting area

---

## 5. UI/UX Feedback

**Player feedback for key events:**

- **Skill Level Up:**
  - Visual: Text popup "Forestry Level 2!" that fades out
  - Audio: Pleasant chime sound
  - Effect: Brief screen flash/particle effect

- **Crafting Success:**
  - Visual: Item icon pops into inventory with bounce animation
  - Audio: Satisfying "craft complete" sound
  - Effect: Small particle burst

- **Crafting Failure:**
  - Visual: "poof" smoke animation, materials disappear
  - Audio: Disappointed "oof" sound
  - UI: Message "Crafting failed! Materials lost."

- **Insufficient Tool/Skill:**
  - Visual: Red "X" icon appears over resource
  - Audio: Dull "thud" sound
  - UI: Tooltip "Requires Iron Pickaxe" or "Mining Skill 5 Required"

- **Low Health Warning:**
  - Visual: Screen edges pulse red
  - Audio: Heartbeat sound intensifies
  - UI: Health bar flashes

- **Low Stamina:**
  - Visual: Character movement slows, slight screen desaturation
  - Audio: Heavy breathing sound
  - UI: Stamina bar flashes yellow

- **Resource Gathered:**
  - Visual: "+5 Wood" floats up from resource node
  - Audio: Appropriate gathering sound (chop, crack, rustle)

- **Building Completed:**
  - Visual: Construction sparkle/dust effect
  - Audio: Satisfying "thunk" or build-complete sound
  - Effect: Structure solidifies from ghost preview

---

## 6. MVP Feature List

**INCLUDED:**
- Single player character with movement and inventory
- Gather 5-6 basic resources
- Craft 10-15 items (tools, weapons, basic equipment)
- Skill-based crafting success system
- Build 5-8 structures (campfire, shelter, storage, workbench, furnace, fences)
- 3-5 enemy types with basic AI
- Skill system (6 skills, improve through use)
- Recipe discovery (mix of automatic and found)
- Small explorable map with 2-3 biomes
- Save/load system

**NOT INCLUDED (Future):**
- Multiple difficulty modes
- Taming/befriending creatures
- NPCs/followers
- Base defense/raid mechanics
- Advanced craft quality tiers
- Large map/extensive content
- Multiplayer
