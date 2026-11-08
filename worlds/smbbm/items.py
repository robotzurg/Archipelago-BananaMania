from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import BananaManiaWorld

ITEM_NAME_TO_ID = {
    "Progressive World Unlock": 1,
    "World 2: Volcanic Magma Unlock": 2,
    "World 3: Under the Ocean Unlock": 3,
    "World 4: Inside a Whale Unlock": 4,
    "World 5: Amusement Park Unlock": 5,
    "World 6: Boiling Pot Unlock": 6,
    "World 7: Bubbly Washing Machine Unlock": 7,
    "World 8: Clock Tower Factory Unlock": 8,
    "World 9: Space Colony Unlock": 9,
    "World 10: Dr. Bad-Boon's Base Unlock": 10,
    "SMB1 Casual Challenge Mode Unlock": 11,
    "SMB1 Normal Challenge Mode Unlock": 12,
    "SMB1 Expert Challenge Mode Unlock": 13,
    "SMB1 Master Challenge Mode Unlock": 14,
    "SMB2 Casual Challenge Mode Unlock": 15,
    "SMB2 Normal Challenge Mode Unlock": 16,
    "SMB2 Expert Challenge Mode Unlock": 17,
    "SMB2 Master Challenge Mode Unlock": 18,
    "Reverse Mode Unlock": 19,
    "Dark Banana Mode Unlock": 20,
    "Golden Banana Mode Unlock": 21,
    "Original Stages Mode Unlock": 22,
    "Deluxe Mode Unlock": 23,
    "Deluxe Beginner Stages Pack": 24,
    "Deluxe Advanced Stages Pack": 25,
    "Deluxe EX Stages Pack": 26,
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
    "World 2: Volcanic Magma Unlock": ItemClassification.progression,
    "World 3: Under the Ocean Unlock": ItemClassification.progression,
    "World 4: Inside a Whale Unlock": ItemClassification.progression,
    "World 5: Amusement Park Unlock": ItemClassification.progression,
    "World 6: Boiling Pot Unlock": ItemClassification.progression,
    "World 7: Bubbly Washing Machine Unlock": ItemClassification.progression,
    "World 8: Clock Tower Factory Unlock": ItemClassification.progression,
    "World 9: Space Colony Unlock": ItemClassification.progression,
    "World 10: Dr. Bad-Boon's Base Unlock": ItemClassification.progression,
    "SMB1 Casual Challenge Mode Unlock": ItemClassification.progression,
    "SMB1 Normal Challenge Mode Unlock": ItemClassification.progression,
    "SMB1 Expert Challenge Mode Unlock": ItemClassification.progression,
    "SMB1 Master Challenge Mode Unlock": ItemClassification.progression,
    "SMB2 Casual Challenge Mode Unlock": ItemClassification.progression,
    "SMB2 Normal Challenge Mode Unlock": ItemClassification.progression,
    "SMB2 Expert Challenge Mode Unlock": ItemClassification.progression,
    "SMB2 Master Challenge Mode Unlock": ItemClassification.progression,
    "Reverse Mode Unlock": ItemClassification.progression,
    "Dark Banana Mode Unlock": ItemClassification.progression,
    "Golden Banana Mode Unlock": ItemClassification.progression,
    "Original Stages Mode Unlock": ItemClassification.progression,
    "Deluxe Mode Unlock": ItemClassification.progression,
    "Deluxe Beginner Stages Pack": ItemClassification.progression,
    "Deluxe Advanced Stages Pack": ItemClassification.progression,
    "Deluxe EX Stages Pack": ItemClassification.progression,
    "Normal Switches": ItemClassification.progression,
    "Wormholes": ItemClassification.progression,
    "Fast Switches": ItemClassification.progression,
    "Pause Switches": ItemClassification.progression,
    "Progressive Time Increase": ItemClassification.progression,
    "+10 Time Bonus": ItemClassification.filler,
    "+20 Time Bonus": ItemClassification.filler,
    "+30 Time Bonus": ItemClassification.filler,
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
    return world.random.choices(
        ["+10 Time Bonus", "+20 Time Bonus", "+30 Time Bonus"],
        weights=[6, 3, 1],
    )[0]

def create_item_with_correct_classification(world: BananaManiaWorld, name: str) -> BananaManiaItem:
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]
    return BananaManiaItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


def create_all_items(world: BananaManiaWorld) -> None:
    itempool: list[Item] = []

    # SMB 2 worlds
    if world.options.world_structure == 0:  # progression
        itempool += [world.create_item("Progressive World Unlock") for _ in range(9)]
    else:  # worlds
        itempool += [world.create_item(name) for name in ITEM_NAME_TO_ID[2:10]]

    if world.options.smb1_casual == 1:
        itempool.append(world.create_item(f"SMB1 Casual Challenge Mode Unlock"))
    if world.options.smb1_normal == 1:
        itempool.append(world.create_item(f"SMB1 Normal Challenge Mode Unlock"))
    if world.options.smb1_expert == 1:
        itempool.append(world.create_item(f"SMB1 Expert Challenge Mode Unlock"))
    if world.options.smb1_master == 1:
        itempool.append(world.create_item(f"SMB1 Master Challenge Mode Unlock"))
        
    if world.options.smb1_normal == 1:
        itempool.append(world.create_item(f"SMB2 Casual Challenge Mode Unlock"))
    if world.options.smb1_normal == 1:
        itempool.append(world.create_item(f"SMB2 Normal Challenge Mode Unlock"))
    if world.options.smb1_normal == 1:
        itempool.append(world.create_item(f"SMB2 Expert Challenge Mode Unlock"))
    if world.options.smb1_normal == 1:
        itempool.append(world.create_item(f"SMB2 Master Challenge Mode Unlock"))

    if world.options.reverse_mode == 1:
        itempool.append(world.create_item(f"Reverse Mode Unlock"))
    if world.options.dark_banana_mode == 1:
        itempool.append(world.create_item(f"Dark Banana Mode Unlock"))
    if world.options.golden_banana_mode == 1:
        itempool.append(world.create_item(f"Golden Banana Mode Unlock"))
    if world.options.original_stages_mode == 1:
        itempool.append(world.create_item(f"Original Stages Mode Unlock"))
        

    if world.options.deluxe_stages:
        if world.options.deluxe_unlock_style == 0: # all
            itempool.append(world.create_item("Deluxe Mode Unlock"))
        else:
            itempool.append(world.create_item("Deluxe Beginner Stages Pack"))
            itempool.append(world.create_item("Deluxe Advanced Stages Pack"))
            itempool.append(world.create_item("Deluxe EX Stages Pack"))

    # Gimmick items
    itempool.append(world.create_item("Normal Switches"))
    itempool.append(world.create_item("Wormholes"))
    itempool.append(world.create_item("Fast Switches"))
    itempool.append(world.create_item("Pause Switches"))

    # 5 Time increases, you start at 10 seconds, max of 60. Increases by 10 seconds each item.
    itempool += [world.create_item("Progressive Time Increase") for _ in range(5)]

    # Character unlock items, these are just filler
    for character in ["AiAi", "MeeMee", "Baby", "GonGon", "YanYan", "Doctor",
                      "Jam", "Jet", "Sonic", "Tails", "Beat", "Kiryu"]:
        itempool.append(world.create_item(character))

    # Fill remaining locations with filler.
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - len(itempool)
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
