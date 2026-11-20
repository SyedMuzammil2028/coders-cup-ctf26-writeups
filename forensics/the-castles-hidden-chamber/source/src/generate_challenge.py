#!/usr/bin/env python3
"""Generate one team-specific JPEG, verify it, and publish it atomically."""

from __future__ import annotations

import argparse
import base64
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from image_builder import inject_app15_strings, validate_jpeg
from metadata_builder import (
    FAKE_FLAG_METADATA,
    METADATA_HINT,
    read_metadata,
    write_metadata,
)


FLAG_PATTERN = re.compile(r"ACM\{[A-Za-z0-9_:-]{1,240}\}\Z")
FAKE_FLAG_STRINGS = "ACM{F4k3_Fl4g}"
PASSWORD_LABEL = b"acm-coders-cup-26:hidden-chamber:passphrase:v1"


class GenerationError(RuntimeError):
    pass


def validate_flag(value: str) -> str:
    if not value or not value.isascii() or not FLAG_PATTERN.fullmatch(value):
        raise GenerationError("runtime FLAG is missing or invalid")
    return value


def derive_passphrase(source: Path) -> str:
    digest = hashlib.sha256(PASSWORD_LABEL)
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    token = base64.urlsafe_b64encode(digest.digest()[:12]).decode("ascii").rstrip("=")
    return f"archway-{token}"


def _cgroup_peak_bytes() -> int | None:
    candidates = (
        Path("/sys/fs/cgroup/memory.peak"),
        Path("/sys/fs/cgroup/memory/memory.max_usage_in_bytes"),
    )
    for candidate in candidates:
        try:
            raw = candidate.read_text(encoding="ascii").strip()
            if raw.isdigit():
                return int(raw)
        except OSError:
            continue
    return None


def log_phase(name: str, status: str) -> None:
    peak = _cgroup_peak_bytes()
    peak_value = str(peak) if peak is not None else "unavailable"
    print(
        f"generation phase={name} status={status} cgroup_peak_bytes={peak_value}",
        flush=True,
    )


def _run(command: list[str], description: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or description
        raise GenerationError(f"{description}: {detail}")
    return result


def _extract(image: Path, password: str, destination: Path) -> None:
    _run(
        [
            "steghide",
            "extract",
            "-sf",
            str(image),
            "-xf",
            str(destination),
            "-p",
            password,
            "-f",
        ],
        "steghide verification failed",
    )


def verify_artifact(image: Path, expected_flag: str, password: str) -> None:
    validate_jpeg(image)
    city, comment = read_metadata(image)
    if city != FAKE_FLAG_METADATA or comment != METADATA_HINT:
        raise GenerationError("required metadata was not preserved")

    binary = image.read_bytes()
    for expected in (FAKE_FLAG_STRINGS.encode("ascii"), f"PASSWORD={password}".encode("ascii")):
        if expected not in binary:
            raise GenerationError("required printable marker is missing")
    if expected_flag.encode("utf-8") in binary:
        raise GenerationError("plaintext runtime flag leaked into the JPEG")

    with tempfile.TemporaryDirectory(prefix="hidden-chamber-extract-") as temporary:
        extracted = Path(temporary) / "flag.txt"
        wrong = subprocess.run(
            [
                "steghide",
                "extract",
                "-sf",
                str(image),
                "-xf",
                str(extracted),
                "-p",
                "incorrect-password",
                "-f",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        if wrong.returncode == 0:
            raise GenerationError("steghide accepted an incorrect password")
        _extract(image, password, extracted)
        encoded = extracted.read_text(encoding="ascii")
        try:
            recovered = base64.b64decode(encoded, validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as error:
            raise GenerationError("embedded flag.txt is not valid Base64") from error
        if recovered != expected_flag:
            raise GenerationError("embedded flag did not round-trip")


def generate(source: Path, output: Path, flag: str) -> None:
    flag = validate_flag(flag)
    if not source.is_file():
        raise GenerationError("base castle image is missing")
    output.parent.mkdir(parents=True, exist_ok=True)
    password = derive_passphrase(source)

    log_phase("startup", "begin")
    with tempfile.TemporaryDirectory(prefix=".hidden-chamber-", dir=output.parent) as temporary:
        work = Path(temporary)
        carrier = work / "carrier.jpg"
        embedded = work / "embedded.jpg"
        metadata_image = work / "metadata.jpg"
        candidate = work / "challenge.jpg"
        payload = work / "flag.txt"

        shutil.copyfile(source, carrier)
        payload.write_text(base64.b64encode(flag.encode("utf-8")).decode("ascii"), encoding="ascii")
        os.chmod(payload, 0o600)
        log_phase("startup", "complete")

        log_phase("steghide", "begin")
        _run(
            [
                "steghide",
                "embed",
                "-cf",
                str(carrier),
                "-ef",
                str(payload),
                "-sf",
                str(embedded),
                "-p",
                password,
                "-f",
            ],
            "steghide embedding failed",
        )
        payload.unlink()
        log_phase("steghide", "complete")

        log_phase("metadata", "begin")
        shutil.copyfile(embedded, metadata_image)
        write_metadata(metadata_image)
        log_phase("metadata", "complete")

        log_phase("printable_markers", "begin")
        inject_app15_strings(
            metadata_image,
            candidate,
            (f"SECOND_SEAL={FAKE_FLAG_STRINGS}", f"PASSWORD={password}"),
        )
        log_phase("printable_markers", "complete")

        log_phase("verification", "begin")
        verify_artifact(candidate, flag, password)
        log_phase("verification", "complete")

        os.chmod(candidate, 0o400)
        os.replace(candidate, output)
        log_phase("publish", "complete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        flag = validate_flag(os.environ.get("FLAG", ""))
        generate(arguments.source, arguments.output, flag)
    except GenerationError as error:
        print(f"challenge generation failed: {error}", flush=True)
        return 64
    print("challenge artifact generated and verified", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

