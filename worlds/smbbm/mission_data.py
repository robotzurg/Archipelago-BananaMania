from numpy import diff

from rule_builder.rules import CanReachLocation, Has, True_, Rule, HasAll, HasAny, OptionFilter, AtLeast, And, Or
from .options import WorldStructure, DeluxeUnlockStyle
from math import ceil
from enum import IntEnum

class Difficulty(IntEnum):
    STANDARD = 0,
    INTERMEDIATE = 1,
    EXPERT = 2,

class MissionType(IntEnum):
    CLEAR = 1,
    BANANA = 2
    TIME = 3,
    GREEN = 4,
    RED = 5,
    NONSTOP = 6,
    CHALLENGE_CLEAR = 7,
    CHALLENGE_CLEAR_EXTRA = 8,
    TURNING_POINT = 9,
    STAGE_COMPLETE = 10,

class MissionData():
    def __init__(self, mission_type: MissionType, req_items: list[Rule], amount: int | str | None = None, add_clear_reqs: bool = False, category_mission: bool = False, challenge_category_mission: bool = False):
        self.mission_type = mission_type
        self.req_items = self.fill_in_req_items(req_items)
        self.amount = amount
        self.mission_name: str = self.get_mission_name()
        self.add_clear_reqs = add_clear_reqs
        if self.mission_type == MissionType.NONSTOP or self.mission_type == MissionType.TIME:
            self.add_clear_reqs = True
        
        # Has unique item rules assigned later
        self.category_mission = category_mission
        self.challenge_category_mission = challenge_category_mission

    def add_req_items_rules(self, req_items: list[Rule]):
        for idx, rule in enumerate(req_items):
            self.req_items[idx] = rule & self.req_items[idx] 
    
    def fill_in_req_items(self, req_items):
        if len(req_items) == 0:
            req_items = [True_(), True_(), True_()]
        elif len(req_items) == 1:
            req_items.append(req_items[0])
            req_items.append(req_items[0])
        elif len(req_items) == 2:
            req_items.append(req_items[1])
        else:
            req_items = req_items
        
        return req_items
    
    def get_mission_name(self):
        name = "N/A"
        match self.mission_type:
            case MissionType.CLEAR: 
                name = "Stage Clear"
            case MissionType.BANANA: 
                name = f"Banana Collector {self.amount}"
            case MissionType.TIME:
                name = f"Time Limit {self.amount}"
            case MissionType.GREEN:
                name = "Green Goal"
            case MissionType.RED:
                name = "Red Goal"
            case MissionType.NONSTOP:
                name = "Nonstop"
            case MissionType.CHALLENGE_CLEAR:
                name = "Course Clear"
            case MissionType.CHALLENGE_CLEAR_EXTRA:
                name = f"Challenge {self.amount}"
            case MissionType.TURNING_POINT:
                name = f"Turning Point {self.amount}"
            case MissionType.STAGE_COMPLETE:
                name = f"Stage Complete {self.amount}"
        
        return name
    
    def get_mission_item_req(self, difficulty: Difficulty) -> Rule:
        return self.req_items[difficulty.value]

class StageData:
    def __init__(self, base_id: int, name: str, region: str, missions: list[MissionData]):
        self.base_id = base_id
        self.name = name
        self.region = region
        self.missions = missions

        self.clear_mission = self.missions[0] if self.missions[0].mission_type == MissionType.CLEAR else None

        # Add the rules from the clear mission to other sub missions
        for mission in self.missions:
            if mission == self.clear_mission:
                continue
            elif mission.add_clear_reqs and self.clear_mission is not None:
                mission.add_req_items_rules(self.clear_mission.req_items)
        
    def get_mission_loc_id(self, mission_idx):
        return self.base_id + self.missions[mission_idx].mission_type.value
        
    def get_named_mission_location(self, mission_idx):
        return f"[{self.region}] {self.name} - {self.missions[mission_idx].mission_name}"
        
    def get_mission_location_list(self):
        mission_list = []
        for idx, mission in enumerate(self.missions):
            mission_list.append((f"[{self.region}] {self.name} - {mission.mission_name}", self.get_mission_loc_id(idx)))
        
        return mission_list
        
class RegionData:
    def __init__(self, name: str, req_items: Rule, stage_data: list[StageData], challenge_region: bool = False):
        self.name = name
        self.req_items = req_items
        self.stage_data = stage_data
        self.challenge_region = challenge_region
        
    def __len__(self):
        return len(self.stage_data)
    
    def get_region_locations(self) -> list[tuple[str, int]]:
        loc_list = []
        for stage in self.stage_data:
            mission_loc_list = stage.get_mission_location_list()
            loc_list.extend(mission_loc_list)
            
        return loc_list
    
    def get_full_stage_clear_rule(self, difficulty: Difficulty) -> Rule:
        stage_rules = []
        for stage in self.stage_data:
            if stage.missions[0].mission_type != MissionType.CLEAR:
                continue
            stage_rules.append((stage.missions[0].get_mission_item_req(difficulty)))
            
        return And(*stage_rules)

class CategoryData:
    def __init__(self, base_id: int, name: str, req_items: Rule, stage_data: list[StageData], missions: list[MissionData], challenge: bool = False):
        self.base_id = base_id
        self.name = name
        self.req_items = req_items
        self.stage_data = stage_data
        self.missions = missions
        self.challenge = challenge
        
    def __len__(self):
            return len(self.stage_data)
        
    def get_region_locations(self) -> list[tuple[str, int]]:
        loc_list = []
        for idx, _ in enumerate(self.missions):
            loc_list.append((self.get_named_mission_location(idx), self.get_mission_loc_id(idx)))
            
        return loc_list
        
    def get_mission_loc_id(self, mission_idx):
            return self.base_id + self.missions[mission_idx].mission_type.value
            
    def get_named_mission_location(self, mission_idx):
        return f"[{self.name}] {self.missions[mission_idx].mission_name}"
        
    def get_stage_win_rule(self, amount: int, difficulty: Difficulty) -> Rule:
        stage_rules = []
        for stage in self.stage_data:
            if stage.missions[0].mission_type != MissionType.CLEAR:
                continue
            stage_rules.append((stage.missions[0].get_mission_item_req(difficulty)))
            
        return AtLeast(amount, *stage_rules)
    
# Returns a rule with the amount of time a level needs, to prevent a lot of annoying copypasting lol
def time(amount: int) -> Rule:
    return Has("Progressive Time Increase", count=amount)

def get_region_rule(region: str) -> Rule:
    match region:
        case "World 2":
            return (
                Has("World 2: Volcanic Magma", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)]) 
                | Has("Progressive World Unlock", count=1, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 3":
            return (
                Has("World 3: Under the Ocean", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=2, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 4":
            return (
                Has("World 4: Inside a Whale", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=3, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 5":
            return (
                Has("World 5: Amusement Park", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=4, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 6":
            return (
                Has("World 6: Boiling Pot", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=5, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 7":
            return (
                Has("World 7: Bubbly Washing Machine", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=6, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 8":
            return (
                Has("World 8: Clock Tower Factory", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=7, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 9":
            return (
                Has("World 9: Space Colony", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=8, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case "World 10":
            return (
                Has("World 10: Dr. Bad-Boon's Base", options=[OptionFilter(WorldStructure, WorldStructure.option_worlds)])
                | Has("Progressive World Unlock", count=9, options=[OptionFilter(WorldStructure, WorldStructure.option_progression)])
            )
        case 'Deluxe Beginner Pack':
            return (
                Has("Deluxe Mode", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_all)])
                | Has("Deluxe Beginner Stages Pack", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_packs)])
            )
        case 'Deluxe Advanced Pack':
            return (
                Has("Deluxe Mode", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_all)])
                | Has("Deluxe Advanced Stages Pack", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_packs)])
            )
        case 'Deluxe EX Pack':
            return (
                Has("Deluxe Mode", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_all)])
                | Has("Deluxe EX Stages Pack", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_packs)])
            )

MISSION_DATA_DICT: dict[str, RegionData] = {
    "World 1": 
        RegionData(name="World 1", req_items=True_(), stage_data=[
            StageData(
                10, "Simple", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                20, "Hollow", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(1), time(0)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                30, "Bumpy", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(3), time(2)], 30),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                40, "Switches", "World 1",
                [
                    MissionData(MissionType.CLEAR, [Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(1)], 25, add_clear_reqs=True),
                    MissionData(MissionType.TIME, [], 10, add_clear_reqs=True),
                    MissionData(MissionType.GREEN, [time(1)], add_clear_reqs=True)
                ]
            ),
            StageData(
                50, "Conveyors", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 30),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                60, "Floaters", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(3), time(2)], 50),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                70, "Tub", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 77),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                80, "Windy Slide", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(3), time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 70),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                90, "Spinning Top", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                100, "Curve Bridge", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(3)]),
                    MissionData(MissionType.BANANA, [time(3)], 60),
                    MissionData(MissionType.TIME, [], 35)
                ]
            ),
        ]
    ),
    "World 2": 
        RegionData(name="World 2", req_items=get_region_rule("World 2"), stage_data=[
            StageData(
                110, "Banks", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 25),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                120, "Eaten Floor", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(5)], 20),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                130, "Hoppers", "World 2",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], "Complete"),
                    MissionData(MissionType.TIME, [], 5)
                ]
            ),
            StageData(
                140, "Coaster", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 55),
                    MissionData(MissionType.TIME, [], 30),
                ]
            ),
            StageData(
                150, "Bumpy Check", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 15),
                ]
            ),
            StageData(
                160, "Swell", "World 2",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 25),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                170, "Gravity Slider", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 70),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                180, "Inchworms", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 30),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1) & Has("Normal Switches")]),
                    MissionData(MissionType.RED, [time(1) & Has("Normal Switches")]),
                ]
            ),
            StageData(
                190, "Totalitarianism", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.NONSTOP, []),
                ]
            ),
            StageData(
                200, "Alternative", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1) & Has("Fast Switches")]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
        ]
    ),
    "World 3": 
        RegionData(name="World 3", req_items=get_region_rule("World 3"), stage_data=[
            StageData(
                210, "Organic Form", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(5)], "Complete"),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                220, "Reversible Gear", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 30),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                230, "Stepping Stones", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 70),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                240, "Dribbles", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3)]),
                    MissionData(MissionType.BANANA, [time(5)], "Complete"),
                    MissionData(MissionType.TIME, [], 40),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                250, "Push Bar", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(4)], "Complete"),
                    MissionData(MissionType.TIME, [], 15),
                ]
            ),
            StageData(
                260, "Mad Rings", "World 3",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 30),
                    MissionData(MissionType.TIME, [], 5),
                    MissionData(MissionType.GREEN, []),
                    MissionData(MissionType.RED, [time(1)])
                ]
            ),
            StageData(
                270, "Curvy Options", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 40),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                280, "Twist & Spin", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(1)], 15),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                290, "Cascade", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                300, "Junction", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(1)], 38),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
        ]
    ),
    "World 4": 
        RegionData(name="World 4", req_items=get_region_rule("World 4"), stage_data=[
            StageData(
                310, "Pro Skaters", "World 4",
                [
                    MissionData(MissionType.CLEAR, [Has("Pause Switches"), True_()]),
                    MissionData(MissionType.BANANA, [time(2) & Has("Pause Switches")], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [])
                ]
            ),
            StageData(
                320, "Giant Comb", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                330, "Beehive", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(5)], 25),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                340, "Dynamic Maze", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4)], 30),
                    MissionData(MissionType.TIME, [], 20),
                ]
            ),
            StageData(
                350, "Triangle Holes", "World 4",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 30),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                360, "Launchers", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(4)], 10),
                    MissionData(MissionType.TIME, [], 20),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
            StageData(
                370, "Randomizer", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(1)], 35),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1)]),
                    MissionData(MissionType.RED, [time(1)])
                ]
            ),
            StageData(
                380, "Coin Slots", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], "Complete"),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
            StageData(
                390, "Seesaw Bridges", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3), time(2)]),
                    MissionData(MissionType.BANANA, [time(4)], 40),
                    MissionData(MissionType.TIME, [], 55)
                ]
            ),
            StageData(
                400, "Arthropod", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4)], "Complete"),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
        ]
    ),
    "World 5": 
        RegionData(name="World 5", req_items=get_region_rule("World 5"), stage_data=[
            StageData(
                410, "Wormhole", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(2) & Has("Wormholes"), time(1) & Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(3) & Has("Wormholes"), time(2) & Has("Wormholes")], 50),
                    MissionData(MissionType.TIME, [], 25),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                420, "Free Fall", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4), time(3)], 50),
                    MissionData(MissionType.TIME, [], 20),
                    MissionData(MissionType.GREEN, [time(2), time(2), time(1)])
                ]
            ),
            StageData(
                430, "Melting Pot", "World 5",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                440, "Mad Shuffle", "World 5",
                [
                    MissionData(MissionType.CLEAR, [Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(4) & Has("Normal Switches") & Has("Wormholes")], "Complete"),
                    MissionData(MissionType.TIME, [], 10),
                ]
            ),
            StageData(
                450, "Bead Screen", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Pause Switches"), True_()]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Pause Switches")], 20),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                460, "Jump Machine", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(2)]),
                    MissionData(MissionType.RED, [time(3)])
                ]
            ),
            StageData(
                470, "Zigzag Slope", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 25),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                480, "Tower", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Wormholes")], 25),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                490, "Toggle", "World 5",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], "Complete"),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                500, "Fluctuation", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3), time(2)], 20),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
        ]
    ),
    "World 6": 
        RegionData(name="World 6", req_items=get_region_rule("World 6"), stage_data=[
            StageData(
                510, "Combination", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(2) & HasAll("Wormholes", "Normal Switches"), Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(4) & HasAll("Wormholes", "Normal Switches")], 25),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                520, "Punched Seesaws", "World 6",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 21),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(2)])
                ]
            ),
            StageData(
                530, "Opera", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3), time(2)]),
                    MissionData(MissionType.BANANA, [time(5)], 70),
                    MissionData(MissionType.TIME, [], 35)
                ]
            ),
            StageData(
                540, "Brandished", "World 6",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 35),
                    MissionData(MissionType.TIME, [], 5),
                ]
            ),
            StageData(
                550, "Tiers", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(3) & Has("Wormholes")], 20),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.GREEN, [time(2) & Has("Wormholes")]),
                    MissionData(MissionType.RED, [time(1) & Has("Wormholes")])
                ]
            ),
            StageData(
                560, "Cliffs", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                570, "Narrow Peaks", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                580, "Detours", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes"), Has("Wormholes"), True_()]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Wormholes")], 20),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1) & Has("Wormholes"), time(1) & Has("Wormholes"), True_()])
                ]
            ),
            StageData(
                590, "Switch Inferno", "World 6",
                [
                    MissionData(MissionType.CLEAR, [Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [Has("Normal Switches")], 9),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                600, "Folders", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 10),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
        ]
    ),
    "World 7": 
        RegionData(name="World 7", req_items=get_region_rule("World 7"), stage_data=[
            StageData(
                610, "Spiral Bridge", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 20),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                620, "Wavy Option", "World 7",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1), time(1), True_()], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                630, "Obstacle", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                640, "Domino", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Normal Switches"), Has("Normal Switches"), True_()]),
                    MissionData(MissionType.BANANA, [time(2) & Has("Normal Switches")], 20),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                650, "Sieve", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                660, "Flock", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(5)], 15),
                    MissionData(MissionType.TIME, [], 50)
                ]
            ),
            StageData(
                670, "Double Spiral", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 25)
                ]
            ),
            StageData(
                680, "Hierarchy", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 25)
                ]
            ),
            StageData(
                690, "8 Bracelets", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 25),
                    MissionData(MissionType.GREEN, [time(2)]),
                    MissionData(MissionType.RED, [time(2)])
                ]
            ),
            StageData(
                700, "Quick Turn", "World 7",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], "Complete"),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
        ]
    ),
    "World 8": 
        RegionData(name="World 8", req_items=get_region_rule("World 8"), stage_data=[
            StageData(
                710, "Pistons", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2), time(1)], 20),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                720, "Soft Cream", "World 8",
                [
                    MissionData(MissionType.CLEAR, [
                        time(1) & Has("Normal Switches"),
                        (time(1) & Has("Normal Switches")) | Has("Fast Switches"),
                        HasAny("Normal Switches", "Fast Switches") | (Has("Pause Switches") & time(1))
                    ]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Normal Switches")], 20),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                730, "Momentum", "World 8",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 21),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                740, "Entangled Path", "World 8",
                [
                    MissionData(MissionType.CLEAR, [
                        (time(4) & HasAll("Fast Switches", "Normal Switches")) | time(5),
                        (time(3) & HasAll("Fast Switches", "Normal Switches")) | time(5),
                        time(2)
                    ]),
                    MissionData(MissionType.BANANA, [time(4) & HasAll("Normal Switches", "Fast Switches")], 30),
                    MissionData(MissionType.TIME, [], 40),
                    MissionData(MissionType.GREEN, [time(3) & HasAll("Normal Switches", "Fast Switches")])
                ]
            ),
            StageData(
                750, "Totters", "World 8",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 28),
                    MissionData(MissionType.TIME, [], 10),
                ]
            ),
            StageData(
                760, "Vortex", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 10),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.GREEN, [time(2)])
                ]
            ),
            StageData(
                770, "Warp", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(4)], 40),
                    MissionData(MissionType.TIME, [], 40),
                    MissionData(MissionType.GREEN, [time(3)])
                ]
            ),
            StageData(
                780, "Trampolines", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 40),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                790, "Swing Shaft", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                800, "Linear Seesaws", "World 8",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 10),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
        ]
    ),
    "World 9": 
        RegionData(name="World 9", req_items=get_region_rule("World 9"), stage_data=[
            StageData(
                810, "Serial Jump", "World 9",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 10),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1)]),
                    MissionData(MissionType.RED, [])
                ]
            ),
            StageData(
                820, "Cross Floors", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 20),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                830, "Spinning Saw", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(2), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(2), time(1)], 20),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                840, "Chipped Pipes", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(1)], 20),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
            StageData(
                850, "Flat Maze", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(5), time(3), time(2)]),
                    MissionData(MissionType.BANANA, [time(5)], 20),
                    MissionData(MissionType.TIME, [], 40),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                860, "Guillotine", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                870, "Cork Screw", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 12),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                880, "Orbiters", "World 9",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 15),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                890, "Twin Basin", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 14),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                900, "Air Hockey", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 40),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
        ]
    ),
    "World 10": 
        RegionData(name="World 10", req_items=get_region_rule("World 10"), stage_data=[
            StageData(
                910, "Training", "World 10",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(3)], 40),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                920, "Gimmick", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(5) & Has("Normal Switches"), time(4) & Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(5) & Has("Normal Switches")], 25),
                    MissionData(MissionType.TIME, [], 55)
                ]
            ),
            StageData(
                930, "Mountain", "World 10",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                940, "Disorder", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 25),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                950, "3D Maze", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                960, "Crazy Maze", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(5), time(4)]),
                    MissionData(MissionType.BANANA, [time(5)], 20),
                    MissionData(MissionType.TIME, [], 59)
                ]
            ),
            StageData(
                970, "Post Modern", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3)]),
                    MissionData(MissionType.BANANA, [time(4)], 10),
                    MissionData(MissionType.TIME, [], 45)
                ]
            ),
            StageData(
                980, "Revolution", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 10),
                    MissionData(MissionType.TIME, [], 20)
                ]
            ),
            StageData(
                990, "Invisible", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(5) & Has("Normal Switches"), time(4) & Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(5) & Has("Normal Switches")], 29),
                    MissionData(MissionType.TIME, [], 50)
                ]
            ),
            StageData(
                1000, "Last Stage", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(2) & Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(2) & Has("Normal Switches")], 25),
                    MissionData(MissionType.TIME, [], 25)
                ]
            ),
        ],
    ),
    "Deluxe Beginner Pack": 
        RegionData(name="Deluxe Beginner Pack", req_items=get_region_rule("Deluxe Beginner Pack"), stage_data=[
            StageData(
                2010, "Edge", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                2020, "Escalators", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                2030, "Serpentine", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                2040, "Swirl", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                2050, "Dormant Pits", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                2060, "Composition", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                2070, "Dynamo", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                2080, "Lunchbox", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_(), True_()])]
            ),
            StageData(
                2090, "Gutter", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                2100, "Scabrous", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                2110, "Jolt Channel", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                2120, "Inertial", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                2130, "Octagonal", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                2140, "Sewer", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                2150, "Arc Bridges", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                2160, "Veer Field", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(4), time(2), time(1)])]
            ),
            StageData(
                2170, "Teeter", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                2180, "Stream", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                2190, "Catwalk", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(3), True_()])]
            ),
            StageData(
                2200, "Catapult", "Deluxe Beginner Pack",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),  
        ],
    ),
    "Deluxe Advanced Pack": 
        RegionData(name="Deluxe Advanced Pack", req_items=get_region_rule("Deluxe Advanced Pack"), stage_data=[
            StageData(
                3010, "Jump Ramp", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                3020, "Hounds Tooth", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                3030, "D.N.A.", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                3040, "Building", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                3050, "Scrolls", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                3060, "Cliff", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(5), time(4), True_()])]
            ),
            StageData(
                3070, "Concentric", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                3080, "Stadium", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                3090, "Dungeon", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [time(4), time(2), time(1)])]
            ),
            StageData(
                3100, "Paraboloid", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                3110, "Spatiotemporal", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                3120, "Shelter", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                3130, "Mobius", "Deluxe Advanced Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ],
    ),
    "Deluxe EX Pack": 
        RegionData(name="Deluxe EX Pack", req_items=get_region_rule("Deluxe EX Pack"), stage_data=[
            StageData(
                4010, "Rhombus", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                4020, "Buoy", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                4030, "Coil Ramp", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(4), time(1), True_()])]
            ),
            StageData(
                4040, "Millefeuille", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                4050, "Waver", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(3), time(3), time(2)])]
            ),
            StageData(
                4060, "Fat Seesaw", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                4070, "Treads", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(4), time(2), time(1)])]
            ),
            StageData(
                4080, "Chaos", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                4090, "Tilt Maze", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(5), True_()])]
            ),
            StageData(
                4100, "Fractal", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                4110, "Hills", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                4120, "Dodge Maze", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [time(5), time(4)])]
            ),
            StageData(
                4130, "Asterisk", "Deluxe EX Pack",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ],
    ),
    "Reverse Mode": 
        RegionData(name="Reverse Mode", req_items=Has("Reverse Mode"), stage_data=[
            StageData(
                5010, "Branch", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                5020, "Waver", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                5030, "Free Throw", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                5040, "Rings", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                5050, "Amida Lot", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                5060, "Carpet", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                5070, "Clover", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                5080, "Punched Seesaw", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                5090, "Checker", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                5100, "Polar Large", "Reverse Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ]
    ),
    "Dark Banana Mode": 
        RegionData(name="Dark Banana Mode", req_items=Has("Dark Banana Mode"), stage_data=[
            StageData(
                6010, "Cross Floors", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                6020, "Ant Lion", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                6030, "Earthquake", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                6040, "Destruction", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                6050, "Narrow Peaks", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                6060, "Centrifugal", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                6070, "Breathe", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                6080, "Twin Basin", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                6090, "Swing Bar Long", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                6100, "Sega Logo", "Dark Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
        ]
    ),
    "Golden Banana Mode": 
        RegionData(name="Golden Banana Mode", req_items=Has("Golden Banana Mode"), stage_data=[
            StageData(
                7010, "Branch", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                7020, "Waver", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7030, "Free Throw", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                7040, "Rings", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7050, "Amida Lot", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7060, "Carpet", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7070, "Clover", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7080, "Punched Seesaw", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7090, "Checker", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                7100, "Polar Large", "Golden Banana Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
        ]
    ),
    "Original Stages Mode": 
        RegionData(name="Original Stages Mode", req_items=Has("Original Stages Mode"), stage_data=[
            StageData(
                8010, "Catwalk", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                8020, "Polar", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                8030, "Launchers", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8040, "Arthropod", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8050, "Polar Large", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                8060, "Chaos", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                8070, "Exam-C", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                8080, "Tracks", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                8090, "Twin Attacker", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                8100, "8 Bracelets", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                8110, "Curvature", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(4)])]
            ),
            StageData(
                8120, "Soft Cream", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Fast Switches")])]
            ),
            StageData(
                8130, "Air Hockey", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                8140, "Cylinders", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8150, "Notch", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8160, "Long Torus", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                8170, "Clock Face", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                8180, "Wave Master", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                8190, "Stamina Master", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8200, "Dance Master", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                8210, "Dodge Master", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                8220, "Bridge Master", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                8230, "Synchronized", "Original Stages Mode",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ]
    ),
    "SMB1 Casual": 
        RegionData(name="SMB1 Casual", req_items=Has("SMB1 Casual Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                9010, "Plain", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9020, "Diamond", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9030, "Hairpin", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9040, "Wide Bridge", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9050, "Bonus Basic (Casual)", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9060, "Slopes", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9070, "Steps", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                9080, "Blocks", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                9090, "Jump Single", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9100, "Exam-A", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                9110, "Blur Bridge (Casual)", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9120, "Hitter", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                9130, "Banana Plate (Casual)", "SMB1 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ]
    ),
    "SMB1 Normal": 
        RegionData(name="SMB1 Normal", req_items=Has("SMB1 Normal Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                10010, "Bump", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10020, "Walking", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10030, "Repulse", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10040, "Narrow Bridge", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10050, "Bonus Basic (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10060, "Break", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10070, "Curves", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                10080, "Downhill", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                10090, "Blocks Slim", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                10100, "Bonus Wave (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                10110, "Choice", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                10120, "Bowl", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10130, "Jumpies", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10140, "Stoppers", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10150, "Floor Bent", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                10160, "Conveyers", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10170, "Exam-B", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10180, "Chaser", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10190, "Jump Double", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10200, "Bonus Grid (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10210, "Middle Jam", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                10220, "Ant Lion", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10230, "Collapse", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10240, "Swing Bar", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10250, "Labyrinth", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                10260, "Spiral", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                10270, "Wavy Jump", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10280, "Spiky", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                10290, "Unrest", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10300, "Polar", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10310, "Blur Bridge (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10320, "Hard Hitter (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10330, "Puzzle", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(3), time(1), True_()])]
            ),
            StageData(
                10340, "Banana Plate (Normal)", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                10350, "Polar Large", "SMB1 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
        ]
    ),
    "SMB1 Expert": 
        RegionData(name="SMB1 Expert", req_items=Has("SMB1 Expert Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                11010, "Ruin", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11020, "Branch", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11030, "Overturn", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11040, "Excursion", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(4), True_()])]
            ),
            StageData(
                11050, "Bonus Basic (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11060, "Dodecagon", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                11070, "Exam-C", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(5), time(4), time(3)])]
            ),
            StageData(
                11080, "Skeleton", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11090, "Tracks", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                11100, "Bonus Wave (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11110, "Downhill Hard", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                11120, "Gears", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(3), time(2), time(1)])]
            ),
            StageData(
                11130, "Destruction", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                11140, "Invasion", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(3), time(2), time(1)])]
            ),
            StageData(
                11150, "Diving", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11160, "Floor Slant", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11170, "Tram", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11180, "Swing Bar Long", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11190, "Paper Work", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11200, "Bonus Grid (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11210, "Twin Attacker", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11220, "Sega Logo", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                11230, "Snake", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11240, "Wind", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(4), time(3)])]
            ),
            StageData(
                11250, "Sliders", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                11260, "Fall Down", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11270, "Twin Cross", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                11280, "Spiral Hard", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(3), True_()])]
            ),
            StageData(
                11290, "Conveyor Hard", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11300, "Bonus Bumpy", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11310, "Gaps", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11320, "Curvature", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(4), time(3), time(2)])]
            ),
            StageData(
                11330, "Ant Lion Super", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11340, "Drum", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11350, "Twister", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11360, "Speedy Jam", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                11370, "Quake", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11380, "Cassiopeia", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11390, "Pirates", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11400, "Bonus Hunting", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11410, "Bowl Open", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11420, "Checker", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11430, "Carpet", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                11440, "Ridge", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                11450, "Mixer", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                11460, "Rings", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11470, "Stairs", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11480, "Clover", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                11490, "Coffee Cup", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11500, "Metamorphosis", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11510, "Blur Bridge (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11520, "Breathe", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11530, "Hard Hitter (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11540, "Ferris Wheel", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11550, "Factory", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11560, "Curl Pipe", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11570, "Magic Hand", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                11580, "Banana Plate (Expert)", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                11590, "Sanctuary", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                11600, "Daa Loo Maa", "SMB1 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
        ]
    ),
    "SMB1 Master": 
        RegionData(name="SMB1 Master", req_items=Has("SMB1 Master Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                12010, "Wave Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(2), time(2), time(1)])]
            ),
            StageData(
                12020, "Fan Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                12030, "Stamina Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(3), time(1)])]
            ),
            StageData(
                12040, "Spring Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(4), time(4), time(1)])]
            ),
            StageData(
                12050, "Dance Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                12060, "Roll Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                12070, "Edge Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                12080, "Dodge Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                12090, "Bridge Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                12100, "Monkey Master", "SMB1 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
        ]
    ),
    "SMB2 Casual": 
        RegionData(name="SMB2 Casual", req_items=Has("SMB2 Casual Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                13010, "Simple", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13020, "Hollow", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                13030, "Bumpy", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13040, "Switches", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13050, "Rising Inclines", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13060, "Floaters", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13070, "Tub", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                13080, "Windy Slide", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(3), time(2), time(1)])]
            ),
            StageData(
                13090, "Spinning Top", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                13100, "Curve Bridge", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                13110, "Conveyers", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13120, "Bumpy Check", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                13130, "Alternative", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(2), Or(time(1) & Has("Fast Switches"), time(2))])]
            ),
            StageData(
                13140, "Junction", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                13150, "Bead Screen", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Pause Switches"), True_()])]
            ),
            StageData(
                13160, "Fluctuation", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                13170, "Folders", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                13180, "Quick Turn", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [Has("Fast Switches")])]
            ),
            StageData(
                13190, "Linear Seesaws", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                13200, "Birth", "SMB2 Casual",
                [MissionData(MissionType.CLEAR, [time(2) & Has("Pause Switches")])]
            ),
        ]
    ),
    "SMB2 Normal": 
        RegionData(name="SMB2 Normal", req_items=Has("SMB2 Normal Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                14010, "Banks", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                14020, "Eaten Floor", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14030, "Hoppers", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14040, "Coaster", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(2), time(1)])]
            ),
            StageData(
                14050, "Board Park", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14060, "Swell", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14070, "Gravity Slider", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                14080, "Inchworms", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14090, "Totalitarianism", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14100, "Leveler", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14110, "Organic Form", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                14120, "Reversible Gear", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                14130, "Stepping Stones", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                14140, "Dribbles", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(4), time(3)])]
            ),
            StageData(
                14150, "Push Bar", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                14160, "Mad Rings", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14170, "Curvy Options", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                14180, "Twist & Spin", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14190, "Cascade", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                14200, "Rampage", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14210, "Pro Skaters", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [Has("Pause Switches"), True_()])]
            ),
            StageData(
                14220, "Giant Comb", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                14230, "Beehive", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                14240, "Dynamic Maze", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14250, "Triangle Holes", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14260, "Launchers", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                14270, "Randomizer", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14280, "Coin Slots", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                14290, "Seesaw Bridges", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(4), time(3), time(2)])]
            ),
            StageData(
                14300, "Arthropod", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                14310, "Auto Doors", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                14320, "Heavy Sphere", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [Has("Normal Switches")])]
            ),
            StageData(
                14330, "Stagger", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                14340, "U.F.O.", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Normal Switches")])]
            ),
            StageData(
                14350, "Ring Bridges", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                14360, "Domes", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                14370, "Amida Lot", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                14380, "Long Slider", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(3), time(3), True_()])]
            ),
            StageData(
                14390, "Grid Bridge", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                14400, "Teapot", "SMB2 Normal",
                [MissionData(MissionType.CLEAR, [Has("Normal Switches")])]
            ),
        ]
    ),
    "SMB2 Expert": 
        RegionData(name="SMB2 Expert", req_items=Has("SMB2 Expert Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                15010, "Wormhole", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2) & Has("Wormholes"), time(1) & Has("Wormholes")])]
            ),
            StageData(
                15020, "Free Fall", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), time(1), True_()])]
            ),
            StageData(
                15030, "Melting Pot", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15040, "Mad Shuffle", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [Has("Wormholes")])]
            ),
            StageData(
                15050, "Partition", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15060, "Jump Machine", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15070, "Zigzag Slope", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15080, "Tower", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")])]
            ),
            StageData(
                15090, "Toggle", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15100, "Combination", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2) & HasAll("Wormholes", "Normal Switches"), Has("Wormholes")])]
            ),
            StageData(
                15110, "Punched Seesaws", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15120, "Opera", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(4), time(3), time(2)])]
            ),
            StageData(
                15130, "Brandished", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15140, "Tiers", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")])]
            ),
            StageData(
                15150, "Cliffs", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                15160, "Narrow Peaks", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                15170, "Detours", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes"), Has("Wormholes")])]
            ),
            StageData(
                15180, "Switch Inferno", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [Has("Normal Switches")])]
            ),
            StageData(
                15190, "Spiral Bridge", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15200, "Wavy Option", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15210, "Obstacle", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15220, "Domino", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Normal Switches"), Has("Normal Switches"), True_()])]
            ),
            StageData(
                15230, "Sieve", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                15240, "Flock", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(4), time(1), True_()])]
            ),
            StageData(
                15250, "Double Spiral", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15260, "Hierarchy", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                15270, "8 Bracelets", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                15280, "Pistons", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                15290, "Soft Cream", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Normal Switches"), Or(time(1) & Has("Normal Switches"), Has("Fast Switches")), HasAny("Normal Switches", "Fast Switches")])]
            ),
            StageData(
                15300, "Momentum", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15310, "Entangled Path", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [Or(time(4) & HasAll("Fast Switches", "Normal Switches"), time(5)), time(3) & HasAll("Fast Switches", "Normal Switches"), time(2)])]
            ),
            StageData(
                15320, "Totters", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15330, "Vortex", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                15340, "Warp", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                15350, "Trampolines", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                15360, "Swing Shaft", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(1)])]
            ),
            StageData(
                15370, "Fighters", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15380, "Serial Jump", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15390, "Cross Floors", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15400, "Spinning Saw", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
            StageData(
                15410, "Chipped Pipes", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                15420, "Flat Maze", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(5), time(3), time(2)])]
            ),
            StageData(
                15430, "Guillotine", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), time(2), time(1)])]
            ),
            StageData(
                15440, "Cork Screw", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15450, "Orbiters", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15460, "Twin Basin", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                15470, "Air Hockey", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                15480, "Charge", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")])]
            ),
            StageData(
                15490, "Strata", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                15500, "Square Dance", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15510, "Giant Swing", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                15520, "5 Drums", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                15530, "Free Throw", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                15540, "Pendulums", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(3), time(3), True_()])]
            ),
            StageData(
                15550, "Conical Slider", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(3) & Has("Wormholes")])]
            ),
            StageData(
                15560, "Construction", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
            StageData(
                15570, "Train Worm", "SMB2 Expert",
                [MissionData(MissionType.CLEAR, [time(2), True_()])]
            ),
        ]
    ),
    "SMB2 Master": 
        RegionData(name="SMB2 Master", req_items=Has("SMB2 Master Challenge Mode"), challenge_region=True, stage_data=[
            StageData(
                16010, "Centrifugal", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(2), time(1), True_()])]
            ),
            StageData(
                16020, "Swing Bridges", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                16030, "Cylinders", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16040, "Passage", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                16050, "Notch", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                16060, "Intermittent", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16070, "Long Torus", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                16080, "Spasmodic", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16090, "Double Twin", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                16100, "Clock Face", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                16110, "Variable Width", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16120, "Striker", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1), True_()])]
            ),
            StageData(
                16130, "Ooparts", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16140, "Planets", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                16150, "Sliced Cheese", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(2)])]
            ),
            StageData(
                16160, "8 Seesaws", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(1)])]
            ),
            StageData(
                16170, "Synchronized", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16180, "Helix", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(5)])]
            ),
            StageData(
                16190, "Dizzy Systems", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [])]
            ),
            StageData(
                16200, "Destiny", "SMB2 Master",
                [MissionData(MissionType.CLEAR, [time(3)])]
            ),
        ]
    ),
}

CATEGORY_DATA_DICT: dict[str, CategoryData] = {
    "Deluxe Mode":
        CategoryData(
            100000, "Deluxe Mode",
            HasAny("Deluxe Beginner Stages Pack", "Deluxe Advanced Stages Pack", "Deluxe EX Stages Pack", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_packs)]) \
            | Has("Deluxe Mode", options=[OptionFilter(DeluxeUnlockStyle, DeluxeUnlockStyle.option_all)]),
            
            sum([
                MISSION_DATA_DICT["Deluxe Beginner Pack"].stage_data, 
                MISSION_DATA_DICT["Deluxe Advanced Pack"].stage_data, 
                MISSION_DATA_DICT["Deluxe EX Pack"].stage_data
            ], []),
            
            [
                MissionData(MissionType.CLEAR, [], 1, category_mission=True),
                MissionData(MissionType.TURNING_POINT, [], 23, category_mission=True),
                MissionData(MissionType.STAGE_COMPLETE, [], 46, category_mission=True)
            ]
        ),
    "Reverse Mode":
        CategoryData(
            110000, "Reverse Mode", Has("Reverse Mode"), MISSION_DATA_DICT["Reverse Mode"].stage_data,
            [
                MissionData(MissionType.CLEAR, [], 1, category_mission=True),
                MissionData(MissionType.TURNING_POINT, [], 5, category_mission=True),
                MissionData(MissionType.STAGE_COMPLETE, [], 10, category_mission=True)
            ]
        ),
    "Dark Banana Mode":
        CategoryData(
            120000, "Dark Banana Mode", Has("Dark Banana Mode"), MISSION_DATA_DICT["Dark Banana Mode"].stage_data,
            [
                MissionData(MissionType.CLEAR, [], 1, category_mission=True),
                MissionData(MissionType.TURNING_POINT, [], 5, category_mission=True),
                MissionData(MissionType.STAGE_COMPLETE, [], 10, category_mission=True)
            ]
        ),
    "Golden Banana Mode":
        CategoryData(
            130000, "Golden Banana Mode", Has("Golden Banana Mode"), MISSION_DATA_DICT["Golden Banana Mode"].stage_data,
            [
                MissionData(MissionType.CLEAR, [], 1, category_mission=True),
                MissionData(MissionType.TURNING_POINT, [], 5, category_mission=True),
                MissionData(MissionType.STAGE_COMPLETE, [], 10, category_mission=True)
            ]
        ),
    "Original Stages Mode":
        CategoryData(
            140000, "Original Stages Mode", Has("Original Stages Mode"), MISSION_DATA_DICT["Original Stages Mode"].stage_data,
            [
                MissionData(MissionType.CLEAR, [], 1, category_mission=True),
                MissionData(MissionType.TURNING_POINT, [], 12, category_mission=True),
                MissionData(MissionType.STAGE_COMPLETE, [], 23, category_mission=True)
            ]
        ),
    "SMB1 Casual":
        CategoryData(
            200000, "SMB1 Casual", Has("SMB1 Casual Challenge Mode"), MISSION_DATA_DICT["SMB1 Casual"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 10, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB1 Normal":
        CategoryData(
            210000, "SMB1 Normal", Has("SMB1 Normal Challenge Mode"), MISSION_DATA_DICT["SMB1 Normal"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 30, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB1 Expert":
        CategoryData(
            220000, "SMB1 Expert", Has("SMB1 Expert Challenge Mode"), MISSION_DATA_DICT["SMB1 Expert"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 99, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB1 Master":
        CategoryData(
            230000, "SMB1 Master", Has("SMB1 Master Challenge Mode"), MISSION_DATA_DICT["SMB1 Master"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 50, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB2 Casual":
        CategoryData(
            300000, "SMB2 Casual", Has("SMB2 Casual Challenge Mode"), MISSION_DATA_DICT["SMB2 Casual"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 10, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB2 Normal":
        CategoryData(
            310000, "SMB2 Normal", Has("SMB2 Normal Challenge Mode"), MISSION_DATA_DICT["SMB2 Normal"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 30, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB2 Expert":
        CategoryData(
            320000, "SMB2 Expert", Has("SMB2 Expert Challenge Mode"), MISSION_DATA_DICT["SMB2 Expert"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 99, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
    "SMB2 Master":
        CategoryData(
            330000, "SMB2 Master", Has("SMB2 Master Challenge Mode"), MISSION_DATA_DICT["SMB2 Master"].stage_data,
            [
                MissionData(MissionType.CHALLENGE_CLEAR,        [], category_mission=True, challenge_category_mission=True),
                MissionData(MissionType.CHALLENGE_CLEAR_EXTRA,  [], 70, category_mission=True, challenge_category_mission=True),
            ], challenge=True
        ),
}