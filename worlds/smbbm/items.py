from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import BananaManiaWorld

ITEM_NAME_TO_ID = {
    "Progressive World Unlock": 1,
    "Jungle Island Unlock": 2,
    "Volcanic Magma Unlock": 3,
    "Under the Ocean Unlock": 4,
    "Inside a Whale Unlock": 5,
    "Amusement Park Unlock": 6,
    "Boiling Pot Unlock": 7,
    "Bubbly Washing Machine Unlock": 8,
    "Clock Tower Factory Unlock": 9,
    "Space Colony Unlock": 10,
    "Dr. Bad-Boon's Base Unlock": 11,
    "SMB1 Casual Challenge Mode Unlock": 12,
    "SMB1 Normal Challenge Mode Unlock": 13,
    "SMB1 Expert Challenge Mode Unlock": 14,
    "SMB1 Master Challenge Mode Unlock": 15,
    "SMB2 Casual Challenge Mode Unlock": 16,
    "SMB2 Normal Challenge Mode Unlock": 17,
    "SMB2 Expert Challenge Mode Unlock": 18,
    "SMB2 Master Challenge Mode Unlock": 19,
    "Reverse Mode Unlock": 20,
    "Dark Banana Mode Unlock": 21,
    "Golden Banana Mode Unlock": 22,
    "Original Stages Mode Unlock": 23,
    "Deluxe Stages Unlock": 24,
    "Deluxe Beginner Stages Pack Unlock": 25,
    "Deluxe Advanced Stages Pack Unlock": 26,
    "Deluxe EX Stages Pack Unlock": 27,
    "Normal Switches": 101,
    "Wormholes": 102,
    "Fast Switches": 103,
    "Pause Switches": 104,
    "Progressive Time Increase": 201,
    "+10 Time Bonus": 202,
    "+20 Time Bonus": 203,
    "+30 Time Bonus": 204,
    "AiAi": 401,
    "MeeMee": 402,
    "Baby": 403,
    "GonGon": 404,
    "YanYan": 405,
    "Doctor": 406,
    "Jam": 407,
    "Jet": 408,
    "Sonic": 409,
    "Tails": 410,
    "Beat": 411,
    "Kiryu": 412
}

DEFAULT_ITEM_CLASSIFICATIONS = {
    "Progressive World Unlock": ItemClassification.progression,
    "Jungle Island Unlock": ItemClassification.progression,
    "Volcanic Magma Unlock": ItemClassification.progression,
    "Under the Ocean Unlock": ItemClassification.progression,
    "Inside a Whale Unlock": ItemClassification.progression,
    "Amusement Park Unlock": ItemClassification.progression,
    "Boiling Pot Unlock": ItemClassification.progression,
    "Bubbly Washing Machine Unlock": ItemClassification.progression,
    "Clock Tower Factory Unlock": ItemClassification.progression,
    "Space Colony Unlock": ItemClassification.progression,
    "Dr. Bad-Boon's Base Unlock": ItemClassification.progression,
    "Normal Switches": ItemClassification.progression,
    "Wormholes": ItemClassification.progression,
    "Fast Switches": ItemClassification.progression,
    "Pause Switches": ItemClassification.progression,
    "Progressive Time Increase": ItemClassification.progression,
    "+10 Time Bonus": ItemClassification.useful,
    "+20 Time Bonus": ItemClassification.useful,
    "+30 Time Bonus": ItemClassification.useful,
    "AiAi": ItemClassification.filler,
    "MeeMee": ItemClassification.filler,
    "Baby": ItemClassification.filler,
    "GonGon": ItemClassification.filler,
    "YanYan": ItemClassification.filler,
    "Doctor": ItemClassification.filler,
    "Jam": ItemClassification.filler,
    "Jet": ItemClassification.filler,
    "Sonic": ItemClassification.filler,
    "Tails": ItemClassification.filler,
    "Beat": ItemClassification.filler,
    "Kiryu": ItemClassification.filler,
}

class BananaManiaItem(Item):
    game = "Super Monkey Ball Banana Mania"

def get_random_filler_item_name(world: BananaManiaWorld) -> str:
    return "10 Banana Points"

def create_item_with_correct_classification(world: BananaManiaWorld, name: str) -> BananaManiaItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return BananaManiaItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


INDIVIDUAL_WORLD_UNLOCKS = [
    "Jungle Island Unlock",
    "Volcanic Magma Unlock",
    "Under the Ocean Unlock",
    "Inside a Whale Unlock",
    "Amusement Park Unlock",
    "Boiling Pot Unlock",
    "Bubbly Washing Machine Unlock",
    "Clock Tower Factory Unlock",
    "Space Colony Unlock",
    "Dr. Bad-Boon's Base Unlock",
]


def create_all_items(world: BananaManiaWorld) -> None:
    itempool: list[Item] = []

    if world.options.world_structure == 0:  # progression
        itempool += [world.create_item("Progressive World Unlock") for _ in range(10)]
    else:  # worlds
        itempool += [world.create_item(name) for name in INDIVIDUAL_WORLD_UNLOCKS]

    # Progression items that gate content.
    itempool.append(world.create_item("Normal Switches"))
    itempool.append(world.create_item("Wormholes"))
    itempool.append(world.create_item("Fast Switches"))
    itempool.append(world.create_item("Pause Switches"))

    # Progressive Time Increases increase by +10, to a max of 60. You start with 10 seconds, so 5.
    itempool += [world.create_item("Progressive Time Increase") for _ in range(5)]

    # Useful time bonus items.
    itempool += [world.create_item("+10 Time Bonus") for _ in range(5)]
    itempool += [world.create_item("+20 Time Bonus") for _ in range(3)]
    itempool += [world.create_item("+30 Time Bonus") for _ in range(2)]

    # Character unlock items.
    for character in ["AiAi", "MeeMee", "Baby", "GonGon", "YanYan", "Doctor",
                      "Jam", "Jet", "Sonic", "Tails", "Beat", "Kiryu"]:
        itempool.append(world.create_item(character))

    # Fill remaining locations with filler.
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - len(itempool)
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
