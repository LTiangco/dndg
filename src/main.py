# ================================
# Dungeon Master Project Skeleton
# ================================
# Each section below represents a separate file in the project
# directory.  Copy these into matching paths, or run `python -m
# dungeon_master.main` after installing the package layout.

# ──────────────────────────────────
# core/__init__.py
# ──────────────────────────────────
"""Core domain logic: no I/O here."""

# ──────────────────────────────────
# core/dm.py
# ──────────────────────────────────
from __future__ import annotations

from pathlib import Path
from typing import List

from .state import GameState
from .party import Party
from .dice import DiceRoller
from .mechanics.combat import CombatEncounter
from .mechanics.growth import GrowthEngine
from ..adapters.persistence import Serializer
from ..content.story_setup import StorySetup


class DM:
    """Director & game loop orchestrator (pure domain)."""

    def __init__(self, rng_seed: int | None = None) -> None:
        self.dice = DiceRoller(rng_seed)
        self.ruleset = None  # Will hold a RuleSet instance (future work)
        self.party: Party | None = None
        self.story: StorySetup | None = None
        self.current_scene_idx: int = -1

    # ──────────────── Public API ────────────────
    def start(self, story_path: Path) -> None:
        """Prepare the campaign: load story & create characters."""
        self.story = StorySetup.load(story_path)
        # TODO: plug in CharSetup UI here
        self.party = Party([])  # placeholder for created characters
        self.current_scene_idx = 0

    def play_next(self) -> None:
        """Advance the game by one logical step (one scene)."""
        if self.story is None or self.party is None:
            raise RuntimeError("DM.start() must be called first.")

        scene = self.story.scenes[self.current_scene_idx]
        scene.enter(self.party, self)

        self.current_scene_idx += 1
        if self.current_scene_idx >= len(self.story.scenes):
            self.win_screen()

    # ──────────────── Helpers ────────────────
    def save(self, path: Path) -> None:
        state = GameState.from_dm(self)
        Serializer.save(state, path)

    def load(self, path: Path) -> None:
        state = Serializer.load(path)
        state.apply_to_dm(self)

    # ──────────────── UI hooks ────────────────
    def win_screen(self) -> None:
        print("Congratulations, you won!")

    def lose_screen(self) -> None:
        print("Game over – better luck next time.")


# ──────────────────────────────────
# core/state.py
# ──────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict


def _dataclass_from_dict(cls, data: Dict[str, Any]):
    return cls(**data)


@dataclass
class GameState:
    """Serializable snapshot of an in‑progress campaign."""

    party: Dict[str, Any]
    story_state: Dict[str, Any]
    current_scene_idx: int
    rng_state: Any = field(repr=False)

    # ───────── Serialization helpers ─────────
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        return _dataclass_from_dict(cls, data)

    # ───────── DM bridge ─────────
    @classmethod
    def from_dm(cls, dm: "DM") -> "GameState":
        return cls(
            party=dm.party.to_dict() if dm.party else {},
            story_state=dm.story.to_dict() if dm.story else {},
            current_scene_idx=dm.current_scene_idx,
            rng_state=dm.dice.get_state(),
        )

    def apply_to_dm(self, dm: "DM") -> None:
        from .party import Party  # local import to avoid cycles
        from ..content.story_setup import StorySetup

        dm.party = Party.from_dict(self.party)
        dm.story = StorySetup.from_dict(self.story_state)
        dm.current_scene_idx = self.current_scene_idx
        dm.dice.set_state(self.rng_state)


# ──────────────────────────────────
# core/character.py
# ──────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Stats:
    str: int = 10
    dex: int = 10
    con: int = 10
    int: int = 10
    wis: int = 10
    cha: int = 10

    def modifier(self, score: int) -> int:
        return (score - 10) // 2


@dataclass
class Inventory:
    items: list[str]
    gold: int = 0


@dataclass
class Character:
    name: str
    stats: Stats = Stats()
    hp: int = 10
    xp: int = 0
    inventory: Inventory = Inventory(items=[])

    # ───────── Serialization ─────────
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        return cls(**data)


# ──────────────────────────────────
# core/party.py
# ──────────────────────────────────
from __future__ import annotations

from typing import List, Dict, Any

from .character import Character


class Party(list):
    """A list‑subclass that adds party‑wide helpers."""

    def any_alive(self) -> bool:
        return any(ch.hp > 0 for ch in self)

    def to_dict(self) -> Dict[str, Any]:
        return {"members": [c.to_dict() for c in self]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Party":
        return cls(Character.from_dict(d) for d in data["members"])


# ──────────────────────────────────
# core/dice.py
# ──────────────────────────────────
import random
import re
from typing import Tuple

_roll_re = re.compile(r"(?P<num>\d+)d(?P<sides>\d+)(?P<mod>[+-]\d+)?")


class DiceRoller:
    """Parses dice notation like `2d6+3` and rolls with RNG injection."""

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def roll(self, expr: str) -> Tuple[int, list[int]]:
        match = _roll_re.fullmatch(expr)
        if not match:
            raise ValueError(f"Invalid dice expression: {expr}")
        num = int(match["num"])
        sides = int(match["sides"])
        mod = int(match["mod"] or 0)
        rolls = [self._rng.randint(1, sides) for _ in range(num)]
        return sum(rolls) + mod, rolls

    # RNG state for save/load
    def get_state(self):
        return self._rng.getstate()

    def set_state(self, state):
        self._rng.setstate(state)


# ──────────────────────────────────
# core/mechanics/__init__.py
# ──────────────────────────────────
"""Combat, growth, and other rule engines."""

# ──────────────────────────────────
# core/mechanics/combat.py
# ──────────────────────────────────
from __future__ import annotations

from typing import List

from ..character import Character


class CombatEncounter:
    """Very barebones until fleshed out."""

    def __init__(self, players: List[Character], monsters: List[Character]):
        self.players = players
        self.monsters = monsters

    def run(self) -> None:
        print("[Combat begins – stub]")
        # TODO: initiative, rounds, victory check


# ──────────────────────────────────
# core/mechanics/growth.py
# ──────────────────────────────────
from __future__ import annotations

from ..character import Character


class GrowthEngine:
    """Applies XP, levels, and loot after encounters."""

    @staticmethod
    def apply(scene, party):
        print("[Growth stub – grant XP / loot]")


# ──────────────────────────────────
# adapters/__init__.py
# ──────────────────────────────────
"""I/O adapters: CLI, WebSocket, persistence, etc."""

# ──────────────────────────────────
# adapters/persistence.py
# ──────────────────────────────────
import json
from pathlib import Path
from typing import Any


class Serializer:
    """JSON save/load wrapper around GameState objects."""

    @staticmethod
    def save(state: Any, path: Path):
        with Path(path).open("w", encoding="utf-8") as fp:
            json.dump(state.to_dict(), fp, indent=2)

    @staticmethod
    def load(path: Path):
        from ..core.state import GameState  # circular import guard

        with Path(path).open(encoding="utf-8") as fp:
            data = json.load(fp)
        return GameState.from_dict(data)


# ──────────────────────────────────
# adapters/cli.py
# ──────────────────────────────────
from pathlib import Path

from ..core.dm import DM


def main():
    dm = DM()
    dm.start(Path(__file__).parent.parent / "content" / "campaigns" / "goblin_caves.yml")

    while True:
        cmd = input("[enter] next, s)ave, q)uit → ")
        if cmd.lower().startswith("s"):
            dm.save(Path("save.json"))
            print("Saved.")
        elif cmd.lower().startswith("q"):
            break
        else:
            dm.play_next()


if __name__ == "__main__":
    main()


# ──────────────────────────────────
# adapters/ws.py
# ──────────────────────────────────
"""Reserved for future WebSocket multiplayer adapter."""

# TODO: implement with FastAPI / Starlette


# ──────────────────────────────────
# content/__init__.py
# ──────────────────────────────────
"""Non‑code assets (campaign YAML, monster stats, etc.)"""

# ──────────────────────────────────
# content/story_setup.py
# ──────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any

import yaml


@dataclass
class Scene:
    id: str
    text: str
    monsters: List[str] = field(default_factory=list)
    choices: Dict[str, str] = field(default_factory=dict)  # key → next scene id

    def enter(self, party, dm):
        print(self.text)
        # TODO: load monster stats & start combat if any


@dataclass
class StorySetup:
    scenes: List[Scene]

    # ───────── Factory helpers ─────────
    @classmethod
    def load(cls, path: Path) -> "StorySetup":
        with Path(path).open(encoding="utf-8") as fp:
            raw = yaml.safe_load(fp)
        scenes = [Scene(**s) for s in raw["scenes"]]
        return cls(scenes)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        scenes = [Scene(**s) for s in data["scenes"]]
        return cls(scenes)


# ──────────────────────────────────
# content/campaigns/goblin_caves.yml
# ──────────────────────────────────
# Minimal starter campaign – expand as desired.
scenes:
  - id: intro
    text: |
      You stand before the mouth of a dank cave.  A foul goblin smell
      wafts out.  Your adventure begins!
    monsters: []
    choices:
      deeper: room1

  - id: room1
    text: |
      A pair of goblins shriek and draw rusty blades.
    monsters: [goblin, goblin]
    choices:
      forward: treasure
      flee: intro

  - id: treasure
    text: |
      The chamber glitters with coins.  You have cleared the cave!
    monsters: []
    choices: {}


# ──────────────────────────────────
# main.py (top‑level entry point)
# ──────────────────────────────────
from adapters.cli import main

if __name__ == "__main__":
    main()
