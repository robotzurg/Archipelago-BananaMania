from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from rule_builder.rules import AtLeast, CanReachRegion, Has, True_, HasAny, Rule
from math import ceil

from .locations import STAGE_GROUPS, Difficulty, Mission, MissionKind, StageData, LOCATION_NAME_TO_DATA
from .regions import WORLD_REGIONS

STARTING_TIME = 10          # Amount of time you start with
PROG_INCREASE_TIME = 10     # Amount of time each prog time increase gives
CHALLENGE_REGIONS = WORLD_REGIONS[10:18] # The regions related to challenges

if TYPE_CHECKING:
    from BaseClasses import CollectionState

    from .world import BananaManiaWorld

SMB2_WORLD_UNLOCK_NAMES = [
    "World 2: Volcanic Magma Unlock",          # World 2
    "World 3: Under the Ocean Unlock",         # World 3
    "World 4: Inside a Whale Unlock",          # World 4
    "World 5: Amusement Park Unlock",          # World 5
    "World 6: Boiling Pot Unlock",             # World 6
    "World 7: Bubbly Washing Machine Unlock",  # World 7
    "World 8: Clock Tower Factory Unlock",     # World 8
    "World 9: Space Colony Unlock",            # World 9
    "World 10: Dr. Bad-Boon's Base Unlock",    # World 10
]

SECONDS_FIELDS = ("seconds", "seconds_int", "seconds_exp")
ITEMS_FIELDS = ("items", "items_int", "items_exp")

def _owns(mission: Mission, fields: tuple[str, ...]) -> bool:
    """True if the mission set any difficulty level of this field itself."""
    return any(getattr(mission, name) is not None for name in fields)

def effective_mission(stage: StageData, mission_kind: MissionKind, mission: Mission) -> Mission:
    """
    Handles inheriting rules from the clear mission, so that we don't have to duplicate rules
    in other places. Returns a mission with added rules from the stage clear.
    """
    clear = stage.clear
    if mission_kind is not MissionKind.CLEAR:
        if not _owns(mission, SECONDS_FIELDS):
            mission = replace(mission, **{name: getattr(clear, name) for name in SECONDS_FIELDS})
        if not _owns(mission, ITEMS_FIELDS):
            mission = replace(mission, **{name: getattr(clear, name) for name in ITEMS_FIELDS})

    # The Standard value is the end of every difficulty chain, so it must be a real value
    if mission.seconds is None:
        mission = replace(mission, seconds=0)
    if mission.items is None:
        mission = replace(mission, items=())
    return mission

def resolve_items(source: Mission | StageData, difficulty: Difficulty = Difficulty.STANDARD) -> tuple[str | Rule, ...]:
    """The item requirement of one mission or stage on the given difficulty."""
    if difficulty is Difficulty.EXPERT and source.items_exp is not None:
        return source.items_exp
    if difficulty in (Difficulty.INTERMEDIATE, Difficulty.EXPERT) and source.items_int is not None:
        return source.items_int
    return source.items

def resolve_seconds(mission: Mission, mission_kind: MissionKind, difficulty: Difficulty = Difficulty.STANDARD) -> int:
    """The time a mission needs on the given difficulty, with the same Expert -> Intermediate fallback."""
    if difficulty is Difficulty.EXPERT and mission.seconds_exp is not None:
        seconds = mission.seconds_exp
    elif difficulty in (Difficulty.INTERMEDIATE, Difficulty.EXPERT) and mission.seconds_int is not None:
        seconds = mission.seconds_int
    else:
        seconds = mission.seconds

    if mission_kind is MissionKind.TIME_LIMIT:
        seconds = min(seconds, mission.amount)
    return seconds

def items_to_rule(requirement) -> Rule:
    rule: Rule = True_()
    for term in requirement:
        rule = rule & (term if isinstance(term, Rule) else Has(term))
    return rule

def get_mission_rule(
    stage: StageData, mission: Mission, mission_kind: MissionKind, difficulty: Difficulty = Difficulty.STANDARD
) -> Rule:
    """Returns a rule with everything the mission/stage needs."""
    rule: Rule = True_()
    mission = effective_mission(stage, mission_kind, mission)

    # Handle prog time increase item rules
    seconds = resolve_seconds(mission, mission_kind, difficulty)
    time_needed = max(0, ceil((seconds - STARTING_TIME) / PROG_INCREASE_TIME))
    if time_needed:
        rule = rule & Has("Progressive Time Increase", time_needed)

    rule = rule & items_to_rule(resolve_items(stage, difficulty)) & items_to_rule(resolve_items(mission, difficulty))
    return rule

def get_all_region_clear_rules(world: BananaManiaWorld, region: str, difficulty: Difficulty = Difficulty.STANDARD):
    """Returns a rule that includes all required mission rules for a region."""
    rule: Rule = True_()
    group = region
    if "World" in region:
        group = f"W{region.split(' ')[1]}"
    for stage in STAGE_GROUPS[group]:
        rule = rule & get_mission_rule(stage, stage.clear, MissionKind.CLEAR, difficulty)
    return rule & CanReachRegion(region)

def get_challenge_mode_clear_logic(world: BananaManiaWorld, region: str, selected_stage: StageData, difficulty: Difficulty = Difficulty.STANDARD):
    """Returns a rule that includes all required rules for a challenge mode level"""
    rule: Rule = True_()
    if not selected_stage.is_challenge():
        raise ValueError(f"{selected_stage.name} is not a challenge mode stage!")
    for stage in STAGE_GROUPS[region]:
        if stage.category:
            continue
        rule = rule & get_mission_rule(stage, stage.clear, MissionKind.CLEAR, difficulty)
        if stage is selected_stage:
            break
    return rule

def set_all_rules(world: BananaManiaWorld) -> None:
    set_all_entrance_rules(world)
    set_all_location_rules(world)
    set_completion_condition(world)

def set_all_entrance_rules(world: BananaManiaWorld) -> None:
    for world_num in range(2, 11):
        entrance = world.get_entrance(f"Menu to World {world_num}")
        if world.options.world_structure == 0:  # progression
            world.set_rule(entrance, Has("Progressive World Unlock", world_num - 1))
        else:  # individual
            unlock_name = SMB2_WORLD_UNLOCK_NAMES[world_num - 2]
            world.set_rule(entrance, Has(unlock_name))
    
    # We handle SMB2 world regions above, so skip those
    for region_idx in range(10, len(WORLD_REGIONS)):
        region = WORLD_REGIONS[region_idx]
        entrance = world.get_entrance(f"Menu to {region}")
        if "SMB1" in region or "SMB2" in region:
            world.set_rule(entrance, Has(f"{region} Challenge Mode Unlock"))
        elif region == "Deluxe Mode":
            world.set_rule(entrance, HasAny("Deluxe Mode Unlock", "Deluxe Beginner Stages Pack", "Deluxe Advanced Stages Pack", "Deluxe EX Stages Pack"))
        elif "Deluxe" in region: # Pack entrance logic
            world.set_rule(entrance, HasAny("Deluxe Mode Unlock", f"Deluxe {region.split(' ')[1]} Stages Pack"))
        else:
            world.set_rule(entrance, Has(f"{region} Unlock"))

def set_all_location_rules(world: BananaManiaWorld) -> None:
    difficulty = list(Difficulty)[world.options.logic_difficulty.value]
    for location in world.multiworld.get_locations(world.player):
        data = LOCATION_NAME_TO_DATA.get(location.name)
        if data is None:
            continue

        rule = get_mission_rule(data.stage, data.mission, data.kind, difficulty)
        region = location.parent_region.name

        if data.stage.is_challenge():
            rule = get_challenge_mode_clear_logic(world, region, data.stage, difficulty)
        elif data.stage.category and region in CHALLENGE_REGIONS: # You have to be able to reach the end to get these
            last = STAGE_GROUPS[region][-1]
            rule = (get_challenge_mode_clear_logic(world, region, last, difficulty)
                    & get_mission_rule(data.stage, data.mission, data.kind, difficulty))

        if data.stage.special and data.stage.category:
            # Deluxe Mode's stages live in the pack regions, everything else holds its own stages
            if region == "Deluxe Mode":
                groups = [(f"Deluxe {pack} Pack", f"SP DX {pack}") for pack in ("Beginner", "Advanced", "EX")]
            else:
                groups = [(region, f"SP {region.split(' ')[0]}")]

            special_stage_rules = []
            for stage_region, group in groups:
                for stage in STAGE_GROUPS[group]:
                    if stage.category:
                        continue
                    special_stage_rules.append(get_mission_rule(stage, stage.clear, MissionKind.CLEAR, difficulty) & CanReachRegion(stage_region))
            rule = AtLeast(data.mission.amount, *special_stage_rules) & get_mission_rule(data.stage, data.mission, data.kind, difficulty)

        world.set_rule(location, rule)

def setup_goal_rules(world: BananaManiaWorld) -> Rule:
    difficulty = list(Difficulty)[world.options.logic_difficulty.value]

    smb2_world_rules = []
    for smb2_world_region in WORLD_REGIONS[0:10]:
        smb2_world_rules.append(get_all_region_clear_rules(world, smb2_world_region, difficulty))

    challenge_mode_rules = []
    if world.options.goal_challenge_modes > 0:
        for challenge_region in WORLD_REGIONS[10:18]:
            challenge_mode_rules.append(get_all_region_clear_rules(world, challenge_region, difficulty))

    return AtLeast(world.options.goal_worlds.value, *smb2_world_rules) & AtLeast(world.options.goal_challenge_modes.value, *challenge_mode_rules)

def set_completion_condition(world: BananaManiaWorld) -> None:
    world.set_rule(world.get_location("Goal"), setup_goal_rules(world))
    world.set_completion_rule(Has("Victory"))
