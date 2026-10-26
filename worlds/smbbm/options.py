from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, DefaultOnToggle

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
    Include the Nonstop missions as checks. These are more difficult.
    """

    display_name = "Nonstop Missions"

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

class LogicDifficulty(Choice):
    """
    The difficulty of logic for beating levels. In the discord channel pins you can find a
    spreadsheet detailing all the specifics of how each of these affects the difficulty of beating levels,
    but in general you can assume that:

    Standard: Dev intended or very obvious skip routes that require minimal difficulty (recommended for most players)
    Intermediate: Some skips required, nothing absurd, but trickier, good if you are good at Super Monkey Ball
    Expert: Very hard tricks and skips fully required to beat levels really fast, VERY hard on some levels and still being refined
    """

    display_name = "Logic Difficulty"

    option_standard = 0
    option_intermediate = 1
    option_expert = 2

    default = option_standard
    
class Smb1CasualChallengeMode(DefaultOnToggle):
    """
    Include SMB1 Casual difficulty challenge mode in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB1 Casual Challenge Mode Stages"
    
class Smb1NormalChallengeMode(DefaultOnToggle):
    """
    Include SMB1 Normal difficulty challenge mode in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB1 Normal Challenge Mode Stages"
    
class Smb1ExpertChallengeMode(Toggle):
    """
    Include SMB1 Expert difficulty challenge mode in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB1 Expert Challenge Mode Stages"
    
class Smb1MasterChallengeMode(Toggle):
    """
    Include SMB1 Master difficulty challenge mode in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB1 Master Challenge Mode Stages"
    
class DeluxeStages(DefaultOnToggle):
    """
    Include the Deluxe stages in logic.
    """
    
    display_name = "Deluxe Stages"
    
class DeluxeUnlockStyle(Choice):
    """
    How the Deluxe stages should be unlocked.
    all: Unlock all deluxe stages at once when sent the Deluxe Stages unlock.
    packs: Unlock the deluxe stages in packs, with 4 total packs added to the item pool.
    Does nothing if deluxe stages are disabled.
    """
    
    display_name = "Deluxe Stages Unlock Style"
    
    option_all = 0
    option_packs = 1
    
    default = option_packs
    
class ReverseModeStages(Toggle):
    """
    Include Reverse Mode stages in logic.
    """
    
    display_name = "Reverse Mode Stages"
    
class DarkBananaStages(Toggle):
    """
    Include Dark Banana Mode stages in logic.
    """
    
    display_name = "Dark Banana Mode Stages"
    
class GoldenBananaStages(Toggle):
    """
    Include Golden Banana Mode stages in logic.
    """
    
    display_name = "Golden Banana Mode Stages"
    
class OriginalStagesMode(Toggle):
    """
    Include Original Stages Mode stages in logic.
    """
    
    display_name = "Original Stages Mode Stages"
    
class Smb2CasualExChallengeMode(Toggle):
    """
    Include the SMB2 Casual EX Challenge Mode stages in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB2 Casual EX Challenge Mode Stages"
    
class Smb2NormalExChallengeMode(Toggle):
    """
    Include the SMB2 Normal EX Challenge Mode stages in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB2 Normal EX Challenge Mode Stages"
    
class Smb2ExpertExChallengeMode(Toggle):
    """
    Include the SMB2 Expert EX Challenge Mode stages in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB2 Expert EX Challenge Mode Stages"
    
class Smb2MasterExChallengeMode(Toggle):
    """
    Include the SMB2 Master EX Challenge Mode stages in logic.
    Adds 2 checks.
    """
    
    display_name = "SMB2 Master EX Challenge Mode Stages"
    

@dataclass
class BananaManiaOptions(PerGameCommonOptions):
    banana_missions: IncludeBananaMissions
    time_missions: IncludeTimeMissions
    extra_goals: IncludeExtraGoals
    nonstop_missions: IncludeNonstopMissions
    world_structure: WorldStructure
    logic_difficulty: LogicDifficulty
    smb1_casual: Smb1CasualChallengeMode
    smb1_normal: Smb1NormalChallengeMode
    smb1_expert: Smb1ExpertChallengeMode
    smb1_master: Smb1MasterChallengeMode
    deluxe_stages: DeluxeStages
    deluxe_unlock_style: DeluxeUnlockStyle
    reverse_mode: ReverseModeStages
    dark_banana_mode: DarkBananaStages
    golden_banana_mode: GoldenBananaStages
    original_stages_mode: OriginalStagesMode
    smb2_casual: Smb2CasualExChallengeMode
    smb2_normal: Smb2NormalExChallengeMode
    smb2_expert: Smb2ExpertExChallengeMode
    smb2_master: Smb2MasterExChallengeMode

option_groups = [
    OptionGroup(
        "Mission Options",
        [IncludeBananaMissions, IncludeTimeMissions, IncludeExtraGoals, IncludeNonstopMissions],
    ),
    OptionGroup(
        "Challenge Mode Options",
        [Smb1CasualChallengeMode, Smb1NormalChallengeMode, Smb1ExpertChallengeMode, Smb1MasterChallengeMode,
         Smb2CasualExChallengeMode, Smb2NormalExChallengeMode, Smb2ExpertExChallengeMode, Smb2MasterExChallengeMode]
    ),
    OptionGroup(
        "Special Mode Options",
        [ReverseModeStages, DarkBananaStages, GoldenBananaStages, OriginalStagesMode]
    ),
    OptionGroup(
        "Extra Options",
        [WorldStructure, DeluxeUnlockStyle, LogicDifficulty],
    ),
]