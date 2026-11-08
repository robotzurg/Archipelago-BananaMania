from rule_builder.rules import AtLeast, CanReachRegion, Has, True_, HasAny, Rule, HasAll
from math import ceil
from enum import Enum

class Difficulty(Enum):
    STANDARD = 0,
    INTERMEDIATE = 1,
    EXPERT = 2,

class MissionType(Enum):
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

class MissionData:
    def __init__(self, mission_type: MissionType, req_items: list[Rule], amount: int | None = None):
        self.mission_type = mission_type
        self.req_items = req_items
        self.amount = amount
        self.mission_name: str = self.get_mission_name()
        
    def get_mission_name(self):
        match self.mission_type:
            case MissionType.CLEAR: 
                self.mission_name = "Stage Clear"
            case MissionType.BANANA: 
                self.mission_name = f"Banana Collector {self.amount}"
            case MissionType.TIME:
                self.mission_name = f"Time Limit {self.amount}"
            case MissionType.GREEN:
                self.mission_name = "Green Goal"
            case MissionType.RED:
                self.mission_name = "Red Goal"
            case MissionType.NONSTOP:
                self.mission_name = "Nonstop"
            case MissionType.CHALLENGE_CLEAR:
                self.mission_name = "Course Clear"
            case MissionType.CHALLENGE_CLEAR_EXTRA:
                self.mission_name = f"Challenge {self.amount}"
            case MissionType.TURNING_POINT:
                self.mission_name = f"Turning Point {self.amount}"
            case MissionType.STAGE_COMPLETE:
                self.mission_name = f"Stage Complete {self.amount}"
    
    def get_mission_item_req(self, difficulty: Difficulty):
        return self.req_items[difficulty.value]
        
class StageData:
    def __init__(self, name: str, region: str, missions: list[MissionData]):
        self.name = name
        self.region = region
        self.missions = missions
        
class RegionData:
    def __init__(self, name: str, req_items: Rule, stage_data: list[StageData]):
        self.name = name
        self.req_items = req_items
        self.stage_data = stage_data
                

MISSION_DATA_DICT: dict[str, RegionData] = {
    "World 1": 
        RegionData(name="W1", req_items=True_(), stage_data=[
            StageData(
                "Simple", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Hollow", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Bumpy", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Switches", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Conveyors", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Floaters", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Tub", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Windy Slide", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Spinning Top", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
            StageData(
                "Curve Bridge", "World 1",
                [
                    MissionData(MissionType.CLEAR, []),
                    MissionData(MissionType.BANANA, [], 10),
                    MissionData(MissionType.TIME, [], 10)
                ]
            ),
        ]
    )
}