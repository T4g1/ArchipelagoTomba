from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle, DefaultOnToggle, Choice


class Emulator(Choice):
    """
    Choose the emulator you want to use
    """

    display_name = "Emulator"

    option_bizhawk = 0
    option_retroarch = 1

    default = 0


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


@dataclass
class TombaOptions(PerGameCommonOptions):
    emulator: Emulator
    bell_warp: BellWarp
    keep_blackjack: KeepBlackjack
    optional_randomized: OptionalItemsRandomized
    bonus_chests_randomized: BonusChestsRandomized
    cleared_event_rewards: ClearedLocation
