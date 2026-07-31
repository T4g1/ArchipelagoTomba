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
    Warning: Expect glitch t 0
    o happens with this
    """

    display_name = "Bell Warp"


class KeepBlackjack(Toggle):
    """
    Toggle if the player starts with a starting weapon
    """

    display_name = "Keep Blackjack ?"


class OptionnalItemsRandomized(DefaultOnToggle):
    """
    Toggle if the optionnal items like Pipe and Broken Vase,
    which are not required to complete their respective events, should be randomized too
    If this is on: Picking the item in the world will give a randomized item
    If this is off: Picking the item in the world will give the original item (Pipe or Broken Vase in this example)
    """

    display_name = "Optionnal randomized ?"


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
    optionnal_randomized: OptionnalItemsRandomized
    cleared_event_rewards: ClearedLocation
