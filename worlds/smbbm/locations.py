from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING
from math import ceil

from BaseClasses import Location

from . import items

from rule_builder.rules import HasAny, Rule, HasAll, Has

if TYPE_CHECKING:
    from .world import BananaManiaWorld

ALL_BANANAS = -1            # Key for needing all bananas

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
    CHALLENGE_CLEAR = ("Challenge", 6) # Amount here is how many fall outs/time overs you can get
    TURNING_POINT = ("Turning Point Clear", 7)
    COMPLETE = ("Stage Complete", 8)

    def __init__(self, label: str, offset: int) -> None:
        self.label = label
        self.offset = offset


@dataclass(frozen=True)
class Mission:
    """
    0-10 seconds means 10 seconds or under, so no items needed
    None means "not set": side missions inherit that field from the stage's clear mission
    """
    seconds: int | None = None                       # General time for the mission used for logic
    seconds_int: int | None = None                   # If set to none, inherits from seconds
    seconds_exp: int | None = None                   # If set to none, inherits from seconds_int, then seconds
    amount: int | None = None                        # bananas to collect, seconds for time limit, or other things. Never inherited
    items: tuple[str | Rule, ...] | None = None      # excludes time increases, as those are handled automatically. () means none needed
    items_int: tuple[str | Rule, ...] | None = None  # Inherits from items unless specified
    items_exp: tuple[str | Rule, ...] | None = None  # Inherits from items_int, then items


@dataclass(frozen=True)
class StageData:
    base_id: int
    name: str = ""                             # in-game stage name, e.g. "Simple"
    clear: Mission = Mission()                 # For clearing, green/red goals inherit from this unless specified otherwise
    missions: dict[MissionKind, Mission] = field(default_factory=dict)
    items: Rule = ()                    # required by every mission on this stage
    items_int: Rule | None = None       # Inherits from standard items unless specified; () means none needed
    items_exp: Rule | None = None       # Inherits from items_int, then items
    category: bool = False                     # Whether this is a category vs an individual stage, just changes text formatting for the name
    special: bool = False                      # Whether this is a special category or not, if special category it handles the clear mission differently

    def all_missions(self) -> list[tuple[MissionKind, Mission]]:
        """Every check this stage offers, in ID order. Stage Clear uses the Standard entry."""
        return [(MissionKind.CLEAR, self.clear), *self.missions.items()]

    def is_challenge(self) -> bool:
        return 11000 <= self.base_id < 12000

# Data collected from this sheet, big shoutout to Friday and their friend for gathering the logic: 
# https://docs.google.com/spreadsheets/d/1xcdeANx_rk76uNjpTzSDubAzXn7za5Z9SlGcoUx4BC0/edit?usp=sharing

# TODO:
# Add entries for SMB1/SMB2 challenge mode individual stages

STAGE_GROUPS: dict[str, list[StageData]] = {
    # World 1 - Jungle Island
    "W1": [
        StageData(1, name="Simple", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=10),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(11, name="Hollow", clear=Mission(seconds=18, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30, seconds_int=20, seconds_exp=0),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(21, name="Bumpy", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=40, seconds_int=30, seconds_exp=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(31, name="Switches", clear=Mission(), items=("Normal Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=20, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=10, items=("Normal Switches",)),
            MissionKind.GREEN_GOAL: Mission(seconds=20, items=("Normal Switches",)),
        }),
        StageData(41, name="Conveyors", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(51, name="Floaters", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=50, seconds=40, seconds_int=30, seconds_exp=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(61, name="Tub", clear=Mission(seconds=15, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=77, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(71, name="Windy Slide", clear=Mission(seconds=32, seconds_int=30, seconds_exp=20), missions={
            MissionKind.BANANAS:    Mission(amount=70, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=30),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(81, name="Spinning Top", clear=Mission(seconds=14, seconds_int=11, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(91, name="Curve Bridge", clear=Mission(seconds=34), missions={
            MissionKind.BANANAS:    Mission(amount=60, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=35),
        }),
    ],

    # World 2 - Volcanic Magma
    "W2": [
        StageData(101, name="Banks", clear=Mission(seconds=15, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(111, name="Eaten Floor", clear=Mission(seconds=15, seconds_int=11, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(121, name="Hoppers", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=5),
        }),
        StageData(131, name="Coaster", clear=Mission(seconds=23, seconds_int=22, seconds_exp=17), missions={
            MissionKind.BANANAS:    Mission(amount=55, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(141, name="Bumpy Check", clear=Mission(seconds=13, seconds_int=12, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(151, name="Swell", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(161, name="Gravity Slider", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=70, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(171, name="Inchworms", clear=Mission(seconds=12, seconds_int=12, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=20, items=("Normal Switches",)),
            MissionKind.RED_GOAL:   Mission(seconds=20, items=("Normal Switches",)),
        }),
        StageData(181, name="Totalitarianism", clear=Mission(seconds=12, seconds_int=12, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(191, name="Alternative", clear=Mission(seconds=21, seconds_int=14), items_int=("Fast Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
    ],

    # World 3 - Under the Ocean
    "W3": [
        StageData(201, name="Organic Form", clear=Mission(seconds=17), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(211, name="Reversible Gear", clear=Mission(seconds=13), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(221, name="Stepping Stones", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=70, seconds=30, seconds_exp=20),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(231, name="Dribbles", clear=Mission(seconds=48, seconds_int=34), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=40),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(241, name="Push Bar", clear=Mission(seconds=13, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(251, name="Mad Rings", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=5),
            MissionKind.GREEN_GOAL: Mission(),
            MissionKind.RED_GOAL:   Mission(seconds=20),
        }),
        StageData(261, name="Curvy Options", clear=Mission(seconds=13), missions={
            MissionKind.BANANAS:    Mission(amount=40, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(271, name="Twist & Spin", clear=Mission(seconds=11, seconds_int=11, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30, seconds_int=20, seconds_exp=20),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(281, name="Cascade", clear=Mission(seconds=29, seconds_int=14, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(291, name="Junction", clear=Mission(seconds=13, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=38, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
        }),
    ],

    # World 4 - Inside a Whale
    "W4": [
        StageData(301, name="Pro Skaters", clear=Mission(), items=("Pause Switches",), items_int=(), items_exp=(), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30, items=("Pause Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=10, items=("Pause Switches",)),
            MissionKind.GREEN_GOAL: Mission(items=()),
        }),
        StageData(311, name="Giant Comb", clear=Mission(seconds=28, seconds_int=12, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(321, name="Beehive", clear=Mission(seconds=27, seconds_int=13), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(331, name="Dynamic Maze", clear=Mission(seconds=19, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(341, name="Triangle Holes", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(351, name="Launchers", clear=Mission(seconds=28, seconds_int=18), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=20),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
        }),
        StageData(361, name="Randomizer", clear=Mission(seconds=14, seconds_int=11, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=35, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
            MissionKind.RED_GOAL:   Mission(seconds=20),
        }),
        StageData(371, name="Coin Slots", clear=Mission(seconds=26, seconds_int=11), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
        }),
        StageData(381, name="Seesaw Bridges", clear=Mission(seconds=48, seconds_int=38, seconds_exp=29), missions={
            MissionKind.BANANAS:    Mission(amount=40, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=55),
        }),
        StageData(391, name="Arthropod", clear=Mission(seconds=12), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
    ],

    # World 5 - Amusement Park
    "W5": [
        StageData(401, name="Wormhole", clear=Mission(seconds=22, seconds_int=19), items=("Wormholes",), missions={
            MissionKind.BANANAS:    Mission(amount=50, seconds=40, items=("Wormholes",)),
            MissionKind.TIME_LIMIT: Mission(amount=25, items=("Wormholes",)),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(411, name="Free Fall", clear=Mission(seconds=18, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=50, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=20),
            MissionKind.GREEN_GOAL: Mission(seconds=30, seconds_int=30, seconds_exp=20),
        }),
        StageData(421, name="Melting Pot", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=10),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(431, name="Mad Shuffle", clear=Mission(), items=("Wormholes",), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=50, items=("Normal Switches", "Wormholes")),
            MissionKind.TIME_LIMIT: Mission(amount=10, items=("Normal Switches", "Wormholes")),
        }),
        StageData(441, name="Bead Screen", clear=Mission(seconds=14, seconds_int=0), items=("Pause Switches",), items_int=(), items_exp=(), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20, items=("Pause Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=15, items=("Pause Switches",)),
        }),
        StageData(451, name="Jump Machine", clear=Mission(seconds=12), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=30),
            MissionKind.RED_GOAL:   Mission(seconds=40),
        }),
        StageData(461, name="Zigzag Slope", clear=Mission(seconds=17), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(471, name="Tower", clear=Mission(seconds=12), items=("Wormholes",), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=20, items=("Wormholes",)),
            MissionKind.TIME_LIMIT: Mission(amount=15, items=("Wormholes",)),
        }),
        StageData(481, name="Toggle", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(491, name="Fluctuation", clear=Mission(seconds=15, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
    ],

    # World 6 - Boiling Pot
    "W6": [
        StageData(501, name="Combination", clear=Mission(seconds=25, seconds_int=0), items=("Wormholes", "Normal Switches"), items_int=("Wormholes",), items_exp=("Wormholes",), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=50, items=("Wormholes", "Normal Switches")),
            MissionKind.TIME_LIMIT: Mission(amount=10, items=("Wormholes", "Normal Switches")),
        }),
        StageData(511, name="Punched Seesaws", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=21, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.GREEN_GOAL: Mission(seconds=30),
        }),
        StageData(521, name="Opera", clear=Mission(seconds=45, seconds_int=34, seconds_exp=29), missions={
            MissionKind.BANANAS:    Mission(amount=70, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=35),
        }),
        StageData(531, name="Brandished", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=35, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=5),
        }),
        StageData(541, name="Tiers", clear=Mission(seconds=16), items=("Wormholes",), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=40, items=("Wormholes",)),
            MissionKind.TIME_LIMIT: Mission(amount=30, items=("Wormholes",)),
            MissionKind.GREEN_GOAL: Mission(seconds=30, items=("Wormholes",)),
            MissionKind.RED_GOAL:   Mission(seconds=20, items=("Wormholes",)),
        }),
        StageData(551, name="Cliffs", clear=Mission(seconds=29, seconds_int=19, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(561, name="Narrow Peaks", clear=Mission(seconds=17, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(571, name="Detours", clear=Mission(seconds=11, seconds_int=0), items=("Wormholes",), items_int=("Wormholes",), items_exp=(), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20, seconds_int=0, items=("Wormholes",)),
            MissionKind.TIME_LIMIT: Mission(amount=15, items=("Wormholes",)),
            MissionKind.GREEN_GOAL: Mission(seconds=20, seconds_int=20, seconds_exp=0, items=("Wormholes",), items_exp=()),
        }),
        StageData(581, name="Switch Inferno", clear=Mission(), items=("Normal Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=9, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=15, items=("Normal Switches",)),
        }),
        StageData(591, name="Folders", clear=Mission(seconds=13), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
    ],

    # World 7 - Bubbly Washing Machine
    "W7": [
        StageData(601, name="Spiral Bridge", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(611, name="Wavy Option", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(621, name="Obstacle", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(631, name="Domino", clear=Mission(seconds=11, seconds_int=0), items=("Normal Switches",), items_int=("Normal Switches",), items_exp=(), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=30, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=15, items=("Normal Switches",)),
        }),
        StageData(641, name="Sieve", clear=Mission(seconds=28), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
            MissionKind.NONSTOP:    Mission(),
        }),
        StageData(651, name="Flock", clear=Mission(seconds=49, seconds_int=19, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=50),
        }),
        StageData(661, name="Double Spiral", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=25),
        }),
        StageData(671, name="Hierarchy", clear=Mission(seconds=24, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=25),
        }),
        StageData(681, name="8 Bracelets", clear=Mission(seconds=21), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=25),
            MissionKind.GREEN_GOAL: Mission(seconds=30),
            MissionKind.RED_GOAL:   Mission(seconds=30),
        }),
        StageData(691, name="Quick Turn", clear=Mission(), items=("Fast Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=ALL_BANANAS),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.NONSTOP:    Mission(),
        }),
    ],

    # World 8 - Clock Tower Factory
    "W8": [
        StageData(701, name="Pistons", clear=Mission(seconds=27, seconds_int=16), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(711, name="Soft Cream", clear=Mission(seconds=17, seconds_int=13, seconds_exp=0), items=("Normal Switches",), items_int=(HasAny("Normal Switches", "Fast Switches"),), items_exp=(HasAny("Normal Switches", "Fast Switches"),), missions={
            MissionKind.BANANAS:    Mission(amount=16, seconds=20, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=20, items=("Normal Switches",)),
        }),
        StageData(721, name="Momentum", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=21, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(731, name="Entangled Path", clear=Mission(seconds=41, seconds_int=31, seconds_exp=30), items=("Normal Switches", "Fast Switches"), items_int=("Normal Switches", "Fast Switches"), items_exp=(), missions={
            MissionKind.BANANAS:    Mission(amount=30, seconds=50, items=("Normal Switches", "Fast Switches")),
            MissionKind.TIME_LIMIT: Mission(amount=40, items=("Normal Switches", "Fast Switches")),
            MissionKind.GREEN_GOAL: Mission(seconds=40, items=("Normal Switches", "Fast Switches")),
        }),
        StageData(741, name="Totters", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=28),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(751, name="Vortex", clear=Mission(seconds=27, seconds_int=18), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=30),
            MissionKind.GREEN_GOAL: Mission(seconds=30),
        }),
        StageData(761, name="Warp", clear=Mission(seconds=27), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=40),
            MissionKind.GREEN_GOAL: Mission(seconds=40),
        }),
        StageData(771, name="Trampolines", clear=Mission(seconds=29, seconds_int=16), missions={
            MissionKind.BANANAS:    Mission(amount=40, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(781, name="Swing Shaft", clear=Mission(seconds=26, seconds_int=14), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(791, name="Linear Seesaws", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
            MissionKind.NONSTOP:    Mission(),
        }),
    ],

    # World 9 - Space Colony
    "W9": [
        StageData(801, name="Serial Jump", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
            MissionKind.RED_GOAL:   Mission(),
        }),
        StageData(811, name="Cross Floors", clear=Mission(seconds=14), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(821, name="Spinning Saw", clear=Mission(seconds=25, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(831, name="Chipped Pipes", clear=Mission(seconds=15, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=15),
            MissionKind.GREEN_GOAL: Mission(seconds=20),
        }),
        StageData(841, name="Flat Maze", clear=Mission(seconds=56, seconds_int=39, seconds_exp=22), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=40),
        }),
        StageData(851, name="Guillotine", clear=Mission(seconds=25, seconds_exp=19), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(861, name="Cork Screw", clear=Mission(seconds=18), missions={
            MissionKind.BANANAS:    Mission(amount=12, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(871, name="Orbiters", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=15, seconds=20),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(881, name="Twin Basin", clear=Mission(seconds=15, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=14, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(891, name="Air Hockey", clear=Mission(seconds=19, seconds_int=0), missions={
            MissionKind.BANANAS:    Mission(amount=40, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
    ],

    # World 10 - Dr. Bad-Boon's Base
    "W10": [
        StageData(901, name="Training", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=40, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(911, name="Gimmick", clear=Mission(seconds=54, seconds_int=48), items=("Normal Switches",), items_int=("Normal Switches",), items_exp=("Normal Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=60, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=55, items=("Normal Switches",)),
        }),
        StageData(921, name="Mountain", clear=Mission(), missions={
            MissionKind.BANANAS:    Mission(amount=10),
            MissionKind.TIME_LIMIT: Mission(amount=10),
        }),
        StageData(931, name="Disorder", clear=Mission(seconds=25, seconds_int=12, seconds_exp=0), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=15),
        }),
        StageData(941, name="3D Maze", clear=Mission(seconds=22, seconds_int=19), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=30),
            MissionKind.TIME_LIMIT: Mission(amount=30),
        }),
        StageData(951, name="Crazy Maze", clear=Mission(seconds=55, seconds_int=48), missions={
            MissionKind.BANANAS:    Mission(amount=20, seconds=60),
            MissionKind.TIME_LIMIT: Mission(amount=59),
        }),
        StageData(961, name="Post Modern", clear=Mission(seconds=46, seconds_int=38), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=50),
            MissionKind.TIME_LIMIT: Mission(amount=45),
        }),
        StageData(971, name="Revolution", clear=Mission(seconds=19), missions={
            MissionKind.BANANAS:    Mission(amount=10, seconds=40),
            MissionKind.TIME_LIMIT: Mission(amount=20),
        }),
        StageData(981, name="Invisible", clear=Mission(seconds=55, seconds_int=47), items=("Normal Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=29, seconds=60, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=50, items=("Normal Switches",)),
        }),
        StageData(991, name="Last Stage", clear=Mission(seconds=25), items=("Normal Switches",), missions={
            MissionKind.BANANAS:    Mission(amount=25, seconds=30, items=("Normal Switches",)),
            MissionKind.TIME_LIMIT: Mission(amount=25, items=("Normal Switches",)),
        }),
    ],

    # SMB1 Challenge Mode
    # The individual level location ids are base id of difficulty stages + 10000 to make it easier to
    # sequentially check them, because you can't play them individually so logic has to work around that.
    "SMB1 Casual": [
        StageData(1001, name="Casual Stages", clear=Mission(seconds=30, seconds_int=20), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=10, seconds=30, seconds_int=20)
        }),
        StageData(11001, name="Plain",                   clear=Mission()),
        StageData(11002, name="Diamond",                 clear=Mission()),
        StageData(11003, name="Hairpin",                 clear=Mission()),
        StageData(11004, name="Wide bridge",             clear=Mission()),
        StageData(11005, name="Bonus Basic (Casual)",    clear=Mission()),
        StageData(11006, name="Slopes",                  clear=Mission()),
        StageData(11007, name="Steps",                   clear=Mission()),
        StageData(11008, name="Blocks",                  clear=Mission(seconds=20)),
        StageData(11009, name="Jump Single",             clear=Mission()),
        StageData(11010, name="Exam-A",                  clear=Mission(seconds=20)),
        StageData(11011, name="Blur Bridge (Casual)",    clear=Mission(seconds=20)),
        StageData(11012, name="Hitter",                  clear=Mission()),
        StageData(11013, name="Banana Plate (Casual)",   clear=Mission(seconds=20)),

    ],

    "SMB1 Normal": [
        StageData(1101, name="Normal Stages", clear=Mission(seconds=39, seconds_int=30), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=30, seconds=39, seconds_int=30)
        }),
        StageData(11101, name="Bump",                   clear=Mission()),
        StageData(11102, name="Walking",                clear=Mission()),
        StageData(11103, name="Repulse",                clear=Mission()),
        StageData(11104, name="Narrow Bridge",          clear=Mission(seconds=20)),
        StageData(11105, name="Bonus Basic (Normal)",   clear=Mission()),
        StageData(11106, name="Break",                  clear=Mission()),
        StageData(11107, name="Curves",                 clear=Mission(seconds=20)),
        StageData(11108, name="Downhill",               clear=Mission(seconds=20)),
        StageData(11109, name="Blocks Slim",            clear=Mission(seconds=20)),
        StageData(11110, name="Bonus Wave (Normal)",    clear=Mission()),
        StageData(11111, name="Choice",                 clear=Mission(seconds=20)),
        StageData(11112, name="Bowl",                   clear=Mission()),
        StageData(11113, name="Jumpies",                clear=Mission()),
        StageData(11114, name="Stoppers",               clear=Mission(seconds=20)),
        StageData(11115, name="Floor Bent",             clear=Mission(seconds=20)),
        StageData(11116, name="Conveyer",               clear=Mission()),
        StageData(11117, name="Exam-B",                 clear=Mission(seconds=20)),
        StageData(11118, name="Chaser",                 clear=Mission(seconds=20)),
        StageData(11119, name="Jump Double",            clear=Mission()),
        StageData(11120, name="Bonus Grid (Normal)",    clear=Mission()),
        StageData(11121, name="Middle Jam",             clear=Mission(seconds=30)),
        StageData(11122, name="Ant Lion",               clear=Mission()),
        StageData(11123, name="Collapse",               clear=Mission(seconds=20)),
        StageData(11124, name="Swing Bar",              clear=Mission()),
        StageData(11125, name="Labyrinth",              clear=Mission(seconds=30)),
        StageData(11126, name="Spiral",                 clear=Mission(seconds=30)),
        StageData(11127, name="Wavy Jump",              clear=Mission()),
        StageData(11128, name="Spiky",                  clear=Mission(seconds=20)),
        StageData(11129, name="Unrest",                 clear=Mission()),
        StageData(11130, name="Polar",                  clear=Mission()),
        StageData(11131, name="Blur Bridge (Normal)",   clear=Mission(seconds=20)),
        StageData(11132, name="Hard Hitter (Normal)",   clear=Mission(seconds=20)),
        StageData(11133, name="Puzzle",                 clear=Mission(seconds=40)),
        StageData(11134, name="Banana Plate (Normal)",  clear=Mission(seconds=20)),
        StageData(11135, name="Polar Large",            clear=Mission(seconds=20)),

    ],

    "SMB1 Expert": [
        StageData(1201, name="Expert Stages", clear=Mission(seconds=60, seconds_int=50), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=99, seconds=60, seconds_int=50)
        }),
        StageData(11201, name="Ruin",                   clear=Mission()),
        StageData(11202, name="Branch",                 clear=Mission()),
        StageData(11203, name="Overturn",               clear=Mission()),
        StageData(11204, name="Excursion",              clear=Mission(seconds=60)),
        StageData(11205, name="Bonus Basic (Expert)",   clear=Mission()),
        StageData(11206, name="Dodecagon",              clear=Mission(seconds=30)),
        StageData(11207, name="Exam-C",                 clear=Mission(seconds=60)),
        StageData(11208, name="Skeleton",               clear=Mission(seconds=20)),
        StageData(11209, name="Tracks",                 clear=Mission(seconds=50)),
        StageData(11210, name="Bonus Wave (Expert)",    clear=Mission()),
        StageData(11211, name="Downhill Hard",          clear=Mission(seconds=30)),
        StageData(11212, name="Gears",                  clear=Mission(seconds=50)),
        StageData(11213, name="Destruction",            clear=Mission()),
        StageData(11214, name="Invasion",               clear=Mission(seconds=20)),
        StageData(11215, name="Diving",                 clear=Mission()),
        StageData(11216, name="Floor Slant",            clear=Mission()),
        StageData(11217, name="Tram",                   clear=Mission(seconds=20)),
        StageData(11218, name="Swing Bar Long",         clear=Mission()),
        StageData(11219, name="Paper Work",             clear=Mission()),
        StageData(11220, name="Bonus Grid (Expert)",    clear=Mission()),
        StageData(11221, name="Twin Attacker",          clear=Mission()),
        StageData(11222, name="Sega Logo",              clear=Mission(seconds=30)),
        StageData(11223, name="Snake",                  clear=Mission()),
        StageData(11224, name="Wind",                   clear=Mission(seconds=60)),
        StageData(11225, name="Sliders",                clear=Mission(seconds=20)),
        StageData(11226, name="Fall Down",              clear=Mission()),
        StageData(11227, name="Twin Cross",             clear=Mission()),
        StageData(11228, name="Spiral Hard",            clear=Mission()),
        StageData(11229, name="Conveyor Parts",         clear=Mission(seconds=40)),
        StageData(11230, name="Bonus Bumpy",            clear=Mission()),
        StageData(11231, name="Gaps",                   clear=Mission()),
        StageData(11232, name="Curvature",              clear=Mission(seconds=60)),
        StageData(11233, name="Ant Lion Super",         clear=Mission()),
        StageData(11234, name="Drum",                   clear=Mission()),
        StageData(11235, name="Twister",                clear=Mission()),
        StageData(11236, name="Speedy Jam",             clear=Mission(seconds=20)),
        StageData(11237, name="Quake",                  clear=Mission()),
        StageData(11238, name="Cassiopeia",             clear=Mission(seconds=30, seconds_int=20, seconds_exp=0)),
        StageData(11239, name="Pirates",                clear=Mission()),
        StageData(11240, name="Bonus Hunting",          clear=Mission()),
        StageData(11241, name="Bowl Open",              clear=Mission()),
        StageData(11242, name="Checker",                clear=Mission()),
        StageData(11243, name="Carpet",                 clear=Mission(seconds=30)),
        StageData(11244, name="Ridge",                  clear=Mission(seconds=30)),
        StageData(11245, name="Mixer",                  clear=Mission(seconds=20)),
        StageData(11246, name="Rings",                  clear=Mission(seconds=20)),
        StageData(11247, name="Stairs",                 clear=Mission()),
        StageData(11248, name="Clover",                 clear=Mission(seconds=30)),
        StageData(11249, name="Coffee Cup",             clear=Mission()),
        StageData(11250, name="Metamorphosis",          clear=Mission()),
        StageData(11251, name="Blur Bridge (Expert)",   clear=Mission(seconds=20)),
        StageData(11252, name="Breathe",                clear=Mission()),
        StageData(11253, name="Hard Hitter (Expert)",   clear=Mission()),
        StageData(11254, name="Ferris Wheel",           clear=Mission()),
        StageData(11255, name="Factory",                clear=Mission(seconds=20)),
        StageData(11256, name="Curl Pipe",              clear=Mission()),
        StageData(11257, name="Magic Hand",             clear=Mission()),
        StageData(11258, name="Banana Plate (Expert)",  clear=Mission()),
        StageData(11259, name="Sanctuary",              clear=Mission(seconds=20)),
        StageData(11260, name="Daa Loo Maa",            clear=Mission(seconds=20)),

    ],

    "SMB1 Master": [
        StageData(1301, name="Master Stages", clear=Mission(seconds=50), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=50, seconds=50)
        }),
        StageData(11301, name="Wave Master",    clear=Mission(seconds=30, seconds_int=30, seconds_exp=20)),
        StageData(11302, name="Fan Master",     clear=Mission(seconds=30, seconds_int=0)),
        StageData(11303, name="Stamina Master", clear=Mission(seconds=40, seconds_int=20)),
        StageData(11304, name="Spring Master",  clear=Mission(seconds=50, seconds_int=50, seconds_exp=20)),
        StageData(11305, name="Dance Master",   clear=Mission()),
        StageData(11306, name="Roll Master",    clear=Mission(seconds=30, seconds_int=0)),
        StageData(11307, name="Edge Master",    clear=Mission(seconds=20)),
        StageData(11308, name="Dodge Master",   clear=Mission()),
        StageData(11309, name="Bridge Master",  clear=Mission(seconds=20, seconds_int=0)),
        StageData(11310, name="Monkey Master",  clear=Mission()),
    ],

    # SMB2 Challenge Mode
    "SMB2 Casual": [
        StageData(1401, name="Casual EX Stages", clear=Mission(seconds=28), items=("Pause Switches",), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=10, seconds=28, items=("Pause Switches",))
        }),
        StageData(11401, name="Simple",           clear=Mission()),
        StageData(11402, name="Hollow",           clear=Mission(seconds=18, seconds_int=0)),
        StageData(11403, name="Bumpy",            clear=Mission()),
        StageData(11404, name="Switches",         clear=Mission(items=("Normal Switches",))),
        StageData(11405, name="Rising Inclines",  clear=Mission(seconds=14, seconds_int=0)),
        StageData(11406, name="Floaters",         clear=Mission()),
        StageData(11407, name="Tub",              clear=Mission(seconds=15, seconds_int=0)),
        StageData(11408, name="Windy Slide",      clear=Mission(seconds=32, seconds_int=29, seconds_exp=19)),
        StageData(11409, name="Spinning Top",     clear=Mission(seconds=14, seconds_int=11, seconds_exp=0)),
        StageData(11410, name="Curve Bridge",     clear=Mission(seconds=34)),

        StageData(11411, name="Conveyors",        clear=Mission()),
        StageData(11412, name="Bumpy Check",      clear=Mission(seconds=13, seconds_int=12, seconds_exp=0)),
        StageData(11413, name="Alternative",      clear=Mission(seconds=21, seconds_int=14)),
        StageData(11414, name="Junction",         clear=Mission(seconds=13, seconds_int=13, seconds_exp=0)),
        StageData(11415, name="Bead Screen",      clear=Mission(seconds=14, seconds_int=0)),
        StageData(11416, name="Fluctuation",      clear=Mission(seconds=15, seconds_int=0)),
        StageData(11417, name="Folders",          clear=Mission(seconds=13)),
        StageData(11418, name="Quick Turn",       clear=Mission()),
        StageData(11419, name="Linear Seesaws",   clear=Mission()),
        StageData(11420, name="Birth",            clear=Mission(seconds=28, items=("Pause Switches",))),

    ],

    "SMB2 Normal": [
        StageData(1501, name="Normal EX Stages", clear=Mission(seconds=32, seconds_int=32, seconds_exp=22), items=("Normal Switches",), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=30, seconds=32, seconds_int=32, seconds_exp=22, items=("Normal Switches",))
        }),
        StageData(11501, name="Banks",            clear=Mission(seconds=15, seconds_int=0)),
        StageData(11502, name="Eaten Floor",      clear=Mission(seconds=15, seconds_int=11, seconds_exp=0)),
        StageData(11503, name="Hoppers",          clear=Mission()),
        StageData(11504, name="Coaster",          clear=Mission(seconds=23, seconds_int=22, seconds_exp=17)),
        StageData(11505, name="Board Park",       clear=Mission()),
        StageData(11506, name="Swell",            clear=Mission()),
        StageData(11507, name="Gravity Slider",   clear=Mission(seconds=19)),
        StageData(11508, name="Inchworms",        clear=Mission(seconds=12, seconds_int=12, seconds_exp=0)),
        StageData(11509, name="Totalitarianism",  clear=Mission(seconds=12, seconds_int=12, seconds_exp=0)),
        StageData(11510, name="Leveler",          clear=Mission()),
        StageData(11511, name="Organic Form",     clear=Mission(seconds=17)),
        StageData(11512, name="Reversible Gear",  clear=Mission(seconds=13)),
        StageData(11513, name="Stepping Stones",  clear=Mission(seconds=19)),
        StageData(11514, name="Dribbles",         clear=Mission(seconds=48, seconds_int=34)),
        StageData(11515, name="Push Bar",         clear=Mission(seconds=13, seconds_int=0)), 
        StageData(11516, name="Mad Rings",        clear=Mission()),
        StageData(11517, name="Curvy Options",    clear=Mission(seconds=13)),
        StageData(11518, name="Twist & Spin",     clear=Mission(seconds=11, seconds_int=11, seconds_exp=0)),
        StageData(11519, name="Cascade",          clear=Mission(seconds=29, seconds_int=14, seconds_exp=0)),
        StageData(11520, name="Rampage",          clear=Mission()),
        StageData(11521, name="Pro Skaters",      clear=Mission(items=("Pause Switches",), items_int=(), items_exp=())),
        StageData(11522, name="Giant Comb",       clear=Mission(seconds=28, seconds_int=12, seconds_exp=0)),
        StageData(11523, name="Beehive",          clear=Mission(seconds=27, seconds_int=13)),
        StageData(11524, name="Dynamic Maze",     clear=Mission(seconds=19, seconds_exp=0)),
        StageData(11525, name="Triangle Holes",   clear=Mission()),
        StageData(11526, name="Launchers",        clear=Mission(seconds=28, seconds_int=18)),
        StageData(11527, name="Randomizer",       clear=Mission(seconds=14, seconds_int=11, seconds_exp=0)),
        StageData(11528, name="Coin Slots",       clear=Mission(seconds=26, seconds_int=11)),
        StageData(11529, name="Seesaw Bridges",   clear=Mission(seconds=48, seconds_int=38, seconds_exp=29)),
        StageData(11530, name="Arthropod",        clear=Mission(seconds=12)),

        StageData(11531, name="Auto Doors",       clear=Mission(seconds=22)),
        StageData(11532, name="Heavy Sphere",     clear=Mission(items=("Normal Switches",))),
        StageData(11533, name="Stagger",          clear=Mission(seconds=22)),
        StageData(11534, name="U.F.O",            clear=Mission(seconds=17, items=("Normal Switches",))),
        StageData(11535, name="Ring Bridges",     clear=Mission(seconds=22, seconds_int=19)),
        StageData(11536, name="Domes",            clear=Mission(seconds=17, seconds_int=0)),
        StageData(11537, name="Amida Lot",        clear=Mission()),
        StageData(11538, name="Long Slider",      clear=Mission(seconds=32, seconds_exp=0)),
        StageData(11539, name="Grid Bridge",      clear=Mission(seconds=15, seconds_exp=0, items=("Normal Switches",), items_int=(), items_exp=())),
        StageData(11540, name="Teapot",           clear=Mission(items=("Normal Switches",))),
    ],

    "SMB2 Expert": [
        StageData(1601, name="Expert EX Stages", clear=Mission(seconds=39), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=99, seconds=39)
        }),
        StageData(11601, name="Wormhole",         clear=Mission(seconds=22, seconds_int=19, items=("Wormholes",))),
        StageData(11602, name="Free Fall",        clear=Mission(seconds=18, seconds_exp=0)),
        StageData(11603, name="Melting Pot",      clear=Mission()),
        StageData(11604, name="Mad Shuffle",      clear=Mission(items=("Wormholes",))),
        StageData(11605, name="Partition",        clear=Mission()), 
        StageData(11606, name="Jump Machine",     clear=Mission(seconds=12)),
        StageData(11607, name="Zigzag Slope",     clear=Mission(seconds=17)),
        StageData(11608, name="Tower",            clear=Mission(seconds=12, items=("Wormholes",))),
        StageData(11609, name="Toggle",           clear=Mission()),
        StageData(11610, name="Pachinko",         clear=Mission()),
        StageData(11611, name="Combination",      clear=Mission(seconds=25, seconds_int=0, items=("Wormholes", "Normal Switches"), items_int=("Wormholes",), items_exp=("Wormholes",))),
        StageData(11612, name="Punched Seesaws",  clear=Mission()),
        StageData(11613, name="Opera",            clear=Mission(seconds=45, seconds_int=34, seconds_exp=29)),
        StageData(11614, name="Brandished",       clear=Mission()),
        StageData(11615, name="Tiers",            clear=Mission(seconds=16, items=("Wormholes",))),
        StageData(11616, name="Cliffs",           clear=Mission(seconds=29, seconds_int=19, seconds_exp=0)),
        StageData(11617, name="Narrow Peaks",     clear=Mission(seconds=17, seconds_int=0)),
        StageData(11618, name="Detours",          clear=Mission(seconds=11, seconds_int=0, items=("Wormholes",))),
        StageData(11619, name="Switch Inferno",   clear=Mission(items=("Normal Switches",))),
        StageData(11620, name="Earthquake",       clear=Mission()),
        StageData(11621, name="Spiral Bridge",    clear=Mission(seconds=19)),
        StageData(11622, name="Wavy Option",      clear=Mission()),
        StageData(11623, name="Obstacle",         clear=Mission(seconds=19)),
        StageData(11624, name="Domino",           clear=Mission(seconds=11, seconds_int=0, items=("Normal Switches",), items_int=("Normal Switches",), items_exp=())),
        StageData(11625, name="Sieve",            clear=Mission(seconds=28)),
        StageData(11626, name="Flock",            clear=Mission(seconds=49, seconds_int=19, seconds_exp=0)),
        StageData(11627, name="Double Spiral",    clear=Mission(seconds=19)),
        StageData(11628, name="Hierarchy",        clear=Mission(seconds=24, seconds_int=0)),
        StageData(11629, name="8 Bracelets",      clear=Mission(seconds=21)),
        StageData(11630, name="Banana Hunting",   clear=Mission()),
        StageData(11631, name="Pistons",          clear=Mission(seconds=27, seconds_int=16)),
        StageData(11632, name="Soft Cream",       clear=Mission(seconds=17, seconds_int=13, seconds_exp=0, items=("Normal Switches",), items_int=(HasAny("Normal Switches", "Fast Switches"),), items_exp=(HasAny("Normal Switches", "Fast Switches"),))),
        StageData(11633, name="Momentum",         clear=Mission()),
        StageData(11634, name="Entangled Path",   clear=Mission(seconds=41, seconds_int=31, seconds_exp=30, items=("Normal Switches", "Fast Switches"), items_int=("Normal Switches", "Fast Switches"), items_exp=())),
        StageData(11635, name="Totters",          clear=Mission()),
        StageData(11636, name="Vortex",           clear=Mission(seconds=27, seconds_int=18)),
        StageData(11637, name="Warp",             clear=Mission(seconds=27)),
        StageData(11638, name="Trampolines",      clear=Mission(seconds=29, seconds_int=16)),
        StageData(11639, name="Swing Shaft",      clear=Mission(seconds=26, seconds_int=14)),
        StageData(11640, name="Fighters",         clear=Mission()),
        StageData(11641, name="Serial Jump",      clear=Mission()),
        StageData(11642, name="Cross Floors",     clear=Mission(seconds=14)),
        StageData(11643, name="Spinning Saw",     clear=Mission(seconds=25, seconds_int=0)),
        StageData(11644, name="Chipped Pipes",    clear=Mission(seconds=15, seconds_int=0)),
        StageData(11645, name="Flat Maze",        clear=Mission(seconds=56, seconds_int=39, seconds_exp=22)),
        StageData(11646, name="Guillotine",       clear=Mission(seconds=25, seconds_exp=19)),
        StageData(11647, name="Cork Screw",       clear=Mission(seconds=18)),
        StageData(11648, name="Orbiters",         clear=Mission()),
        StageData(11649, name="Twin Basin",       clear=Mission(seconds=15, seconds_int=0)),
        StageData(11650, name="Air Hockey",       clear=Mission(seconds=19, seconds_int=0)),

        StageData(11651, name="Charge",           clear=Mission(seconds=11, items=("Wormholes",))),
        StageData(11652, name="Strata",           clear=Mission(seconds=27)),
        StageData(11653, name="Square Dance",     clear=Mission()),
        StageData(11654, name="Giant Swing",      clear=Mission(seconds=39)),
        StageData(11655, name="5 Drums",          clear=Mission(seconds=18)),
        StageData(11656, name="Free Throw",       clear=Mission()),
        StageData(11657, name="Pendulums",        clear=Mission(seconds=36, seconds_exp=0)),
        StageData(11658, name="Conical Slider",   clear=Mission(seconds=35), items=("Wormholes",)),
        StageData(11659, name="Construction",     clear=Mission(seconds=39)),
        StageData(11660, name="Train Worm",       clear=Mission(seconds=29, seconds_int=0)),
    ],

    "SMB2 Master": [
        StageData(1701, name="Master EX Stages", clear=Mission(seconds=53), category=True, missions={
            MissionKind.CHALLENGE_CLEAR: Mission(amount=70, seconds=53)
        }),
        StageData(11701, name="Centrifugal",      clear=Mission(seconds=22, seconds_int=18, seconds_exp=0)),
        StageData(11702, name="Swing Bridges",    clear=Mission(seconds=18)),
        StageData(11703, name="Cylinders",        clear=Mission()),
        StageData(11704, name="Passage",          clear=Mission(seconds=23)),
        StageData(11705, name="Notch",            clear=Mission(seconds=15)),
        StageData(11706, name="Intermittent",     clear=Mission()),
        StageData(11707, name="Long Torus",       clear=Mission(seconds=22)),
        StageData(11708, name="Spasmodic",        clear=Mission()),
        StageData(11709, name="Double Twin",      clear=Mission(seconds=18)),
        StageData(11710, name="Clock Face",       clear=Mission(seconds=23)),

        StageData(11711, name="Variable Width",   clear=Mission()),
        StageData(11712, name="Striker",          clear=Mission(seconds=15, seconds_int=0)),
        StageData(11713, name="Ooparts",          clear=Mission()),
        StageData(11714, name="Planets",          clear=Mission(seconds=18)),
        StageData(11715, name="Sliced Cheese",    clear=Mission(seconds=23)),
        StageData(11716, name="8 Seesaws",        clear=Mission(seconds=12)),
        StageData(11717, name="Synchronized",     clear=Mission()),
        StageData(11718, name="Helix",            clear=Mission(seconds=53)),
        StageData(11719, name="Dizzy System",     clear=Mission()),
        StageData(11720, name="Destiny",          clear=Mission(seconds=31)),
    ],

    # Deluxe Stages
    "SP DX": [
        StageData(2001, name="Stages", clear=Mission(amount=1), category=True, special=True, missions={
            MissionKind.TURNING_POINT: Mission(amount=23),
            MissionKind.COMPLETE: Mission(amount=46, seconds=60, items=("Wormholes", "Fast Switches"), items_int=("Wormholes",))
        }),
    ],

    # Deluxe Beginner Pack
    "SP DX Beginner": [
        StageData(2101, name="Edge",            clear=Mission()),
        StageData(2111, name="Escalator",       clear=Mission(seconds=21, seconds_int=18)),
        StageData(2121, name="Serpentine",      clear=Mission(seconds=11, seconds_int=0)),
        StageData(2131, name="Swirl",           clear=Mission(seconds=35)),
        StageData(2141, name="Dormant Pits",    clear=Mission()),
        StageData(2151, name="Composition",     clear=Mission(seconds=25, seconds_int=20)),
        StageData(2161, name="Dynamo",          clear=Mission(seconds=25, seconds_int=12, seconds_exp=0)),
        StageData(2171, name="Lunchbox",        clear=Mission(seconds=12, seconds_int=0)),
        StageData(2181, name="Gutter",          clear=Mission(seconds=29, seconds_int=19, seconds_exp=0)),
        StageData(2191, name="Scabrous",        clear=Mission()),
        StageData(2201, name="Jolt Channel",    clear=Mission(seconds=26, seconds_int=20)),
        StageData(2211, name="Inertial",        clear=Mission()),
        StageData(2221, name="Octagonal",       clear=Mission(seconds=18, seconds_int=0)),
        StageData(2231, name="Sewer",           clear=Mission(seconds=19, seconds_int=19, seconds_exp = 0)),
        StageData(2241, name="Arc Bridges",     clear=Mission(seconds=27, seconds_int=19)),
        StageData(2251, name="Veer Field",      clear=Mission(seconds=45, seconds_int=28, seconds_exp = 20)),
        StageData(2261, name="Teeter",          clear=Mission(seconds=26, seconds_int=19)),
        StageData(2271, name="Stream",          clear=Mission(seconds=15, seconds_int=0)),
        StageData(2281, name="Catwalk",         clear=Mission(seconds=38, seconds_int=0)),
        StageData(2291, name="Catapult",        clear=Mission(seconds=12)),
    ],

    # Deluxe Advanced Pack
    "SP DX Advanced": [
        StageData(2301, name="Jump Ramp",       clear=Mission(seconds=11, seconds_int=11, seconds_exp=0)),
        StageData(2311, name="Hounds Tooth",    clear=Mission()),
        StageData(2321, name="D.N.A.",          clear=Mission(seconds=19, seconds_int=0)),
        StageData(2331, name="Building",        clear=Mission(seconds=28)),
        StageData(2341, name="Scrolls",         clear=Mission(seconds=21, seconds_int=19)),
        StageData(2351, name="Cliff",           clear=Mission(seconds=58, seconds_int=48, seconds_exp=0)),
        StageData(2361, name="Concentric",      clear=Mission(seconds=18, seconds_int=18, seconds_exp=0)),
        StageData(2371, name="Stadium",         clear=Mission(seconds=15, seconds_int=0)),
        StageData(2381, name="Dungeon",         clear=Mission(seconds=45, seconds_int=29, seconds_exp=21)),
        StageData(2391, name="Paraboloid",      clear=Mission()),
        StageData(2401, name="Saptiotemporal",  clear=Mission()),
        StageData(2411, name="Shelter",         clear=Mission(seconds=18, seconds_int=0)),
        StageData(2421, name="Mobius",          clear=Mission(seconds=25, seconds_int=0), items=("Fast Switches",), items_int=None),
    ],

    # Deluxe EX Pack
    "SP DX EX": [
        StageData(2501, name="Rhombus",               clear=Mission()),
        StageData(2511, name="Buoy",                  clear=Mission()),
        StageData(2521, name="Coil Ramp",             clear=Mission(seconds=48, seconds_int=16, seconds_exp=0)),
        StageData(2531, name="Millefueille",          clear=Mission(seconds=11, seconds_int=0)),
        StageData(2541, name="Waver",                 clear=Mission(seconds=38, seconds_int=31, seconds_exp=29)),
        StageData(2551, name="Fat Seesaw",            clear=Mission()),
        StageData(2561, name="Treads",                clear=Mission(seconds=43, seconds_int=26, seconds_exp=15)),
        StageData(2571, name="Chaos",                 clear=Mission(seconds=57)),
        StageData(2581, name="Tilt Maze",             clear=Mission(seconds=55, seconds_int=0)),
        StageData(2591, name="Fractal",               clear=Mission(seconds=18, seconds_int=0)),
        StageData(2601, name="Hills",                 clear=Mission(seconds=12, seconds_int=0)),
        StageData(2611, name="Dodge Maze",            clear=Mission(seconds=55, seconds_int=47)),
        StageData(2621, name="Asterisk",              clear=Mission()),
    ],

    # Reverse Mode
    "SP Reverse": [
        StageData(3001, name="Stages", clear=Mission(amount=1), category=True, special=True, missions={
            MissionKind.TURNING_POINT: Mission(amount=5),
            MissionKind.COMPLETE: Mission(amount=10, seconds=60)
        }),

        # Reverse Mode Stages
        StageData(3101, name="Branch",          clear=Mission(seconds=20)),
        StageData(3111, name="Waver",           clear=Mission(seconds=50)),
        StageData(3121, name="Free Throw",      clear=Mission(seconds=40)),
        StageData(3131, name="Rings",           clear=Mission(seconds=20)),
        StageData(3141, name="Amida Lot",       clear=Mission(seconds=20)),
        StageData(3151, name="Carpet",          clear=Mission(seconds=40)),
        StageData(3161, name="Clover",          clear=Mission(seconds=30)),
        StageData(3171, name="Punched Seesaw",  clear=Mission(seconds=30)),
        StageData(3181, name="Checker",         clear=Mission(seconds=60)),
        StageData(3191, name="Polar Large",     clear=Mission()),
    ],

    # Dark Banana Mode
    "SP Dark": [
        StageData(4001, name="Stages", clear=Mission(amount=1), category=True, special=True, missions={
            MissionKind.TURNING_POINT: Mission(amount=5),
            MissionKind.COMPLETE: Mission(amount=10, seconds=60)
        }),

        # Dark Banana Mode Stages
        StageData(4101, name="Cross Floors",   clear=Mission(seconds=20)),
        StageData(4111, name="Ant Lion",       clear=Mission()),
        StageData(4121, name="Earthquake",     clear=Mission(seconds=20)),
        StageData(4131, name="Destruction",    clear=Mission(seconds=60)),
        StageData(4141, name="Narrow Peaks",   clear=Mission(seconds=40)),
        StageData(4151, name="Centrifugal",    clear=Mission(seconds=30)),
        StageData(4161, name="Breathe",        clear=Mission(seconds=20)),
        StageData(4171, name="Twin Basin",     clear=Mission(seconds=20)),
        StageData(4181, name="Swing Bar Long", clear=Mission(seconds=20)),
        StageData(4191, name="Sega Logo",      clear=Mission(seconds=60)),
    ],

    # Golden Banana Mode
    "SP Golden": [
        StageData(5001, name="Stages", clear=Mission(amount=1), category=True, special=True, missions={
            MissionKind.TURNING_POINT: Mission(amount=5),
            MissionKind.COMPLETE: Mission(amount=10, seconds=60)
        }),

        # Golden Banana Mode Stages
        StageData(5101, name="Blur Bridge",  clear=Mission(seconds=40)),
        StageData(5111, name="Dungeon",      clear=Mission(seconds=60)),
        StageData(5121, name="Mad Rings",    clear=Mission(seconds=40)),
        StageData(5131, name="Dodge Maze",   clear=Mission(seconds=60)),
        StageData(5141, name="Paper Work",   clear=Mission(seconds=60)),
        StageData(5151, name="Chaos",        clear=Mission(seconds=60)),
        StageData(5161, name="Training",     clear=Mission(seconds=60)),
        StageData(5171, name="Flat Maze",    clear=Mission(seconds=60)),
        StageData(5181, name="Strata",       clear=Mission(seconds=60)),
        StageData(5191, name="Crazy Maze",  clear=Mission(seconds=60)),
    ],

    # Original Stages Mode
    "SP Original": [
        StageData(6001, name="Stages", clear=Mission(amount=1), category=True, special=True, missions={
            MissionKind.TURNING_POINT: Mission(amount=12),
            MissionKind.COMPLETE: Mission(amount=23, seconds=60, items=("Fast Switches",))
        }),

        # Original Stages Mode Stages
        StageData(6101, name="Catwalk",        clear=Mission(seconds=50)),
        StageData(6111, name="Polar",          clear=Mission()),
        StageData(6121, name="Launchers",      clear=Mission(seconds=20)),
        StageData(6131, name="Arthropod",      clear=Mission(seconds=20)),
        StageData(6141, name="Polar Large",    clear=Mission(seconds=50)),
        StageData(6151, name="Chaos",          clear=Mission(seconds=60)),
        StageData(6161, name="Exam-C",         clear=Mission(seconds=50)),
        StageData(6171, name="Tracks",         clear=Mission(seconds=50)),
        StageData(6181, name="Twin Attacker",  clear=Mission()),
        StageData(6191, name="8 Bracelets",    clear=Mission(seconds=30)),
        StageData(6201, name="Curvature",      clear=Mission(seconds=50)),
        StageData(6211, name="Soft Cream",     clear=Mission(seconds=20, items=("Fast Switches",))),
        StageData(6221, name="Air Hockey",     clear=Mission()),
        StageData(6231, name="Cylinders",      clear=Mission(seconds=20)),
        StageData(6241, name="Notch",          clear=Mission(seconds=20)),
        StageData(6251, name="Long Torus",     clear=Mission(seconds=30)),
        StageData(6261, name="Clock Face",     clear=Mission(seconds=30)),
        StageData(6271, name="Wave Master",    clear=Mission(seconds=30)),
        StageData(6281, name="Stamina Master", clear=Mission(seconds=20)),
        StageData(6291, name="Dance Master",   clear=Mission()),
        StageData(6301, name="Dodge Master",   clear=Mission()),
        StageData(6311, name="Bridge Master",  clear=Mission(seconds=20)),
        StageData(6321, name="Synchronized",   clear=Mission()),
    ],
}


class BananaManiaLocation(Location):
    game = "Super Monkey Ball Banana Mania"


def labeled_stages(group: str) -> list[tuple[str, StageData]]:
    """Label stages with their group/stage number"""
    labeled = []
    number = 0
    for stage in STAGE_GROUPS[group]:
        if stage.category:
            labeled.append((f"[{group}]", stage))
        elif group.startswith(("SMB1", "SMB2", "SP")):
            labeled.append((f"[{group}]", stage))
        else:
            number += 1
            labeled.append((f"[{group}-{number}]", stage))
    return labeled


def location_name(label: str, stage: StageData, kind: MissionKind, mission: Mission) -> str:
    """Build the display name for stages/categories"""
    # Categories only show their group label, not the stage name
    prefix = f"{label} {stage.name} -" if stage.name and not stage.category else label

    if kind is MissionKind.BANANAS and mission.amount == ALL_BANANAS:
        return f"{prefix} Banana Complete"
    if stage.category and stage.special == False:
        if kind is MissionKind.CLEAR:
            return f"{prefix} Course Clear"
        elif kind is MissionKind.CHALLENGE_CLEAR:
            return f"{prefix} {kind.label} {mission.amount}"
    if stage.category and stage.special == True:
        return f"{prefix} {kind.label}"
    if mission.amount is not None:
        return f"{prefix} {kind.label} {mission.amount}"
    return f"{prefix} {kind.label}"

@dataclass(frozen=True)
class LocationData:
    stage: StageData
    kind: MissionKind
    mission: Mission

LOCATION_NAME_TO_DATA: dict[str, LocationData] = {
    location_name(label, stage, kind, mission): LocationData(stage, kind, mission)
    for group in STAGE_GROUPS
    for label, stage in labeled_stages(group)
    for kind, mission in stage.all_missions()
}

LOCATION_NAME_TO_ID: dict[str, int] = {
    location_name(label, stage, kind, mission): stage.base_id + kind.offset
    for group in STAGE_GROUPS
    for label, stage in labeled_stages(group)
    for kind, mission in stage.all_missions()
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

def create_mission_locations(world: BananaManiaWorld, region, stage_label):
        region = world.get_region(region)
        stage_locations = get_location_names_with_ids([
            location_name(label, stage, kind, mission)
            for label, stage in labeled_stages(stage_label)
            for kind, mission in stage.all_missions() if _include_mission(kind, world)
        ])
        region.add_locations(stage_locations, BananaManiaLocation)

def create_regular_locations(world: BananaManiaWorld) -> None:
    # Each world's stage group (W1 through W10) goes in that world's region.
    for world_num in range(1, 11):
        create_mission_locations(world, f"World {world_num}", f"W{world_num}")

    # Create challenge modes
    if world.options.smb1_casual:
        create_mission_locations(world, "SMB1 Casual", "SMB1 Casual")
    if world.options.smb1_normal:
        create_mission_locations(world, "SMB1 Normal", "SMB1 Normal")
    if world.options.smb1_expert:
        create_mission_locations(world, "SMB1 Expert", "SMB1 Expert")
    if world.options.smb1_master:
        create_mission_locations(world, "SMB1 Master", "SMB1 Master")
    if world.options.smb2_casual:
        create_mission_locations(world, "SMB2 Casual", "SMB2 Casual")
    if world.options.smb2_normal:
        create_mission_locations(world, "SMB2 Normal", "SMB2 Normal")
    if world.options.smb2_expert:
        create_mission_locations(world, "SMB2 Expert", "SMB2 Expert")
    if world.options.smb2_master:
        create_mission_locations(world, "SMB2 Master", "SMB2 Master")

    # Special Modes
    if world.options.deluxe_stages:
        create_mission_locations(world, "Deluxe Mode", "SP DX")
        create_mission_locations(world, "Deluxe Beginner Pack", "SP DX Beginner")
        create_mission_locations(world, "Deluxe Advanced Pack", "SP DX Advanced")
        create_mission_locations(world, "Deluxe EX Pack", "SP DX EX")

    if world.options.reverse_mode:
        create_mission_locations(world, "Reverse Mode", "SP Reverse")

    if world.options.dark_banana_mode:
        create_mission_locations(world, "Dark Banana Mode", "SP Dark")

    if world.options.golden_banana_mode:
        create_mission_locations(world, "Golden Banana Mode", "SP Golden")

    if world.options.original_stages_mode:
        create_mission_locations(world, "Original Stages Mode", "SP Original")

def create_events(world: BananaManiaWorld) -> None:
    # Temporary goal
    world_10 = world.get_region("World 10")
    world_10.add_event(
        "Cleared World 10", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem
    )
    pass