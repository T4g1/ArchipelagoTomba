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
* It's a complex matter to match items found in game with Archipelago locations. The current algorithm has some flaws, it uses the position of the items to determines what was picked up but Tombi can grab some items and finish picking them up at another position so two of the same item can be picked at the same location. Because of that, the algorithm uses nearest location position with some error margin:
  1. Save state
  2. Pick an item close to another item of the same type (a good example are Bunk Flower in the Lava Caves or Chick in the Forest of All Beginings): Location is checked
  3. Load state
  4. Pick the same item: The location for the other item will be checked
There are few uses for this and it's not such a big deal so expect a few inconsistencies in the log when using save states like that

## Notes

### Open chest and leave area

If the player does that without taking the item, the object flag is not set so the chest respawn exept if there are two items in it and at least one is grabbed. So every chest that contains two locations should be reset unless both locations are checked (happens only for cheese and charity wings probably)

## References

* https://docs.google.com/spreadsheets/d/1eImavd7tPoulWOoT0km9wRioWRnIiDSCMftlX3A6swk/edit?usp=sharing
* https://github.com/hansbonini/psx_tomba
* https://docs.google.com/spreadsheets/d/1Ox03xmqWjtua23k9BP_nXFVbgvh-ot8RoQxDIXw4kFk/edit?usp=sharing
* https://www.deviantart.com/vgcartography/gallery
