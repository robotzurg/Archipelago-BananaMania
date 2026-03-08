from __future__ import annotations

from typing import TYPE_CHECKING

from BaseClasses import Location

from . import items

if TYPE_CHECKING:
    from .world import BananaManiaWorld

# Every location must have a unique integer ID associated with it.
# We will have a lookup from location name to ID here that, in world.py, we will import and bind to the world class.
# Even if a location doesn't exist on specific options, it must be present in this lookup.
LOCATION_NAME_TO_ID = {
    # W1-1
    "[W1-1] Stage Clear": 1,
    "[W1-1] Banana Collector 10": 2,
    "[W1-1] Time Limit 10": 3,
    # W1-2
    "[W1-2] Stage Clear": 11,
    "[W1-2] Banana Collector 20": 12,
    "[W1-2] Time Limit 10": 13,
    # W1-3
    "[W1-3] Stage Clear": 21,
    "[W1-3] Banana Collector 30": 22,
    "[W1-3] Time Limit 10": 23,
    # W1-4
    "[W1-4] Stage Clear": 31,
    "[W1-4] Banana Collector 25": 32,
    "[W1-4] Time Limit 10": 33,
    "[W1-4] Green Goal": 34,
    # W1-5
    "[W1-5] Stage Clear": 41,
    "[W1-5] Banana Collector 30": 42,
    "[W1-5] Time Limit 10": 43,
    "[W1-5] Nonstop": 44,
    # W1-6
    "[W1-6] Stage Clear": 51,
    "[W1-6] Banana Collector 50": 52,
    "[W1-6] Time Limit 10": 53,
    # W1-7
    "[W1-7] Stage Clear": 61,
    "[W1-7] Banana Collector 77": 62,
    "[W1-7] Time Limit 10": 63,
    # W1-8
    "[W1-8] Stage Clear": 71,
    "[W1-8] Banana Collector 70": 72,
    "[W1-8] Time Limit 30": 73,
    "[W1-8] Nonstop": 74,
    # W1-9
    "[W1-9] Stage Clear": 81,
    "[W1-9] Banana Collector 20": 82,
    "[W1-9] Time Limit 15": 83,
    # W1-10
    "[W1-10] Stage Clear": 91,
    "[W1-10] Banana Collector 60": 92,
    "[W1-10] Time Limit 35": 93,

    # W2-1
    "[W2-1] Stage Clear": 101,
    "[W2-1] Banana Collector 25": 102,
    "[W2-1] Time Limit 10": 103,
    # W2-2
    "[W2-2] Stage Clear": 111,
    "[W2-2] Banana Collector 20": 112,
    "[W2-2] Time Limit 15": 113,
    # W2-3
    "[W2-3] Stage Clear": 121,
    "[W2-3] Banana Complete": 122,
    "[W2-3] Time Limit 5": 123,
    # W2-4
    "[W2-4] Stage Clear": 131,
    "[W2-4] Banana Collector 55": 132,
    "[W2-4] Time Limit 30": 133,
    # W2-5
    "[W2-5] Stage Clear": 141,
    "[W2-5] Banana Collector 25": 142,
    "[W2-5] Time Limit 15": 143,
    # W2-6
    "[W2-6] Stage Clear": 151,
    "[W2-6] Banana Collector 25": 152,
    "[W2-6] Time Limit 10": 153,
    # W2-7
    "[W2-7] Stage Clear": 161,
    "[W2-7] Banana Collector 70": 162,
    "[W2-7] Time Limit 20": 163,
    # W2-8
    "[W2-8] Stage Clear": 171,
    "[W2-8] Banana Collector 30": 172,
    "[W2-8] Time Limit 15": 173,
    "[W2-8] Green Goal": 174,
    "[W2-8] Red Goal": 175,
    # W2-9
    "[W2-9] Stage Clear": 181,
    "[W2-9] Banana Collector 15": 182,
    "[W2-9] Time Limit 15": 183,
    "[W2-9] Nonstop": 184,
    # W2-10
    "[W2-10] Stage Clear": 191,
    "[W2-10] Banana Collector 18": 192,
    "[W2-10] Time Limit 15": 193,

    # W3-1
    "[W3-1] Stage Clear": 201,
    "[W3-1] Banana Complete": 202,
    "[W3-1] Time Limit 20": 203,
    # W3-2
    "[W3-2] Stage Clear": 211,
    "[W3-2] Banana Collector 30": 212,
    "[W3-2] Time Limit 15": 213,
    # W3-3
    "[W3-3] Stage Clear": 221,
    "[W3-3] Banana Collector 70": 222,
    "[W3-3] Time Limit 20": 223,
    # W3-4
    "[W3-4] Stage Clear": 231,
    "[W3-4] Banana Complete": 232,
    "[W3-4] Time Limit 40": 233,
    "[W3-4] Nonstop": 234,
    # W3-5
    "[W3-5] Stage Clear": 241,
    "[W3-5] Banana Complete": 242,
    "[W3-5] Time Limit 15": 243,
    # W3-6
    "[W3-6] Stage Clear": 251,
    "[W3-6] Banana Collector 30": 252,
    "[W3-6] Time Limit 5": 253,
    "[W3-6] Green Goal": 254,
    "[W3-6] Red Goal": 255,
    # W3-7
    "[W3-7] Stage Clear": 261,
    "[W3-7] Banana Collector 40": 262,
    "[W3-7] Time Limit 15": 263,
    # W3-8
    "[W3-8] Stage Clear": 271,
    "[W3-8] Banana Collector 15": 272,
    "[W3-8] Time Limit 15": 273,
    # W3-9
    "[W3-9] Stage Clear": 281,
    "[W3-9] Banana Collector 25": 282,
    "[W3-9] Time Limit 30": 283,
    # W3-10
    "[W3-10] Stage Clear": 291,
    "[W3-10] Banana Collector 38": 292,
    "[W3-10] Time Limit 15": 293,
    "[W3-10] Green Goal": 294,

    # W4-1
    "[W4-1] Stage Clear": 301,
    "[W4-1] Banana Collector 20": 302,
    "[W4-1] Time Limit 10": 303,
    "[W4-1] Green Goal": 304,
    # W4-2
    "[W4-2] Stage Clear": 311,
    "[W4-2] Banana Collector 20": 312,
    "[W4-2] Time Limit 15": 313,
    "[W4-2] Nonstop": 314,
    # W4-3
    "[W4-3] Stage Clear": 321,
    "[W4-3] Banana Collector 25": 322,
    "[W4-3] Time Limit 15": 323,
    # W4-4
    "[W4-4] Stage Clear": 331,
    "[W4-4] Banana Collector 30": 332,
    "[W4-4] Time Limit 20": 333,
    # W4-5
    "[W4-5] Stage Clear": 341,
    "[W4-5] Banana Collector 30": 342,
    "[W4-5] Time Limit 10": 343,
    "[W4-5] Nonstop": 344,
    # W4-6
    "[W4-6] Stage Clear": 351,
    "[W4-6] Banana Collector 10": 352,
    "[W4-6] Time Limit 20": 353,
    "[W4-6] Green Goal": 354,
    # W4-7
    "[W4-7] Stage Clear": 361,
    "[W4-7] Banana Collector 35": 362,
    "[W4-7] Time Limit 15": 363,
    "[W4-7] Green Goal": 364,
    "[W4-7] Red Goal": 365,
    # W4-8
    "[W4-8] Stage Clear": 371,
    "[W4-8] Banana Complete": 372,
    "[W4-8] Time Limit 30": 373,
    "[W4-8] Green Goal": 374,
    # W4-9
    "[W4-9] Stage Clear": 381,
    "[W4-9] Banana Collector 40": 382,
    "[W4-9] Time Limit 55": 383,
    # W4-10
    "[W4-10] Stage Clear": 391,
    "[W4-10] Banana Complete": 392,
    "[W4-10] Time Limit 30": 393,

    # W5-1
    "[W5-1] Stage Clear": 401,
    "[W5-1] Banana Collector 50": 402,
    "[W5-1] Time Limit 25": 403,
    "[W5-1] Nonstop": 404,
    # W5-2
    "[W5-2] Stage Clear": 411,
    "[W5-2] Banana Collector 50": 412,
    "[W5-2] Time Limit 20": 413,
    "[W5-2] Green Goal": 414,
    # W5-3
    "[W5-3] Stage Clear": 421,
    "[W5-3] Banana Collector 10": 422,
    "[W5-3] Time Limit 15": 423,
    # W5-4
    "[W5-4] Stage Clear": 431,
    "[W5-4] Banana Complete": 432,
    "[W5-4] Time Limit 10": 433,
    # W5-5
    "[W5-5] Stage Clear": 441,
    "[W5-5] Banana Collector 20": 442,
    "[W5-5] Time Limit 15": 443,
    # W5-6
    "[W5-6] Stage Clear": 451,
    "[W5-6] Banana Collector 25": 452,
    "[W5-6] Time Limit 15": 453,
    "[W5-6] Green Goal": 454,
    "[W5-6] Red Goal": 455,
    # W5-7
    "[W5-7] Stage Clear": 461,
    "[W5-7] Banana Collector 25": 462,
    "[W5-7] Time Limit 20": 463,
    # W5-8
    "[W5-8] Stage Clear": 471,
    "[W5-8] Banana Collector 25": 472,
    "[W5-8] Time Limit 15": 473,
    # W5-9
    "[W5-9] Stage Clear": 481,
    "[W5-9] Banana Complete": 482,
    "[W5-9] Time Limit 10": 483,
    # W5-10
    "[W5-10] Stage Clear": 491,
    "[W5-10] Banana Collector 20": 492,
    "[W5-10] Time Limit 20": 493,

    # W6-1
    "[W6-1] Stage Clear": 501,
    "[W6-1] Banana Collector 25": 502,
    "[W6-1] Time Limit 10": 503,
    # W6-2
    "[W6-2] Stage Clear": 511,
    "[W6-2] Banana Collector 21": 512,
    "[W6-2] Time Limit 10": 513,
    "[W6-2] Green Goal": 514,
    # W6-3
    "[W6-3] Stage Clear": 521,
    "[W6-3] Banana Collector 70": 522,
    "[W6-3] Time Limit 35": 523,
    # W6-4
    "[W6-4] Stage Clear": 531,
    "[W6-4] Banana Collector 35": 532,
    "[W6-4] Time Limit 5": 533,
    # W6-5
    "[W6-5] Stage Clear": 541,
    "[W6-5] Banana Collector 20": 542,
    "[W6-5] Time Limit 30": 543,
    "[W6-5] Green Goal": 544,
    "[W6-5] Red Goal": 545,
    # W6-6
    "[W6-6] Stage Clear": 551,
    "[W6-6] Banana Collector 20": 552,
    "[W6-6] Time Limit 30": 553,
    # W6-7
    "[W6-7] Stage Clear": 561,
    "[W6-7] Banana Collector 15": 562,
    "[W6-7] Time Limit 20": 563,
    # W6-8
    "[W6-8] Stage Clear": 571,
    "[W6-8] Banana Collector 20": 572,
    "[W6-8] Time Limit 15": 573,
    "[W6-8] Green Goal": 574,
    # W6-9
    "[W6-9] Stage Clear": 581,
    "[W6-9] Banana Collector 9": 582,
    "[W6-9] Time Limit 15": 583,
    # W6-10
    "[W6-10] Stage Clear": 591,
    "[W6-10] Banana Collector 10": 592,
    "[W6-10] Time Limit 20": 593,

    # W7-1
    "[W7-1] Stage Clear": 601,
    "[W7-1] Banana Collector 20": 602,
    "[W7-1] Time Limit 20": 603,
    # W7-2
    "[W7-2] Stage Clear": 611,
    "[W7-2] Banana Collector 20": 612,
    "[W7-2] Time Limit 10": 613,
    "[W7-2] Nonstop": 614,
    # W7-3
    "[W7-3] Stage Clear": 621,
    "[W7-3] Banana Collector 20": 622,
    "[W7-3] Time Limit 20": 623,
    # W7-4
    "[W7-4] Stage Clear": 631,
    "[W7-4] Banana Collector 25": 632,
    "[W7-4] Time Limit 15": 633,
    # W7-5
    "[W7-5] Stage Clear": 641,
    "[W7-5] Banana Collector 15": 642,
    "[W7-5] Time Limit 30": 643,
    "[W7-5] Nonstop": 644,
    # W7-6
    "[W7-6] Stage Clear": 651,
    "[W7-6] Banana Collector 15": 652,
    "[W7-6] Time Limit 50": 653,
    # W7-7
    "[W7-7] Stage Clear": 661,
    "[W7-7] Banana Collector 10": 662,
    "[W7-7] Time Limit 25": 663,
    # W7-8
    "[W7-8] Stage Clear": 671,
    "[W7-8] Banana Collector 15": 672,
    "[W7-8] Time Limit 25": 673,
    # W7-9
    "[W7-9] Stage Clear": 681,
    "[W7-9] Banana Collector 10": 682,
    "[W7-9] Time Limit 25": 683,
    "[W7-9] Green Goal": 684,
    "[W7-9] Red Goal": 685,
    # W7-10
    "[W7-10] Stage Clear": 691,
    "[W7-10] Banana Complete": 692,
    "[W7-10] Time Limit 10": 693,
    "[W7-10] Nonstop": 694,

    # W8-1
    "[W8-1] Stage Clear": 701,
    "[W8-1] Banana Collector 20": 702,
    "[W8-1] Time Limit 20": 703,
    # W8-2
    "[W8-2] Stage Clear": 711,
    "[W8-2] Banana Collector 16": 712,
    "[W8-2] Time Limit 20": 713,
    # W8-3
    "[W8-3] Stage Clear": 721,
    "[W8-3] Banana Collector 21": 722,
    "[W8-3] Time Limit 10": 723,
    # W8-4
    "[W8-4] Stage Clear": 731,
    "[W8-4] Banana Collector 30": 732,
    "[W8-4] Time Limit 40": 733,
    "[W8-4] Green Goal": 734,
    # W8-5
    "[W8-5] Stage Clear": 741,
    "[W8-5] Banana Collector 28": 742,
    "[W8-5] Time Limit 10": 743,
    # W8-6
    "[W8-6] Stage Clear": 751,
    "[W8-6] Banana Collector 10": 752,
    "[W8-6] Time Limit 30": 753,
    "[W8-6] Green Goal": 754,
    # W8-7
    "[W8-7] Stage Clear": 761,
    "[W8-7] Banana Collector 10": 762,
    "[W8-7] Time Limit 40": 763,
    "[W8-7] Green Goal": 764,
    # W8-8
    "[W8-8] Stage Clear": 771,
    "[W8-8] Banana Collector 40": 772,
    "[W8-8] Time Limit 30": 773,
    # W8-9
    "[W8-9] Stage Clear": 781,
    "[W8-9] Banana Collector 10": 782,
    "[W8-9] Time Limit 30": 783,
    # W8-10
    "[W8-10] Stage Clear": 791,
    "[W8-10] Banana Collector 10": 792,
    "[W8-10] Time Limit 10": 793,
    "[W8-10] Nonstop": 794,

    # W9-1
    "[W9-1] Stage Clear": 801,
    "[W9-1] Banana Collector 10": 802,
    "[W9-1] Time Limit 15": 803,
    "[W9-1] Green Goal": 804,
    "[W9-1] Red Goal": 805,
    # W9-2
    "[W9-2] Stage Clear": 811,
    "[W9-2] Banana Collector 20": 812,
    "[W9-2] Time Limit 15": 813,
    # W9-3
    "[W9-3] Stage Clear": 821,
    "[W9-3] Banana Collector 20": 822,
    "[W9-3] Time Limit 15": 823,
    # W9-4
    "[W9-4] Stage Clear": 831,
    "[W9-4] Banana Collector 20": 832,
    "[W9-4] Time Limit 15": 833,
    "[W9-4] Green Goal": 834,
    # W9-5
    "[W9-5] Stage Clear": 841,
    "[W9-5] Banana Collector 20": 842,
    "[W9-5] Time Limit 40": 843,
    # W9-6
    "[W9-6] Stage Clear": 851,
    "[W9-6] Banana Collector 10": 852,
    "[W9-6] Time Limit 30": 853,
    # W9-7
    "[W9-7] Stage Clear": 861,
    "[W9-7] Banana Collector 12": 862,
    "[W9-7] Time Limit 20": 863,
    # W9-8
    "[W9-8] Stage Clear": 871,
    "[W9-8] Banana Collector 15": 872,
    "[W9-8] Time Limit 10": 873,
    # W9-9
    "[W9-9] Stage Clear": 881,
    "[W9-9] Banana Collector 14": 882,
    "[W9-9] Time Limit 15": 883,
    # W9-10
    "[W9-10] Stage Clear": 891,
    "[W9-10] Banana Collector 40": 892,
    "[W9-10] Time Limit 20": 893,

    # W10-1
    "[W10-1] Stage Clear": 901,
    "[W10-1] Banana Collector 40": 902,
    "[W10-1] Time Limit 10": 903,
    # W10-2
    "[W10-2] Stage Clear": 911,
    "[W10-2] Banana Collector 30": 912,
    "[W10-2] Time Limit 55": 913,
    # W10-3
    "[W10-3] Stage Clear": 921,
    "[W10-3] Banana Collector 10": 922,
    "[W10-3] Time Limit 10": 923,
    # W10-4
    "[W10-4] Stage Clear": 931,
    "[W10-4] Banana Collector 25": 932,
    "[W10-4] Time Limit 15": 933,
    # W10-5
    "[W10-5] Stage Clear": 941,
    "[W10-5] Banana Collector 20": 942,
    "[W10-5] Time Limit 30": 943,
    # W10-6
    "[W10-6] Stage Clear": 951,
    "[W10-6] Banana Collector 20": 952,
    "[W10-6] Time Limit 59": 953,
    # W10-7
    "[W10-7] Stage Clear": 961,
    "[W10-7] Banana Collector 10": 962,
    "[W10-7] Time Limit 45": 963,
    # W10-8
    "[W10-8] Stage Clear": 971,
    "[W10-8] Banana Collector 10": 972,
    "[W10-8] Time Limit 20": 973,
    # W10-9
    "[W10-9] Stage Clear": 981,
    "[W10-9] Banana Collector 29": 982,
    "[W10-9] Time Limit 50": 983,
    # W10-10
    "[W10-10] Stage Clear": 991,
    "[W10-10] Banana Collector 25": 992,
    "[W10-10] Time Limit 25": 993,

    # Shop Locations
    "Banana Shop Item 1": 1000,
    "Banana Shop Item 2": 1001,
    "Banana Shop Item 3": 1002,
    "Banana Shop Item 4": 1003,
    "Banana Shop Item 5": 1004,
    "Banana Shop Item 6": 1005,
    "Banana Shop Item 7": 1006,
    "Banana Shop Item 8": 1007,
    "Banana Shop Item 9": 1008,
    "Banana Shop Item 10": 1009,
    "Banana Shop Item 11": 1010,
    "Banana Shop Item 12": 1011,
    "Banana Shop Item 13": 1012,
    "Banana Shop Item 14": 1013,
    "Banana Shop Item 15": 1014,
    "Banana Shop Item 16": 1015,
    "Banana Shop Item 17": 1016,
    "Banana Shop Item 18": 1017,
    "Banana Shop Item 19": 1018,
    "Banana Shop Item 20": 1019,
    "Banana Shop Item 21": 1020,
    "Banana Shop Item 22": 1021,
    "Banana Shop Item 23": 1022,
    "Banana Shop Item 24": 1023,
    "Banana Shop Item 25": 1024,
    "Banana Shop Item 26": 1025,
    "Banana Shop Item 27": 1026,
    "Banana Shop Item 28": 1027,
    "Banana Shop Item 29": 1028,
    "Banana Shop Item 30": 1029,
    "Banana Shop Item 31": 1030,
    "Banana Shop Item 32": 1031,

}


# Each Location instance must correctly report the "game" it belongs to.
# To make this simple, it is common practice to subclass the basic Location class and override the "game" field.
class BananaManiaLocation(Location):
    game = "Super Monkey Ball Banana Mania"


# Let's make one more helper method before we begin actually creating locations.
# Later on in the code, we'll want specific subsections of LOCATION_NAME_TO_ID.
# To reduce the chance of copy-paste errors writing something like {"Chest": LOCATION_NAME_TO_ID["Chest"]},
# let's make a helper method that takes a list of location names and returns them as a dict with their IDs.
# Note: There is a minor typing quirk here. Some functions want location addresses to be an "int | None",
# so while our function here only ever returns dict[str, int], we annotate it as dict[str, int | None].
def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: BananaManiaWorld) -> None:
    create_regular_locations(world)
    create_events(world)


def _include_location(name: str, world: BananaManiaWorld) -> bool:
    """Return True if this stage location should be created given the current options."""
    if "Stage Clear" in name:
        return True
    if ("Banana Collector" in name or "Banana Complete" in name) and not world.options.banana_missions:
        return False
    if "Time Limit" in name and not world.options.time_missions:
        return False
    if ("Green Goal" in name or "Red Goal" in name or "Nonstop" in name) and not world.options.extra_goals:
        return False
    return True


def create_regular_locations(world: BananaManiaWorld) -> None:
    # Group stage locations by world number (W1 through W10).
    for world_num in range(1, 11):
        prefix = f"[W{world_num}-"
        region = world.get_region(f"World {world_num}")
        stage_locations = get_location_names_with_ids(
            [name for name in LOCATION_NAME_TO_ID
             if name.startswith(prefix) and _include_location(name, world)]
        )
        region.add_locations(stage_locations, BananaManiaLocation)

    # Banana Shop locations.
    banana_shop = world.get_region("Banana Shop")
    shop_locations = get_location_names_with_ids(
        [name for name in LOCATION_NAME_TO_ID if name.startswith("Banana Shop Item")]
    )
    banana_shop.add_locations(shop_locations, BananaManiaLocation)


def create_events(world: BananaManiaWorld) -> None:
    # Place the Victory event on World 10, representing completion of the final world.
    world_10 = world.get_region("World 10")
    world_10.add_event(
        "Cleared World 10", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem
    )
