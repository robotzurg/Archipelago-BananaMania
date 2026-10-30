from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

from .options import option_groups

# NOTICE: This is human made and is just an edit of the APQuest template. Leave it be.

class BananaManiaWebWorld(WebWorld):
    game = "Super Monkey Ball Banana Mania"

    theme = "grassFlowers"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Super Monkey Ball Banana Mania for MultiWorld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Jeffdev"],
    )

    tutorials = [setup_en]

    option_groups = option_groups
