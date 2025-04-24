# D&D Roguelike (working title)

A minimal, text‑based RPG that assembles a **random yet coherent** adventure from plug‑and‑play story blocks (intro → encounters/events → resolution). Built in Python, played in the terminal, and organized for incremental growth.

---

## Project Milestones

| Milestone                     | Goal                                     | Deliverable                                              |
| ----------------------------- | ---------------------------------------- | -------------------------------------------------------- |
| **M1 – Project Bootstrap**    | Set up repo, virtual‑env, directory tree | Working `Dice` utility • initial commit pushed to GitHub |
| **M2 – Characters & Enemies** | Implement player/enemy dataclasses       | Unit‑tested `Character`, `Enemy`, `Item` models          |
| **M3 – Campaign Generator**   | Load JSON blocks & build linear campaign | `Campaign.next_block()` returns ordered‑random sequence  |
| **M4 – Combat Loop**          | Dice‑based turn combat                   | `Combat` resolves encounters until one side’s HP ≤ 0     |
| **M5 – CLI Wrapper (MVP)**    | Playable demo                            | `main.py` runs full game in the terminal                 |

> **Tip:** Treat each milestone as its own small pull‑request; keep diffs focused and reviewable.

---

## Implementation Plan (High Level)

1. **Bootstrap**   – Create repo in VS Code, initialise Git, add `.venv`, push.
2. **Core Utilities** – Finish `utils/dice.py`; add pytest for edge‑cases.
3. **Domain Models** – Build dataclasses in `models/`; implement basic inventory.
4. **Story Data**   – Author JSON story blocks in `data/blocks/`.
5. **Campaign Logic** – Assemble orderly‑random block list in `engine/campaign.py`.
6. **Combat Engine** – Dice rolls, initiative, damage in `engine/combat.py`.
7. **Game Orchestrator** – High‑level loop in `engine/game.py`.
8. **CLI Layer**    – Text I/O only in `cli/interface.py`; no business logic.
9. **Polish & Docs** – README updates, docstrings, type hints, CI.

---

## Directory Layout

```
dnd_roguelike/
├── README.md
├── pyproject.toml
├── .gitignore
├── data/
│   └── blocks/
│       ├── intro.json
│       ├── encounters.json
│       ├── events.json
│       └── resolution.json
├── src/
│   ├── main.py
│   ├── engine/
│   │   ├── game.py
│   │   ├── campaign.py
│   │   └── combat.py
│   ├── models/
│   │   ├── character.py
│   │   ├── enemy.py
│   │   ├── item.py
│   │   └── story_block.py
│   ├── utils/
│   │   └── dice.py
│   └── cli/
│       └── interface.py
└── tests/
    └── test_campaign.py
```

---

## Game Logic

|File | Class | Responsibility (one‑liner)|
|-----|-------|---------------------------|
|utils/dice.py | Dice (static) | Parse “XdY+Z” strings and return random rolls.|
|models/story_block.py | StoryBlock (@dataclass) | Holds description, difficulty, block_type.|
|models/character.py | Character (@dataclass) | Player attributes, attack, take_damage, basic inventory.|
|models/enemy.py | Enemy(Character) | Adds AI stub: decide_action().|
|models/item.py | Item (@dataclass) | Name, modifiers (e.g., +2 strength).|
|engine/campaign.py | Campaign | Load JSON, build ordered‑random block list, expose next_block().|
|engine/combat.py | Combat | Resolve one encounter: turn order, roll to‑hit, damage.|
|engine/game.py | Game | High‑level loop: menu → create character → play campaign.|
|cli/interface.py | CLI | Display menus, read user input, call Game methods.|

---

Happy hacking — and may your crits be natural 20s!

