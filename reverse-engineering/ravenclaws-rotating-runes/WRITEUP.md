
---
title: "Ravenclaw's Rotating Runes"
ctf: "Coders Cup"
date: 2026-10-25
category: reverse
difficulty: medium
flag_format: "ACM{r4v3ncl4w_........}"
author: "Organizer"
---

# Ravenclaw's Rotating Runes

## Challenge description

An ancient Ravenclaw rune is masked, turned, and combined into a final spell value. Follow the calculation in `main` and determine the 32-bit value in `EAX` produced by the final assignment.

Submit the result as `ACM{r4v3ncl4w_<eight lowercase hexadecimal digits>}`.

## Summary

This challenge combines a 64-bit mask, a 64-bit rotate-left, 32-bit truncation, a signed 16-bit value, and bitwise operations. The result of the final assignment is the required rune value.

**Difficulty:** Medium for this beginner track. **Enjoyability:** 7/10. The rotate and sign extension give it a satisfying step up from simple arithmetic without adding unrelated obfuscation.

## Solution

### Step 1: Follow the 64-bit rune transformation

The program begins with:

```text
ancient_rune = 0xdeadbeefcafefeed
masked_rune  = ancient_rune AND 0xff08f37f4167f901
turned_rune  = ROL64(masked_rune, 6)
```

The intermediate values are:

| Value | Result |
|---|---|
| `ancient_rune` | `0xdeadbeefcafefeed` |
| `masked_rune` | `0xde08b26f4066f801` |
| `turned_rune` | `0x822c9bd019be0077` |

`rol r15, 6` is a rotate, not a shift. The six high bits that leave the left side reappear at the low end. A plain left shift gives a different result.

### Step 2: Account for truncation and sign extension

The final C expression is grouped as:

```c
final_rune = (uint32_t)turned_rune |
             (first_fragment & (second_fragment + (int16_t)ancient_rune));
```

The low 16 bits of `ancient_rune` are `0xfeed`. Interpreted as signed 16-bit, that is `-275`, rather than positive `65261`.

| Value | Result |
|---|---|
| `first_fragment = low32(ancient_rune XOR turned_rune)` | `0xd340fe9a` |
| `second_fragment = low32(masked_rune)` | `0x4066f801` |
| `(int16_t)ancient_rune` | `-275` |
| `second_fragment - 275` | `0x4066f6ee` |
| `first_fragment AND previous value` | `0x4040f68a` |
| `low32(turned_rune)` | `0x19be0077` |
| Final OR | `0x59fef6ff` |

All of the final arithmetic uses 32-bit values, so the solver masks results to 32 bits.

### Step 3: Reproduce the final assignment

The complete solver is `solve.py`:

```python
mask32 = 0xffffffff
mask64 = 0xffffffffffffffff

ancient = 0xdeadbeefcafefeed
masked = ancient & 0xff08f37f4167f901
turned = ((masked << 6) | (masked >> 58)) & mask64

first = (ancient ^ turned) & mask32
second = masked & mask32
signed_low16 = (ancient & 0xffff) - 0x10000
final = ((turned & mask32) | (first & ((second + signed_low16) & mask32))) & mask32

print(f"ACM{{r4v3ncl4w_{final:08x}}}")
```

It prints:

```text
ACM{r4v3ncl4w_59fef6ff}
```

The verifier stops the original program at the instruction after its final `or eax, ecx` and observes this same value in `EAX`.

## Flag

```text
ACM{r4v3ncl4w_59fef6ff}
```

## Organizer notes

- `-masm=intel` is required to rebuild the inline assembly as written.
- Keep the final assignment observable at `-O0`; optimisation can remove unused calculations or materially change the register flow.
- Suggested hint sequence: “Confirm the width of each instruction.” Then: “Inspect `movsx`; its source is the low 16 bits.”

## Intended flag

```text
ACM{r4v3ncl4w_59fef6ff}
```
