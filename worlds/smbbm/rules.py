from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from rule_builder.rules import AtLeast, CanReachRegion, Has, True_, HasAny, Rule
from math import ceil

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from .world import BananaManiaWorld

def set_all_rules(world: BananaManiaWorld) -> None:
    set_completion_condition(world)

def set_completion_condition(world: BananaManiaWorld) -> None:
    world.set_completion_rule(Has("Victory"))
