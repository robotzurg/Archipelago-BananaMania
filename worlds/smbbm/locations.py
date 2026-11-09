from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING
import json

from BaseClasses import Location
from . import items
from .regions import WORLD_REGIONS
from .data.mission_data import MISSION_DATA_DICT

if TYPE_CHECKING:
    from .world import BananaManiaWorld

class BananaManiaLocation(Location):
    game = "Super Monkey Ball Banana Mania"

def get_location_names_with_ids() -> dict[str, int | None]:
    loc_list = {}
    
    for region in WORLD_REGIONS:
        region_loc_list = MISSION_DATA_DICT[region].get_region_locations()
        for loc in region_loc_list:
            loc_list[loc[0]] = loc[1]
            
    return loc_list

def get_disabled_regions(world: BananaManiaWorld) -> list[str]:
    disabled_regions = []
    if world.options.reverse_mode == 0:
        disabled_regions.append("Reverse Mode")
    if world.options.deluxe_stages == 0:
        disabled_regions.append("Deluxe Beginner Pack")
        disabled_regions.append("Deluxe Advanced Pack")
        disabled_regions.append("Deluxe EX Pack")
    
    return disabled_regions

def create_all_locations(world: BananaManiaWorld) -> None:
    create_regular_locations(world)
    create_events(world) 

def create_regular_locations(world: BananaManiaWorld) -> None:
    disabled_regions = get_disabled_regions(world)
    
    for region in WORLD_REGIONS:
        region_data = MISSION_DATA_DICT[region]
        world_region = world.get_region(region)
        
        if region in disabled_regions:
            continue
        
        if len(region_data) != 0:
            region_entrance = world.get_entrance(f"Menu to {region}")
            world.set_rule(region_entrance, region_data.req_items)
            
            for stage in region_data.stage_data:
                for idx, mission in enumerate(stage.missions):
                    loc_name = stage.get_named_mission_location(idx)
                    loc_id = stage.get_mission_loc_id(idx)
                    
                    world_region.add_locations({loc_name: loc_id}, BananaManiaLocation)
                    loc = world.get_location(loc_name)
                    world.set_rule(loc, mission.get_mission_item_req(world.options.logic_difficulty))
    

def create_events(world: BananaManiaWorld) -> None:
    menu = world.get_region("Menu")
    menu.add_event(
        "Goal", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem
    )