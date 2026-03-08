from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import BananaManiaWorld

# Maps world number (1-10) to its individual unlock item name.
WORLD_UNLOCK_NAMES = [
    "Jungle Island Unlock",           # World 1
    "Volcanic Magma Unlock",          # World 2
    "Under the Ocean Unlock",         # World 3
    "Inside a Whale Unlock",          # World 4
    "Amusement Park Unlock",          # World 5
    "Boiling Pot Unlock",             # World 6
    "Bubbly Washing Machine Unlock",  # World 7
    "Clock Tower Factory Unlock",     # World 8
    "Space Colony Unlock",            # World 9
    "Dr. Bad-Boon's Base Unlock",     # World 10
]


def set_all_rules(world: BananaManiaWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: BananaManiaWorld) -> None:
    for world_num in range(1, 11):
        entrance = world.get_entrance(f"Overworld to World {world_num}")
        if world.options.world_structure == 0:  # progression
            # Each world N requires N "Progressive World Unlock" items.
            entrance.access_rule = (
                lambda state, n=world_num: state.has("Progressive World Unlock", world.player, n)
            )
        else:  # worlds — each world has its own specific unlock
            unlock_name = WORLD_UNLOCK_NAMES[world_num - 1]
            entrance.access_rule = (
                lambda state, name=unlock_name: state.has(name, world.player)
            )


def set_all_location_rules(world: BananaManiaWorld) -> None:
    for location in world.multiworld.get_locations(world.player):
        name = location.name

        # Time Limit missions require enough Progressive Time Increases.
        # The player starts with 10 seconds; each upgrade adds 10 seconds (max 60s).
        # Formula: upgrades_needed = ceil((limit - 10) / 10)
        time_match = re.search(r"Time Limit (\d+)", name)
        if time_match:
            limit = int(time_match.group(1))
            upgrades = math.ceil((limit - 10) / 10)
            if upgrades > 0:
                location.access_rule = (
                    lambda state, n=upgrades: state.has("Progressive Time Increase", world.player, n)
                )
            continue


def set_completion_condition(world: BananaManiaWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
