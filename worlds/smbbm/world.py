from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as smb_options  

class BananaManiaWorld(World):
    """
    Super Monkey Ball Banana Mania is a Super Monkey Ball game that brings together the
    classic levels from Super Monkey Ball 1 and 2, with remastered graphics and new modes.
    """

    game = "Super Monkey Ball Banana Mania"

    web = web_world.BananaManiaWebWorld()

    options_dataclass = smb_options.BananaManiaOptions
    options: smb_options.BananaManiaOptions

    location_name_to_id = locations.LOCATION_NAME_TO_ID
    item_name_to_id = items.ITEM_NAME_TO_ID

    origin_region_name = "Overworld"

    def create_regions(self) -> None:
        regions.create_and_connect_regions(self)
        locations.create_all_locations(self)

    def set_rules(self) -> None:
        rules.set_all_rules(self)

    def create_items(self) -> None:
        items.create_all_items(self)

    def create_item(self, name: str) -> items.BananaManiaItem:
        return items.create_item_with_correct_classification(self, name)
    
    def get_filler_item_name(self) -> str:
        return items.get_random_filler_item_name(self)

    def fill_slot_data(self) -> Mapping[str, Any]:
        return self.options.as_dict(
            "banana_missions", "time_missions", "extra_goals", "nonstop_missions", "world_structure"
        )
