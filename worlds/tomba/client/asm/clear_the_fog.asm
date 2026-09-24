    # Patch the new game method to set Clear The Fog event to cleared
    ori    v0, zero, 0xFF        
    sb     v0, 0xC10E(at)
    sb     a1, 0xC42C(at)
