#!/usr/bin/env python3
"""Build the public evidence archive for the Three Clocks forensic challenge."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "public" / "three_clocks.zip"
UTC = timezone.utc
PKT = timezone(timedelta(hours=5), name="PKT")
CHROME_EPOCH = datetime(1601, 1, 1, tzinfo=UTC)

TARGET_USER = "ali"
TARGET_SESSION = "S-8F3C19"
TARGET_DOCUMENT = "HR-2026-044"
TARGET_FILENAME = "FY2026_Restructuring_Plan.pdf"
TARGET_EXPORT_UTC = datetime(2026, 11, 10, 14, 34, 42, tzinfo=UTC)


def chromium_time(value: datetime) -> int:
    """Return Chromium's UTC microseconds since 1601-01-01."""
    delta = value.astimezone(UTC) - CHROME_EPOCH
    return (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds


def unix_time(value: datetime) -> int:
    return int(value.astimezone(UTC).timestamp())


def ts(hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(2026, 11, 10, hour, minute, second, tzinfo=UTC)


def make_history(path: Path) -> None:
    """Create a compact Chromium-compatible history database."""
    visits = [
        (ts(13, 48, 11), "https://intranet.havenridge.example/news", "Havenridge Intranet - News"),
        (ts(13, 50, 42), "https://mail.havenridge.example/mail/u/0/#inbox", "Havenridge Mail - Inbox"),
        (ts(13, 54, 26), "https://calendar.havenridge.example/week", "Havenridge Calendar"),
        (ts(13, 57, 53), "https://weather.example/karachi", "Karachi Weather"),
        (ts(14, 3, 18), "https://wiki.havenridge.example/engineering/handbook", "Engineering Handbook"),
        (ts(14, 8, 4), "https://hr.havenridge.example/leave", "Leave Management"),
        (ts(14, 13, 37), "https://portal.havenridge.example/help/exporting-documents", "Portal Help - Exporting Documents"),
        (ts(14, 19, 29), "https://portal.havenridge.example/dashboard", "Havenridge Internal Portal"),
        (ts(14, 24, 56), "https://wiki.havenridge.example/finance/quarterly-close", "Quarterly Close Checklist"),
        (ts(14, 28, 12), "https://portal.havenridge.example/login?next=/documents/HR-2026-044", "Havenridge Internal Portal - Sign in"),
        (ts(14, 28, 36), f"https://portal.havenridge.example/dashboard?session={TARGET_SESSION}", "Havenridge Internal Portal"),
        (ts(14, 30, 8), f"https://portal.havenridge.example/documents/{TARGET_DOCUMENT}?session={TARGET_SESSION}", "FY2026 Restructuring Plan"),
        (ts(14, 31, 45), f"https://portal.havenridge.example/documents/{TARGET_DOCUMENT}/preview?session={TARGET_SESSION}", "FY2026 Restructuring Plan - Preview"),
        (ts(14, 33, 2), "https://portal.havenridge.example/documents/FIN-2026-019", "Quarterly Travel Controls"),
        (ts(14, 34, 10), f"https://portal.havenridge.example/documents/{TARGET_DOCUMENT}/export?format=pdf&session={TARGET_SESSION}", "Export FY2026 Restructuring Plan"),
        (ts(14, 36, 5), "https://portal.havenridge.example/dashboard", "Havenridge Internal Portal"),
        (ts(14, 39, 44), "https://mail.havenridge.example/mail/u/0/#sent", "Havenridge Mail - Sent"),
        (ts(14, 44, 7), "https://intranet.havenridge.example/directory", "Employee Directory"),
        (ts(14, 51, 16), "https://support.havenridge.example/tickets", "IT Service Desk"),
        (ts(15, 2, 25), "https://intranet.havenridge.example/news", "Havenridge Intranet - News"),
    ]

    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            PRAGMA user_version = 72;
            CREATE TABLE urls (
                id INTEGER PRIMARY KEY,
                url LONGVARCHAR,
                title LONGVARCHAR,
                visit_count INTEGER DEFAULT 0 NOT NULL,
                typed_count INTEGER DEFAULT 0 NOT NULL,
                last_visit_time INTEGER NOT NULL,
                hidden INTEGER DEFAULT 0 NOT NULL
            );
            CREATE TABLE visits (
                id INTEGER PRIMARY KEY,
                url INTEGER NOT NULL,
                visit_time INTEGER NOT NULL,
                from_visit INTEGER,
                transition INTEGER DEFAULT 0 NOT NULL,
                segment_id INTEGER,
                visit_duration INTEGER DEFAULT 0 NOT NULL,
                incremented_omnibox_typed_score BOOLEAN DEFAULT 0 NOT NULL,
                opener_visit INTEGER DEFAULT 0 NOT NULL,
                originator_cache_guid TEXT,
                originator_from_visit INTEGER DEFAULT 0 NOT NULL,
                duration INTEGER DEFAULT 0 NOT NULL
            );
            CREATE INDEX visits_time_index ON visits (visit_time);
            CREATE INDEX visits_url_index ON visits (url);
            """
        )
        previous_visit = 0
        for identifier, (when, url, title) in enumerate(visits, start=1):
            chrome_value = chromium_time(when)
            connection.execute(
                "INSERT INTO urls (id, url, title, visit_count, typed_count, last_visit_time, hidden) VALUES (?, ?, ?, 1, 0, ?, 0)",
                (identifier, url, title, chrome_value),
            )
            connection.execute(
                "INSERT INTO visits (id, url, visit_time, from_visit, transition, segment_id, visit_duration, incremented_omnibox_typed_score, opener_visit, originator_from_visit, duration) VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, 0, 0)",
                (identifier, identifier, chrome_value, previous_visit or None),
            )
            previous_visit = identifier
        connection.commit()
    finally:
        connection.close()


def audit_line(
    identifier: int,
    when: datetime,
    user: str,
    session: str,
    document: str,
    filename: str,
    event: str,
    status: str,
    authorization: str,
    client: str = "web",
) -> str:
    local = when.astimezone(PKT).isoformat(timespec="seconds")
    return (
        f"{local} level=INFO event_id=AUD-20261110-{identifier:04d} "
        f"user={user} session={session} document={document} filename={filename} "
        f"event={event} status={status} authorization={authorization} client={client}"
    )


def make_audit_log() -> str:
    public_doc = "PUB-2026-011"
    public_file = "November_All_Hands_Agenda.pdf"
    travel_doc = "FIN-2026-019"
    travel_file = "Quarterly_Travel_Controls.pdf"
    events = [
        (ts(9, 2, 14), "mariam", "S-1A7D02", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(9, 4, 3), "mariam", "S-1A7D02", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(9, 5, 18), "mariam", "S-1A7D02", public_doc, public_file, "EXPORT_REQUEST", "SUCCESS", "APPROVED"),
        (ts(9, 5, 22), "mariam", "S-1A7D02", public_doc, public_file, "EXPORT_COMPLETED", "SUCCESS", "APPROVED"),
        (ts(9, 7, 40), "mariam", "S-1A7D02", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(10, 11, 5), "bilal", "S-4C20B8", travel_doc, travel_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(10, 15, 12), "bilal", "S-4C20B8", travel_doc, travel_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(10, 18, 55), "bilal", "S-4C20B8", travel_doc, travel_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(11, 42, 8), "sana", "S-30AA41", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(11, 45, 38), "sana", "S-30AA41", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(11, 48, 4), "sana", "S-30AA41", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(12, 26, 19), "naveed", "S-76B9D0", TARGET_DOCUMENT, TARGET_FILENAME, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(12, 28, 46), "naveed", "S-76B9D0", TARGET_DOCUMENT, TARGET_FILENAME, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(12, 30, 7), "naveed", "S-76B9D0", TARGET_DOCUMENT, TARGET_FILENAME, "EXPORT_REQUEST", "DENIED", "NO_APPROVAL"),
        (ts(12, 32, 19), "naveed", "S-76B9D0", TARGET_DOCUMENT, TARGET_FILENAME, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(13, 6, 54), "bilal", "S-77E01D", travel_doc, travel_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(13, 9, 12), "bilal", "S-77E01D", travel_doc, travel_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(13, 12, 44), "bilal", "S-77E01D", travel_doc, travel_file, "EXPORT_REQUEST", "SUCCESS", "APPROVED"),
        (ts(13, 12, 48), "bilal", "S-77E01D", travel_doc, travel_file, "EXPORT_COMPLETED", "SUCCESS", "APPROVED"),
        (ts(13, 14, 20), "bilal", "S-77E01D", travel_doc, travel_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(13, 51, 36), "sana", "S-C1F909", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(13, 53, 10), "sana", "S-C1F909", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(13, 56, 42), "sana", "S-C1F909", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(14, 16, 3), "ali", "S-1B3D60", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(14, 17, 11), "ali", "S-1B3D60", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(14, 18, 23), "ali", "S-1B3D60", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(14, 28, 12), TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(14, 30, 8), TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(14, 31, 45), TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "DOCUMENT_PREVIEW", "SUCCESS", "APPROVED"),
        (ts(14, 34, 9), TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "EXPORT_REQUEST", "SUCCESS", "NO_APPROVAL"),
        (TARGET_EXPORT_UTC, TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "EXPORT_COMPLETED", "SUCCESS", "UNAUTHORIZED"),
        (ts(14, 36, 58), TARGET_USER, TARGET_SESSION, TARGET_DOCUMENT, TARGET_FILENAME, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(14, 42, 17), "mariam", "S-F101A4", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(14, 44, 3), "mariam", "S-F101A4", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(14, 45, 26), "mariam", "S-F101A4", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(15, 7, 51), "bilal", "S-D9C4E3", travel_doc, travel_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(15, 9, 2), "bilal", "S-D9C4E3", travel_doc, travel_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(15, 11, 40), "bilal", "S-D9C4E3", travel_doc, travel_file, "LOGOUT", "SUCCESS", "APPROVED"),
        (ts(15, 21, 11), "sana", "S-0C23A7", public_doc, public_file, "LOGIN_SUCCESS", "SUCCESS", "APPROVED"),
        (ts(15, 24, 59), "sana", "S-0C23A7", public_doc, public_file, "DOCUMENT_VIEW", "SUCCESS", "APPROVED"),
        (ts(15, 28, 7), "sana", "S-0C23A7", public_doc, public_file, "LOGOUT", "SUCCESS", "APPROVED"),
    ]
    header = [
        "# Havenridge Internal Portal audit export",
        "# application_timezone=UTC+05:00 (Pakistan Standard Time)",
        "# Fields: timestamp level event_id user session document filename event status authorization client",
    ]
    return "\n".join(header + [audit_line(index, *event) for index, event in enumerate(events, start=1)]) + "\n"


def artifact_hash(filename: str, document: str, size: int) -> str:
    data = f"Havenridge forensic metadata|{filename}|{document}|{size}".encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def make_filesystem_csv() -> str:
    target_appearance = TARGET_EXPORT_UTC + timedelta(seconds=5)
    rows = [
        ("meeting_notes.docx", r"C:\\Users\\ali\\Documents\\meeting_notes.docx", 38412, ts(12, 12, 19), "last_modified_utc", "HR-2026-032"),
        ("quarterly_summary.xlsx", r"C:\\Users\\ali\\Documents\\quarterly_summary.xlsx", 91648, ts(13, 47, 2), "last_modified_utc", "FIN-2026-012"),
        ("portal_export_HR-2026-044.tmp", r"C:\\Users\\ali\\AppData\\Local\\Temp\\portal_export_HR-2026-044.tmp", 17428, TARGET_EXPORT_UTC + timedelta(seconds=2), "created_utc", TARGET_DOCUMENT),
        (TARGET_FILENAME, r"C:\\Users\\ali\\Downloads\\Portal Exports\\FY2026_Restructuring_Plan.pdf", 248736, target_appearance, "created_utc", TARGET_DOCUMENT),
        ("browser_cache.bin", r"C:\\Users\\ali\\AppData\\Local\\Chromium\\Cache\\browser_cache.bin", 529920, ts(14, 36, 12), "last_modified_utc", "BROWSER-CACHE"),
        ("November_All_Hands_Agenda.pdf", r"C:\\Users\\ali\\Downloads\\November_All_Hands_Agenda.pdf", 73214, ts(15, 41, 9), "created_utc", "PUB-2026-011"),
    ]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=("filename", "original_path", "size_bytes", "unix_timestamp", "timestamp_type", "sha256", "document_id", "collector_note"),
    )
    writer.writeheader()
    for filename, path, size, when, timestamp_type, document in rows:
        note = "appeared after portal export completion" if filename == TARGET_FILENAME else "forensic metadata export"
        writer.writerow(
            {
                "filename": filename,
                "original_path": path,
                "size_bytes": size,
                "unix_timestamp": unix_time(when),
                "timestamp_type": timestamp_type,
                "sha256": artifact_hash(filename, document, size),
                "document_id": document,
                "collector_note": note,
            }
        )
    return output.getvalue()


ACQUISITION_NOTE = """Three Clocks evidence acquisition note

Case reference: HR-2026-044
Workstation: HR-LT-044 (suspected employee workstation)
Collection scope: Chromium activity, internal-portal audit export, and filesystem metadata.

Timestamp conventions
- History is a Chromium SQLite database. visits.visit_time and urls.last_visit_time are microseconds since 1601-01-01 00:00:00 UTC.
- portal_audit.log records ISO 8601 timestamps with an explicit UTC+05:00 offset (Pakistan Standard Time).
- filesystem_metadata.csv records Unix epoch seconds. Interpret those values as UTC.

The filesystem collection records when files appeared on the workstation. The portal audit record is the authoritative source for whether an export completed successfully. Preserve the archive contents when examining the evidence; extracting files can change host filesystem timestamps.
"""


def write_zip(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="three-clocks-"))
    try:
        history = temporary / "History"
        make_history(history)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.write(history, arcname="History")
            archive.writestr("portal_audit.log", make_audit_log())
            archive.writestr("filesystem_metadata.csv", make_filesystem_csv())
            archive.writestr("acquisition_note.txt", ACQUISITION_NOTE)
    finally:
        shutil.rmtree(temporary)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="path for three_clocks.zip")
    args = parser.parse_args()
    write_zip(args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
