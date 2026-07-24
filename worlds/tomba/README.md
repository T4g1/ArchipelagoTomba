# Tomba! APWorld

## Technical stuff

The game is patched at run time because:
* It's cool
* I wanted to
* It removes some complexity for end-user

## Known limitations

* Baron is not randomized: There are too much event linked to that dog, it would remove too much content
* Furious Tornado is not randomized: There is an event on the Mailbox closely related to that item and it cause too much trouble to randomize it
* Healing mushroom, frog and Blue powder are not randomized: Don't really know what to do with those as they are infinite
* If the client crashes, the game will store items it grabs in a LIFO list because it's much much easier to do in Assembly. Functionaly, it means that once the client reconnects, Archipelago will receive checks in reverse order! It's good enough probably besides, you should not continue playing while the client is down anyway
* You can walk in the Masakari River if Archipelago send you that way (getting Fuel Bar before learning how to swim), in that case, you will receive a free Charity Wing to get out.

## Issues

* Prevent player out of lunch box for the event in hidden village
* When grabbing the key of 100 Year Old Wise Man: The sprite stays there
* Fight with Blue Evil Pig is glitched when accessing with Million Year Old Bell (but doable)

## Ideas

* [REVERSE] Display custom text
* Heal Tomba
* Change Tomba status (normal, cry, laugh)
* [REVERSE] Intercept Life pickup and Max life pickup
* [REVERSE] Intercept animal dash
* Cache RAM to free some RetroArch exchange
* Deathlink can be done by triggering a call to 0x8001B0A4 which kills Tomba (or maybe set life to 0 instead ?)
* [REVERSE] Trigger event cleared/started display (usefull for Take Out softlock prevention)

## Tasks

* Link location that are reward for event to the event that triggers it: This will allow externaly forced cleared event to still give the reward

## Notes

### Open chest and leave area

If the player does that without taking the item, the object flag is not set so the chest respawn exept if there are two items in it and at least one is grabbed. So every chest that contains two locations should be reset unless both locations are checked (happens only for cheese and charity wings probably)

## References

* https://docs.google.com/spreadsheets/d/1eImavd7tPoulWOoT0km9wRioWRnIiDSCMftlX3A6swk/edit?usp=sharing
* https://github.com/hansbonini/psx_tomba
* https://docs.google.com/spreadsheets/d/1Ox03xmqWjtua23k9BP_nXFVbgvh-ot8RoQxDIXw4kFk/edit?usp=sharing
* https://www.deviantart.com/vgcartography/gallery
