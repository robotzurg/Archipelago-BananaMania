from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from rule_builder.rules import AtLeast, CanReachRegion, Has, True_, HasAny, Rule
from math import ceil

"""
NOTICE: This is the other file that AI touched the most, albeit also a file I spent SO MUCH time on myself editing and tweaking and fixing.
I would highly recommend ensuring you are using rule_builder if you rewrite any of these rules, as it is an EXTREMELY useful resource
and provides built in support for /explain on Universal Tracker.
It's a bit difficult to describe exactly which parts of this were AI and which were me, because I wrote a lot of these and then had the AI
"point out" mistakes without writing them for me to fix. Parts of this are snippets it gave me.

If you want the optimal way to remove this, rewriting this file is probably optimal. It also will likely need to be rewritten anyways to
account for whatever the new datastructure is.

If I had to give an estimate, I would say this is 60% human written and 40% ai written, however the AI did look over and give a lot of
suggestions in this section that I hand wrote based on its advice, so mileage may vary. The biggest use case of AI was asking it
"Is this code good? Does it work?" and edited it based on advice it gives me.

Most of these comments are my own, a very select few aren't.
"""

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from .world import BananaManiaWorld

def set_all_rules(world: BananaManiaWorld) -> None:
    # set_all_entrance_rules(world)
    # set_all_location_rules(world)
    set_completion_condition(world)

# def set_all_entrance_rules(world: BananaManiaWorld) -> None:
#     for world_num in range(2, 11):
#         entrance = world.get_entrance(f"Menu to World {world_num}")
#         if world.options.world_structure == 0:  # progression
#             world.set_rule(entrance, Has("Progressive World Unlock", world_num - 1))
#         else:  # individual
#             unlock_name = SMB2_WORLD_UNLOCK_NAMES[world_num - 2]
#             world.set_rule(entrance, Has(unlock_name))
    
#     # We handle SMB2 world regions above, so skip those
#     for region_idx in range(10, len(WORLD_REGIONS)):
#         region = WORLD_REGIONS[region_idx]
#         entrance = world.get_entrance(f"Menu to {region}")
#         if "SMB1" in region or "SMB2" in region:
#             world.set_rule(entrance, Has(f"{region} Challenge Mode Unlock"))
#         elif region == "Deluxe Mode":
#             world.set_rule(entrance, HasAny("Deluxe Mode Unlock", "Deluxe Beginner Stages Pack", "Deluxe Advanced Stages Pack", "Deluxe EX Stages Pack"))
#         elif "Deluxe" in region: # Pack entrance logic
#             world.set_rule(entrance, HasAny("Deluxe Mode Unlock", f"Deluxe {region.split(' ')[1]} Stages Pack"))
#         else:
#             world.set_rule(entrance, Has(f"{region} Unlock"))

# def set_all_location_rules(world: BananaManiaWorld) -> None:
#     difficulty = list(Difficulty)[world.options.logic_difficulty.value]
#     for location in world.multiworld.get_locations(world.player):
#         data = LOCATION_NAME_TO_DATA.get(location.name)
#         if data is None:
#             continue

#         rule = get_mission_rule(data.stage, data.mission, data.kind, difficulty)
#         region = location.parent_region.name

#         if data.stage.is_challenge():
#             rule = get_challenge_mode_clear_logic(world, region, data.stage, difficulty)
#         elif data.stage.category and region in CHALLENGE_REGIONS: # You have to be able to reach the end to get these
#             last = STAGE_GROUPS[region][-1]
#             rule = (get_challenge_mode_clear_logic(world, region, last, difficulty)
#                     & get_mission_rule(data.stage, data.mission, data.kind, difficulty))

#         if data.stage.special and data.stage.category:
#             # Deluxe Mode's stages live in the pack regions, everything else holds its own stages
#             if region == "Deluxe Mode":
#                 groups = [(f"Deluxe {pack} Pack", f"SP DX {pack}") for pack in ("Beginner", "Advanced", "EX")]
#             else:
#                 groups = [(region, f"SP {region.split(' ')[0]}")]

#             special_stage_rules = []
#             for stage_region, group in groups:
#                 for stage in STAGE_GROUPS[group]:
#                     if stage.category:
#                         continue
#                     special_stage_rules.append(get_mission_rule(stage, stage.clear, MissionKind.CLEAR, difficulty) & CanReachRegion(stage_region))
#             rule = AtLeast(data.mission.amount, *special_stage_rules) & get_mission_rule(data.stage, data.mission, data.kind, difficulty)

#         world.set_rule(location, rule)

# NOTICE: Make sure you keep this intact if you rewrite this file. This part is important for ensuring the APWorld knows when to goal.
def set_completion_condition(world: BananaManiaWorld) -> None:
    # world.set_rule(world.get_location("Goal"), setup_goal_rules(world))
    world.set_completion_rule(True_())
