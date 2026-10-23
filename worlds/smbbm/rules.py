from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING
from rule_builder.rules import Has

from .locations import AnyOf, Requirement

if TYPE_CHECKING:
    from BaseClasses import CollectionState

    from .world import BananaManiaWorld

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


def has_requirement(state: CollectionState, player: int, requirement: Requirement) -> bool:
    """True when every term of the requirement is satisfied. AnyOf terms need one alternative."""
    return all(_has_term(state, player, term) for term in requirement)


def _has_term(state: CollectionState, player: int, term: str | AnyOf) -> bool:
    if isinstance(term, AnyOf):
        return any(has_requirement(state, player, alt) for alt in term.alternatives)
    return state.has(term, player)


def set_all_rules(world: BananaManiaWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: BananaManiaWorld) -> None:
    for world_num in range(1, 11):
        entrance = world.get_entrance(f"Overworld to World {world_num}")
        if world.options.world_structure == 0:  # progression
            world.set_rule(entrance, Has("Progressive World Unlock", world_num))
        else:  # individual
            unlock_name = WORLD_UNLOCK_NAMES[world_num - 1]
            world.set_rule(entrance, Has(unlock_name))


def set_all_location_rules(world: BananaManiaWorld) -> None:
    for location in world.multiworld.get_locations(world.player):
        name = location.name

        # Time Limit logic, you start with 10 seconds
        time_match = re.search(r"Time Limit (\d+)", name)
        if time_match:
            limit = int(time_match.group(1))
            upgrades = math.ceil((limit - 10) / 10)
            if upgrades > 0:
                world.set_rule(location, Has("Progressive Time Increase", upgrades))
            continue


def set_completion_condition(world: BananaManiaWorld) -> None:
    world.set_completion_rule(Has("Victory"))
