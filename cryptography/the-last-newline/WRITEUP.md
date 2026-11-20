
# The Last Newline — Organizer solution

Maintenance removed one invisible byte from the recovery document after the archivist certified it. The same archive also contains an older snapshot from before the recovery phrase was retired. The current ledger and earlier snapshots are enough to recover the exact document and credential.

## File inventory and revision timeline

| Revision | Change | Files held at that revision |
|---|---|---|
| 01 · Initial Archive Registration | Registered the recovery documents | Original `message.txt`, `records/vault-passphrase.txt` |
| 02 · Access Record Retired | Removed the credential file | Original `message.txt` |
| 03 · Integrity Certification | Recorded the SHA-256 of the original recovery note | Original `message.txt`, `audit.log` |
| 04 · Formatting Maintenance | Removed the final LF from the recovery note | Current `message.txt`, unchanged `audit.log` |

Each file carries the same instance-specific case reference. The recovery note references `records/vault-passphrase.txt`. Revision 01 is the only revision that offers this file. Preview or download it and copy the `OWL-` value from the recovery phrase line.

## Prove the integrity discrepancy

1. Download `message.txt` and `audit.log` from **Archive Files**. Read the certified digest from `audit.log` and hash the downloaded message with SHA-256. The current file’s digest differs from the certified digest.
2. From **Revision History**, open **03 · Integrity Certification** and download that revision’s `message.txt`. The notes in revisions 01 and 02 are also valid. Its SHA-256 matches the 64-digit hexadecimal digest in `audit.log`.
3. Compare the two downloaded files in a hex viewer or read them as bytes. The original is exactly the current byte sequence followed by `0A`. Hexadecimal `0A` is the ASCII line feed (LF) byte. A text preview can display both versions identically even though SHA-256 hashes the complete byte stream.

If the current and historical downloads are saved as `current.txt` and `certified.txt`, this standard-library command confirms the relationship:

```sh
python -c "from pathlib import Path; a=Path('current.txt').read_bytes(); b=Path('certified.txt').read_bytes(); print(b[:-1] == a, b[-1:].hex().upper())"
```

The command should print `True 0A`.

## Submit to the vault

Upload the historical `message.txt` directly from the download. Enter the full `OWL-` phrase from Revision 01 and enter `0A` in the missing-byte field. Lowercase `0a` also works. After verification, copy the displayed flag and submit it to CTFd. The vault returns the exact value injected in `FLAG` for the running instance. For the local run, that value is `ACM{LOCAL_TEST_ONLY}`.

## Common mistakes

- The two downloads may share the same basename. Browsers often append `(1)` to the second. Use the SHA-256 result to identify the certified file. The vault verifies its bytes and accepts a renamed copy.
- Copying text from the preview or saving through an editor can change newline bytes or add a UTF-8 BOM. Upload the downloaded file directly.
- In a hex viewer, `0D` is carriage return. The missing byte here is the single `0A` after the last visible character.
- Use the recovery phrase value by itself, including the `OWL-` prefix. Check the case reference if the credential was recovered before a container restart or from a different team’s instance.

## Intended flag

```text
ACM{r3v1s10n_1nt3gr1ty_<hash>}
```
