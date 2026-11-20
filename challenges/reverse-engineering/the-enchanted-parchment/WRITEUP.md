
---
title: "The Enchanted Parchment"
ctf: "Coders Cup"
date: 2026-10-25
category: reverse
difficulty: easy
flag_format: "ACM{...}"
author: "Organizer"
---

# The Enchanted Parchment

## Challenge description

An enchanted parchment shifts every rune in its secret message according to its place in the sentence. Reverse the parchment's checker and recover the exact phrase that reveals its hidden message.

Run the supplied binary with your candidate `ACM{...}` flag as its only argument.

## Summary

The binary transforms each flag character by a position-dependent shift in a 93-character alphabet, then compares the transformed bytes to a stored target. Inverting the shift recovers the accepted flag.

**Difficulty:** Easy. **Enjoyability:** 7/10. The encoded string is discoverable through static inspection, yet students must still read the loop and write a small inverse script.

## Solution

### Step 1: Locate the stored enchanted ink

The binary contains a 34-byte global array named `enchanted_ink`. `objdump -s -j .rodata enchanted_parchment` or a decompiler reveals these bytes:

```text
42 45 50 22 38 74 6a 70 3d 78 22 3f 71 6d 22 44
26 75 7b 24 48 27 2e 77 4a 30 7a 33 32 4f 25 2e
3d 42
```

The program accepts exactly one 34-character argument. It allows only byte values 33 (`!`) through 125 (`}`), then calculates:

```c
transformed[i] = (rune - 33 + i + 1) % 93 + 33;
```

The transformed input, rather than the input itself, is compared to `enchanted_ink`.

### Step 2: Undo the position shift

For a stored byte `target[i]`, undo the alphabet offset and the one-based position shift:

```text
flag[i] = ((target[i] - 33 - i - 1) mod 93) + 33
```

The `+1` matters because the loop starts at index zero while the first rune shifts by one. The modulus is 93 because the permitted alphabet runs from `!` to `}` inclusive.

The complete solver is included in `solve.py`:

```python
flag = bytes((byte - 33 - i - 1) % 93 + 33
             for i, byte in enumerate(enchanted_ink))
print(flag.decode("ascii"))
```

It recovers and verifies:

```text
ACM{3nch4nt3d_p4rchm3nt_1s_tr1cky}
The enchanted parchment reveals its message!
```

## Flag

```text
ACM{3nch4nt3d_p4rchm3nt_1s_tr1cky}
```

## Organizer notes

- This revised checker verifies the exact argument length and the intended 93-character alphabet. It no longer accepts an extra suffix or an alternative character separated by 93.
- The code uses `memcmp` for exact transformed-byte comparison and caches no ambiguous zero-padded input.
- Suggested hint: “The parchment moves each rune further along the same alphabet.”

## Intended flag

```text
ACM{3nch4nt3d_p4rchm3nt_1s_tr1cky}
```
