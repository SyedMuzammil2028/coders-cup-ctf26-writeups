"""Original reversible memory transport used by The Seventh Spire."""

from __future__ import annotations

import base64
import hashlib


KEY_RECIPE = "sha256_utf8(serial + '|' + tower)[:8]"


def derive_key(serial: str, tower: str) -> bytes:
    """Derive the documented eight-byte repeating-XOR key."""
    return hashlib.sha256(f"{serial}|{tower}".encode("utf-8")).digest()[:8]


def xor_repeating(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("XOR key must not be empty")
    return bytes(value ^ key[index % len(key)] for index, value in enumerate(data))


def encode_memory(flag: str, serial: str, tower: str) -> str:
    ciphertext = xor_repeating(flag.encode("utf-8"), derive_key(serial, tower))
    return base64.b64encode(ciphertext).decode("ascii")


def split_encoded(encoded: str, total: int = 6) -> list[str]:
    if total < 2:
        raise ValueError("at least two fragments are required")
    width, remainder = divmod(len(encoded), total)
    fragments: list[str] = []
    offset = 0
    for part in range(total):
        next_offset = offset + width + (1 if part < remainder else 0)
        fragments.append(encoded[offset:next_offset])
        offset = next_offset
    if any(not fragment for fragment in fragments):
        raise ValueError("encoded memory is too short for requested split")
    return fragments

