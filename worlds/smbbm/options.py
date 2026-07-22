from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

class IncludeBananaMissions(Toggle):
    """
    Includes the Banana Collect Missions. These are more difficult.
    """

    display_name = "Banana Collect Missions"

class IncludeTimeMissions(Toggle):
    """
    Includes the Time Limit Missions. These are more difficult.
    """

    display_name = "Time Limit Missions"

class IncludeExtraGoals(Toggle):
    """
    Includes the extra goals as checks. These are more difficult.
    """

    display_name = "Extra Goals"

class IncludeNonstopMissions(Toggle):
    """
    Include the Deluxe Stages in logic.
    """

    display_name = "Deluxe Stages"

class WorldStructure(Choice):
    """
    How the SMB2 campaign world items should be structured.
    progression: Receive "Progressive World Unlock", which unlocks the next world in order.
    worlds: Receive specific world unlocks, making you do worlds out of order.
    """

    display_name = "World Structure"

    option_progression = 0
    option_worlds = 1

    default = option_progression


@dataclass
class BananaManiaOptions(PerGameCommonOptions):
    banana_missions: IncludeBananaMissions
    time_missions: IncludeTimeMissions
    extra_goals: IncludeExtraGoals
    nonstop_missions: IncludeNonstopMissions
    world_structure: WorldStructure


option_groups = [
    OptionGroup(
        "Mission Options",
        [IncludeBananaMissions, IncludeTimeMissions, IncludeExtraGoals, IncludeNonstopMissions],
    ),
    OptionGroup(
        "Item Options",
        [WorldStructure],
    ),
]