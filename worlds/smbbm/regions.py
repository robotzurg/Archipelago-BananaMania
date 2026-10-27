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
    "SMB1 Challenge Mode Casual",
    "SMB1 Challenge Mode Normal",
    "SMB1 Challenge Mode Expert",
    "SMB1 Challenge Mode Master",
    "SMB2 Challenge Mode Casual",
    "SMB2 Challenge Mode Normal",
    "SMB2 Challenge Mode Expert",
    "SMB2 Challenge Mode Master",
    "Deluxe Mode",
    "Reverse Mode",
    "Dark Banana Mode",
    "Golden Banana Mode",
    "Original Stages Mode"
]


def create_and_connect_regions(world: BananaManiaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)


def create_all_regions(world: BananaManiaWorld) -> None:
    menu = Region("Menu", world.player, world.multiworld)
    regions = [Region(name, world.player, world.multiworld) for name in WORLD_REGIONS]
    world.multiworld.regions += [menu, *regions]


def connect_regions(world: BananaManiaWorld) -> None:
    menu = world.get_region("Menu")

    for region_name in WORLD_REGIONS:
        menu.connect(world.get_region(region_name), f"Menu to {region_name}")