# Write-up — The Ravenclaw Cipher

The description identifies a classical repeating-key cipher and points to
Ravenclaw for the key. That is a Vigenère cipher with key `RAVENCLAW`.

Decrypt `FWG_TBUE_DACIQIEGO` by subtracting the repeating key letters from
the ciphertext letters while leaving underscores unchanged. The plaintext
is `OWL_POST_DELIVERED`, so the historical event submission was:

```text
ACM{OWL_POST_DELIVERED}
```

A short script or any Vigenère tool works, provided it preserves the
underscores and original capitalization.

## Intended flag

```text
ACM{OWL_POST_DELIVERED}
```
