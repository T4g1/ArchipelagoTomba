.BASE 0x80040690            # Where this code is located

FUN_FOUND_ITEM:0x80029788

    # Save context
    addiu   $sp,$sp,-0x18
    sw      $ra,0x0C($sp)
    sw      $s1,0x08($sp)
    sw      $s0,0x04($sp)

    addu    $s0, $a0, $zero

    # Indicate the entity is consumed/deleted
    lbu     $v0, 0x04($s0)
    nop
    addiu   $v0, $v0, 0x01
    sb      $v0, 0x04($s0)

    # Load parameters
    ori     $a0, $zero, 0xFE
    ori     $a1, $zero, 0x01
    
    jal     FUN_FOUND_ITEM
    nop

    # # Restore context
    lw      $s0,0x04($sp)
    lw      $s1,0x08($sp)
    lw      $ra,0x0C($sp)
    addiu   $sp,$sp,0x18

    jr      $ra
    nop
