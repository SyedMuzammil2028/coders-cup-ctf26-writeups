# Write-up — Operation Spoiled Brackets

## Step 1 — Inspect the image

The supplied `lapi.png` contains useful metadata. Run:

```sh
exiftool lapi.png
```

The metadata points to Xenon and his Blogger page.

## Step 2 — Find Xenon’s blog

Open:

```text
https://xenonafterhours.blogspot.com/
```

The post **Before Everything Went Wrong** mentions *Night Shift Sessions* and
the incident around `02:17`. Follow the Night Shift Sessions link.

## Step 3 — Follow Session 0217

On the Night Shift Sessions site, inspect session `0217` and the **People**
section. Mira Vale’s profile links to her portfolio:

```text
https://mira-vale-portfolio.tpgamer354.workers.dev/
```

## Step 4 — Recover the archive password

Mira’s portfolio contains **Snapshot Locker**, which links to a password-
protected archive. Her old archive notes describe the password format:

- Night Shift Sessions → `NSS`
- Session number → `0217`
- Mira Vale → `MV`

Combine the uppercase values with hyphens:

```text
NSS-0217-MV
```

## Step 5 — Extract the evidence

Open `evidence_0217.7z` with 7-Zip using that password. The extracted text
file contains the flag:

```text
ACM{the_ghost_behind_the_brackets}
```

## Intended flag

```text
ACM{the_ghost_behind_the_brackets}
```
