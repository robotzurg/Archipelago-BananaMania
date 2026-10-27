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

    origin_region_name = "Menu"

    ut_can_gen_without_yaml = True

    def generate_early(self) -> None:
        passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if self.game in passthrough:
            for key, value in passthrough[self.game].items():
                if hasattr(self.options, key):
                    getattr(self.options, key).value = value


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
            "banana_missions", "time_missions", "extra_goals", "nonstop_missions", "world_structure",
            "logic_difficulty", "smb1_casual", "smb1_normal", "smb1_expert", "smb1_master", 
            "smb2_casual", "smb2_normal", "smb2_expert", "smb2_master", "deluxe_stages",
            "deluxe_unlock_style", "reverse_mode", "dark_banana_mode", "golden_banana_mode", "original_stages_mode" 
        )

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        return slot_data

