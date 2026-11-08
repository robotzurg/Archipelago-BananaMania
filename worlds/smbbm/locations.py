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

def get_location_names_with_ids(location_names: list[str]) -> dict[str, int | None]:
    return {location_name: LOCATION_NAME_TO_ID[location_name] for location_name in location_names}


def create_all_locations(world: BananaManiaWorld) -> None:
    create_regular_locations(world)
    create_events(world) 

# This is janky right now just while I test my new data method
def create_regular_locations(world: BananaManiaWorld) -> None:
    region_idx = 0
    stage_idx = 0
    
    for region in WORLD_REGIONS:
        region_data = MISSION_DATA_DICT[region]
        world_region = world.get_region(region)
        region_idx += 10
        if len(region_data) != 0:
            world.set_rule("region", region_data.req_items)
            stage_idx = 0
            
            for stage in region_data.stage_data:
                stage_idx += 1
                
                for mission in stage.missions:
                    world_region.add_locations({mission.mission_name: region_idx + stage_idx + mission.mission_type.value})
                    world.set_rule(mission.get_mission_item_req(world.options.logic_difficulty))
    

def create_events(world: BananaManiaWorld) -> None:
    menu = world.get_region("Menu")
    menu.add_event(
        "Goal", "Victory", location_type=BananaManiaLocation, item_type=items.BananaManiaItem
    )