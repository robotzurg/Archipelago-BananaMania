from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Item, ItemClassification

if TYPE_CHECKING:
    from .world import BananaManiaWorld

# Every item must have a unique integer ID associated with it.
# We will have a lookup from item name to ID here that, in world.py, we will import and bind to the world class.
# Even if an item doesn't exist on specific options, it must be present in this lookup.
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
    "Switches": 12,
    "Wormholes": 13,
    "Progressive Time Increase": 14,
    "+10 Time Bonus": 15,
    "+20 Time Bonus": 16,
    "+30 Time Bonus": 17,
    "10 Banana Points": 18,
    "100 Banana Points": 19,
    "1000 Banana Points": 20,
    "AiAi": 21,
    "MeeMee": 22,
    "Baby": 23,
    "GonGon": 24,
    "YanYan": 25,
    "Doctor": 26,
    "Jam": 27,
    "Jet": 28,
    "Sonic": 29,
    "Tails": 30,
    "Beat": 31,
    "Kiryu": 32,
}

# Items should have a defined default classification.
# In our case, we will make a dictionary from item name to classification.
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
    "Switches": ItemClassification.progression,
    "Wormholes": ItemClassification.progression,
    "Progressive Time Increase": ItemClassification.progression,
    "+10 Time Bonus": ItemClassification.useful,
    "+20 Time Bonus": ItemClassification.useful,
    "+30 Time Bonus": ItemClassification.useful,
    "10 Banana Points": ItemClassification.useful,
    "100 Banana Points": ItemClassification.useful,
    "1000 Banana Points": ItemClassification.useful,
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


# Each Item instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Item class and override the "game" field.
class BananaManiaItem(Item):
    game = "Super Monkey Ball Banana Mania"


# Ontop of our regular itempool, our world must be able to create arbitrary amounts of filler as requested by core.
# To do this, it must define a function called world.get_filler_item_name(), which we will define in world.py later.
# For now, let's make a function that returns the name of a random filler item here in items.py.
def get_random_filler_item_name(world: BananaManiaWorld) -> str:
    return "10 Banana Points"


def create_item_with_correct_classification(world: BananaManiaWorld, name: str) -> BananaManiaItem:
    # Our world class must have a create_item() function that can create any of our items by name at any time.
    # So, we make this helper function that creates the item by name with the correct classification.
    # Note: This function's content could just be the contents of world.create_item in world.py directly,
    # but it seemed nicer to have it in its own function over here in items.py.
    classification = DEFAULT_ITEM_CLASSIFICATIONS[name]

    # It is perfectly normal and valid for an item's classification to differ based on the player's options.
    # Not currently used in Banana Mania

    return BananaManiaItem(name, classification, ITEM_NAME_TO_ID[name], world.player)


# With those two helper functions defined, let's now get to actually creating and submitting our itempool.
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

    # World unlock items: either 10 Progressive World Unlocks or 10 individual world unlocks.
    if world.options.world_structure == 0:  # progression
        itempool += [world.create_item("Progressive World Unlock") for _ in range(10)]
    else:  # worlds
        itempool += [world.create_item(name) for name in INDIVIDUAL_WORLD_UNLOCKS]

    # Progression items that gate content.
    itempool.append(world.create_item("Switches"))
    itempool.append(world.create_item("Wormholes"))

    # Progressive Time Increases increase by +10, to a max of 60. You start with 10 seconds, so 5.
    itempool += [world.create_item("Progressive Time Increase") for _ in range(5)]

    # Useful time bonus items.
    itempool += [world.create_item("+10 Time Bonus") for _ in range(5)]
    itempool += [world.create_item("+20 Time Bonus") for _ in range(3)]
    itempool += [world.create_item("+30 Time Bonus") for _ in range(2)]

    # Banana point items.
    itempool += [world.create_item("10 Banana Points") for _ in range(10)]
    itempool += [world.create_item("100 Banana Points") for _ in range(10)]
    itempool += [world.create_item("1000 Banana Points") for _ in range(10)]

    # Character unlock items.
    for character in ["AiAi", "MeeMee", "Baby", "GonGon", "YanYan", "Doctor",
                      "Jam", "Jet", "Sonic", "Tails", "Beat", "Kiryu"]:
        itempool.append(world.create_item(character))

    # Fill remaining locations with filler.
    number_of_unfilled_locations = len(world.multiworld.get_unfilled_locations(world.player))
    needed_number_of_filler_items = number_of_unfilled_locations - len(itempool)
    itempool += [world.create_filler() for _ in range(needed_number_of_filler_items)]

    world.multiworld.itempool += itempool
