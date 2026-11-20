#!/usr/bin/env python3
"""Generate the static released PCAP for The Seventh Spire."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from scapy.all import rdpcap, wrpcap

from build_traffic import CHALLENGE_FLAG, build_capture


def generate(output: Path, timeline_output: Path | None = None) -> int:
    packets, timeline = build_capture()
    output.parent.mkdir(parents=True, exist_ok=True)
    wrpcap(str(output), packets)
    reloaded = rdpcap(str(output))
    if len(reloaded) != len(packets):
        raise RuntimeError("written PCAP packet count does not match generated capture")
    if CHALLENGE_FLAG.encode("utf-8") in output.read_bytes():
        raise RuntimeError("plaintext flag leaked into PCAP bytes")
    if timeline_output:
        timeline_output.parent.mkdir(parents=True, exist_ok=True)
        with timeline_output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=("stage", "detail"))
            writer.writeheader()
            writer.writerows(timeline)
    return len(packets)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeline", type=Path)
    arguments = parser.parse_args()
    count = generate(arguments.output.resolve(), arguments.timeline.resolve() if arguments.timeline else None)
    print(f"generated {count} packets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

