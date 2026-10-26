from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from BaseClasses import Location

from . import items

if TYPE_CHECKING:
    from .world import BananaManiaWorld

# Used if we need to collect all bananas
ALL_BANANAS = -1
# Item Requirements are a list of strings or any ofs
Requirement = tuple["str | AnyOf", ...]


@dataclass(frozen=True)
class AnyOf:
    """One requirement satisfied by ANY of several alternatives.

    Each alternative is itself an AND-set, so
    ``AnyOf("Wormholes", ("Normal Switches", "Fast Switches"))`` reads as
    "Wormholes, OR both switch types". A bare string is shorthand for a one-item set,
    and alternatives may nest further AnyOf groups.
    """

    alternatives: tuple[Requirement, ...]

    def __init__(self, *alternatives: str | AnyOf | Sequence[str | AnyOf]) -> None:
        object.__setattr__(self, "alternatives", tuple(
            (alt,) if isinstance(alt, (str, AnyOf)) else tuple(alt)
            for alt in alternatives
        ))


class Difficulty(Enum):
    """Which difficulty's variant of a stage is being played."""

    STANDARD = "std"
    INTERMEDIATE = "int"
    EXPERT = "exp"


class MissionKind(Enum):
    """The kinds of check a stage can offer. The offset is added to the stage's base_id."""

    CLEAR = ("Stage Clear", 0)
    BANANAS = ("Banana Collector", 1)
    TIME_LIMIT = ("Time Limit", 2)
    GREEN_GOAL = ("Green Goal", 3)
    RED_GOAL = ("Red Goal", 4)
    NONSTOP = ("Nonstop", 5)

    def __init__(self, label: str, offset: int) -> None:
        self.label = label
        self.offset = offset


@dataclass(frozen=True)
class Mission:
    """0-10 seconds means under 10 seconds, so no items needed."""
    seconds: int = 0                   # General time for the mission used for logic, also sets the baseline time limit time
    seconds_int: int | None = None     # If set to none, inherits from seconds. Also is used for logic with time limit
    seconds_exp: int | None = None     # If set to none, inherits from seconds_int, then seconds
    amount: int | None = None          # bananas to collect, or seconds that must remain on the clock
    items: Requirement = ()            # excludes time increases, as those are handled automatically
    items_int: Requirement | None = None  # Inherits from standard items unless specified; () means none needed
    items_exp: Requirement | None = None  # Inherits from items_int, then items


@dataclass(frozen=True)
class StageData:
    base_id: int
    name: str = ""                             # in-game stage name, e.g. "Simple"
    clear: Mission = Mission()  # For clearing, green/red goals inherit from this unless specified otherwise
    missions: dict[MissionKind, Mission] = field(default_factory=dict)
    items: Requirement = ()                    # required by every mission on this stage
    items_int: Requirement | None = None       # Inherits from standard items unless specified; () means none needed
    items_exp: Requirement | None = None       # Inherits from items_int, then items

    def all_missions(self) -> list[tuple[MissionKind, Mission]]:
        """Every check this stage offers, in ID order. Stage Clear uses the Standard entry."""
        return [(MissionKind.CLEAR, self.clear), *self.missions.items()]


def resolve_items(source: Mission | StageData, difficulty: Difficulty = Difficulty.STANDARD) -> Requirement:
    """The item requirement of one mission or stage on the given difficulty."""
    if difficulty is Difficulty.EXPERT and source.items_exp is not None:
        return source.items_exp
    if difficulty in (Difficulty.INTERMEDIATE, Difficulty.EXPERT) and source.items_int is not None:
        return source.items_int
    return source.items


def resolve_seconds(mission: Mission, difficulty: Difficulty = Difficulty.STANDARD) -> int:
    """The time a mission needs on the given difficulty, with the same Expert -> Intermediate fallback."""
    if difficulty is Difficulty.EXPERT and mission.seconds_exp is not None:
        return mission.seconds_exp
    if difficulty in (Difficulty.INTERMEDIATE, Difficulty.EXPERT) and mission.seconds_int is not None:
        return mission.seconds_int
    return mission.seconds


def mission_items(
    stage: StageData, mission: Mission, difficulty: Difficulty = Difficulty.STANDARD
) -> Requirement:
    """Everything needed for one check: the stage-wide items plus the mission's own."""
    return (*resolve_items(stage, difficulty), *resolve_items(mission, difficulty))

# Data collected from this sheet, big shoutout to Friday and their friend for gathering the logic: 
# https://docs.google.com/spreadsheets/d/1xcdeANx_rk76uNjpTzSDubAzXn7za5Z9SlGcoUx4BC0/edit?usp=sharing

# TODO:
# Add item logic for green/red goals
# Add logic for deluxe stages
# Add logic for SMB1 Challenge Mode
# Add logic for Reverse, Dark Banana, Golden Banana, Original Stages modes
# Add logic for SMB1 Casual/Normal/Expert/Master

STAGES: dict[str, StageData] = {
    # World 1 - Jungle Island
    "W1-1": StageData(1, name="Simple", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=10),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W1-2": StageData(11, name="Hollow", clear=Mission(seconds=18, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30, seconds_int=20, seconds_exp=0),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W1-3": StageData(21, name="Bumpy", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=40, seconds_int=30, seconds_exp=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W1-4": StageData(31, name="Switches", clear=Mission(), items=("Normal Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=20, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=10, items=("Normal Switches",)),
        MissionKind.GREEN_GOAL: Mission(items=("Normal Switches",)),
    }),
    "W1-5": StageData(41, name="Conveyors", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W1-6": StageData(51, name="Floaters", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=50, seconds=40, seconds_int=30, seconds_exp=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W1-7": StageData(61, name="Tub", clear=Mission(seconds=15, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=77, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W1-8": StageData(71, name="Windy Slide", clear=Mission(seconds=32, seconds_int=30, seconds_exp=20), missions={
        MissionKind.BANANAS:    Mission(amount=70, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=30),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W1-9": StageData(81, name="Spinning Top", clear=Mission(seconds=14, seconds_int=11, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W1-10": StageData(91, name="Curve Bridge", clear=Mission(seconds=34), missions={
        MissionKind.BANANAS:    Mission(amount=60, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=35),
    }),

    # World 2 - Volcanic Magma
    "W2-1": StageData(101, name="Banks", clear=Mission(seconds=15, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W2-2": StageData(111, name="Eaten Floor", clear=Mission(seconds=15, seconds_int=11, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W2-3": StageData(121, name="Hoppers", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=5),
    }),
    "W2-4": StageData(131, name="Coaster", clear=Mission(seconds=23, seconds_int=22, seconds_exp=17), missions={
        MissionKind.BANANAS:    Mission(amount=55, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W2-5": StageData(141, name="Bumpy Check", clear=Mission(seconds=13, seconds_int=12, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W2-6": StageData(151, name="Swell", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W2-7": StageData(161, name="Gravity Slider", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=70, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W2-8": StageData(171, name="Inchworms", clear=Mission(seconds=12, seconds_int=12, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(seconds=20, items=("Normal Switches",)),
        MissionKind.RED_GOAL:   Mission(seconds=20, items=("Normal Switches",)),
    }),
    "W2-9": StageData(181, name="Totalitarianism", clear=Mission(seconds=12, seconds_int=12, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W2-10": StageData(191, name="Alternative", clear=Mission(seconds=21, seconds_int=14), items_int=("Fast Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),

    # World 3 - Under the Ocean
    "W3-1": StageData(201, name="Organic Form", clear=Mission(seconds=17), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W3-2": StageData(211, name="Reversible Gear", clear=Mission(seconds=13), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W3-3": StageData(221, name="Stepping Stones", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=70, seconds=30, seconds_exp=20),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W3-4": StageData(231, name="Dribbles", clear=Mission(seconds=48, seconds_int=34), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=40),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W3-5": StageData(241, name="Push Bar", clear=Mission(seconds=13, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W3-6": StageData(251, name="Mad Rings", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=5),
        MissionKind.GREEN_GOAL: Mission(),
        MissionKind.RED_GOAL:   Mission(seconds=20),
    }),
    "W3-7": StageData(261, name="Curvy Options", clear=Mission(seconds=13), missions={
        MissionKind.BANANAS:    Mission(amount=40, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W3-8": StageData(271, name="Twist & Spin", clear=Mission(seconds=11, seconds_int=11, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30, seconds_int=20, seconds_exp=20),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W3-9": StageData(281, name="Cascade", clear=Mission(seconds=29, seconds_int=14, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W3-10": StageData(291, name="Junction", clear=Mission(seconds=13, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=38, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(seconds=20),
    }),

    # World 4 - Inside a Whale
    "W4-1": StageData(301, name="Pro Skaters", clear=Mission(), items=("Pause Switches",), items_int=(), items_exp=(), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30, items=("Pause Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=10, items=("Pause Switches",)),
        MissionKind.GREEN_GOAL: Mission(items=("Pause Switches",)),
    }),
    "W4-2": StageData(311, name="Giant Comb", clear=Mission(seconds=28, seconds_int=12, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W4-3": StageData(321, name="Beehive", clear=Mission(seconds=27, seconds_int=13), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W4-4": StageData(331, name="Dynamic Maze", clear=Mission(seconds=19, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W4-5": StageData(341, name="Triangle Holes", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W4-6": StageData(351, name="Launchers", clear=Mission(seconds=28, seconds_int=18), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=20),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W4-7": StageData(361, name="Randomizer", clear=Mission(seconds=14, seconds_int=11, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=35, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(),
        MissionKind.RED_GOAL:   Mission(),
    }),
    "W4-8": StageData(371, name="Coin Slots", clear=Mission(seconds=26, seconds_int=11), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W4-9": StageData(381, name="Seesaw Bridges", clear=Mission(seconds=48, seconds_int=38, seconds_exp=29), missions={
        MissionKind.BANANAS:    Mission(amount=40, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=55),
    }),
    "W4-10": StageData(391, name="Arthropod", clear=Mission(seconds=12), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),

    # World 5 - Amusement Park
    "W5-1": StageData(401, name="Wormhole", clear=Mission(seconds=22, seconds_int=19), items=("Wormholes",), missions={
        MissionKind.BANANAS:    Mission(amount=50, seconds=40, items=("Wormholes",)),
        MissionKind.TIME_LIMIT: Mission(amount=25, items=("Wormholes",)),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W5-2": StageData(411, name="Free Fall", clear=Mission(seconds=18, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=50, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=20),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W5-3": StageData(421, name="Melting Pot", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=10),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W5-4": StageData(431, name="Mad Shuffle", clear=Mission(), items=("Wormholes",), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50, items=("Normal Switches", "Wormholes")),
        MissionKind.TIME_LIMIT: Mission(amount=10, items=("Normal Switches", "Wormholes")),
    }),
    "W5-5": StageData(441, name="Bead Screen", clear=Mission(seconds=14, seconds_int=0), items=("Pause Switches",), items_int=(), items_exp=(), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20, items=("Pause Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=15, items=("Pause Switches",)),
    }),
    "W5-6": StageData(451, name="Jump Machine", clear=Mission(seconds=12), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(),
        MissionKind.RED_GOAL:   Mission(),
    }),
    "W5-7": StageData(461, name="Zigzag Slope", clear=Mission(seconds=17), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W5-8": StageData(471, name="Tower", clear=Mission(seconds=12), items=("Wormholes",), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=20, items=("Wormholes",)),
        MissionKind.TIME_LIMIT: Mission(amount=15, items=("Wormholes",)),
    }),
    "W5-9": StageData(481, name="Toggle", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W5-10": StageData(491, name="Fluctuation", clear=Mission(seconds=15, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),

    # World 6 - Boiling Pot
    "W6-1": StageData(501, name="Combination", clear=Mission(seconds=25, seconds_int=0), items=("Wormholes", "Normal Switches"), items_int=("Wormholes",), items_exp=("Wormholes",), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=50, items=("Wormholes", "Normal Switches")),
        MissionKind.TIME_LIMIT: Mission(amount=10, items=("Wormholes", "Normal Switches")),
    }),
    "W6-2": StageData(511, name="Punched Seesaws", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=21, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W6-3": StageData(521, name="Opera", clear=Mission(seconds=45, seconds_int=34, seconds_exp=29), missions={
        MissionKind.BANANAS:    Mission(amount=70, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=35),
    }),
    "W6-4": StageData(531, name="Brandished", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=35, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=5),
    }),
    "W6-5": StageData(541, name="Tiers", clear=Mission(seconds=16), items=("Wormholes",), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=40, items=("Wormholes",)),
        MissionKind.TIME_LIMIT: Mission(amount=30, items=("Wormholes",)),
        MissionKind.GREEN_GOAL: Mission(items=("Wormholes",)),
        MissionKind.RED_GOAL:   Mission(items=("Wormholes",)),
    }),
    "W6-6": StageData(551, name="Cliffs", clear=Mission(seconds=29, seconds_int=19, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W6-7": StageData(561, name="Narrow Peaks", clear=Mission(seconds=17, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W6-8": StageData(571, name="Detours", clear=Mission(seconds=11, seconds_int=0), items=("Wormholes",), items_int=("Wormholes",), items_exp=(), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20, items=("Wormholes",)),
        MissionKind.TIME_LIMIT: Mission(amount=15, items=("Wormholes",)),
        MissionKind.GREEN_GOAL: Mission(items=("Wormholes",)),
    }),
    # TODO: source data lists "Play Switch" for the banana mission; there is no such item in items.py yet.
    "W6-9": StageData(581, name="Switch Inferno", clear=Mission(), items=("Normal Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=9, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=15, items=("Normal Switches",)),
    }),
    "W6-10": StageData(591, name="Folders", clear=Mission(seconds=13), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),

    # World 7 - Bubbly Washing Machine
    "W7-1": StageData(601, name="Spiral Bridge", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W7-2": StageData(611, name="Wavy Option", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W7-3": StageData(621, name="Obstacle", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W7-4": StageData(631, name="Domino", clear=Mission(seconds=11, seconds_int=0), items=("Normal Switches",), items_int=("Normal Switches",), items_exp=(), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=30, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=15, items=("Normal Switches",)),
    }),
    "W7-5": StageData(641, name="Sieve", clear=Mission(seconds=28), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
        MissionKind.NONSTOP:    Mission(),
    }),
    "W7-6": StageData(651, name="Flock", clear=Mission(seconds=49, seconds_int=19, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=50),
    }),
    "W7-7": StageData(661, name="Double Spiral", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=25),
    }),
    "W7-8": StageData(671, name="Hierarchy", clear=Mission(seconds=24, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=25),
    }),
    "W7-9": StageData(681, name="8 Bracelets", clear=Mission(seconds=21), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=25),
        MissionKind.GREEN_GOAL: Mission(),
        MissionKind.RED_GOAL:   Mission(),
    }),
    "W7-10": StageData(691, name="Quick Turn", clear=Mission(), items=("Fast Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=ALL_BANANAS),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.NONSTOP:    Mission(),
    }),

    # World 8 - Clock Tower Factory
    "W8-1": StageData(701, name="Pistons", clear=Mission(seconds=27, seconds_int=16), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W8-2": StageData(711, name="Soft Cream", clear=Mission(seconds=17, seconds_int=13, seconds_exp=0), items=("Normal Switches",), items_int=(AnyOf("Normal Switches", "Fast Switches"),), items_exp=(AnyOf("Normal Switches", "Fast Switches"),), missions={
        MissionKind.BANANAS:    Mission(amount=16, seconds=20, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=20, items=("Normal Switches",)),
    }),
    "W8-3": StageData(721, name="Momentum", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=21, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W8-4": StageData(731, name="Entangled Path", clear=Mission(seconds=41, seconds_int=31, seconds_exp=30), items=("Normal Switches", "Fast Switches"), items_int=("Normal Switches", "Fast Switches"), items_exp=(), missions={
        MissionKind.BANANAS:    Mission(amount=30, seconds=50, items=("Normal Switches", "Fast Switches")),
        MissionKind.TIME_LIMIT: Mission(amount=40, items=("Normal Switches", "Fast Switches")),
        MissionKind.GREEN_GOAL: Mission(items=("Normal Switches", "Fast Switches")),
    }),
    "W8-5": StageData(741, name="Totters", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=28),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W8-6": StageData(751, name="Vortex", clear=Mission(seconds=27, seconds_int=18), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=30),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W8-7": StageData(761, name="Warp", clear=Mission(seconds=27), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=40),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W8-8": StageData(771, name="Trampolines", clear=Mission(seconds=29, seconds_int=16), missions={
        MissionKind.BANANAS:    Mission(amount=40, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W8-9": StageData(781, name="Swing Shaft", clear=Mission(seconds=26, seconds_int=14), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W8-10": StageData(791, name="Linear Seesaws", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
        MissionKind.NONSTOP:    Mission(),
    }),

    # World 9 - Space Colony
    "W9-1": StageData(801, name="Serial Jump", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(),
        MissionKind.RED_GOAL:   Mission(),
    }),
    "W9-2": StageData(811, name="Cross Floors", clear=Mission(seconds=14), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W9-3": StageData(821, name="Spinning Saw", clear=Mission(seconds=25, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W9-4": StageData(831, name="Chipped Pipes", clear=Mission(seconds=15, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=15),
        MissionKind.GREEN_GOAL: Mission(),
    }),
    "W9-5": StageData(841, name="Flat Maze", clear=Mission(seconds=56, seconds_int=39, seconds_exp=22), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=40),
    }),
    "W9-6": StageData(851, name="Guillotine", clear=Mission(seconds=25, seconds_exp=19), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W9-7": StageData(861, name="Cork Screw", clear=Mission(seconds=18), missions={
        MissionKind.BANANAS:    Mission(amount=12, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W9-8": StageData(871, name="Orbiters", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=15, seconds=20),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W9-9": StageData(881, name="Twin Basin", clear=Mission(seconds=15, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=14, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W9-10": StageData(891, name="Air Hockey", clear=Mission(seconds=19, seconds_int=0), missions={
        MissionKind.BANANAS:    Mission(amount=40, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),

    # World 10 - Dr. Bad-Boon's Base
    "W10-1": StageData(901, name="Training", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=40, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W10-2": StageData(911, name="Gimmick", clear=Mission(seconds=54, seconds_int=48), items=("Normal Switches",), items_int=("Normal Switches",), items_exp=("Normal Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=60, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=55, items=("Normal Switches",)),
    }),
    "W10-3": StageData(921, name="Mountain", clear=Mission(), missions={
        MissionKind.BANANAS:    Mission(amount=10),
        MissionKind.TIME_LIMIT: Mission(amount=10),
    }),
    "W10-4": StageData(931, name="Disorder", clear=Mission(seconds=25, seconds_int=12, seconds_exp=0), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=15),
    }),
    "W10-5": StageData(941, name="3D Maze", clear=Mission(seconds=22, seconds_int=19), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=30),
        MissionKind.TIME_LIMIT: Mission(amount=30),
    }),
    "W10-6": StageData(951, name="Crazy Maze", clear=Mission(seconds=55, seconds_int=48), missions={
        MissionKind.BANANAS:    Mission(amount=20, seconds=60),
        MissionKind.TIME_LIMIT: Mission(amount=59),
    }),
    "W10-7": StageData(961, name="Post Modern", clear=Mission(seconds=46, seconds_int=38), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=50),
        MissionKind.TIME_LIMIT: Mission(amount=45),
    }),
    "W10-8": StageData(971, name="Revolution", clear=Mission(seconds=19), missions={
        MissionKind.BANANAS:    Mission(amount=10, seconds=40),
        MissionKind.TIME_LIMIT: Mission(amount=20),
    }),
    "W10-9": StageData(981, name="Invisible", clear=Mission(seconds=55, seconds_int=47), items=("Normal Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=29, seconds=60, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=50, items=("Normal Switches",)),
    }),
    "W10-10": StageData(991, name="Last Stage", clear=Mission(seconds=25), items=("Normal Switches",), missions={
        MissionKind.BANANAS:    Mission(amount=25, seconds=30, items=("Normal Switches",)),
        MissionKind.TIME_LIMIT: Mission(amount=25, items=("Normal Switches",)),
    }),
}

# SHOP_LOCATION_NAME_TO_ID: dict[str, int] = {
#     f"Banana Shop Item {n}": 999 + n for n in range(1, 33)
# }


class BananaManiaLocation(Location):
    game = "Super Monkey Ball Banana Mania"


def location_name(stage_id: str, stage: StageData, kind: MissionKind, mission: Mission) -> str:
    """Build the display name for one of a stage's checks."""
    prefix = f"[{stage_id}] {stage.name} -" if stage.name else f"[{stage_id}]"

    if kind is MissionKind.BANANAS and mission.amount == ALL_BANANAS:
        return f"{prefix} Banana Complete"
    if mission.amount is not None:
        return f"{prefix} {kind.label} {mission.amount}"
    return f"{prefix} {kind.label}"


LOCATION_NAME_TO_ID: dict[str, int] = {
    **{
        location_name(stage_id, stage, kind, mission): stage.base_id + kind.offset
        for stage_id, stage in STAGES.items()
        for kind, mission in stage.all_missions()
    },
    # **SHOP_LOCATION_NAME_TO_ID,
}


def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: BananaManiaWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def _include_mission(kind: MissionKind, world: BananaManiaWorld) -> bool:
    """Return True if this kind of check should be created given the current options."""
    if kind is MissionKind.BANANAS:
        return bool(world.options.banana_missions)
    if kind is MissionKind.TIME_LIMIT:
        return bool(world.options.time_missions)
    if kind in (MissionKind.GREEN_GOAL, MissionKind.RED_GOAL):
        return bool(world.options.extra_goals)
    if kind is MissionKind.NONSTOP:
        return bool(world.options.nonstop_missions)
    return True


def create_regular_locations(world: BananaManiaWorld) -> None:
    # Group stage locations by world number (W1 through W10).
    for world_num in range(1, 11):
        prefix = f"W{world_num}-"
        region = world.get_region(f"World {world_num}")
        stage_locations = get_location_names_with_ids([
            location_name(stage_id, stage, kind, mission)
            for stage_id, stage in STAGES.items() if stage_id.startswith(prefix)
            for kind, mission in stage.all_missions() if _include_mission(kind, world)
        ])
        region.add_locations(stage_locations, BananaManiaLocation)

    # Banana Shop locations.
    # banana_shop = world.get_region("Banana Shop")
    # banana_shop.add_locations(dict(SHOP_LOCATION_NAME_TO_ID), BananaManiaLocation)


def create_events(world: BananaManiaWorld) -> None:
    # Place the Victory event on World 10, representing completion of the final world.
    world_10 = world.get_region("World 10")
    world_10.add_event(
        "Cleared World 10", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem
    )
