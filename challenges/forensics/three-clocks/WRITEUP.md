
# Organizer solution for Three Clocks

Keep this file private. It contains the expected flag and the complete solve.

## 1. Inspect the participant archive

```bash
unzip -l three_clocks.zip
unzip three_clocks.zip -d evidence
cd evidence
```

The archive contains exactly `History`, `portal_audit.log`,
`filesystem_metadata.csv`, and `acquisition_note.txt`. The acquisition note
states the three timestamp conventions:

- Chromium microseconds since 1601 UTC in `History`.
- ISO 8601 timestamps with a UTC+05:00 offset in `portal_audit.log`.
- Unix epoch seconds in `filesystem_metadata.csv`.

## 2. Reconstruct the browser sequence

Open `History` in DB Browser for SQLite, or use this SQLite query. Chromium
microseconds become Unix seconds after subtracting `11644473600` seconds.

```bash
sqlite3 History <<'SQL'
.headers on
.mode column
SELECT
  datetime((v.visit_time / 1000000) - 11644473600, 'unixepoch') || ' UTC' AS visit_utc,
  u.url,
  u.title
FROM visits AS v
JOIN urls AS u ON u.id = v.url
WHERE u.url LIKE '%HR-2026-044%'
ORDER BY v.visit_time;
SQL
```

The relevant entries are:

```text
2026-11-10 14:28:12 UTC  .../login?next=/documents/HR-2026-044
2026-11-10 14:30:08 UTC  .../documents/HR-2026-044?session=S-8F3C19
2026-11-10 14:31:45 UTC  .../documents/HR-2026-044/preview?session=S-8F3C19
2026-11-10 14:34:10 UTC  .../documents/HR-2026-044/export?format=pdf&session=S-8F3C19
```

This shows that session `S-8F3C19` navigated to export document
`HR-2026-044`. A browser navigation only indicates an attempted export, so it
is not the flag timestamp.

## 3. Identify the confirmed export

Find a completed export that was successful and unauthorized:

```bash
grep 'event=EXPORT_COMPLETED status=SUCCESS authorization=UNAUTHORIZED' portal_audit.log
```

The single matching entry is:

```text
2026-11-10T19:34:42+05:00 level=INFO event_id=AUD-20261110-0031 user=ali session=S-8F3C19 document=HR-2026-044 filename=FY2026_Restructuring_Plan.pdf event=EXPORT_COMPLETED status=SUCCESS authorization=UNAUTHORIZED client=web
```

The log timestamp has an explicit `+05:00` offset. Convert it rather than
submitting the displayed local time:

```bash
python3 - <<'PY'
from datetime import datetime, timezone
raw = "2026-11-10T19:34:42+05:00"
print(datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat())
PY
```

Output:

```text
2026-11-10T14:34:42+00:00
```

The responsible account is `ali`; the canonical completion time is
`2026-11-10 14:34:42 UTC`.

## 4. Corroborate with filesystem metadata

Use the document ID and filename from the audit record to select the matching
metadata row:

```bash
python3 - <<'PY'
import csv
from datetime import datetime, timezone

with open("filesystem_metadata.csv", newline="") as handle:
    for row in csv.DictReader(handle):
        if row["document_id"] == "HR-2026-044" and row["filename"] == "FY2026_Restructuring_Plan.pdf":
            print(row["filename"])
            print(datetime.fromtimestamp(int(row["unix_timestamp"]), timezone.utc).isoformat())
PY
```

Output:

```text
FY2026_Restructuring_Plan.pdf
2026-11-10T14:34:47+00:00
```

The exported PDF appeared five seconds after the confirmed portal completion.
That difference is expected: filesystem metadata corroborates that the output
arrived on the workstation, while the portal's `EXPORT_COMPLETED` record is the
authoritative completion event.

## 5. Construct the flag

The flag format uses the UTC date, UTC hour and minute, and the lowercase user
name. Seconds are not part of the flag format.

```text
ACM{20261110_1434_ali}
```

## Intended flag

```text
ACM{20261110_1434_ali}
```
