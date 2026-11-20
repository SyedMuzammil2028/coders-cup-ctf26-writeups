
# Organizer write-up

Keep this document private during the competition.

## Intended workflow

### 1. Download the evidence

```bash
wget http://HOST:PORT/challenge.jpg
file challenge.jpg
```

The file is a genuine 1600×900 JPEG.

### 2. Inspect metadata

```bash
exiftool challenge.jpg
```

Relevant output includes:

```text
City                            : ACM{f4k3_fl4g}
User Comment                    : The first seal is a deception. The passphrase is written among the image's printable strings. Search for PASSWORD.
```

The City value is the first static decoy. The explicit comment tells the
player both that it is deceptive and what to inspect next.

### 3. Inspect printable strings

```bash
strings -a challenge.jpg | grep 'ACM{'
```

The output includes the second labelled decoy:

```text
SECOND_SEAL=ACM{F4k3_Fl4g}
```

It is also not accepted by CTFd. Find the password marker:

```bash
strings -a challenge.jpg | grep '^PASSWORD='
```

The released carrier produces:

```text
PASSWORD=archway-a4-jTeQbyUF-8mOu
```

The passphrase is already plaintext; do not Base64-decode this marker.

### 4. Extract the real payload

```bash
steghide extract \
  -sf challenge.jpg \
  -xf flag.txt \
  -p 'archway-a4-jTeQbyUF-8mOu' \
  -f
```

The recovered filename is `flag.txt`. It contains only Base64. For the local
dummy instance it contains:

```text
QUNNe2hpZGRlbl9jaGFtYmVyX2xvY2FsX3Rlc3R9
```

### 5. Decode the team flag

```bash
base64 -d flag.txt
```

For the local test instance the output is:

```text
ACM{hidden_chamber_local_test}
```

In competition, the output is the exact team-specific flag injected by CTFd.
Only this final, steghide-extracted value follows the complete evidence chain;
the two earlier flags are explicitly identified as seals and deceptions.

## Independent solver

The private solver uses the final artifact only. It reads real metadata,
locates printable markers, reads the plaintext password, invokes steghide, and decodes
the extracted payload. It never reads `FLAG`:

```bash
python3 organizer/solver.py challenge.jpg
```

The automated two-instance test compares this recovered value with each dummy
container's expected flag outside the solver.

## Intended flag

```text
ACM{d33p_st3g4n0gr4phy_<hash>}
```
