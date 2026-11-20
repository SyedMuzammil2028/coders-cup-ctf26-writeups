"""JPEG marker helpers used by the one-time challenge generator."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable


JPEG_SOI = b"\xff\xd8"
APP15_MARKER = b"\xff\xef"
MARKER_PREFIX = b"CASTLE_ARCHIVE_RECORD\x00"


def build_printable_payload(records: Iterable[str]) -> bytes:
    encoded = [record.encode("ascii", errors="strict") for record in records]
    payload = MARKER_PREFIX + b"\n".join(encoded) + b"\n"
    if len(payload) + 2 > 65_535:
        raise ValueError("APP15 payload is too large")
    return payload


def inject_app15_strings(source: Path, destination: Path, records: Iterable[str]) -> None:
    """Insert a standards-compliant APP15 segment directly after the JPEG SOI."""
    payload = build_printable_payload(records)
    segment = APP15_MARKER + (len(payload) + 2).to_bytes(2, "big") + payload
    with source.open("rb") as source_handle, destination.open("wb") as output_handle:
        if source_handle.read(2) != JPEG_SOI:
            raise ValueError("source is not a JPEG")
        output_handle.write(JPEG_SOI)
        output_handle.write(segment)
        shutil.copyfileobj(source_handle, output_handle, length=64 * 1024)


def validate_jpeg(path: Path) -> None:
    with path.open("rb") as handle:
        if handle.read(2) != JPEG_SOI:
            raise ValueError("generated artifact has an invalid JPEG header")
        handle.seek(-2, 2)
        if handle.read(2) != b"\xff\xd9":
            raise ValueError("generated artifact has an invalid JPEG trailer")

