# Write-up — Lost in Translation

The service publishes an encoded transmission at `/ciphertext.json`. The
visual unlock is only a client-side gate, so inspecting the page source or
requesting that endpoint directly reveals the ciphertext.

The transformations must be reversed in the opposite order to the startup
encoder:

1. Remove the spaces from the eight-bit groups and convert each binary
   octet to its ASCII character.
2. Reverse the complete resulting Base64 string, including any padding
   characters.
3. Base64-decode that reversed string.
4. Apply ROT13 to the decoded plaintext.

The final plaintext is the runtime `ACM{...}` value. In the event, every
private instance received a different team-specific flag, so use a local
dummy `FLAG` value when replaying the challenge.

## Intended flag

```text
ACM{r3v3rs3d_3nc0d1ng_<hash>}
```
