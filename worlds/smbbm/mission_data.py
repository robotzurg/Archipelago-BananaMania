from rule_builder.rules import Has, True_, Rule, HasAll, HasAny, OptionFilter
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
    def __init__(self, mission_type: MissionType, req_items: list[Rule], amount: int | str | None = None, add_clear_reqs: bool = False):
        self.mission_type = mission_type
        self.req_items = self.fill_in_req_items(req_items)
        self.amount = amount
        self.mission_name: str = self.get_mission_name()
        self.add_clear_reqs = add_clear_reqs

    def add_req_items_rules(self, req_items):
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
    
    def get_mission_item_req(self, difficulty: Difficulty):
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
    def __init__(self, name: str, req_items: Rule, stage_data: list[StageData]):
        self.name = name
        self.req_items = req_items
        self.stage_data = stage_data
        
    def __len__(self):
        return len(self.stage_data)
    
    def get_region_locations(self) -> list[tuple[str, int]]:
        loc_list = []
        for stage in self.stage_data:
            mission_loc_list = stage.get_mission_location_list()
            loc_list.extend(mission_loc_list)
            
        return loc_list

class CategoryData:
    def __init__(self, name: str, stage_data: list[StageData], missions: list[MissionData]):
        self.name = name
        self.stage_data = stage_data
        self.missions = missions
    
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

# TODO: Add logic for banana/time/nonstop

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
                    MissionData(MissionType.TIME, [], 10, add_clear_reqs=True)
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
                    MissionData(MissionType.TIME, [], 10, add_clear_reqs=True)
                ]
            ),
            StageData(
                80, "Windy Slide", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(3), time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 70),
                    MissionData(MissionType.TIME, [], 30, add_clear_reqs=True),
                    MissionData(MissionType.NONSTOP, [], add_clear_reqs=True)
                ]
            ),
            StageData(
                90, "Spinning Top", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 15, add_clear_reqs=True)
                ]
            ),
            StageData(
                100, "Curve Bridge", "World 1",
                [
                    MissionData(MissionType.CLEAR, [time(3)]),
                    MissionData(MissionType.BANANA, [time(3)], 60),
                    MissionData(MissionType.TIME, [], 35, add_clear_reqs=True)
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
                    MissionData(MissionType.TIME, [], 10, add_clear_reqs=True)
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                140, "Coaster", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 55),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
                ]
            ),
            StageData(
                150, "Bumpy Check", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                180, "Inchworms", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 30),
                    MissionData(MissionType.TIME, [], 30),
                    MissionData(MissionType.GREEN, [time(1) & Has("Normal Switches")]),
                    MissionData(MissionType.RED, [time(1) & Has("Normal Switches")]),
                ]
            ),
            StageData(
                190, "Totalitarianism", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                200, "Alternative", "World 2",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1) & Has("Fast Switches")]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                220, "Reversible Gear", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 30),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                230, "Stepping Stones", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 70),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                240, "Dribbles", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3)]),
                    MissionData(MissionType.BANANA, [time(5)], "Complete"),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                250, "Push Bar", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(4)], "Complete"),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                260, "Mad Rings", "World 3",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 30),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, []),
                    MissionData(MissionType.RED, [time(1)])
                ]
            ),
            StageData(
                270, "Curvy Options", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 40),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                280, "Twist & Spin", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(1)], 15),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                290, "Cascade", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                300, "Junction", "World 3",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(1)], 38),
                    MissionData(MissionType.TIME, [], 35),
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                330, "Beehive", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(5)], 25),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                340, "Dynamic Maze", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4)], 30),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
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
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
            StageData(
                370, "Randomizer", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(1)], 35),
                    MissionData(MissionType.TIME, [], 10),
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
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                400, "Arthropod", "World 4",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4)], "Complete"),
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                420, "Free Fall", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(4), time(3)], 50),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(2), time(2), time(1)])
                ]
            ),
            StageData(
                430, "Melting Pot", "World 5",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                440, "Mad Shuffle", "World 5",
                [
                    MissionData(MissionType.CLEAR, [Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(4) & Has("Normal Switches") & Has("Wormholes")], "Complete"),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
                ]
            ),
            StageData(
                450, "Bead Screen", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Pause Switches"), True_()]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Pause Switches")], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                460, "Jump Machine", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 25),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(2)]),
                    MissionData(MissionType.RED, [time(3)])
                ]
            ),
            StageData(
                470, "Zigzag Slope", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 25),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                480, "Tower", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Wormholes")], 25),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                490, "Toggle", "World 5",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], "Complete"),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                500, "Fluctuation", "World 5",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(3), time(2)], 20),
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                540, "Brandished", "World 6",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(2)], 35),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
                ]
            ),
            StageData(
                550, "Tiers", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes")]),
                    MissionData(MissionType.BANANA, [time(3) & Has("Wormholes")], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, []),
                    MissionData(MissionType.GREEN, [time(2) & Has("Wormholes")]),
                    MissionData(MissionType.RED, [time(1) & Has("Wormholes")])
                ]
            ),
            StageData(
                560, "Cliffs", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                570, "Narrow Peaks", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                580, "Detours", "World 6",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Wormholes"), Has("Wormholes"), True_()]),
                    MissionData(MissionType.BANANA, [time(1) & Has("Wormholes")], 20),
                    MissionData(MissionType.TIME, [], 30),
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
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                620, "Wavy Option", "World 7",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1), time(1), True_()], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                630, "Obstacle", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                640, "Domino", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1) & Has("Normal Switches"), Has("Normal Switches"), True_()]),
                    MissionData(MissionType.BANANA, [time(2) & Has("Normal Switches")], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
                ]
            ),
            StageData(
                650, "Sieve", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                660, "Flock", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(5)], 15),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                670, "Double Spiral", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                680, "Hierarchy", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2), True_()]),
                    MissionData(MissionType.BANANA, [time(2)], 15),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                690, "8 Bracelets", "World 7",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 15),
                    MissionData(MissionType.GREEN, [time(2)]),
                    MissionData(MissionType.RED, [time(2)])
                ]
            ),
            StageData(
                700, "Quick Turn", "World 7",
                [
                    MissionData(MissionType.CLEAR, [Has("Fast Switches")]),
                    MissionData(MissionType.BANANA, [Has("Fast Switches") | time(1)], "Complete"),
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
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
                    MissionData(MissionType.TIME, [], 10)
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
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(3) & HasAll("Normal Switches", "Fast Switches")])
                ]
            ),
            StageData(
                750, "Totters", "World 8",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 28),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                760, "Vortex", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 10),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(2)])
                ]
            ),
            StageData(
                770, "Warp", "World 8",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(4)], 40),
                    MissionData(MissionType.TIME, [], 10),
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
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                800, "Linear Seesaws", "World 8",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 10),
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(1)]),
                    MissionData(MissionType.RED, [])
                ]
            ),
            StageData(
                820, "Cross Floors", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                830, "Spinning Saw", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(2), True_()]),
                    MissionData(MissionType.BANANA, [time(2), time(2), time(1)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                840, "Chipped Pipes", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1), True_()]),
                    MissionData(MissionType.BANANA, [time(1)], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [time(1)])
                ]
            ),
            StageData(
                850, "Flat Maze", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(5), time(3), time(2)]),
                    MissionData(MissionType.BANANA, [time(5)], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                860, "Guillotine", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(2)]),
                    MissionData(MissionType.BANANA, [time(2)], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                870, "Cork Screw", "World 9",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(1)], 12),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                880, "Orbiters", "World 9",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [time(1)], 15),
                    MissionData(MissionType.TIME, [], 30)
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
                    MissionData(MissionType.TIME, [], 35)
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
                    MissionData(MissionType.TIME, [], 10)
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
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.GREEN, [HasAll("Progressive Time Increase", "Normal Switches")])
                ]
            ),
            StageData(
                950, "3D Maze", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(2), time(1)]),
                    MissionData(MissionType.BANANA, [time(2)], 20),
                    MissionData(MissionType.TIME, [], 10),
                    MissionData(MissionType.NONSTOP, [])
                ]
            ),
            StageData(
                960, "Crazy Maze", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(5), time(4)]),
                    MissionData(MissionType.BANANA, [time(5)], 20),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                970, "Post Modern", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(4), time(3)]),
                    MissionData(MissionType.BANANA, [time(4)], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                980, "Revolution", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(1)]),
                    MissionData(MissionType.BANANA, [time(3)], 10),
                    MissionData(MissionType.TIME, [], 30)
                ]
            ),
            StageData(
                990, "Invisible", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(5) & Has("Normal Switches"), time(4) & Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(5) & Has("Normal Switches")], 29),
                    MissionData(MissionType.TIME, [], 15)
                ]
            ),
            StageData(
                1000, "Last Stage", "World 10",
                [
                    MissionData(MissionType.CLEAR, [time(2) & Has("Normal Switches")]),
                    MissionData(MissionType.BANANA, [time(2) & Has("Normal Switches")], 25),
                    MissionData(MissionType.TIME, [], 35)
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
}