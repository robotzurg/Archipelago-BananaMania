from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .world import BananaManiaWorld


def set_all_rules(world: BananaManiaWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)


def set_all_entrance_rules(world: BananaManiaWorld) -> None:
    # Entrance rules between worlds can be added here later.
    # For now, all worlds are freely accessible from the Overworld.
    pass


def set_all_location_rules(world: BananaManiaWorld) -> None:
    # Per-location rules can be added here later.
    pass


def set_completion_condition(world: BananaManiaWorld) -> None:
    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)
