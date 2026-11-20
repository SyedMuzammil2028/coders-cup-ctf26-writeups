# Coder’s Cup ’26 — Solved Challenge Write-ups

This post-event educational release contains only challenges with at least one recorded solve in the verified CTFd event export.
It intentionally excludes zero-solve challenges, production `.env` files, database data, Docker runtime data, Git history, organizer solvers, and CTFd secrets.

Each challenge package contains:

- `CHALLENGE.md` — the original event statement, category, initial points, and author.
- `WRITEUP.md` — author solution notes or a clearly marked archival note.
- `RUN_LOCALLY.md` — local launch steps for challenges that run as a service.
- `challenge-files/` — original participant downloads, where provided.
- `source/` — sanitized educational source, where a local author project was available.

Do not use this repository to operate the original event infrastructure. Dynamic services must be replayed only with dummy local flags.

## How to use this repository

1. Open a challenge directory from the category list below.
2. Read `CHALLENGE.md` for the original event brief and context.
3. Follow `WRITEUP.md` to understand the intended solution.
4. When present, use `RUN_LOCALLY.md` and the included `challenge-files/` or `source/` directory to replay the challenge locally.

Some challenges were delivered as files or OSINT investigations and do not need a local service. Dynamic-container write-ups show the original fixed flag prefix and use `<hash>` in place of the private team-specific value.

## Authors and categories

| Author | Primary contributions in this release |
| --- | --- |
| Muz4mmil / Syed Muzammil | Forensics; selected Cryptography, Reverse Engineering, Miscellaneous, and OSINT challenges |
| Ah54n | Cryptography; selected Miscellaneous and OSINT challenges |
| H454N | PWN and Reverse Engineering challenges |
| k4zim | Web Exploitation challenges |

Individual challenge attribution is recorded in each challenge table and in its `CHALLENGE.md` file.

## Included challenges

### Cryptography

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [Baby RSA](challenges/cryptography/baby-rsa/) | 200 | Muz4mmil | Included |
| [Lost in Translation](challenges/cryptography/lost-in-translation/) | 350 | Ah54n | Included |
| [The Last Newline](challenges/cryptography/the-last-newline/) | 500 | Ah54n | Included |
| [The Ravenclaw Cipher](challenges/cryptography/the-ravenclaw-cipher/) | 200 | Ah54n | Included |

### Flag Format

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [Welcome Party](challenges/flag-format/welcome-party/) | 50 | Not recorded | Archival files only |

### Forensics

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [The Castle's Hidden Chamber](challenges/forensics/the-castles-hidden-chamber/) | 200 | Muz4mmil | Included |
| [The Secrets of Hogwarts Castle](challenges/forensics/the-secrets-of-hogwarts-castle/) | 350 | Muz4mmil | Included |
| [The Seventh Spire](challenges/forensics/the-seventh-spire/) | 500 | Muz4mmil | Included |
| [Three Clocks](challenges/forensics/three-clocks/) | 350 | Muz4mmil | Included |

### Miscellaneous

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [The Forgotten Handshake](challenges/miscellaneous/the-forgotten-handshake/) | 200 | Muz4mmil | Archival files only |
| [The Goblin’s Debt](challenges/miscellaneous/the-goblins-debt/) | 500 | Ah54n | Included |

### OSINT

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [Between Two Eras](challenges/osint/between-two-eras/) | 350 | Muz4mmil | Archival files only |
| [Binod](challenges/osint/binod/) | 200 | Ah54n | Archival files only |
| [Dead Drop](challenges/osint/dead-drop/) | 500 | Ah54n | Archival files only |
| [Echoes of Olympus](challenges/osint/echoes-of-olympus/) | 350 | Muz4mmil | Archival files only |
| [Operation Spoiled Brackets](challenges/osint/operation-spoiled-brackets/) | 500 | Ah54n | Archival files only |
| [The Professional Footprint](challenges/osint/the-professional-footprint/) | 200 | Syed Muzammil | Archival files only |

### PWN

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [The Forbidden Shelf](challenges/pwn/the-forbidden-shelf/) | 350 | H454N | Included |
| [The Sorting Hat's Permission Slip](challenges/pwn/sorting-hats-permission-slip/) | 200 | H454N | Included |

### Reverse Engineering

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [Ravenclaw's Rotating Runes](challenges/reverse-engineering/ravenclaws-rotating-runes/) | 350 | H454N | Included |
| [Snape's Potion Ledger](challenges/reverse-engineering/snapes-potion-ledger/) | 200 | H454N | Included |
| [The Enchanted Parchment](challenges/reverse-engineering/the-enchanted-parchment/) | 350 | H454N | Included |
| [The Forbidden Payload](challenges/reverse-engineering/the-forbidden-payload/) | 350 | Muz4mmil | Included |

### Web Exploitation

| Challenge | Initial points | Author | Source |
| --- | ---: | --- | --- |
| [Catalog Filter](challenges/web-exploitation/catalog-filter/) | 350 | k4zim | Included |
| [Report Vault](challenges/web-exploitation/report-vault/) | 350 | k4zim | Included |
| [Student Greeter](challenges/web-exploitation/student-greeter/) | 350 | k4zim | Included |

## Archival limitations

Eight solved challenges were created directly in CTFd and had no corresponding source project or author solution in this workspace: Welcome Party, Binod, Dead Drop, The Professional Footprint, Echoes of Olympus, Between Two Eras, Operation Spoiled Brackets, and The Forgotten Handshake. Their packages preserve the event statement and original file(s), if any, without inventing missing source or canonical details.

## Safety

This repository must not contain CTFd event-state exports, `.env` files, Docker volumes, team credentials, or original production infrastructure.

## Note on unpublished challenges

Write-ups for challenges that received no successful solves during the event have not been published.
