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

## Per‑File Docstrings

Copy‑paste the appropriate snippet as the first lines of each file.

```python
# src/main.py
"""Entry point for the game; parses CLI args and starts a Game instance."""

# src/engine/game.py
"""Orchestrates the high‑level game flow: menu, character creation, campaign loop."""

# src/engine/campaign.py
"""Generates and manages a linear list of StoryBlocks forming a single campaign."""

# src/engine/combat.py
"""Resolves one combat encounter: initiative, attack rolls, damage, victory checks."""

# src/models/character.py
"""Player‑controlled Character with base stats, HP, inventory, and simple actions."""

# src/models/enemy.py
"""NPC Enemy inheriting from Character and adding simple AI action selection."""

# src/models/item.py
"""Data class for items that modify Character stats or are used in encounters."""

# src/models/story_block.py
"""Data class representing a modular narrative unit within a campaign."""

# src/utils/dice.py
"""Utility for parsing and rolling dice expressions such as '2d6+3'."""

# src/cli/interface.py
"""Thin CLI layer: displays text menus, reads input, delegates to Game logic."""
```

---

Happy hacking — and may your crits be natural 20s!

