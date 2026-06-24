# Cosmac VIP

fronts:

- https://emudev.org/system_resources
- https://bitsavers.trailing-edge.com/components/rca/cosmac/MPM-201A_User_Manual_for_the_CDP1802_COSMAC_Microprocessor_1976.pdf
- https://bitsavers.org/components/rca/cosmac/COSMAC_VIP_Instruction_Manual_1978.pdf

## CPU (RCA 1802)

- Has 16 registers of 16 bits each, from R0 to RF.

- The CPU does not have a dedicated Program Counter register.

- Instead, the 4-bit register P selects which scratchpad register
  (R0-RF) acts as the Program Counter.

Example:

```
R1 = 0x0300
P  = 0x1
```

In this case, R1 is being used as the Program Counter.

The next instruction will be fetched from address 0x0300.

### Important

The Program Counter is not copied from R1.

R1 itself becomes the Program Counter.

When an instruction is fetched:

R1 = R1 + 1

Example:

Before fetch:

```
R1 = 0x0300
P  = 0x1
```

Fetch opcode at 0x0300

After fetch:

```
R1 = 0x0301
```

Conclusion: R1 will be incremented right like any PC would be.

