# Tomba! Archipelago developement

# DONE

* Fix softlock for bitting plant flower when grabbing fruit instead of hitting it
-> SET 09C3E3 TO 01 (02 = Grabbed)
* Disable animation of falling apple when Tomba! attacks it in Area0 section1
-> SET SECTION FLAG for that BLUE APPLE to 1 preventing it to be grabbed aswell
* How does the game handle crystal balls ? (code already identified, not given until three acquired ?)
-> Good enough
* Prevent barrel to break in Wobbly Wharf
-> Unset the barrel flag while event is not discovered
* Handle refresh with a timer per function ? Or increase tick for game ?
-> Handler class: Maybe make that more generic...
* Refactor game Events into Locations
-> Sounds good
* Remove virtual cleared game event and check logics (do we need started ?)
-> Both are real location now

# TODO

* Pre-patch ROM before playing
* Find a way to use tornado without being forced to clear mailbox: even with locked placement: load state with tornado = tornado in inventory before opening mailbox...
  * TODO: Force mailbox flag to 1 if tornado already given
* Can't grab the key of 100 Year Old Wise Man: The sprite stays there, remove it
* Intercept Life pickup and Max life pickup
* Can't give flower seeds to the dwarf until they are picked up: Find how to set that manualy/remove limitation
-> Save 3
* Cache RAM to free some RetroArch exchange
* Golden bowl cant be grabbed: forbidden item
* BUG: Race condition: Save area and section when item received (PATCH)
* BUG: Unable to assign Charity wings in mushroom forest chests to correct location: use camera position ? (PATCH)
* Fix items that can fall out of the map ? Mark as filler ?
* Force clear the TAKE OUT event if yan's already found (Hide and Go Seek cleared) and/or prevent usage of Yan lunch box
* Prevent player out of lunch box for the event in hidden village
* Take out reward cheese: rule the 5 locations for it to happen ?
* Possible softlock if has fuel bar and goes to the mermaid singing rock without knowing how to swim (spawn with baron ?) as only exit is masakari river
* Remove starting player inventory (at least blackjack and unequip it ? is that possible ?)
* Can't open chests with 10.000 year old key if given
* Can't use baron if given


# Reverse engineering stuff

Don't forget endianness: it's big endian on 4 bytes (32 bits): So each 4 bytes is reversed if human reading

## Finding give item method

Upon research for the inventory size address in Ghidra, this code is given:
```
                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined FUN_80029788()
                               assume gp = 0x80097fa8
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     800297ac(W), 
                                                                                                   8002992c(R)  
             undefined4        Stack[-0xc]:4  local_c                                 XREF[2]:     80029794(W), 
                                                                                                   80029930(R)  
             undefined4        Stack[-0x10]:4 local_10                                XREF[2]:     8002978c(W), 
                                                                                                   80029934(R)  
                             FUN_80029788                                    XREF[20]:    FUN_8003e408:8003ed1c(c), 
                                                                                          800400f8(c), 800403fc(c), 
                                                                                          8004048c(c), 8004057c(c), 
                                                                                          800405e0(c), 80040644(c), 
                                                                                          80040844(c), 80040974(c), 
                                                                                          800409e4(c), 80040acc(c), 
                                                                                          80040b4c(c), 80040be0(c), 
                                                                                          80040c44(c), 80040dd8(c), 
                                                                                          80040e94(c), 80040eec(c), 
                                                                                          80040f50(c), 80040ffc(c), 
                                                                                          80041128(c)  
        80029788 d8 ff bd 27     addiu      sp,sp,-0x28
        8002978c 18 00 b0 af     sw         s0,local_10(sp)
        80029790 21 80 80 00     move       s0,a0
        80029794 1c 00 b1 af     sw         s1,local_c(sp)
        80029798 21 88 a0 00     move       s1,a1
        8002979c 08 80 03 3c     lui        v1,0x8008
        800297a0 b8 c2 63 90     lbu        v1,-0x3d48(v1)=>DAT_8007c2b8
        800297a4 ff 00 02 24     li         v0,0xff
        800297a8 1a 00 62 10     beq        v1,v0,LAB_80029814
        800297ac 20 00 bf af     _sw        ra,local_8(sp)
        800297b0 ff 00 07 24     li         a3,0xff
        800297b4 08 80 04 3c     lui        a0,0x8008
        800297b8 b8 c2 84 24     addiu      a0,a0,-0x3d48
        800297bc 21 28 00 00     clear      a1
        800297c0 00 00 82 90     lbu        v0,0x0(a0)=>DAT_8007c2b8
                             LAB_800297c4                                    XREF[1]:     8002980c(j)  
        800297c4 00 00 00 00     nop
        800297c8 0d 00 50 14     bne        v0,s0,LAB_80029800
        800297cc 00 00 00 00     _nop
        800297d0 08 80 01 3c     lui        at,0x8008
        800297d4 21 08 25 00     addu       at,at,a1
        800297d8 b9 c2 22 90     lbu        v0,-0x3d47(at)=>DAT_8007c2b9                     = 63h
        800297dc 0a 80 01 3c     lui        at,0x800a
        800297e0 21 08 30 00     addu       at,at,s0
        800297e4 0c c4 23 90     lbu        v1,-0x3bf4(at)=>DAT_8009c40c                     = ??
        800297e8 00 00 00 00     nop
        800297ec 2b 10 62 00     sltu       v0,v1,v0
        800297f0 04 00 40 14     bne        v0,zero,LAB_80029804
        800297f4 02 00 84 24     _addiu     a0,a0,0x2
        800297f8 4b a6 00 08     j          LAB_8002992c
        800297fc 21 10 60 00     _move      v0,v1
                             LAB_80029800                                    XREF[1]:     800297c8(j)  
        80029800 02 00 84 24     addiu      a0,a0,0x2
                             LAB_80029804                                    XREF[1]:     800297f0(j)  
        80029804 00 00 82 90     lbu        v0,0x0(a0)=>DAT_8007c2ba                         = 03h
                                                                                             = 07h
        80029808 00 00 00 00     nop
        8002980c ed ff 47 14     bne        v0,a3,LAB_800297c4
        80029810 02 00 a5 24     _addiu     a1,a1,0x2
                             LAB_80029814                                    XREF[1]:     800297a8(j)  
        80029814 03 00 c0 10     beq        a2,zero,LAB_80029824
        80029818 21 20 00 02     _move      a0,s0
        8002981c 49 c4 00 0c     jal        FUN_80031124                                     undefined FUN_80031124()
        80029820 21 28 00 00     _clear     a1
                             LAB_80029824                                    XREF[1]:     80029814(j)  
        80029824 0a 80 02 3c     lui        v0,0x800a
        80029828 0c c6 42 94     lhu        v0,-0x39f4(v0)=>DAT_8009c60c                     = ??
        8002982c 00 00 00 00     nop
        80029830 1b 00 40 18     blez       v0,LAB_800298a0
        80029834 21 18 00 00     _clear     v1
                             LAB_80029838                                    XREF[1]:     80029890(j)  
        80029838 0a 80 01 3c     lui        at,0x800a
        8002983c 21 08 23 00     addu       at,at,v1
        80029840 0c c5 22 90     lbu        v0,-0x3af4(at)=>DAT_8009c50c                     = ??
        80029844 00 00 00 00     nop
        80029848 0d 00 50 14     bne        v0,s0,LAB_80029880
        8002984c 01 00 63 24     _addiu     v1,v1,0x1
        80029850 0a 80 01 3c     lui        at,0x800a
        80029854 21 08 30 00     addu       at,at,s0
        80029858 0c c4 22 90     lbu        v0,-0x3bf4(at)=>DAT_8009c40c                     = ??
        8002985c 00 00 00 00     nop
        80029860 21 10 51 00     addu       v0,v0,s1
        80029864 0a 80 01 3c     lui        at,0x800a
        80029868 21 08 30 00     addu       at,at,s0
        8002986c 0c c4 22 a0     sb         v0,-0x3bf4(at)=>DAT_8009c40c                     = ??
        80029870 fa 7f 00 0c     jal        FUN_8001ffe8                                     undefined FUN_8001ffe8()
        80029874 0a 00 04 24     _li        a0,0xa
        80029878 48 a6 00 08     j          LAB_80029920
        8002987c 00 00 00 00     _nop
                             LAB_80029880                                    XREF[1]:     80029848(j)  
        80029880 0a 80 02 3c     lui        v0,0x800a
        80029884 0c c6 42 94     lhu        v0,-0x39f4(v0)=>DAT_8009c60c                     = ??
        80029888 00 00 00 00     nop
        8002988c 2a 10 62 00     slt        v0,v1,v0
        80029890 e9 ff 40 14     bne        v0,zero,LAB_80029838
        80029894 00 00 00 00     _nop
        80029898 0a 80 02 3c     lui        v0,0x800a
        8002989c 0c c6 42 94     lhu        v0,-0x39f4(v0)=>DAT_8009c60c                     = ??
                             LAB_800298a0                                    XREF[1]:     80029830(j)  
        800298a0 00 00 00 00     nop
        800298a4 ff ff 43 24     addiu      v1,v0,-0x1
        800298a8 0a 00 60 04     bltz       v1,LAB_800298d4
        800298ac 00 00 00 00     _nop
                             LAB_800298b0                                    XREF[1]:     800298cc(j)  
        800298b0 0a 80 01 3c     lui        at,0x800a
        800298b4 21 08 23 00     addu       at,at,v1
        800298b8 0c c5 22 90     lbu        v0,-0x3af4(at)=>DAT_8009c50b                     = ??
        800298bc 0a 80 01 3c     lui        at,0x800a
        800298c0 21 08 23 00     addu       at,at,v1
        800298c4 0d c5 22 a0     sb         v0,-0x3af3(at)=>DAT_8009c50c                     = ??
        800298c8 ff ff 63 24     addiu      v1,v1,-0x1
        800298cc f8 ff 61 04     bgez       v1,LAB_800298b0
        800298d0 00 00 00 00     _nop
                             LAB_800298d4                                    XREF[1]:     800298a8(j)  
        800298d4 0a 80 01 3c     lui        at,0x800a
        800298d8 0c c5 30 a0     sb         s0,-0x3af4(at)=>DAT_8009c50c                     = ??
        800298dc 0a 80 01 3c     lui        at,0x800a
        800298e0 21 08 30 00     addu       at,at,s0
        800298e4 0c c4 31 a0     sb         s1,-0x3bf4(at)=>DAT_8009c40c                     = ??
        800298e8 0a 80 02 3c     lui        v0,0x800a
        800298ec 0c c6 42 94     lhu        v0,-0x39f4(v0)=>DAT_8009c60c                     = ??
        800298f0 00 00 00 00     nop
        800298f4 01 00 42 24     addiu      v0,v0,0x1
        800298f8 0a 80 01 3c     lui        at,0x800a
        800298fc 0c c6 22 a4     sh         v0,-0x39f4(at)=>DAT_8009c60c                     = ??
        80029900 fa 7f 00 0c     jal        FUN_8001ffe8                                     undefined FUN_8001ffe8()
        80029904 0a 00 04 24     _li        a0,0xa
        80029908 0a 80 02 3c     lui        v0,0x800a
        8002990c 0e c6 42 94     lhu        v0,-0x39f2(v0)=>DAT_8009c60e                     = ??
        80029910 00 00 00 00     nop
        80029914 00 80 42 34     ori        v0,v0,0x8000
        80029918 0a 80 01 3c     lui        at,0x800a
        8002991c 0e c6 22 a4     sh         v0,-0x39f2(at)=>DAT_8009c60e                     = ??
                             LAB_80029920                                    XREF[1]:     80029878(j)  
        80029920 0a 80 01 3c     lui        at,0x800a
        80029924 21 08 30 00     addu       at,at,s0
        80029928 0c c4 22 90     lbu        v0,-0x3bf4(at)=>DAT_8009c40c                     = ??
                             LAB_8002992c                                    XREF[1]:     800297f8(j)  
        8002992c 20 00 bf 8f     lw         ra,local_8(sp)
        80029930 1c 00 b1 8f     lw         s1,local_c(sp)
        80029934 18 00 b0 8f     lw         s0,local_10(sp)
        80029938 28 00 bd 27     addiu      sp,sp,0x28
        8002993c 08 00 e0 03     jr         ra
        80029940 00 00 00 00     _nop
```

AI Analysis suggests a match:
```
// Known Global Variables mapped from your data
unsigned short *inv_counter    = (unsigned short *)0x8009C60C;
unsigned short *ui_refresh_flag= (unsigned short *)0x8009C60E;
unsigned char  *inv_stack      = (unsigned char *)0x8009C50C;
unsigned char  *inv_quantities = (unsigned char *)0x8009C40C; // Tracks item count by ID

// Maximum item capacities table (Stored as ID, Max pairs, terminated by 0xFF)
unsigned char *max_capacity_table = (unsigned char *)0x8007C2B8; 

unsigned char give_item(unsigned int item_id, char quantity_to_add, int trigger_event) {
    
    // 1. MAXIMUM CAPACITY CHECK
    if (max_capacity_table[0] != 0xFF) {
        int i = 0;
        unsigned int checked_id = max_capacity_table[0];
        do {
            // If this item has a specific max cap, check if current quantity >= max cap
            if ((checked_id == item_id) && (max_capacity_table[i + 1] <= inv_quantities[item_id])) {
                return inv_quantities[item_id]; // Return current quantity, block acquisition
            }
            i += 2;
            checked_id = max_capacity_table[i];
        } while (checked_id != 0xFF);
    }

    // 2. TRIGGER OPTIONAL ACQUISITION CALL
    if (trigger_event != 0) {
        FUN_80031124(item_id, 0); // Likely shows "Obtained [Item]" pop-up text
    }

    // 3. CHECK IF PLAYER ALREADY OWNS THE ITEM (DUPLICATE CHECK)
    int stack_index = 0;
    if (*inv_counter != 0) {
        do {
            // If item already exists in the visual inventory list
            if (inv_stack[stack_index] == item_id) {
                inv_quantities[item_id] += quantity_to_add; // Increase owned counter
                FUN_8001ffe8(10);                           // Play pickup sound
                goto RETURN_QUANTITY;                       // Skip array shifting
            }
            stack_index++;
        } while (stack_index < (int)*inv_counter);
    }

    // 4. NEW ITEM LOGIC: SHIFT ARRAY RIGHT TO MAKE ROOM AT INDEX 0
    unsigned int uVar1 = (unsigned int)*inv_counter;
    while ((int)(uVar1 - 1) > -1) {
        inv_stack[uVar1] = inv_stack[uVar1 - 1]; // Ghidra offset math resolves to this
        uVar1--;
    }

    // 5. INSERT NEW ITEM AT FRONT & SET INITIAL QUANTITY
    inv_stack[0] = (unsigned char)item_id;
    inv_quantities[item_id] = quantity_to_add;
    *inv_counter = *inv_counter + 1; // Increment total inventory size

    // 6. REFRESH AUDIO AND GRAPHICS
    FUN_8001ffe8(10);                // Play menu sound effect
    *ui_refresh_flag |= 0x8000;      // Tell menu renderer to redraw screen

RETURN_QUANTITY:
    return inv_quantities[item_id];
}
```

## Show EVENT

This is called when picking up a Bitting Plant Flower (at the start when dropping the apple on the bitting plant)
```
                             LAB_8004083c                                    XREF[1]:     80040824(j)  
        8004083c 08 00 04 24     li         a0,0x8
        80040840 01 00 05 24     li         a1,0x1
        80040844 e2 a5 00 0c     jal        FUN_80029788_pickup_item                         undefined FUN_80029788_pickup_it
        80040848 01 00 06 24     _li        a2,0x1
        8004084c a9 00 04 24     li         a0,0xa9
        80040850 21 28 00 00     clear      a1
        80040854 88 78 00 0c     jal        FUN_8001e220                                     undefined FUN_8001e220()
        80040858 21 30 00 00     _clear     a2
        8004085c 0a 80 02 3c     lui        v0,0x800a
        80040860 c8 bc 42 94     lhu        v0,-0x4338(v0)=>DAT_8009bcc8                     = ??
        80040864 00 00 00 00     nop
        80040868 03 00 40 14     bne        v0,zero,LAB_80040878
        8004086c 02 00 02 24     _li        v0,0x2
        80040870 0a 80 01 3c     lui        at,0x800a
        80040874 e3 c3 22 a0     sb         v0,-0x3c1d(at)=>DAT_8009c3e3                     = ??
```

It adds the flower then calls FUN_8001e220

Which is:
```
                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined __stdcall FUN_8001e220_check_event(byte event_
                               assume gp = 0x80097fa8
             undefined         <UNASSIGNED>   <RETURN>
             byte              a0:1           event_id
             undefined         <UNASSIGNED>   param_2
             undefined         <UNASSIGNED>   param_3
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     8001e22c(W), 
                                                                                                   8001e304(R)  
             undefined4        Stack[-0xc]:4  local_c                                 XREF[2]:     8001e230(W), 
                                                                                                   8001e308(R)  
             undefined4        Stack[-0x10]:4 local_10                                XREF[2]:     8001e224(W), 
                                                                                                   8001e30c(R)  
                             FUN_8001e220_check_event                        XREF[11]:    8002ddb0(c), 80033dc4(c), 
                                                                                          80033df8(c), 80033e30(c), 
                                                                                          8004023c(c), 8004049c(c), 
                                                                                          80040854(c), 80040a8c(c), 
                                                                                          80040bb0(c), 80040d74(c), 
                                                                                          80040f8c(c)  
        8001e220 e0 ff bd 27     addiu      sp,sp,-0x20
        8001e224 10 00 b0 af     sw         s0,local_10(sp)
        8001e228 21 80 80 00     move       s0,event_id
        8001e22c 18 00 bf af     sw         ra,local_8(sp)
        8001e230 14 00 b1 af     sw         s1,local_c(sp)
        8001e234 0a 80 01 3c     lui        at,0x800a
        8001e238 21 08 30 00     addu       at,at,s0
        8001e23c 0c c1 23 90     lbu        v1,-0x3ef4(at)=>DAT_8009c10c                     = ??
        8001e240 00 00 00 00     nop
        8001e244 2c 00 60 14     bne        v1,zero,LAB_8001e2f8
        8001e248 21 88 c0 00     _move      s1,a2
        8001e24c 01 00 02 24     li         v0,0x1
        8001e250 0e 00 02 16     bne        s0,v0,LAB_8001e28c
        8001e254 01 00 62 24     _addiu     v0,v1,0x1
        8001e258 0a 80 02 3c     lui        v0,0x800a
        8001e25c c8 bc 42 8c     lw         v0,-0x4338(v0)=>DAT_8009bcc8                     = ??
        8001e260 00 00 00 00     nop
        8001e264 0c 00 40 14     bne        v0,zero,LAB_8001e298
        8001e268 00 00 00 00     _nop
        8001e26c 0a 80 02 3c     lui        v0,0x800a
        8001e270 0d c1 42 90     lbu        v0,-0x3ef3(v0)=>DAT_8009c10d                     = ??
        8001e274 00 00 00 00     nop
        8001e278 01 00 42 24     addiu      v0,v0,0x1
        8001e27c 0a 80 01 3c     lui        at,0x800a
        8001e280 0d c1 22 a0     sb         v0,-0x3ef3(at)=>DAT_8009c10d                     = ??
        8001e284 a6 78 00 08     j          LAB_8001e298
        8001e288 00 00 00 00     _nop
                             LAB_8001e28c                                    XREF[1]:     8001e250(j)  
        8001e28c 0a 80 01 3c     lui        at,0x800a
        8001e290 21 08 30 00     addu       at,at,s0
        8001e294 0c c1 22 a0     sb         v0,-0x3ef4(at)=>DAT_8009c10c                     = ??
                             LAB_8001e298                                    XREF[2]:     8001e264(j), 8001e284(j)  
        8001e298 07 80 01 3c     lui        at,0x8007
        8001e29c 21 08 30 00     addu       at,at,s0
        8001e2a0 40 75 22 90     lbu        v0,offset DAT_80077540(at)
        8001e2a4 00 00 00 00     nop
        8001e2a8 80 10 02 00     sll        v0,v0,0x2
        8001e2ac 07 80 01 3c     lui        at,0x8007
        8001e2b0 21 08 22 00     addu       at,at,v0
        8001e2b4 20 75 24 8c     lw         event_id,offset DAT_80077520(at)
        8001e2b8 52 a5 00 0c     jal        FUN_80029548                                     undefined FUN_80029548()
        8001e2bc 00 00 00 00     _nop
        8001e2c0 0a 00 02 24     li         v0,0xa
        8001e2c4 0c 00 02 12     beq        s0,v0,LAB_8001e2f8
        8001e2c8 21 28 00 00     _clear     a1
        8001e2cc 21 20 00 02     move       event_id,s0
        8001e2d0 3c 00 06 24     li         a2,0x3c
        8001e2d4 fb 78 00 0c     jal        FUN_8001e3ec                                     undefined FUN_8001e3ec()
        8001e2d8 21 38 20 02     _move      a3,s1
        8001e2dc 21 20 00 02     move       event_id,s0
        8001e2e0 36 7b 00 0c     jal        FUN_8001ecd8                                     undefined FUN_8001ecd8()
        8001e2e4 21 28 00 00     _clear     a1
        8001e2e8 fa 7f 00 0c     jal        FUN_8001ffe8                                     undefined FUN_8001ffe8()
        8001e2ec 2a 00 04 24     _li        event_id,0x2a
        8001e2f0 ec b8 00 0c     jal        FUN_8002e3b0                                     undefined FUN_8002e3b0()
        8001e2f4 21 20 00 00     _clear     event_id
                             LAB_8001e2f8                                    XREF[2]:     8001e244(j), 8001e2c4(j)  
        8001e2f8 0a 80 01 3c     lui        at,0x800a
        8001e2fc 21 08 30 00     addu       at,at,s0
        8001e300 0c c1 22 90     lbu        v0,-0x3ef4(at)=>DAT_8009c10c                     = ??
        8001e304 18 00 bf 8f     lw         ra,local_8(sp)
        8001e308 14 00 b1 8f     lw         s1,local_c(sp)
        8001e30c 10 00 b0 8f     lw         s0,local_10(sp)
        8001e310 20 00 bd 27     addiu      sp,sp,0x20
        8001e314 08 00 e0 03     jr         ra
        8001e318 00 00 00 00     _nop

```

```
// Globals mapped from assembly offsets
unsigned char  *event_flags    = (unsigned char *)0x8009C10C;
unsigned int   *trigger_status = (unsigned int *)0x8009BCC8;
unsigned char  *lut_indices    = (unsigned char *)0x80077540; // Lookup table indices
unsigned int   *pointer_table  = (unsigned int *)0x80077520;  // Table of data/string pointers

unsigned char check_and_trigger_event(unsigned char event_id, int param_2, int notification_type) {
    
    // 1. If event flag is already non-zero, skip activation entirely
    if (event_flags[event_id] != 0) {
        goto EXIT_SEQUENCE;
    }

    // 2. Special exception for Event ID 1
    if (event_id == 1) {
        if (*trigger_status == 0) {
            event_flags[1 + 1]++; // Increment sub-counter at 0x8009C10D
        }
        goto RUN_DISPATCHER;
    }

    // 3. Standard Event Activation: Set the flag to 1 (v0 contains 0x1 from line 8001e24c)
    event_flags[event_id] = 1;

RUN_DISPATCHER:
    // 4. Dynamic Data Lookup Table (LUT) Math
    // Reads an index, multiplies it by 4 (sll 2), and pulls a pointer
    unsigned char lut_index = lut_indices[event_id];
    unsigned int data_ptr = pointer_table[lut_index];
    
    // Execute primary event handler using the fetched data pointer as an argument
    FUN_80029548(data_ptr);

    // 5. Hardcoded Exclusion Check
    if (event_id == 10) { // 0x0A
        goto EXIT_SEQUENCE; // Event 10 skips the graphical text notifications below
    }

    // 6. Trigger On-Screen UI Banners and Visual Notifications
    FUN_8001e3ec(event_id, 0, 0x3C, notification_type); // Set up display timer/type (0x3C frames = 1 second)
    FUN_8001ecd8(event_id, 0);                         // Render string/layout to screen buffer
    FUN_8001ffe8(42);                                  // 0x2A - Play "Quest Unlocked / Event" sound effect
    FUN_8002e3b0(0);                                   // Refresh engine states

EXIT_SEQUENCE:
    return event_flags[event_id]; // Returns current state (0 = inactive, 1+ = active)
}
```

EVENT_FLAG_ADDRESS = 0x09C10C

Each byte = 1 event status
Status enum:
* 00: Not discovered
* 01: Discovered
* FF: Finished

0x09C1B4 - 0xA9

### Show pick up text

Setting the 4 bytes at address 0x02981C from `21 20 00 02` (MOVE a0, s0) to `07 00 04 24` (LI a0, 0x0007) where 0x07 is the item code of Charity Wings (can be anything) successfully trigger the Charity Wings acquired text upon item acquisition

## IRQ

```
                             **************************************************************
                             *                          FUNCTION                          *
                             **************************************************************
                               undefined startIntr()
                               assume gp = 0x80097fa8
             undefined         <UNASSIGNED>   <RETURN>
             undefined4        Stack[-0x4]:4  local_4                                 XREF[2]:     80067fcc(W), 
                                                                                                   80068084(R)  
             undefined4        Stack[-0x8]:4  local_8                                 XREF[2]:     80067fc0(W), 
                                                                                                   80068088(R)  
                             startIntr                                       XREF[2]:     ResetCallback:80067e3c(c), 
                                                                                          8009748c(*)  
        80067fbc e8 ff bd 27     addiu      sp,sp,-0x18
        80067fc0 10 00 b0 af     sw         s0,local_8(sp)
        80067fc4 09 80 10 3c     lui        s0,0x8009
        80067fc8 18 64 10 26     addiu      s0,s0,0x6418
        80067fcc 14 00 bf af     sw         ra,local_4(sp)
        80067fd0 00 00 02 96     lhu        v0,0x0(s0)=>DAT_80096418
        80067fd4 00 00 00 00     nop
        80067fd8 2a 00 40 14     bne        v0,zero,INTR_OBJ_260
        80067fdc 21 10 00 00     _clear     v0
        80067fe0 09 80 03 3c     lui        v1,0x8009
        80067fe4 a4 74 63 8c     lw         v1,offset ->I_STAT(v1)                           = 1f801070
        80067fe8 09 80 02 3c     lui        v0,0x8009
        80067fec a8 74 42 8c     lw         v0,offset ->I_MASK(v0)                           = 1f801074
        80067ff0 33 33 05 3c     lui        a1,0x3333
        80067ff4 00 00 40 a4     sh         zero,0x0(v0)=>I_MASK                             = ??
        80067ff8 00 00 42 94     lhu        v0,0x0(v0)=>I_MASK                               = ??
        80067ffc 33 33 a5 34     ori        a1,a1,0x3333
        80068000 00 00 62 a4     sh         v0,0x0(v1)=>I_STAT                               = ??
        80068004 09 80 02 3c     lui        v0,0x8009
        80068008 ac 74 42 8c     lw         v0,offset ->DMA_DPCR(v0)                         = 1f8010f0
        8006800c 21 20 00 02     move       a0=>DAT_80096418,s0
        80068010 00 00 45 ac     sw         a1,0x0(v0)=>DMA_DPCR                             = ??
        80068014 42 a1 01 0c     jal        memclr                                           undefined memclr()
        80068018 1a 04 05 24     _li        a1,0x41a
        8006801c 61 a1 01 0c     jal        setjmp                                           undefined setjmp()
        80068020 38 00 04 26     _addiu     a0=>DAT_80096450,s0,0x38
        80068024 03 00 40 10     beq        v0,zero,INTR_OBJ_210
        80068028 00 00 00 00     _nop
        8006802c 26 a0 01 0c     jal        trapIntr                                         undefined trapIntr()
        80068030 00 00 00 00     _nop
                             INTR_OBJ_210                                    XREF[1]:     80068024(j)  
        80068034 09 80 10 3c     lui        s0,0x8009
        80068038 54 64 10 26     addiu      s0,s0,0x6454
        8006803c fc ff 04 26     addiu      a0=>DAT_80096450,s0,-0x4
        80068040 dc 0f 02 26     addiu      v0,s0,0xfdc
        80068044 5d a1 01 0c     jal        HookEntryInt                                     undefined HookEntryInt()
        80068048 00 00 02 ae     _sw        v0=>DAT_80097430,0x0(s0)=>DAT_80096454
        8006804c 01 00 02 24     li         v0,0x1
        80068050 81 a1 01 0c     jal        startIntrVSync                                   undefined startIntrVSync()
        80068054 c4 ff 02 a6     _sh        v0,-0x3c(s0)=>DAT_80096418
        80068058 09 80 03 3c     lui        v1,0x8009
        8006805c a0 74 63 8c     lw         v1,offset PTR_PTR_800974a0(v1)                   = 80097480
        80068060 cb a1 01 0c     jal        startIntrDMA                                     undefined startIntrDMA()
        80068064 14 00 62 ac     _sw        v0,0x14(v1)=>DAT_80097494
        80068068 09 80 04 3c     lui        a0,0x8009
        8006806c a0 74 84 8c     lw         a0=>PTR_s_$Id:_intr.c,v_1.74_1996/12/04_07_800   = 800161f8
                                                                                             = 80097480
        80068070 4f a1 01 0c     jal        FUN_8006853c                                     undefined FUN_8006853c()
        80068074 04 00 82 ac     _sw        v0,0x4(a0)=>DAT_80097484
        80068078 0b 6d 01 0c     jal        FUN_8005b42c                                     undefined FUN_8005b42c()
        8006807c c4 ff 10 26     _addiu     s0,s0,-0x3c
        80068080 21 10 00 02     move       v0=>DAT_80096418,s0
                             INTR_OBJ_260                                    XREF[1]:     80067fd8(j)  
        80068084 14 00 bf 8f     lw         ra,local_4(sp)
        80068088 10 00 b0 8f     lw         s0,local_8(sp)
        8006808c 18 00 bd 27     addiu      sp,sp,0x18
        80068090 08 00 e0 03     jr         ra
        80068094 00 00 00 00     _nop

```

# Patch

* Put player name somewhere

* Rewrite give_item:
** Dummy function that stores a new stack of items ID in the free-ed space where the function was (<COUNT> <stack 0> <stack 1> ...)
*** Increment count
*** Write item at stack end

* Find how to change displayed text for acquired popup
** Patch relevant texts from Archipelago

## Play arbitrary SFX at 0x8000B140
Suggested:
```
Address   Hex Code            MIPS Assembly          Description
--------------------------------------------------------------------------------------
; --- 1. PROLOGUE: Secure the Register State ---
8000B150  e0 ff bd 27         addiu   sp,sp,-0x20    ; Allocate 32 bytes on stack
8000B154  1c 00 bf af         sw      ra,0x1C(sp)    ; Save original Return Address (Parent caller)
8000B158  18 00 b0 af         sw      s0,0x18(sp)    ; Save s0
8000B15C  14 00 84 af         sw      a0,0x14(sp)    ; Save a0
8000B160  10 00 42 af         sw      v0,0x10(sp)    ; Save v0

; --- 2. LOAD DATA FROM YOUR TARGET ADDRESS ---
8000B164  00 80 10 3c         lui     s0,0x800A      ; Load upper 16 bits of target address
8000B168  40 B1 04 92         lbu     a0,0x0000(s0)  ; !! REPLACE 0xB140 with lower 16 bits !!
                                                     ; (a0 now holds your custom SFX byte ID)

; --- 3. NULL/ZERO VALIDATION CHECK ---
8000B16C  05 00 80 10         beq     a0,zero,CLEANUP; If a0 == 0, skip to cleanup and exit
8000B170  00 00 00 00         _nop                   ; Delay slot for the branch conditional

; --- 4. CLEAR THE VALUE AT THE ADDRESS (SET TO NULL) ---
8000B174  40 B1 00 a0         sb      zero,0x0000(s0); !! REPLACE 0xB140 with same lower 16 bits !!
                                                     ; Overwrites target address with 0 immediately

; --- 5. TRIGGER SOUND ENGINE PLAYBACK ---
8000B178  fa 7f 00 0c         jal     F_PLAY_SFX     ; Jump and Link directly to sound trigger
8000B17C  00 00 00 00         _nop                   ; Delay slot for the audio engine branch

; --- 6. EPILOGUE: Restore Register State ---
                             CLEANUP                 XREF: 8000B16C(j)
8000B180  10 00 42 8f         lw      v0,0x10(sp)    ; Restore original v0
8000B184  14 00 84 8f         lw      a0,0x14(sp)    ; Restore original a0
8000B188  18 00 b0 8f         lw      s0,0x18(sp)    ; Restore original s0
8000B18C  1c 00 bf 8f         lw      ra,0x1C(sp)    ; Restore original Return Address
8000B190  20 00 bd 27         addiu   sp,sp,0x20     ; Free stack allocation space

; --- 7. SAFE RETURN TO PARENT FRAME LOOP ---
8000B194  08 00 e0 03         jr      ra             ; Jump back to parent function seamlessly
8000B198  00 00 00 00         _nop                   ; Delay slot for safe return
```

Updated:
```
Address   Hex Code            MIPS Assembly          Description
--------------------------------------------------------------------------------------
; --- 1. PROLOGUE: Secure the Register State ---
8000B150  e0 ff bd 27         addiu   sp,sp,-0x20    ; Allocate 32 bytes on stack
8000B154  1c 00 bf af         sw      ra,0x1C(sp)    ; Save original Return Address (Parent caller)
8000B158  18 00 b0 af         sw      s0,0x18(sp)    ; Save s0
8000B15C  14 00 84 af         sw      a0,0x14(sp)    ; Save a0
8000B160  10 00 42 af         sw      v0,0x10(sp)    ; Save v0


; --- 2. LOAD DATA FROM YOUR TARGET ADDRESS ---
xxxxxxxx  01 80 10 3C         lui     s0,0x8001      ; Load upper 16 bits of target address
xxxxxxxx  40 B1 10 26         addiu   s0,s0,-0x4318  ; Substract from S0
xxxxxxxx  00 00 04 92         lbu     a0,0x0(s0)     ; load value from S0 into A0


; --- 3. NULL/ZERO VALIDATION CHECK ---
8000B170  04 00 80 10         beq     a0,zero,AFTER_SFX; If a0 == 0, skip to cleanup and exit                      CHANGEME ON CODE CHANGE
8000B174  00 00 00 00         _nop                   ; Delay slot for the branch conditional


; --- 4. CLEAR THE VALUE AT THE ADDRESS (SET TO NULL) ---
8000B178  00 00 00 A2         sb      zero,0x0000(s0); Clear byte at $S0

; --- 5. TRIGGER SOUND ENGINE PLAYBACK ---
8000B17C  fa 7f 00 0c         jal     F_PLAY_SFX     ; Jump and Link directly to sound trigger
8000B180  00 00 00 00         _nop                   ; Delay slot for the audio engine branch

; --- SEE IF OBTAINED ITEM STACK SHOULD BE CLEARED
; S0 = command address 
; A0 = command value
; A1 = temp var (masked command)

                             AFTER_SFX                
; ----- LOAD reset COMMAND 
8000B184  01 80 04 3C         lui     a0,0x8001      ; Load upper 16 bits of target address
8000B188  41 B1 84 24         addiu   a0,a0,-0xxxxx  ; Substract from S0
8000B18C  00 00 84 90         lbu     a0,0x0(a0)     ; load value from S0 into A0
          00 00 05 24         addiu   a1,zero,0x00   ; clear A1
8000B190  01 00 85 30         andi    a1,a0,0x01     ; Apply mask 01

; ------ SKIP RESET if not commanded to reset
8000B194  05 00 a0 10         beq a1,$zero, CLEANUP  ; branch if 0
8000B198  00 00 00 00         nop                    ; Delay slot

8000B19C  01 80 10 3C         lui     s0,0x8001      ; Load upper 16 bits of target address
8000B1A0  00 B4 10 A2         sb $zero, 0xB400($s0)   Wipe stack counter [1]

8000B1A4  FE 00 84 30         andi $a0, $a0, 0xFE     Clear bit 0 [1]
8000B1A8  41 B1 10 A2         sb $a0, 0xB141($s0)     RESET COMMAND



; --- 6. EPILOGUE: Restore Register State ---
                             CLEANUP                 XREF: 8000B16C(j)
8000B1AC  10 00 42 8f         lw      v0,0x10(sp)    ; Restore original v0
8000B1B0  14 00 84 8f         lw      a0,0x14(sp)    ; Restore original a0
8000B1B4  18 00 b0 8f         lw      s0,0x18(sp)    ; Restore original s0
8000B1B8  1c 00 bf 8f         lw      ra,0x1C(sp)    ; Restore original Return Address
8000B1BC  20 00 bd 27         addiu   sp,sp,0x20     ; Free stack allocation space

; --- 7. SAFE RETURN TO PARENT FRAME LOOP ---
8000B1C0  08 00 e0 03         jr      ra             ; Jump back to parent function seamlessly
8000B1C4  00 00 00 00         _nop                   ; Delay slot for safe return
```

* Using lives counter:
XX XX = 0A 80
YY YY = E8 BC

* Using 0x8000B140
XX XX = 01 80 (0x8001)
YY YY = 40 B1 (0xB140)


#### Patch COMMAND and SFX
Final code: (read value at 0x8000B140 and play SFX) (spam with 0x32 to fart eh eh)

Start: ```E0FFBD271C00BFAF1800B0AF1400A4AF1000A2AF```
End: ```1000A28F1400A48F1800B08F1C00BF8F2000BD270800E00300000000```

Patch at 0x8000B150
```
DCFFBD272000BFAF1C00B0AF1800A5AF1400A4AF1000A2AF0180103C40B11026000004920400801000000000000000A2FA7F000C000000000180043C41B184240000849000000524010085300500A010000000000180103C00B410A2FE00843041B110A21000428F1400848F1800A58F1C00B08F2000BF8F2400BD270800E00300000000
```
Hook at 0x8001E110 (backward jump x4 for word size) : ORIGINAL: 0800E003
```
542C0008
```


## Patch of receive_item

The original receive_item method sits at 0x80029788 but we keep initialization and start patch at 0x800297b0

S0: Item ID
S1: Count

PATH adress: B200
STACK counter: B400
STACK: B401

T0 = base adress
T1 = VAL stack size value
T2 = PTR current stack free cell

```
# Initialize registers
0x800297B0      01 80 08 3C         lui   $t0, 0x8001       # Load upper 16-bit address for counters
0x800297B4      00 B4 09 91         lbu   $t1, 0xB400($t0)  # $t1 = STACK counter value (from 0x8000B400)

LOOP:
0x800297B8      08 00 20 12         beq   $s1, $zero, DONE  # If count ($s1) == 0, exit loop
0x800297BC      00 00 00 00         nop                     # Branch delay slot

# Calculate current stack write destination
0x800297C0      01 B4 0A 21         addi  $t2, $t0, 0x0401  # $t2 = Base STACK address (0x8000B401)
0x800297C4      21 50 49 01         addu  $t2, $t2, $t1     # $t2 = 0x8000B401 + current stack counter

# Store Item ID and update tracking
0x800297C8      00 00 50 A1         sb    $s0, 0($t2)       # Store Item ID ($s0) into STACK memory
0x800297CC      01 00 29 21         addi  $t1, $t1, 1       # Increment STACK counter value
0x800297D0      FF FF 31 22         addi  $s1, $s1, -1      # Decrement loop counter (Count)

0x800297D4      EE A5 00 08         j     LOOP              # Repeat loop
0x800297D8      00 00 00 00         nop                     # Branch delay slot

DONE:
# Save the updated STACK counter back to memory
0x800297DC      00 B4 09 A1         sb    $t1, 0xB400($t0)  # Update memory at 0x8000B400

# RETURN
0x8002992c      20 00 bf 8f         lw         ra,local_8(sp)
0x80029930      1c 00 b1 8f         lw         s1,local_c(sp)
0x80029934      18 00 b0 8f         lw         s0,local_10(sp)
0x80029938      28 00 bd 27         addiu      sp,sp,0x28
0x8002993c      08 00 e0 03         jr         ra
0x80029940      00 00 00 00         _nop


```

PATCH is: at 0x800297b0
ORIGINAL: FF0007240880043CB8C284242128000000008290000000000D005014000000000880013C21082500B9C222900A80013C210830000CC42390000000002B1062000400401402008424
```
0180083C00B40991080020120000000001B40A2121504901000050A101002921FFFF3122EEA500080000000000B409A12000BF8F1C00B18F1800B08F2800BD270800E00300000000
```

No hook needed here



# SFX codes

* 00: None
* 01: None ?
* 0A: Item acquired
* 1A: Strange bell (low ?)
* 1F: Hurt (oya)
* 20: Laugh (mushroom)
* 22: Hola (?)
* 25: Cry (mushroom)
* 2A: Bell ring: Event started
* 32: Fart
* 3A: Piou (bird chip)
* FF: None

# State
There is a context pointer at 0x1f8001d4 but the address dont match (in my tests it points to 0x801FD950) but it should point to 0x801FD800 as the actual state (which i can modify an trigger game over/try again screen) is at 0x801FD84E
* 4E is the offset to state variable
* 4C is some kind of frame count/cleanup variable (?)

So a delta of 0x0150 exists somewhere ? (or 0x8150 for negative representation ?)


# Display TEXT

F_DISPLAY_PICKUP_TEXT uses:
UI selector:
* 0x14: One Up,
* 0x0C: Key progression item <- Capacity acquired
STRING ENTRY:
* 0x03: One up and progression

Display:
```
03000524
14000424
49C4000C
```

0x0C03: Animal Dash
0x1403: 1UP Acquired
0x1503: Vitality Max +1 Acquired


# DEBUG

Display value of A0 in adress S0:
```
0180103C          lui s0, 0x8001            ; S0 0x8000B100
00B11026          addui s0, 0xB100 (-)

000004AE          sw a0, 0(s0)              ; A0 shown at S0
000005AE          sw a1, 0(s0)              ; A0 shown at S0
```

# Init player

80017aa4 is the adress at which the default inventory is set: Size = 2

# Tornado/Mailbox/Fog Handling

SHOW_FOG = 0x09BCCE # Also determines if can use FURIOUS TORNADO OR NOT
* 02 = FOG not shown, cant use tornado
* 01 = FOG shown, can use tornado

MAILBOX_STATE = 0x09BCEC, setting it:
* 00 = Normal state, tornado still there
* 01 = Trigger tornado VFX where tomba grabs it and is moved

Using tornado prior to MAILBOX_STATE freeze the game.
