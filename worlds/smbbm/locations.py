from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from BaseClasses import Location
from . import items
from .regions import WORLD_REGIONS
from .mission_data import MISSION_DATA_DICT, CATEGORY_DATA_DICT, MissionType
from rule_builder.rules import HasAny, Or, OptionFilter, Has, Rule, AtLeast
from .options import DeluxeUnlockStyle

if TYPE_CHECKING:
    from .world import BananaManiaWorld

class BananaManiaLocation(Location):
    game = "Super Monkey Ball Banana Mania"

def get_location_names_with_ids() -> dict[str, int | None]:
    loc_list = {}
    
    for region in WORLD_REGIONS:
        if region in MISSION_DATA_DICT:
            region_loc_list = MISSION_DATA_DICT[region].get_region_locations()
            for loc in region_loc_list:
                loc_list[loc[0]] = loc[1]
                
        if region in CATEGORY_DATA_DICT:
            region_loc_list = CATEGORY_DATA_DICT[region].get_region_locations()  
            for loc in region_loc_list:
                loc_list[loc[0]] = loc[1] 
        
    return loc_list

def get_disabled_regions(world: BananaManiaWorld) -> list[str]:
    disabled_regions = []
    if world.options.reverse_mode == 0:
        disabled_regions.append("Reverse Mode")
    if world.options.dark_banana_mode == 0:
        disabled_regions.append("Dark Banana Mode")
    if world.options.golden_banana_mode == 0:
        disabled_regions.append("Golden Banana Mode")
    if world.options.original_stages_mode == 0:
        disabled_regions.append("Original Stages Mode")
    if world.options.deluxe_stages == 0:
        disabled_regions.append("Deluxe Mode")
        disabled_regions.append("Deluxe Beginner Pack")
        disabled_regions.append("Deluxe Advanced Pack")
        disabled_regions.append("Deluxe EX Pack")
    
    return disabled_regions

def get_disabled_missions(world: BananaManiaWorld) -> list[MissionType]:
    disabled_missions = []
    if world.options.time_missions == 0:
        disabled_missions.append(MissionType.TIME)
    if world.options.banana_missions == 0:
        disabled_missions.append(MissionType.BANANA)
    if world.options.extra_goals == 0:
        disabled_missions.append(MissionType.GREEN)
        disabled_missions.append(MissionType.RED)
    if world.options.nonstop_missions == 0:
        disabled_missions.append(MissionType.NONSTOP)
        
    return disabled_missions

def create_all_locations(world: BananaManiaWorld) -> None:
    create_regular_locations(world)
    create_events(world) 

def create_regular_locations(world: BananaManiaWorld) -> None:
    disabled_regions = get_disabled_regions(world)
    disabled_missions = get_disabled_missions(world)
    
    for region in WORLD_REGIONS:
        if region in disabled_regions:
            continue
        
        if region != "Deluxe Mode":
            region_data = MISSION_DATA_DICT[region] 
            world_region = world.get_region(region)
        
            if len(region_data) != 0:
                region_entrance = world.get_entrance(f"Menu to {region}")
                world.set_rule(region_entrance, region_data.req_items)
                
                for stage in region_data.stage_data:
                    for idx, mission in enumerate(stage.missions):
                        if mission.mission_type in disabled_missions:
                            continue
                        loc_name = stage.get_named_mission_location(idx)
                        loc_id = stage.get_mission_loc_id(idx)
                        
                        world_region.add_locations({loc_name: loc_id}, BananaManiaLocation)
                        loc = world.get_location(loc_name)
                        world.set_rule(loc, mission.get_mission_item_req(world.options.logic_difficulty))
            
        if region == "Deluxe Mode":
            world_region = world.get_region(region)
            category_data = CATEGORY_DATA_DICT[region]
            world.set_rule(world.get_entrance(f"Menu to {region}"), category_data.req_items)
        
        if region in CATEGORY_DATA_DICT:
            category_data = CATEGORY_DATA_DICT[region]
            for idx, mission in enumerate(category_data.missions):
                loc_name = category_data.get_named_mission_location(idx)
                loc_id = category_data.get_mission_loc_id(idx)
                
                world_region.add_locations({loc_name: loc_id}, BananaManiaLocation)
                loc = world.get_location(loc_name)
                world.set_rule(loc, category_data.get_stage_win_rule(mission.amount, world.options.logic_difficulty))
    

def create_events(world: BananaManiaWorld) -> None:
    menu = world.get_region("Menu")
    smb2_world_complete_rules: list[Rule] = []
    for world_region in WORLD_REGIONS[0:10]:
        smb2_world_complete_rules.append(MISSION_DATA_DICT[world_region].get_full_stage_clear_rule(world.options.logic_difficulty))

    menu.add_event(
        "Goal", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem,
        rule=AtLeast(world.options.goal_worlds.value, *smb2_world_complete_rules)
    )
    
    world.set_completion_rule(Has("Victory"))