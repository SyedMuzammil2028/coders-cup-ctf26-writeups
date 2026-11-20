
# Baby RSA organizer write-up

Keep this guide private during the event. The challenge is deliberately
textbook RSA: it exposes `p`, `q`, and `d` so the intended solve is basic RSA
decryption, not factorization or a mathematical attack.

## Player workflow

Connect using the address assigned by CTFd:

```bash
nc HOST PORT
```

The service prints complete decimal values for `n`, `e`, `p`, `q`, `d`, and
`c`. The CTFd runtime has already supplied a team-specific flag through the
`FLAG` environment variable; the service encrypts that exact string for the
current connection.

## Decrypt the ciphertext

Copy the decimal `c`, `d`, and `n` values into Python:

```python
m = pow(c, d, n)
plaintext = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(plaintext.decode("utf-8"))
```

`pow(c, d, n)` computes the RSA private operation, returning the integer form
of the original UTF-8 flag. Converting it back to bytes reveals the exact flag
for that team instance. Submit that value to CTFd; the TCP server does not
accept submissions.

## Local organizer check

Start the service with a dummy value:

```bash
FLAG='ACM{baby_rsa_local_test}' PORT=1337 python3 src/server.py
```

Then exercise only the network protocol:

```bash
python3 organizer/solver.py 127.0.0.1 1337
```

The solver validates `n = p*q`, the modular inverse relationship for `d`, and
the recovered flag format. It never reads the server process environment.

## Why parameters change after reconnecting

The service uses fresh cryptographic primes for every TCP connection. A second
connection therefore has a different `p`, `q`, `n`, `d`, and `c`, but decrypts
to the same CTFd-injected flag. This is RSA session freshness only; CTFd still
controls team flag freshness and validation.

## Intended flag

```text
ACM{r54_pr1v4t3_k3y_<hash>}
```
