# Tomba! Archipelago developement

## Issues

* Prevent player out of lunch box for the event in hidden village
* When grabbing the key of 100 Year Old Wise Man: The sprite stays there
* Fight with Blue Evil Pig is glitched when accessing with Million Year Old Bell (but doable)

## Ideas

* [REVERSE] Display custom text
* Heal Tomba
* Change Tomba status (normal, cry, laugh)
* [REVERSE] Intercept Life pickup and Max life pickup
* [REVERSE] Intercept animal dash, swim, dive
* Cache RAM to free some RetroArch exchange
* Deathlink can be done by triggering a call to 0x8001B0A4 which kills Tomba (or maybe set life to 0 instead ?)
* [REVERSE] Trigger event cleared/started display (usefull for Take Out softlock prevention)
* [REVERSE] Can't use baron if given: Requires Drink for Grownups and Road to Baccus Lake to be cleared
* [REVERSE] SFX values are tied to the section loaded (Fart is another sound in Masakari Jungle for example)
* [REVERSE] A method is making sure that Tomba has a weapon at the start (after the player init method), this makes it messy to remove starting weapon

## Tasks

* Link location that are reward for event to the event that triggers it: This will allow externaly forced cleared event to still give the reward

## Notes

### Open chest and leave area

If the player does that without taking the item, the object flag is not set so the chest respawn exept if there are two items in it and at least one is grabbed. So every chest that contains two locations should be reset unless both locations are checked (happens only for cheese and charity wings probably)

## References

* https://docs.google.com/spreadsheets/d/1eImavd7tPoulWOoT0km9wRioWRnIiDSCMftlX3A6swk/edit?usp=sharing
* https://github.com/hansbonini/psx_tomba
* https://docs.google.com/spreadsheets/d/1Ox03xmqWjtua23k9BP_nXFVbgvh-ot8RoQxDIXw4kFk/edit?usp=sharing
