from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

# In this file, we define the options the player can pick.
# The most common types of options are Toggle, Range and Choice.

# Options will be in the game's template yaml.
# They will be represented by checkboxes, sliders etc. on the game's options page on the website.
# (Note: Options can also be made invisible from either of these places by overriding Option.visibility.
#  APQuest doesn't have an example of this, but this can be used for secret / hidden / advanced options.)

# For further reading on options, you can also read the Options API Document:
# https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md


# The first type of Option we'll discuss is the Toggle.
# A toggle is an option that can either be on or off. This will be represented by a checkbox on the website.
# The default for a toggle is "off".
# If you want a toggle to be on by default, you can use the "DefaultOnToggle" class instead of the "Toggle" class.
class IncludeBananaMissions(Toggle):
    """
    Includes the Banana Collect Missions. These are more difficult.
    """

    # The docstring of an option is used as the description on the website and in the template yaml.

    # You'll also want to set a display name, which will determine what the option is called on the website.
    display_name = "Banana Collect Missions"

class IncludeTimeMissions(Toggle):
    """
    Includes the Time Limit Missions. These are more difficult.
    """

    # The docstring of an option is used as the description on the website and in the template yaml.

    # You'll also want to set a display name, which will determine what the option is called on the website.
    display_name = "Time Limit Missions"

class IncludeExtraGoals(Toggle):
    """
    Includes the extra goals as checks. These are more difficult.
    """

    # The docstring of an option is used as the description on the website and in the template yaml.

    # You'll also want to set a display name, which will determine what the option is called on the website.
    display_name = "Extra Goals"

class WorldStructure(Choice):
    """
    How the world items should be structured.
    progression: Receive "Progressive World Unlock", which unlocks the next world in order.
    worlds: Receive specific world unlocks, making you do worlds out of order.
    """

    display_name = "Player Sprite"

    option_progression = 0
    option_worlds = 1

    # Choice options must define an explicit default value.
    default = option_progression


# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class BananaManiaOptions(PerGameCommonOptions):
    banana_missions: IncludeBananaMissions
    time_missions: IncludeTimeMissions
    extra_goals: IncludeExtraGoals
    world_structure: WorldStructure


# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Mission Options",
        [IncludeBananaMissions, IncludeTimeMissions, IncludeExtraGoals],
    ),
    OptionGroup(
        "Item Options",
        [WorldStructure],
    ),
]