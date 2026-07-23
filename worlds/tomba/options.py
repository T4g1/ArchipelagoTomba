from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle


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


@dataclass
class TombaOptions(PerGameCommonOptions):
    bell_warp: BellWarp
    keep_blackjack: KeepBlackjack
