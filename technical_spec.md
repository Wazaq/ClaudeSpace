# TECHNICAL SPECIFICATION v0.1
**Project Name:** Kindling
**Engine:** Godot 4.5.1 stable
**Language:** GDScript
**Target Platform:** Windows Desktop (initial), Linux/Mac later
**Last Updated:** 2025-12-18

---

## 1. Project Structure

```
/project_root/
├── scenes/
│   ├── player/
│   │   ├── player.tscn
│   │   └── player.gd
│   ├── world/
│   │   ├── world.tscn
│   │   ├── tilemap.tscn
│   │   └── biomes/
│   ├── resources/
│   │   ├── tree.tscn
│   │   ├── rock.tscn
│   │   ├── plant.tscn
│   │   └── ore_node.tscn
│   ├── buildings/
│   │   ├── campfire.tscn
│   │   ├── shelter.tscn
│   │   ├── workbench.tscn
│   │   ├── furnace.tscn
│   │   └── storage_chest.tscn
│   ├── enemies/
│   │   ├── base_enemy.tscn
│   │   ├── passive_creature.tscn
│   │   └── aggressive_creature.tscn
│   └── ui/
│       ├── hud.tscn
│       ├── inventory.tscn
│       ├── crafting_menu.tscn
│       └── build_menu.tscn
├── scripts/
│   ├── autoloads/
│   │   ├── game_manager.gd
│   │   ├── inventory_manager.gd
│   │   ├── crafting_system.gd
│   │   ├── skill_system.gd
│   │   ├── recipe_database.gd
│   │   ├── feedback_system.gd
│   │   └── game_settings.gd
│   └── components/
│       ├── health_component.gd
│       ├── gatherable_component.gd
│       └── placeable_component.gd
├── data/
│   ├── recipes.json
│   ├── items.json
│   ├── skills.json
│   └── world_generation.json
└── assets/
    ├── sprites/
    ├── audio/
    └── fonts/
```

---

## 2. Core Systems Architecture

### 2.1 Player System
**Scene:** `player.tscn`
**Script:** `player.gd`

**Components:**
- CharacterBody2D for movement
- AnimationPlayer for animations (idle, walk, chop, mine, attack)
- Camera2D for following player
- Interaction raycast/area for detecting nearby objects

**Properties:**
- `max_health: int`
- `current_health: int`
- `max_stamina: int`
- `current_stamina: int`
- `stamina_regen_rate: float` (per second when idle)
- `base_move_speed: float`
- `sprint_speed_multiplier: float`
- `current_tool: Item` (equipped tool)
- `current_weapon: Item` (equipped weapon)
- `is_sprinting: bool`

**Methods:**
- `_physics_process()` - Handle movement input, stamina regeneration
- `interact()` - Interact with nearby resource/building/enemy
- `take_damage(amount: int)`
- `use_stamina(amount: int) -> bool` (returns false if insufficient)
- `regenerate_stamina(delta: float)` (called when not performing stamina-draining actions)
- `sprint()` - Increases speed, drains stamina continuously

---

### 2.2 Inventory System
**Autoload:** `InventoryManager` (singleton)

**Data Structure:**
```gdscript
var inventory: Array[InventorySlot] = []
var max_slots: int = 20

class InventorySlot:
    var item_id: String
    var quantity: int
    var stack_size: int
```

**Methods:**
- `add_item(item_id: String, quantity: int) -> bool`
- `remove_item(item_id: String, quantity: int) -> bool`
- `has_items(requirements: Dictionary) -> bool`
- `get_item_count(item_id: String) -> int`

**Signals:**
- `inventory_changed()`
- `item_added(item_id, quantity)`
- `item_removed(item_id, quantity)`

---

### 2.3 Crafting System
**Autoload:** `CraftingSystem` (singleton)

**Data Structure (recipes.json):**
```json
{
  "crude_axe": {
    "name": "Crude Axe",
    "requirements": {
      "stick": 1,
      "stone": 1
    },
    "result": "crude_axe",
    "quantity": 1,
    "skill_required": "woodworking",
    "min_skill_level": 0,
    "base_success_rate": 0.7,
    "crafting_station": null,
    "discovered": true
  },
  "iron_sword": {
    "name": "Iron Sword",
    "requirements": {
      "iron_ingot": 3,
      "wood": 1
    },
    "result": "iron_sword",
    "quantity": 1,
    "skill_required": "smithing",
    "min_skill_level": 10,
    "base_success_rate": 0.5,
    "crafting_station": "workbench",
    "discovered": false
  }
}
```

**Methods:**
- `can_craft(recipe_id: String) -> bool` (check materials + skill + station)
- `craft_item(recipe_id: String) -> bool` (roll success, consume materials, grant item)
- `discover_recipe(recipe_id: String)`
- `get_available_recipes() -> Array[String]`
- `calculate_success_chance(recipe_id: String) -> float`
- `try_experiment(ingredients: Array[String]) -> String` (returns recipe_id if match, else "")
- `check_auto_unlock_recipes(new_item_id: String)` (unlocks basic recipes when first obtaining materials)
- `check_skill_unlock_recipes(skill_name: String, new_level: int)` (unlocks recipes at skill thresholds)

**Recipe Discovery Types:**
1. **Automatic:** When player first obtains required materials (e.g., stick + stone unlocks crude_axe)
2. **Exploration:** Recipe Scrolls as loot items - using the scroll unlocks the recipe
3. **Experimentation:** "Discovery" tab in crafting UI where players drag ingredients to test combinations
4. **Skill-based:** Recipes auto-unlock at specific skill levels (stored in recipe.json as `unlock_at_skill_level`)

**Success Calculation:**
```gdscript
func calculate_success_chance(recipe_id: String) -> float:
    var recipe = recipes[recipe_id]
    var skill_level = SkillSystem.get_skill_level(recipe.skill_required)
    var base_rate = recipe.base_success_rate
    var min_skill = recipe.min_skill_level

    # Non-linear curve: early skill points matter more
    # Uses power curve for smoother progression feel
    var skill_above_min = max(0, skill_level - min_skill)
    var skill_bonus = pow(skill_above_min / 20.0, 0.7) * (1.0 - base_rate)

    return clamp(base_rate + skill_bonus, base_rate, 1.0)

# Example progression for base_rate=0.5, min_skill=0:
# Skill 0: 50%, Skill 5: 65%, Skill 10: 76%, Skill 20: 100%
# Early levels feel more impactful, later levels round out to 100%
```

---

### 2.4 Skill System
**Autoload:** `SkillSystem` (singleton)

**Data Structure:**
```gdscript
var skills: Dictionary = {
    "forestry": {"level": 0, "xp": 0},
    "mining": {"level": 0, "xp": 0},
    "woodworking": {"level": 0, "xp": 0},
    "smithing": {"level": 0, "xp": 0},
    "combat": {"level": 0, "xp": 0},
    "foraging": {"level": 0, "xp": 0}
}

const XP_PER_LEVEL: int = 100 # Simple linear progression for MVP
```

**Methods:**
- `add_skill_xp(skill_name: String, amount: int)`
- `get_skill_level(skill_name: String) -> int`
- `check_level_up(skill_name: String)` (auto-called after XP gain)

**Signals:**
- `skill_leveled_up(skill_name, new_level)`
- `skill_xp_gained(skill_name, xp_amount)`

**XP Triggers:**
- Chop tree → forestry XP
- Mine ore/stone → mining XP
- Craft wood item → woodworking XP
- Craft metal item → smithing XP
- Defeat enemy → combat XP
- Gather plant → foraging XP

---

### 2.5 Building System
**Component:** `PlaceableComponent.gd` (attached to building scenes)

**Build Menu UI:**
- Shows available buildings (filtered by discovered + materials)
- Click building → enter placement mode
- Ghost preview follows mouse
- Valid placement: green tint, invalid: red tint
- Click to place construction site (if valid + materials available)

**Two-Stage Construction Process:**
1. **Placement:** Player places "construction site" ghost (materials consumed)
2. **Completion:** Player must interact and "hammer" the site 3-5 times
3. **Finalization:** Construction sparkle animation, structure becomes functional

**Construction Site Properties:**
```gdscript
var building_type: String
var hammer_count: int = 0
var required_hammers: int = 3
var is_complete: bool = false
```

**Placement Validation:**
- Check collision with existing buildings/terrain
- Check minimum distance from other structures (optional)
- Check material availability

**Methods:**
- `enter_placement_mode(building_scene: PackedScene)`
- `update_ghost_preview(mouse_position: Vector2)`
- `try_place_construction_site() -> bool`
- `check_valid_placement(position: Vector2) -> bool`
- `hammer_construction_site()` (increments count, completes if threshold met)
- `complete_construction()` (replaces site with actual building)

---

### 2.6 Resource Gathering
**Component:** `GatherableComponent.gd` (attached to resource nodes)

**Properties:**
- `resource_type: String` (wood, stone, iron_ore, etc)
- `yield_amount: int` (how much you get)
- `required_tool: String` (null, "axe", "pickaxe")
- `required_skill_level: int`
- `respawn_time: float` (seconds, -1 for no respawn)
- `health: int` (how many hits to gather)

**Gathering Flow:**
1. Player interacts with resource node
2. Check if player has correct tool
3. Check if player skill level is sufficient
4. Play gathering animation
5. Reduce resource health
6. Grant skill XP
7. If health reaches 0 → give items, destroy/hide node, start respawn timer

---

### 2.7 Combat System
**Component:** `HealthComponent.gd` (attached to player + enemies)

**Properties:**
- `max_health: int`
- `current_health: int`

**Methods:**
- `take_damage(amount: int)`
- `heal(amount: int)`
- `die()`

**Signals:**
- `health_changed(new_health)`
- `died()`

**Enemy AI (Basic):**
- **Passive:** Wander randomly, flee when player approaches
- **Aggressive:** Wander randomly, chase + attack when player in range

**Enemy Base Script:**
```gdscript
extends CharacterBody2D

@export var movement_speed: float = 50.0
@export var detection_range: float = 100.0
@export var attack_range: float = 20.0
@export var attack_damage: int = 5
@export var attack_cooldown: float = 1.0
@export var is_aggressive: bool = true

var player: Node2D
var state: String = "wander" # wander, chase, attack, flee

func _physics_process(delta):
    match state:
        "wander": wander_behavior()
        "chase": chase_player()
        "attack": attack_player()
        "flee": flee_from_player()
```

---

### 2.8 Feedback System
**Autoload:** `FeedbackSystem` (singleton)

**Purpose:** Centralized system for all player feedback (visual, audio, UI popups)

**Methods:**
- `show_skill_levelup(skill_name: String, new_level: int)`
- `show_craft_success(item_name: String)`
- `show_craft_failure()`
- `show_insufficient_tool(required_tool: String)`
- `show_insufficient_skill(skill_name: String, required_level: int)`
- `show_resource_gathered(resource_name: String, amount: int, position: Vector2)`
- `play_low_health_warning()`
- `play_low_stamina_warning()`

**Implementation:**
- Spawns floating text labels at world positions
- Plays appropriate audio via AudioStreamPlayer
- Triggers screen effects (flashes, pulses) via CanvasModulate
- Manages particle effects (sparkles, poof clouds)

---

### 2.9 Game Settings
**Autoload:** `GameSettings` (singleton)

**Properties:**
```gdscript
var difficulty_mode: String = "chill" # Future: "normal", "hard", "hardcore"
var master_volume: float = 1.0
var sfx_volume: float = 1.0
var music_volume: float = 1.0
```

**Methods:**
- `get_difficulty_multiplier(stat_type: String) -> float`
  - Returns multipliers for enemy health, damage, spawn rates based on difficulty
  - MVP always returns "chill" values
- `save_settings()`
- `load_settings()`

**Difficulty Modifiers (for future modes):**
```gdscript
const DIFFICULTY_MODIFIERS = {
    "chill": {
        "enemy_health": 0.7,
        "enemy_damage": 0.7,
        "enemy_spawn_rate": 0.5
    },
    "normal": {
        "enemy_health": 1.0,
        "enemy_damage": 1.0,
        "enemy_spawn_rate": 1.0
    },
    "hard": {
        "enemy_health": 1.5,
        "enemy_damage": 1.5,
        "enemy_spawn_rate": 1.5
    }
}
```

---

## 3. World Generation

**Approach for MVP:** Pre-designed tilemap (not procedural)

**TileMap Layers:**
- Ground layer (grass, dirt, stone)
- Decoration layer (flowers, small rocks)
- Collision layer (impassable terrain)

**Resource Spawning (MVP Approach):**
- **Manually place resource nodes in Godot editor** for MVP
  - Allows for intentional, natural-looking placement
  - Avoids ugly clumping from random spawning
  - Faster to implement than procedural generation
  - Each node gets unique name/ID for save system (e.g., "Tree001", "Rock023")

**Future Enhancement (Post-MVP):**
- Script-based spawning with Poisson-disc sampling for natural distribution:
  ```gdscript
  # Future: Use Poisson-disc sampling for better resource distribution
  func spawn_resources_procedural():
      var points = poisson_disc_sampling(map_size, min_distance_between_resources)
      for point in points:
          var resource = select_resource_for_biome(point)
          resource.position = point
          add_child(resource)
  ```

---

## 4. Save/Load System

**Save Data Structure (save_game.json):**
```json
{
  "game_time": 3600,
  "player": {
    "position": {"x": 100, "y": 200},
    "health": 80,
    "stamina": 50
  },
  "inventory": [
    {"item_id": "wood", "quantity": 15},
    {"item_id": "stone", "quantity": 8}
  ],
  "skills": {
    "forestry": {"level": 3, "xp": 45},
    "mining": {"level": 1, "xp": 20}
  },
  "discovered_recipes": ["crude_axe", "campfire"],
  "world_state": {
    "resource_nodes": [
      {"id": "tree_001", "last_gathered": 3200, "respawn_time": 300},
      {"id": "rock_042", "last_gathered": 3450, "respawn_time": 600}
    ],
    "placed_buildings": [
      {"type": "campfire", "position": {"x": 150, "y": 250}}
    ]
  }
}
```

**Resource Respawn Logic:**
Each resource node checks on world load:
```gdscript
func check_respawn_on_load(current_game_time: float):
    var time_since_gathered = current_game_time - last_gathered_time
    if time_since_gathered >= respawn_time:
        visible = true # Resource has respawned
        health = max_health
    else:
        visible = false # Still waiting to respawn
```

This approach is more robust than tracking destroyed nodes - nodes determine their own state based on game time.

**Methods:**
- `save_game()`
- `load_game()`
- Auto-save on exit (optional)

---

## 5. Data Files

**items.json:**
```json
{
  "stick": {
    "name": "Stick",
    "description": "A sturdy stick",
    "stack_size": 99,
    "icon": "res://assets/sprites/items/stick.png"
  },
  "crude_axe": {
    "name": "Crude Axe",
    "description": "A basic tool for chopping",
    "stack_size": 1,
    "tool_type": "axe",
    "tool_power": 1,
    "icon": "res://assets/sprites/items/crude_axe.png"
  }
}
```

---

## 6. UI/UX Flow

**HUD:**
- Health bar
- Stamina bar
- Quick-access inventory slots (hotbar)
- Current tool/weapon display

**Menus:**
- Inventory (I key) - Grid view, drag-drop items
- Crafting (C key) - List of recipes, click to craft
- Building (B key) - Grid of buildings, click to enter placement mode
- Skills (K key) - Progress bars for each skill

---

## 7. Performance Considerations

**MVP Optimizations:**
- Object pooling for common entities (trees, rocks)
- Limit active enemies on screen (spawn/despawn based on distance)
- Use TileMap for ground (efficient rendering)
- Simple collision shapes (avoid complex polygons)

**Later Optimizations (if needed):**
- Chunk-based world loading
- LOD system for distant objects
- Multithreaded resource spawning

---

## 8. Development Milestones

**Phase 1: Core Movement & World**
- Player movement controller
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
- Building instantiation
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
