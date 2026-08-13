from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle, DefaultOnToggle, Choice, Range


class Emulator(Choice):
    """
    Choose the emulator you want to use
    """

    display_name = "Emulator"

    option_bizhawk = 0
    option_retroarch = 1

    default = 0


class Deathlink(Toggle):
    """
    Toggle to synchronize death across the multi world
    """

    display_name = "Deathlink"


class BellWarp(Toggle):
    """
    Allow sequence break using the bells.
    Warning: Expect glitch to happens with this
    """

    display_name = "Bell Warp"


class KeepBlackjack(Toggle):
    """
    Toggle if the player starts with a starting weapon
    """

    display_name = "Keep Blackjack ?"


class StatusAlteration(Toggle):
    """
    Toggle if the player can receive status alteration as a handicap
    """

    display_name = "Random status alteration ?"


class GodMode(Toggle):
    """
    Toggle this if you want to never run out of lifes
    """

    display_name = "No Game Over"


class OptionalItemsRandomized(DefaultOnToggle):
    """
    Toggle if the optional items like Pipe and Broken Vase,
    which are not required to complete their respective events, should be randomized too
    If this is on: Picking the item in the world will give a randomized item
    If this is off: Picking the item in the world will give the original item (Pipe or Broken Vase in this example)
    """

    display_name = "Optional randomized ?"


class BonusChestsRandomized(DefaultOnToggle):
    """
    Toggle if chests containing AP Crystals or Apples, should give a random item too.
    If this is on: Picking the AP Crystals/Apples from these chests will also give a randomized item too
    If this is off: Picking the AP Crystals/Apples from these chests will NOT give a randomized item too.
    """

    display_name = "Bonus Chests randomized ?"


class ClearedLocation(DefaultOnToggle):
    """
    Toggle if event cleared should count as a location check or not
    If on: You will get random rewards when clearing event
    If off: Clearing events will give you nothing
    """

    display_name = "Cleared event rewards"


class ChickAmount(Range):
    """Allows to control how many chick will be available
    This is usefull to prevent being stuck in the first area early.
    You only require 4 of those so a higher number means you're more likely
    to be able to pass the count check early.
    Note: This is not used if chick are not randomized"""

    range_start = 4
    range_end = 50
    default = 4

    display_name = "Chick amount"


class ChickRandomized(DefaultOnToggle):
    """
    Toggle wether or not the Chick should be randomized.
    Enabling this means you can get blocked and have to wait until all the Chick are found in the multiworld
    """

    display_name = "Chick randomized ?"


class FuriousTornadoRandomized(DefaultOnToggle):
    """
    Toggle wether or not the Furious Tornado should be randomized.
    Enabling this means you can get blocked and have to wait until the tornado is found in the multiworld
    """

    display_name = "Furious Tornado randomized ?"


@dataclass
class TombaOptions(PerGameCommonOptions):
    emulator: Emulator
    bell_warp: BellWarp
    keep_blackjack: KeepBlackjack
    chick_randomized: ChickRandomized
    furious_tornado_randomized: FuriousTornadoRandomized
    optional_randomized: OptionalItemsRandomized
    bonus_chests_randomized: BonusChestsRandomized
    cleared_event_rewards: ClearedLocation
    chick_amount: ChickAmount
    status_alteration: StatusAlteration
    deathlink: Deathlink
    god_mode: GodMode
