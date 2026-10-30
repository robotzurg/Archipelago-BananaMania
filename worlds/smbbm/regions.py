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
    "SMB1 Casual",
    "SMB1 Normal",
    "SMB1 Expert",
    "SMB1 Master",
    "SMB2 Casual",
    "SMB2 Normal",
    "SMB2 Expert",
    "SMB2 Master",
    "Deluxe Mode",
    "Deluxe Beginner Pack",
    "Deluxe Advanced Pack",
    "Deluxe EX Pack",
    "Reverse Mode",
    "Dark Banana Mode",
    "Golden Banana Mode",
    "Original Stages Mode"
]


def create_and_connect_regions(world: BananaManiaWorld) -> None:
    create_all_regions(world)
    connect_regions(world)

# NOTICE: Almost everything in here is just from the APQuest template, though I think
# this function was edited to be a little more efficient with AI? I can't remember. It's pretty straightforward.
def create_all_regions(world: BananaManiaWorld) -> None:
    menu = Region("Menu", world.player, world.multiworld)
    regions = [Region(name, world.player, world.multiworld) for name in WORLD_REGIONS]
    world.multiworld.regions += [menu, *regions]


def connect_regions(world: BananaManiaWorld) -> None:
    menu = world.get_region("Menu")

    for region_name in WORLD_REGIONS:
        menu.connect(world.get_region(region_name), f"Menu to {region_name}")