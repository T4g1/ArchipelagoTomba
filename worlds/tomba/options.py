from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle, DefaultOnToggle


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


class OptionnalItemsRandomized(DefaultOnToggle):
    """
    Toggle if the optionnal items like Pipe and Broken Vase,
    which are not required to complete their respective events, should be randomized too
    If this is on: Picking the item in the world will give a randomized item
    If this is off: Picking the item in the world will give the original item (Pipe or Broken Vase in this example)
    """

    display_name = "Optionnal randomized ?"


@dataclass
class TombaOptions(PerGameCommonOptions):
    bell_warp: BellWarp
    keep_blackjack: KeepBlackjack
    optionnal_randomized: OptionnalItemsRandomized
