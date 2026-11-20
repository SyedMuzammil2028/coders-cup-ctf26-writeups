
# Organizer write-up — The Forbidden Payload

> Keep this Markdown document organizer-only. It describes the intended
> white-box solve path and must not be attached to the CTFd challenge.

## Intended solution

1. Start the team's private instance and download its artifact:

   ```bash
   curl -fOJ http://TEAM-INSTANCE/download
   file malware.pyc
   ```

   `file` identifies a hash-based CPython 3.8 bytecode file. Running it with
   `python3.8 malware.pyc` asks for a magic number, but running unknown
   bytecode is not required for the solve.

2. Decompile the Python 3.8 loader with the tested tool:

   ```bash
   python3 -m pip install 'uncompyle6==3.9.3'
   uncompyle6 malware.pyc > loader.py
   ```

3. Inspect `loader.py`. It assigns eleven long Base64 fragments—`owl_ink`
   through `starless_seal`—and combines them in the `sealed_scroll` expression
   before decoding and executing the result.

4. Recover the second-stage source without executing it. Copy the eleven
   strings in the expression's order and decode them, for example:

   ```python
   import base64

   encoded = (
       owl_ink + moon_salt + quiet_ash + raven_quill + dusk_thread
       + mirror_dust + tower_chalk + amber_wax + frosted_vellum
       + cinder_key + starless_seal
   )
   print(base64.b64decode(encoded).decode('utf-8'))
   ```

5. The decoded program stores a numeric `runes` list plus `anchor`, `stride`,
   and `modulus`. It reconstructs the flag with a position-dependent XOR:

   ```python
   flag = ''.join(
       chr(value ^ (anchor + ((index * stride) % modulus)))
       for index, value in enumerate(runes)
   )
   ```

6. It calculates the requested magic number as:

   ```python
   magic_number = sum(ord(character) for character in flag)
   ```

   Players can calculate that sum and enter it, or statically inspect the
   reconstruction and print the already-recovered `flag`. Either route is
   valid for this intentionally white-box challenge.

7. Submit the recovered `ACM{...}` value. A CTFd instance returns that team's
   freshness value, so it is expected to differ between teams.

## Private static solver

`organizer/solver.py` validates the intended solution without accessing the
container environment. Run it with CPython 3.8 because Python marshal code
objects are version-specific:

```bash
python3.8 organizer/solver.py malware.pyc
```

It reads literal constants from the `.pyc`, decodes the payload, parses it as
an AST, and reverses the numeric transformation. It never calls `exec`,
`eval`, or reads `FLAG`.

## Why this is white-box

The artifact itself contains the data needed to recover its flag. Obfuscation
creates the intended reverse-engineering work; it is not an access-control
mechanism. Per-team CTFd instances ensure the recoverable artifact corresponds
only to the solver's own freshness flag.

## Troubleshooting

- **Decompiler rejects the file:** ensure it recognizes CPython 3.8 bytecode;
  use the pinned `uncompyle6==3.9.3` command above.
- **The program rejects the magic number:** recompute the ASCII sum from the
  reconstructed flag; do not sum transformed `runes` values.
- **Two teams obtain different flags:** this is correct. CTFd injects a
  different freshness value into each team's container at startup.
- **A static local file differs from an instance artifact:** expected. There
  is no universal production `.pyc`; each running CTFd instance generates one.

## Intended flag

```text
ACM{pyt0n_byt3c0d3_<hash>}
```
