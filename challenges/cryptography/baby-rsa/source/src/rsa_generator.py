"""Textbook RSA parameters for the intentionally vulnerable Baby RSA service.

This module is solely for a CTF exercise. Textbook RSA and exposing private
parameters are not safe for real-world encryption.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from Crypto.Util.number import getPrime, isPrime


PUBLIC_EXPONENT = 65_537
MODULUS_BITS = 1024


@dataclass(frozen=True)
class RSAChallenge:
    n: int
    e: int
    p: int
    q: int
    d: int
    c: int
    m: int


def flag_to_integer(flag: str) -> int:
    return int.from_bytes(flag.encode("utf-8"), "big")


def generate_challenge(flag: str) -> RSAChallenge:
    """Generate fresh 1024-bit RSA parameters that encrypt *flag* exactly."""
    message = flag_to_integer(flag)
    if message <= 0:
        raise ValueError("flag must encode to a non-zero integer")

    while True:
        p = getPrime(MODULUS_BITS // 2)
        q = getPrime(MODULUS_BITS // 2)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if math.gcd(PUBLIC_EXPONENT, phi) != 1:
            continue
        n = p * q
        if message >= n:
            continue
        d = pow(PUBLIC_EXPONENT, -1, phi)
        ciphertext = pow(message, PUBLIC_EXPONENT, n)
        challenge = RSAChallenge(n=n, e=PUBLIC_EXPONENT, p=p, q=q, d=d, c=ciphertext, m=message)
        validate_challenge(challenge)
        return challenge


def validate_challenge(challenge: RSAChallenge) -> None:
    """Raise ValueError unless the advertised RSA values are self-consistent."""
    if challenge.p == challenge.q or not isPrime(challenge.p) or not isPrime(challenge.q):
        raise ValueError("invalid prime pair")
    if challenge.n != challenge.p * challenge.q:
        raise ValueError("invalid modulus")
    phi = (challenge.p - 1) * (challenge.q - 1)
    if challenge.e != PUBLIC_EXPONENT or math.gcd(challenge.e, phi) != 1:
        raise ValueError("invalid public exponent")
    if (challenge.e * challenge.d) % phi != 1:
        raise ValueError("invalid private exponent")
    if not 0 < challenge.m < challenge.n:
        raise ValueError("message does not fit the modulus")
    if pow(challenge.c, challenge.d, challenge.n) != challenge.m:
        raise ValueError("ciphertext does not round-trip")


def render_challenge(challenge: RSAChallenge) -> bytes:
    """Render the complete parameter set, deliberately including private values."""
    text = f"""
=======================================
          ACM CODER'S CUP '26
               BABY RSA
=======================================

Our cryptographer left you everything.

Can you recover the secret?

n = {challenge.n}

e = {challenge.e}

p = {challenge.p}

q = {challenge.q}

d = {challenge.d}

c = {challenge.c}

Decrypt the ciphertext to recover the flag.
""".lstrip()
    return text.encode("ascii")
