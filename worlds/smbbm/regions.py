from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Region

if TYPE_CHECKING:
    from .world import BananaManiaWorld

WORLD_REGIONS = [
    "World 1",
    "World 2",
    "World 3",
    "World 4",
    "World 5",
    "World 6",
    "World 7",
    "World 8",
    "World 9",
    "World 10",
]


def create_and_connect_regions(world: BananaManiaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: BananaManiaWorld) -> None:
    overworld = Region("Overworld", world.player, world.multiworld)

    stage_regions = [Region(name, world.player, world.multiworld) for name in WORLD_REGIONS]
    banana_shop = Region("Banana Shop", world.player, world.multiworld)

    world.multiworld.regions += [overworld, *stage_regions, banana_shop]


def connect_regions(world: BananaManiaWorld) -> None:
    overworld = world.get_region("Overworld")

    for region_name in WORLD_REGIONS:
        overworld.connect(world.get_region(region_name), f"Overworld to {region_name}")

    overworld.connect(world.get_region("Banana Shop"), "Overworld to Banana Shop")
