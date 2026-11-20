"""ExifTool-backed metadata operations for the challenge artifact."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


FAKE_FLAG_METADATA = "ACM{f4k3_fl4g}"
METADATA_HINT = (
    "The first seal is a deception. The passphrase is written among the "
    "image's printable strings. Search for PASSWORD."
)


class MetadataError(RuntimeError):
    pass


def _exiftool() -> str:
    executable = shutil.which("exiftool")
    if not executable:
        raise MetadataError("exiftool is unavailable")
    return executable


def write_metadata(image: Path) -> None:
    command = [
        _exiftool(),
        "-overwrite_original",
        f"-IPTC:City={FAKE_FLAG_METADATA}",
        f"-EXIF:UserComment={METADATA_HINT}",
        "-XMP-dc:Creator=Castle Archive Recovery Unit",
        "-EXIF:Software=Archive Restoration Workstation 4.2",
        "-XMP-photoshop:Credit=Recovered Photograph Collection",
        str(image),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or "metadata update failed"
        raise MetadataError(message)


def read_metadata(image: Path) -> tuple[str, str]:
    command = [
        _exiftool(),
        "-j",
        "-IPTC:City",
        "-EXIF:UserComment",
        str(image),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise MetadataError(result.stderr.strip() or "metadata read failed")
    records = json.loads(result.stdout)
    if len(records) != 1:
        raise MetadataError("unexpected metadata response")
    return str(records[0].get("City", "")), str(records[0].get("UserComment", ""))

