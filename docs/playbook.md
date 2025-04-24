Below is a **Python-centric “playbook”** you can keep beside you while you build.  It lists the core classes, grouped by layer, with the single-sentence *job description* for each and the key methods/attributes you’ll probably need.  Think of it as a living contract: you can add columns (e.g. “Events emitted”, “Thread-safety”) as the project grows.

---

## 0. Naming conventions

| Symbol | Meaning |
|--------|---------|
| **⬛**  | Pure domain logic (no I/O) → easiest to unit-test |
| **🟦** | Adapter that touches the outside world (files, sockets, CLI, etc.) |
| **▷**  | Composition (“has-a”) |
| *italics* | Interface / abstract base class |

---

## 1. Orchestration layer

| Class | Layer | Responsibility | Key fields / methods |
|-------|-------|----------------|----------------------|
| **DM** | ⬛ | High-level game director & state machine | `start()`, `play()`, `save(path)`, `load(path)`, `players`, `story`, `dice`, `ruleset`, `rng` |
| **GameState** | ⬛ | *Serializable* snapshot of everything mutable | `players`, `current_scene_id`, `story_state`, `log` |
| **SessionManager** | 🟦 | Wraps a `DM` instance and exposes multiplayer hooks (WebSocket or CLI) | `connect(player_id)`, `dispatch_command()`, `broadcast()` |

---

## 2. Domain: characters & parties

| Class | Layer | Responsibility |
|-------|-------|----------------|
| **Character** | ⬛ | Stats, inventory, abilities, conditions, XP |
| **Party** | ⬛ | Collection ▷ `Character` + party-wide actions (`any_alive()`, `surrendered`) |
| **Inventory** | ⬛ | Items, gold, capacity rules |
| **Stats** | ⬛ | STR, DEX, … + derived modifiers; `apply_level_up()` |

---

## 3. Domain: stories & scenes

| Class / Interface | Layer | Responsibility |
|-------------------|-------|----------------|
| *IScene* | ⬛ | Duck-type: must implement `enter(party, dm)` and return a `SceneOutcome` |
| **Scene** | ⬛ | Concrete implementation loaded from JSON/YAML (text, monsters, choices) |
| **Encounter** | ⬛ | Base for `CombatEncounter`, `SocialEncounter`, etc. |
| **Choice** | ⬛ | Presents branching options, resolves to next-scene ID |
| **StoryGraph** | ⬛ | Directed acyclic graph (or full graph) of scene IDs; `next(scene_id, branch_key)` |
| **StorySetup** | ⬛ | Factory: loads a campaign file, applies difficulty tweaks, shuffles, hands a `StoryGraph` to the DM |

---

## 4. Mechanics

| Class | Layer | Responsibility |
|-------|-------|----------------|
| **DiceRoller** | ⬛ | Low-level `roll("2d6+3")` → `RollResult`; configurable RNG seed |
| **RuleSet** | ⬛ | Encapsulates edition-specific math (advantage, crits, proficiency) |
| **InitiativeTracker** | ⬛ | Turn order queue |
| **CombatEncounter** | ⬛ | Runs rounds until one side is defeated; emits loot / XP |
| **GrowthEngine** | ⬛ | Calculates XP gain, level-up thresholds, loot tables |

---

## 5. Persistence & content

| Class / File | Layer | Responsibility |
|--------------|-------|----------------|
| **Serializer** | 🟦 | `<GameState> ↔ JSON` (or msgpack) |
| **CampaignLoader** | 🟦 | Reads YAML/JSON scene files, validates schema, returns `StorySetup` |
| `*.yml` / `*.json` | — | Human-editable campaign files (monsters, choices, text) |

---

## 6. User interfaces (pluggable)

| Component | Approach |
|-----------|----------|
| **CLIAdapter** | Simplest: `input()`/`print()` loop talking to `SessionManager` |
| **WebSocketAdapter** | For multiplayer browser UI later |
| **SaveFileAdapter** | Implements “Save/Load” menu via `Serializer` |

---

## 7. Suggested file/folder layout

```
dungeon_master/
├─ core/                 # Pure domain logic
│  ├─ dm.py
│  ├─ state.py
│  ├─ character.py
│  ├─ party.py
│  ├─ dice.py
│  └─ mechanics/
│     ├─ combat.py
│     └─ growth.py
├─ content/
│  ├─ campaigns/
│  │  └─ goblin_caves.yml
│  └─ monsters.yml
├─ adapters/
│  ├─ cli.py
│  ├─ ws.py
│  └─ persistence.py
└─ main.py               # Entry point (creates CLIAdapter + SessionManager)
```

---

## 8. How it all talks in single-player mode

1. **main.py** starts `CLIAdapter`, which spins up a `SessionManager`.
2. `SessionManager` builds `DM`, then calls `dm.start()`.
3. `DM.start()`:
   * Loads a `StorySetup` via `CampaignLoader`.
   * Runs `CharSetup` (interactive or premade characters).
4. The CLI loop keeps feeding commands to `SessionManager`, which delegates to `DM.play()` for the next state transition.
5. On “save”, the adapter requests `dm.save("savefile.json")`; the `Serializer` dumps the `GameState`.

---

## 9. Next concrete step

If you give me the green light, I can drop a **fully wired skeleton** (empty methods, docstrings, one-line YAML scene) into the canvas so you can run `python main.py` and watch it print “Coming soon…”. We’d then flesh out each module test-first.

Let me know if that skeleton would be helpful or if you’d like to zoom in on any slice (e.g. DiceRoller API, Story YAML schema) first!