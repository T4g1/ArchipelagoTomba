# Tomba! Archipelago developement

## TODO

* Pre-patch ROM before playing
* [REVERSE] Can't give flower seeds to the dwarf until they are picked up: Find how to set that manualy/remove limitation
* Force clear the TAKE OUT event if yan's already found (Hide and Go Seek cleared) and/or prevent usage of Yan lunch box
* Prevent player out of lunch box for the event in hidden village
* "Take out" event reward cheese: rule the 5 locations for it to happen ?
* [REVERSE] Possible softlock if has fuel bar and goes to the mermaid singing rock without knowing how to swim (spawn with baron ?) as only exit is masakari river. Give charity wing if player ends up there without knowing how to swim
* [REVERSE] Can't open chests with 10.000 year old key if given
* [REVERSE] Can't use baron if given
* If player gives himself furious tornado at start, he can softlock the fog event
* [REVERSE] Display custom text

### Secondary

* [REVERSE] Intercept Life pickup and Max life pickup
* [REVERSE] Intercept animal dash, swim, dive
* Remove starting player inventory (at least blackjack and unequip it ? is that possible ?)
* Cache RAM to free some RetroArch exchange

### Optional

* [REVERSE] Find Tomba! position to be more accurate than camera position on location filters (very much not required)
* When grabbing the key of 100 Year Old Wise Man: The sprite stays there

## Notes

### Open chest and leave area

If the player does that without taking the item, the object flag is not set so the chest respawn exept if there are two items in it and at least one is grabbed. So every chest that contains two locations should be reset unless both locations are checked (happens only for cheese and charity wings probably)

## References

* https://docs.google.com/spreadsheets/d/1eImavd7tPoulWOoT0km9wRioWRnIiDSCMftlX3A6swk/edit?usp=sharing
* https://github.com/hansbonini/psx_tomba
