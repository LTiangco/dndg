"""character.py
Core data model representing a playable (or non-playable) character in the game.

This module is designed to stay *framework-agnostic* - you can import it in a
Django/Pydantic/SQLAlchemy project just as easily as in a plain script.  Treat
it as the single source of truth for character-related domain logic; persistence
can be layered on elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Optional

# --------------------------------------------------------------------------- #
# Enumerations & helper functions                                              #
# --------------------------------------------------------------------------- #

class Ability(Enum):
    """The six D&D-style ability scores."""

    STR = "STR"
    DEX = "DEX"
    CON = "CON"
    INT = "INT"
    WIS = "WIS"
    CHA = "CHA"

    @classmethod
    def list(cls) -> List["Ability"]:
        """Return abilities in the canonical order (STR->CHA)."""
        return [cls.STR, cls.DEX, cls.CON, cls.INT, cls.WIS, cls.CHA]


def ability_modifier(score: int) -> int:
    """Return the standard D20 ability modifier for a raw *score*."""
    return (score - 10) // 2


# --------------------------------------------------------------------------- #
# Character dataclass                                                          #
# --------------------------------------------------------------------------- #

@dataclass
class Character:
    """Lightweight domain object for a character.

    Feel free to subclass this or extend via *mixins* for bespoke rule sets -
    e.g. adding spell-casting, feats, equipment, or home-brew mechanics. Keep
    core math & invariants here.
    """

    name: str
    race: str  # TODO: replace with enum or separate model when ready
    char_class: str  # TODO: replace with enum or separate model when ready
    level: int = 1
    abilities: Dict[Ability, int] = field(
        default_factory=lambda: {ability: 10 for ability in Ability}
    )
    max_hp: Optional[int] = None  # can be set once CON & hit die are finalised

    # Derived fields (computed in __post_init__). These are intentionally *not*
    # passed via constructor so we always stay consistent with *level*.
    proficiency_bonus: int = field(init=False)

    # --------------------------------------------------------------------- #
    # Lifecycle helpers                                                    #
    # --------------------------------------------------------------------- #

    def __post_init__(self) -> None:
        if self.level < 1:
            raise ValueError("level must be >= 1")
        self._sync_proficiency_bonus()

    # --------------------------------------------------------------------- #
    # Public helpers                                                       #
    # --------------------------------------------------------------------- #

    def ability_mod(self, ability: Ability) -> int:
        """Convenience wrapper around :func:`ability_modifier`."""
        return ability_modifier(self.abilities[ability])

    @property
    def initiative(self) -> int:
        """Dexterity modifier - override if feats or items apply bonuses."""
        return self.ability_mod(Ability.DEX)

    def level_up(self) -> None:
        """Increment *level* and recalculate derived stats.

        Callers are responsible for increasing *max_hp*, features, spells, etc.
        """
        self.level += 1
        self._sync_proficiency_bonus()

    # ------------------------------------------------------------------ #
    # Internal utilities                                                 #
    # ------------------------------------------------------------------ #

    def _sync_proficiency_bonus(self) -> None:
        """Compute proficiency bonus from *level* (RAW 5e progression)."""
        self.proficiency_bonus = 2 + (self.level - 1) // 4

    # ------------------------------------------------------------------ #
    # Representation                                                     #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:  # pragma: no cover - human-friendly only
        abilities = ", ".join(
            f"{abbr}:{self.abilities[abbr]}({self.ability_mod(abbr):+d})"
            for abbr in Ability.list()
        )
        return (
            f"<Character {self.name} - L{self.level} {self.race} {self.char_class} | "
            f"HP:{self.max_hp or '?'} | {abilities}>"
        )


# --------------------------------------------------------------------------- #
# Demo / quick test (executed only when run directly)                         #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    hero = Character(name="Lyra", race="Elf", char_class="Rogue")
    print(hero)
    hero.level_up()
    print("After levelling:", hero)
