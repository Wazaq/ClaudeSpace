# Kindling - Phase 0: Architecture Enhancements
**Optional improvements to implement before or during early development**
**Source:** Gemini's second review (2025-12-18)
**Status:** Not required for MVP, but highly recommended for cleaner architecture

---

## Minor Gaps to Address During Development

### 1. Player State Machine
**Current:** Player uses boolean flags (`is_sprinting`, etc.)
**Issue:** Can lead to logical conflicts (e.g., attacking while gathering)

**Recommendation:** Implement formal state machine

```gdscript
# player.gd
enum PlayerState {
    IDLE,
    MOVING,
    GATHERING,
    ATTACKING,
    BUILDING,
    SPRINTING
}

var current_state: PlayerState = PlayerState.IDLE

func change_state(new_state: PlayerState):
    match current_state:
        PlayerState.GATHERING:
            # Clean up gathering animation/logic
            pass
        PlayerState.ATTACKING:
            # Clean up attack animation/logic
            pass

    current_state = new_state

    match new_state:
        PlayerState.IDLE:
            play_animation("idle")
        PlayerState.MOVING:
            play_animation("walk")
        PlayerState.GATHERING:
            play_animation("gather")
        # etc...
```

**Benefits:**
- Prevents conflicting actions
- Cleaner animation management
- Easier debugging

---

### 2. Tool Equipping UI Flow
**Current:** Tech spec mentions `current_tool` but not how it's equipped

**Need to Define:**
- How does player select/equip tools?
- Hotbar with number keys (1-9)?
- Right-click in inventory to equip?
- Automatic equipping when needed?

**Recommended Approach (MVP):**
```
- Hotbar: Bottom of screen, 10 slots
- Number keys 1-0 to equip from hotbar
- Right-click item in inventory → "Equip to Hotbar" menu
- Tool auto-equips to first empty hotbar slot when crafted
- Currently equipped tool shows highlight in hotbar
```

**Implementation:**
- Add hotbar UI scene
- Expand InventoryManager with `equip_to_hotbar(slot_index, item_id)`
- Player checks `hotbar[0]` through `hotbar[9]` for current_tool on key press

---

### 3. Skill Progression Terminology Clarity
**Current:** GDD says "not XP/levels" but spec uses `add_skill_xp()`

**Clarification:** It IS an XP system, just XP-per-use rather than XP-per-kill/quest

**Terminology Fix:**
- Update GDD § 2.5 to say: "Skills improve through use (XP-per-use system), not traditional quest/kill XP"
- This maintains the design philosophy while being technically accurate

---

## Architecture Enhancements (Post-MVP or Early Implementation)

### Enhancement 1: Global EventBus

**Problem:** Systems need direct references to each other to connect signals
**Solution:** Central event bus for maximum decoupling

**Implementation:**

Create `event_bus.gd` autoload:
```gdscript
# scripts/autoloads/event_bus.gd
extends Node

# Crafting Events
signal item_crafted(item_id: String, quantity: int)
signal crafting_failed()

# Skill Events
signal skill_leveled_up(skill_name: String, new_level: int)
signal skill_xp_gained(skill_name: String, amount: int)

# Resource Events
signal resource_gathered(resource_type: String, amount: int, position: Vector2)

# Combat Events
signal enemy_killed(enemy_type: String)
signal player_damaged(amount: int)
signal player_died()

# Building Events
signal building_placed(building_type: String, position: Vector2)
signal building_completed(building_type: String)

# Recipe Events
signal recipe_discovered(recipe_id: String)

# Inventory Events
signal item_added(item_id: String, quantity: int)
signal item_removed(item_id: String, quantity: int)
```

**Usage Example:**

```gdscript
# CraftingSystem emits when craft succeeds
func craft_item(recipe_id: String) -> bool:
    # ... crafting logic ...
    if success:
        EventBus.item_crafted.emit(recipe_id, 1)
        return true

# SkillSystem listens for crafts and grants XP
func _ready():
    EventBus.item_crafted.connect(_on_item_crafted)

func _on_item_crafted(item_id: String, quantity: int):
    var recipe = RecipeDatabase.get_recipe_for_result(item_id)
    add_skill_xp(recipe.skill_required, 10)

# FeedbackSystem also listens to show UI
func _ready():
    EventBus.item_crafted.connect(_on_item_crafted)

func _on_item_crafted(item_id: String, quantity: int):
    show_craft_success(item_id)
```

**Benefits:**
- Systems don't need to know about each other
- Easy to add new listeners without modifying existing code
- Clean separation of concerns
- Easier testing (can emit events manually)

---

### Enhancement 2: Data-Driven Components

**Problem:** Game balance requires code changes (recompiling, testing)
**Solution:** Move hardcoded values to @export component properties

**Example - GatherableComponent:**

**Before (hardcoded):**
```gdscript
func gather():
    if resource_type == "wood":
        SkillSystem.add_skill_xp("forestry", 5)
    elif resource_type == "stone":
        SkillSystem.add_skill_xp("mining", 5)
```

**After (data-driven):**
```gdscript
# gatherable_component.gd
@export var resource_type: String = "wood"
@export var skill_to_grant: String = "forestry"
@export var xp_per_hit: int = 2
@export var yield_amount: int = 3
@export var required_tool: String = "axe"
@export var required_skill_level: int = 0
@export var respawn_time: float = 300.0
@export var health: int = 3

func gather():
    SkillSystem.add_skill_xp(skill_to_grant, xp_per_hit)
    InventoryManager.add_item(resource_type, yield_amount)
    health -= 1
```

**Benefits:**
- Balance entire game in Godot editor without touching code
- Easy A/B testing (duplicate scene, change values)
- Designers can iterate without programming knowledge
- Less error-prone than code changes

**Apply to:**
- GatherableComponent (resource properties)
- HealthComponent (base health, armor, resistances)
- Enemy scenes (damage, speed, aggression range)
- Building scenes (material costs, construction time)

---

### Enhancement 3: Stats Component

**Problem:** Player/enemy stats are simple variables, hard to extend with modifiers
**Solution:** Dedicated StatsComponent for handling base values + modifiers

**Implementation:**

```gdscript
# components/stats_component.gd
class_name StatsComponent
extends Node

@export var base_stats: Dictionary = {
    "max_health": 100,
    "max_stamina": 100,
    "move_speed": 100.0,
    "attack_damage": 10,
    "defense": 0
}

var stat_modifiers: Dictionary = {}

func get_stat(stat_name: String) -> float:
    var base = base_stats.get(stat_name, 0)
    var modifier_total = 0.0

    # Sum all modifiers for this stat
    if stat_modifiers.has(stat_name):
        for mod_value in stat_modifiers[stat_name].values():
            modifier_total += mod_value

    return base + modifier_total

func add_modifier(stat_name: String, modifier_id: String, value: float):
    if not stat_modifiers.has(stat_name):
        stat_modifiers[stat_name] = {}
    stat_modifiers[stat_name][modifier_id] = value

func remove_modifier(stat_name: String, modifier_id: String):
    if stat_modifiers.has(stat_name):
        stat_modifiers[stat_name].erase(modifier_id)

func clear_modifiers(stat_name: String = ""):
    if stat_name.is_empty():
        stat_modifiers.clear()
    else:
        stat_modifiers.erase(stat_name)
```

**Usage:**

```gdscript
# Player equips iron armor
stats.add_modifier("defense", "iron_armor", 10)
stats.add_modifier("move_speed", "iron_armor", -5) # Heavy armor slows you

# Player drinks speed potion
stats.add_modifier("move_speed", "speed_potion", 20)

# Get actual move speed (accounts for all modifiers)
var current_speed = stats.get_stat("move_speed")

# Potion wears off
stats.remove_modifier("move_speed", "speed_potion")
```

**Benefits:**
- Easy to add buffs/debuffs/equipment effects
- Transparent stat calculation
- Clean implementation of status effects
- Supports temporary and permanent modifiers
- Foundation for future systems (skill trees, enchantments, etc.)

**Future Extensions:**
- Percentage-based modifiers (e.g., +10% health)
- Duration tracking for temporary buffs
- Stat caps/floors
- Stat categories (additive vs multiplicative)

---

## Implementation Priority

**Phase 0a (Before Phase 1):**
1. Player state machine (prevents bugs early)
2. Tool equipping UI flow design (needed for core loop)
3. Terminology clarification in GDD (5-minute doc update)

**Phase 0b (During Phase 1-2):**
1. Global EventBus (makes future systems easier)
2. Data-driven GatherableComponent (speeds up balancing)

**Phase 0c (Phase 3+):**
1. Stats Component (needed before complex combat/equipment)
2. Full data-driven approach for all components

---

## Notes

- None of these are REQUIRED for MVP
- All will make development smoother and cleaner
- Gemini strongly recommends EventBus and data-driven components
- Stats Component is "nice to have" but can wait until equipment system

**Gemini's Closing:** *"These documents provide a fantastic starting point for Kindling."*
