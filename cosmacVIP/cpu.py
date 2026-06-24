"""
    Most of docstrings has been copied from RCA CDP1802 Manual.

    You can get the manual and several more cool things at emudev.org
"""


class CDP1802:
    def __init__(self, memory) -> None:
        # Memory must be provided by dependency injection (byte-addressable)
        if memory is None:
            raise ValueError("memory must be provided (dependency injection)")

        # 16 general-purpose registers R0..RF (16-bit each)
        self.r = [0] * 16

        # Memory object (must support indexing)
        self.m = memory

        # Points to the register used as PC right now (index 0..15)
        self.p = 0x00

        # X register index (4-bit select)
        self.x = 0x00

        # Accumulator (8-bit)
        self.d = 0x00

        # Data Flag (used as carry)
        self.df = 0x00

        # Interrupt registers / temporaries
        self.i = 0x00
        self.ie = 0x00
        self.t = 0x00

    """
    Register Operations

    This group includes seven in-
    structions used to count and to move data between
    internal COSMAC registers.
    """
    
    def i1_INC(self, n: int):
        """
        INC: 0x1N
        
        When 1=1, the scratchpad register specified by the hex digit in N is incremented by 1.
        
        Note that FFFF+l=0000.
        """

        self.r[n] = (self.r[n] + 1) & 0xFFFF

        return self.r[n]        
    
    def i2_DEC(self, n: int):
        """
        DEC: 0x2N

        Decrement the scratchpad register specified by the hex digit in N by 1.
        Wraps around on underflow (0000 - 1 = FFFF).
        """

        self.r[n] = (self.r[n] - 1) & 0xFFFF
        return
    
    def i60_IRX(self):
        """
        IRX: 0x6X

        Increment the register selected by X. Commonly used to advance
        an index register. Wraps at 16 bits.
        """

        self.r[self.x] = (self.r[self.x] + 1) & 0xFFFF
        return

    def i8_GLO(self, n: int):
        """
        GLO: 0x8N

        Load the low-order byte (bits 7..0) of register Rn into the
        8-bit accumulator D.
        """

        self.d = self.r[n] & 0x00FF
        return
    
    def i9_GHI(self, n: int):
        """
        GHI: 0x9N

        Load the high-order byte (bits 15..8) of register Rn into the
        8-bit accumulator D.
        """

        self.d = (self.r[n] >> 8) & 0x00FF
        return
    
    def iA_PLO(self, n: int):
        """
        PLO: 0xAN

        Place the low-order byte of accumulator D into the low byte
        of register Rn; the high byte of Rn is preserved.
        """

        self.r[n] = ((self.r[n] & 0xFF00) | (self.d & 0xFF)) & 0xFFFF
        return

    def iB_PHI(self, n: int):
        """
        PHI: 0xBN

        Place the low-order byte of accumulator D into the high byte
        of register Rn (D becomes the high-order byte); the low byte
        of Rn is preserved.
        """

        self.r[n] = ((self.r[n] & 0x00FF) | ((self.d & 0xFF) << 8)) & 0xFFFF
        return
    
    """
    Memory Reference

    Memory Reference - Seven instructions are provided to load or store a memory byte.
    """

    def i0_LDN(self, n):
        """
        LDN: 0x0N

        Load D from memory at the 16-bit address contained in register Rn.
        Does not change Rn.
        """

        addr = self.r[n] & 0xFFFF
        self.d = self.m[addr] & 0xFF

        return
    
    def LDX(self):
        """
        LDX: (no operand)

        Load D from memory at the address contained in register R(X).
        Does not change R(X).
        """

        addr = self.r[self.x] & 0xFFFF
        self.d = self.m[addr] & 0xFF

        return
    
    def LDXA(self):
        """
        LDXA: (no operand)

        Load D from memory at the address contained in register R(X),
        then increment R(X). Useful for sequential parameter access.
        """

        addr = self.r[self.x] & 0xFFFF
        self.d = self.m[addr] & 0xFF
        self.r[self.x] = (self.r[self.x] + 1) & 0xFFFF
        return
    
    def STR(self, n):
        """
        STR: 0x3N (store)

        Store the low-order byte of accumulator D into memory at the
        16-bit address contained in register Rn.
        """

        addr = self.r[n] & 0xFFFF
        self.m[addr] = self.d & 0xFF
        return
    
    def STXD(self):
        """
        STXD: (no operand)

        Store D into memory at the address in R(X), then decrement R(X).
        Typically used for stack-like stores (store then decrement).
        """

        addr = self.r[self.x] & 0xFFFF
        self.m[addr] = self.d & 0xFF
        self.r[self.x] = (self.r[self.x] - 1) & 0xFFFF
        return

    def LDI(self):
        """
        LDI: (immediate)

        Load immediate byte into D from the memory location pointed to by
        the register selected by P (the current program counter register),
        then increment that PC register. Used to fetch immediate operands
        embedded in the program stream.
        """

        pc_addr = self.r[self.p] & 0xFFFF
        self.d = self.m[pc_addr] & 0xFF
        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF

        return

    """
    Logic operations

    Logic and bitwise operations
    """
    
    def OR(self):
        addr = self.r[self.x] & 0xFFFF
        self.d = (self.d | (self.m[addr] & 0xFF)) & 0xFF
    
    def ORI(self):
        pc_addr = self.r[self.p] & 0xFFFF
        self.d = (self.d | (self.m[pc_addr] & 0xFF)) & 0xFF
        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF
    
    def AND(self):
        addr = self.r[self.x] & 0xFFFF
        self.d = (self.d & (self.m[addr] & 0xFF)) & 0xFF

    def ANI(self):
        pc_addr = self.r[self.p] & 0xFFFF
        self.d = (self.d & (self.m[pc_addr] & 0xFF)) & 0xFF
        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF
        return

    def XOR(self):
        addr = self.r[self.x] & 0xFFFF
        self.d = (self.d ^ (self.m[addr] & 0xFF)) & 0xFF

    def XRI(self):
        pc_addr = self.r[self.p] & 0xFFFF
        self.d = (self.d ^ (self.m[pc_addr] & 0xFF)) & 0xFF
        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF

    def SHR(self):
        """
        SHR: 0xF8 (Shift Right)
        Shifts D one position to the right. 
        The original bit 0 is shifted into DF. Bit 7 receives a 0.
        """
        # Isolate bit 0 (rightmost bit) to become the new DF
        new_df = self.d & 1
        
        # Shift the accumulator to the right
        self.d = self.d >> 1
        
        # Ensure D stays within 8 bits (bit 7 becomes 0 automatically via '>>')
        self.d &= 0xFF
        
        # Update the Data Flag
        self.df = new_df
        return

    def SHRC(self):
        """
        SHRC: 0x78 (Shift Right through Carry)
        Shifts D one position to the right.
        The original bit 0 is shifted into DF. Bit 7 receives the OLD DF value.
        """
        # Isolate bit 0 to become the next DF
        next_df = self.d & 1
        
        # Shift the old DF value to the position of bit 7
        old_df_to_bit7 = self.df << 7
        
        # Shift D to the right and inject the old DF into bit 7
        self.d = (self.d >> 1) | old_df_to_bit7
        self.d &= 0xFF
        
        # Update DF with the bit that dropped out
        self.df = next_df
        return

    def SHL(self):
        """
        SHL: 0xFE (Shift Left)
        Shifts D one position to the left.
        The original bit 7 is shifted into DF. Bit 0 receives a 0.
        """
        # Isolate bit 7 (leftmost bit). If it is 128 (0x80), DF becomes 1, else 0
        new_df = 1 if (self.d & 0x80) else 0
        
        # Shift the accumulator to the left
        self.d = self.d << 1
        
        # Mask to 8 bits (the rightmost bit 0 automatically becomes 0)
        self.d &= 0xFF
        
        # Update the Data Flag
        self.df = new_df
        return

    def SHLC(self):
        """
        SHLC: 0x7E (Shift Left through Carry)

        Shifts D one position to the left. The original bit 7 is shifted
        into DF. Bit 0 receives the OLD DF value.
        """

        # Isolate bit 7 to become the next DF
        next_df = 1 if (self.d & 0x80) else 0

        # The old DF value will enter the position of bit 0
        old_df_to_bit0 = self.df & 1

        # Shift D to the left and inject the old DF into bit 0
        self.d = ((self.d << 1) | old_df_to_bit0) & 0xFF

        # Update DF with the bit that dropped out
        self.df = next_df
        return
    
    """
    Arithmetic operations
    """
    def iF4_ADD(self):
        pc_addr = self.r[self.x] & 0xFFFF
        value = self.m[pc_addr] & 0xFF
        total = self.d + value

        # Set Data Flag if carry out of 8 bits
        self.df = 1 if total > 0xFF else 0

        # Store low 8 bits into D
        self.d = total & 0xFF


        return

    def iFC_ADI(self):
        # Add immediate byte (from memory at PC) to accumulator D
        pc_addr = self.r[self.p] & 0xFFFF
        value = self.m[pc_addr] & 0xFF
        total = self.d + value

        # Set Data Flag if carry out of 8 bits
        self.df = 1 if total > 0xFF else 0

        # Store low 8 bits into D
        self.d = total & 0xFF

        # Increment PC register (mask to 16 bits)
        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF
 
        return
    
    def i7C_ADCI(self):
        addr = self.m[self.r[self.p]]
        sum = addr + self.d + self.df

        self.r[self.p] = (self.r[self.p] + 1) & 0xFFFF
        return

    