from rule_builder.rules import Has, CanReachLocation

from .constants import Events, Items


def Started(event_name: str):
    return f"{event_name} Started"


def Cleared(event_name: str):
    return f"{event_name} Cleared"


def HasStarted(event_name: str):
    return CanReachLocation(Started(event_name))


def HasCleared(event_name: str):
    return CanReachLocation(Cleared(event_name))


class Rules:
    CAN_GRAPPLE = Has(Items.GRAPPLE) | Has(Items.GRAPPLEJACK)
    CAN_LIGHT_BREAK_STUFF = Has(Items.BLACKJACK) | Has(Items.WOOD_BOOMERANG)
    CAN_BREAK_STUFF = (
        CAN_LIGHT_BREAK_STUFF
        | Has(Items.STONE_BOOMERANG)
        | Has(Items.IRON_BOOMERANG)
        | Has(Items.GRAPPLEJACK)
        | Has(Items.JEWEL_OF_FIRE)
        | Has(Items.JEWEL_OF_WATER)
    )
    CAN_DASH = HasCleared(Events.A_HUNGRY_MONKEY) | Has(Items.SACRED_FISH)
    CAN_SWIM = HasCleared(Events.I_CANT_SWIM) | Has(Items.SACRED_FISH)
    CAN_DIVE = HasCleared(Events.WHATS_UNDERWATER)
    CAN_BIG_JUMP = (
        HasCleared(Events.A_HUNGRY_MONKEY)
        | Has(Items.FLASH_PANTS)
        | Has(Items.DASHING_PANTS)
        | Has(Items.JUMPING_PANTS)
        | Has(Items.SACRED_FISH)
        | Has(Items.PSYCHIC_FISH)
        | (Has(Items.BLUE_POWDER) & HasStarted(Events.TO_PHOENIX_MOUNTAIN))
    )
