.BASE 0x800297b0            # Where this code is located

# Stack is organized as:
# STACK_SIZE: 1
# STACK: Up to 64 items should be ok (0x8000B400 to 0x8000B800)
# Item Structure is defined as:
# * CAMERA_H: 2
# * CAMERA_V: 2
# * ITEM_ID: 1
# * AREA: 1
# * SECTION: 1
# * unused: 1 (for byte alignement/optimization)
# Used size: 7 (8 counting unused)

    # Initialize registers
    lui   $t0, 0x8001       # Load upper 16-bit address for counters
    lbu   $t1, 0xB3F0($t0)  # $t1 = STACK counter value (from 0x8000B3F0)

LOOP:
    beq   $s1, $zero, DONE  # If count ($s1) == 0, exit loop
    nop                     # Branch delay slot

    # Calculate current stack write destination
    addi  $t2, $t0, 0xB400  # $t2 = Base STACK address (0x8000B400)
    sll   $t4, $t1, 3       # Multiply stack by 8 (structure size)
    addu  $t2, $t2, $t4     # $t2 = 0x8000B400 + current stack counter

    # Fetch camera informations
    lui   $t3, 0x1F80       # Its on the scratch pad
    lhu   $t4, 0x00EE($t3)  # Load HORIZONTAL position (DELAY SLOT as its RAM operation)

    lhu   $t5, 0x00F2($t3)  # Load VERTICAL position (DELAY SLOT as its RAM operation), also fills delay slots of horizontal position loading

    sh    $t4, 0x00($t2)
    sh    $t5, 0x02($t2)
    sb    $s0, 0x04($t2)    # Store Item ID ($s0) into STACK memory
    
    # Fetch Area/Section informations
    lui   $t3, 0x800A       # Go one higher as index below will be interpreted as negative
    lbu   $t4, 0xBCC8($t3)  # Load AREA (DELAY SLOT as its RAM operation)
    
    lbu   $t5, 0xBCCA($t3)  # Load SECTION (DELAY SLOT as its RAM operation), also fills delay slots of previous loading
    
    sb    $t4, 0x05($t2)    # Store AREA
    sb    $t5, 0x06($t2)    # Store SECTION
    # Last byte is unused, its more efficient to use 8 byte so we can shift left 3 times to index it

    # Store Item ID and update tracking
    addi  $t1, $t1, 1       # Increment STACK counter value
    addi  $s1, $s1, -1      # Decrement loop counter (Count)

    j     LOOP              # Repeat loop
    nop                     # Branch delay slot

DONE:
    # Save the updated STACK counter back to memory
    sb    $t1, 0xB3F0($t0)  # Update memory at 0x8000B3F0

    # RETURN
    lw         ra,0x20(sp)
    lw         s1,0x1C(sp)
    lw         s0,0x18(sp)
    addiu      sp,sp,0x28
    jr         ra
    nop
