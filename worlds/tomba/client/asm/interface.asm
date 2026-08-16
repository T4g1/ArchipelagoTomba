.BASE 0x80000B150            # Where this code is located

FUN_PLAY_SFX:0x8001FFE8
FUN_PRINT_INFO_MESSAGE:0x80031124

# Kills the player
FUN_KILL_CALL:0x8001b0a4

# Display the event text
FUN_SET_EVENT_CALL:0x8001e118

LAB_PLAY_SFX:
    # Save context
    addiu   sp,sp,-0x28
    sw      ra,0x24(sp)
    sw      s1,0x20(sp)
    sw      s0,0x1c(sp)
    sw      a1,0x18(sp)
    sw      a0,0x14(sp)
    sw      v0,0x10(sp)

    # Check SFX command
    lui     s0,0x8001
    addiu   s0,s0,-0x4ec0
    lbu     a0,0x0(s0)      # Read DAT_SFX_COMMAND
    beq     a0,zero,LAB_POP_STACK
    nop

    # Play SFX
    sb      zero,0x0(s0)    # Reset DAT_SFX_COMMAND
    jal     FUN_PLAY_SFX
    nop

LAB_POP_STACK:
    # Check command
    lui     a0,0x8001
    addiu   a0,a0,-0x4ebf
    lbu     a0,0x0(a0)      # Read DAT_COMMAND
    addiu   a1,zero,0x0
    andi    a1,a0,0x1
    beq     a1,zero,LAB_SHOW_MESSAGE
    nop

    # Pop stack item
    # Algorithm: The item on top of the stack (at the index 0 so 0x8000 B400) is considered processed by Archipelago once this command is set
    # In that case, we pick the item on the bottom of the stack, save it on top and decrement the stack size
    # That way, item at position 0 is always the next to process, this is LIFO but this should be good enough

    # Register Usage:
    # s0 = Base register (0x80010000)
    # s1 = Stack size counter / Current index
    # t0 = Calculated memory offset for the bottom structure
    # t1 = Temporary storage for first 4 bytes of structure
    # t2 = Temporary storage for last 4 bytes of structure
    lui     s0, 0x8001          # s0 = 0x80010000

    # 1. LOAD STACK SIZE
    lbu     s1, 0xB3F0(s0)     # Load current stack size from 0x8000B3F0
    nop
    beq     s1, zero, LAB_EMPTY_STACK
    nop

    # 2. DECREMENT SIZE
    addi    s1, s1, -1          # Decrement size (s1 now holds the index of the bottom item)
    sb      s1, 0xB3F0(s0)      # Save the updated stack size back to 0x8000B3F0
    
    #beq     s1, zero, LAB_EMPTY_STACK
    #nop

    # 3. CALCULATE BOTTOM ITEM POINTER
    sll     t0, s1, 3           # Multiply index by 8 (shift left by 3) to get byte offset

    # 4. FETCH BOTTOM STRUCTURE (8 BYTES)
    # Base target is 0x8000B400
    # We add our calculated index offset (t0) to the memory load address
    addu    t0, t0, s0          # t0 = 0x80010000 + structural byte offset
    lw      t1, 0xB400(t0)      # Load first 4 bytes of bottom item
    lw      t2, 0xB404(t0)      # Load last 4 bytes of bottom item

    # 5. OVERWRITE TOP ITEM (INDEX 0)
    sw      t1, 0xB400(s0)      # Overwrite first 4 bytes at 0x8000B400
    sw      t2, 0xB404(s0)      # Overwrite last 4 bytes at 0x8000B400

LAB_EMPTY_STACK:
    andi    a0,a0,0xfe
    sb      a0,0xB141(s0)       # Reset DAT_COMMAND

LAB_SHOW_MESSAGE:
    # Check command
    lui     a0,0x8001
    addiu   a0,a0,-0x4ebf
    lbu     a0,0x0(a0)      # Read DAT_COMMAND
    addiu   a1,zero,0x0
    andi    a1,a0,0x2
    beq     a1,zero,LAB_KILL_METHOD
    nop

    # Load info message
    addiu   a0,zero,0x00
    addiu   a1,zero,0x00

    # Display message
    jal     FUN_PRINT_INFO_MESSAGE
    nop
    lui     s0,0x8001
    addiu   s0,s0,-0x4ebf
    lbu     a0,0x0(s0)      # Read DAT_COMMAND
    nop
    andi    a0,a0,0xfd
    nop
    sb      a0,0x0(s0)  # Reset DAT_COMMAND

LAB_KILL_METHOD:
    # Check command
    lui     a0,0x8001
    addiu   a0,a0,-0x4ebf
    lbu     a0,0x0(a0)      # Read DAT_COMMAND
    addiu   a1,zero,0x0
    andi    a1,a0,0x4
    beq     a1,zero,LAB_EVENT_DISPLAY_METHOD
    nop

    # Debug call
    addiu   a0,zero,0x01
    addiu   a1,zero,0x01
    addiu   a2,zero,0x01
    jal     FUN_KILL_CALL
    nop
    lui     s0,0x8001
    addiu   s0,s0,-0x4ebf
    lbu     a0,0x0(s0)      # Read DAT_COMMAND
    nop
    andi    a0,a0,0xfb
    nop
    sb      a0,0x0(s0)  # Reset DAT_COMMAND

LAB_EVENT_DISPLAY_METHOD:
    # Check command
    lui     a0,0x8001
    addiu   a0,a0,0xB141
    lbu     a0,0x0(a0)      # Read DAT_COMMAND
    addiu   a1,zero,0x0
    andi    a1,a0,0x8
    beq     a1,zero,LAB_RETURN
    nop

    # Load info message
    lui     t0,0x8001       # Read event ID
    addiu   t0,t0,0xB142
    lbu     a0,0x0(t0)      
    addiu   t1,t0,0x01      # Read event state (0: start, 1: cleared)
    lbu     a1,0x0(t1)      
    addiu   a2,zero,0x00
    jal     FUN_SET_EVENT_CALL
    nop
    lui     s0,0x8001
    addiu   s0,s0,-0x4ebf
    lbu     a0,0x0(s0)      # Read DAT_COMMAND
    nop
    andi    a0,a0,0xf7
    nop
    sb      a0,0x0(s0)  # Reset DAT_COMMAND

LAB_RETURN:
    # Restore context
    lw      v0,0x10(sp)
    lw      a0,0x14(sp)
    lw      a1,0x18(sp)
    lw      s0,0x1c(sp)
    lw      s1,0x20(sp)
    lw      ra,0x24(sp)
    addiu   sp,sp,0x28

    # Return to caller
    jr      ra
    nop
