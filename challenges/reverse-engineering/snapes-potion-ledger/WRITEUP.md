
---
title: "Snape's Potion Ledger"
ctf: "Coders Cup"
date: 2026-10-25
category: reverse
difficulty: easy
flag_format: "ACM{p0t10n5_........}"
author: "Organizer"
---

# Snape's Potion Ledger

## Challenge description

Professor Snape's ledger tracks a cauldron essence and powdered moonstone in registers. Follow the potion arithmetic in `main` and determine the final 32-bit value in `EBX` after its final addition.

Submit the result as `ACM{p0t10n5_<eight lowercase hexadecimal digits>}`.

## Summary

This is a fixed-width arithmetic tracing challenge. Two 32-bit values are adjusted, then the second is added into the first twice. Arithmetic in 32-bit registers keeps only the low 32 bits after every operation.

**Difficulty:** Easy. **Enjoyability:** 6/10. It is a direct first assembly exercise that teaches register tracking and wraparound arithmetic.

## Solution

### Step 1: Read the arithmetic in `main`

The relevant instructions in the supplied executable are equivalent to:

```c
cauldron_essence = 0x00423874;
powdered_moonstone = 0x00236874;

powdered_moonstone -= 0xdeadbeef;
cauldron_essence += 0xbabeb00b;

cauldron_essence += powdered_moonstone;
cauldron_essence += powdered_moonstone;
```

`cauldron_essence` is intentionally bound to `EBX`, and `powdered_moonstone` is bound to `R12D`. The compiler may use `EAX` as temporary storage, then assign the final result back to `EBX`. The player objective is the value after the final assignment created by the final addition, before the function epilogue restores saved registers.

The negative-looking subtraction wraps modulo `2^32`:

| Operation | Low 32-bit result |
|---|---|
| Initial cauldron essence | `0x00423874` |
| Initial powdered moonstone | `0x00236874` |
| Moonstone after subtraction | `0x2175a985` |
| Essence after first adjustment | `0xbb00e87f` |
| Essence after first moonstone addition | `0xdc769204` |
| Essence after final moonstone addition | `0xfdec3b89` |

### Step 2: Reproduce the calculation

The complete solver is included as `solve.py`:

```python
mask = 0xffffffff
essence = 0x00423874
moonstone = 0x00236874

moonstone = (moonstone - 0xdeadbeef) & mask
essence = (essence + 0xbabeb00b) & mask
essence = (essence + moonstone) & mask
essence = (essence + moonstone) & mask

print(f"ACM{{p0t10n5_{essence:08x}}}")
```

Output:

```text
ACM{p0t10n5_fdec3b89}
```

The organizer verifier independently stops the actual binary in GDB immediately after the final compiler assignment to `EBX` and observes `0xfdec3b89`.

## Flag

```text
ACM{p0t10n5_fdec3b89}
```

## Organizer notes

- Keep the current `uint32_t` types and `-O0` build. The arithmetic now has defined 32-bit wraparound semantics.
- The named register bindings make the stated `EBX` objective stable for the current x86-64 GCC build. Confirm the distributed binary with `make verify` after a toolchain change.
- A suitable first hint is: “Track only the lowest 32 bits after each operation.”

## Intended flag

```text
ACM{p0t10n5_fdec3b89}
```
