from collections.abc import Mapping
from typing import Any

from worlds.AutoWorld import World

from . import items, locations, regions, rules, web_world
from . import options as smb_options  

# NOTICE: This class, game, web, options/options_dataclass, location_name_to_id, item_name_to_id, origin_region_name, and ut_can_gen_without_yaml
# are human written and required.

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

    # Sort by region then location ids within that region
    # NOTICE: This was ai written, but I came up with the concept. In general, I would recommend just rewriting this to be a better form of
    # sorting each region by their ids, in the order of the WORLD_REGIONS. It looks nice.
    def custom_ut_sort(self, region_label: str, location_label: str) -> int:
        if region_label in regions.WORLD_REGIONS:
            region_index = regions.WORLD_REGIONS.index(region_label)
        else:
            region_index = len(regions.WORLD_REGIONS)
        location_id = self.location_name_to_id.get(location_label, 999999)
        return region_index * 1_000_000 + location_id

    def generate_early(self) -> None:

        # NOTICE: I had the basic idea for this and wrote out the initial, but I had AI make it a little cleaner for me. This 
        # just basically takes the amount of options we have enabled, and ensures that our goal challenge modes option doesn't
        # exceed the amount we have available. Easy to rewrite.
        enabled = sum(bool(getattr(self.options, f"smb{g}_{d}"))
                    for g in (1, 2) for d in ("casual", "normal", "expert", "master"))
        self.options.goal_challenge_modes.value = min(enabled, self.options.goal_challenge_modes.value)

        # NOTICE: This is just the basic template for easy UT access, copy pasted from the UT docs.
        passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if self.game in passthrough:
            for key, value in passthrough[self.game].items():
                if hasattr(self.options, key):
                    getattr(self.options, key).value = value

    # NOTICE: All of the below is from the APQuest template, and fill_slot_data/interpret_slot_data is hand written from the UT docs
    # for universal tracker support. Leave all of this be.
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
            "goal_worlds", "goal_challenge_modes",
            "banana_missions", "time_missions", "extra_goals", "nonstop_missions", "world_structure",
            "logic_difficulty", "smb1_casual", "smb1_normal", "smb1_expert", "smb1_master", 
            "smb2_casual", "smb2_normal", "smb2_expert", "smb2_master", "deluxe_stages",
            "deluxe_unlock_style", "reverse_mode", "dark_banana_mode", "golden_banana_mode", "original_stages_mode" 
        )

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        return slot_data

