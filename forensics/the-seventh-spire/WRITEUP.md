
# Organizer write-up — The Seventh Spire

Keep this solution private until ACM Coder's Cup '26 has ended.

## 1. Inspect the capture

```bash
file seventh-spire.pcap
capinfos seventh-spire.pcap
wireshark seventh-spire.pcap
```

The capture contains Ethernet/IP traffic, UDP broadcasts on port 41842, and
ordinary HTTP/1.1 conversations on TCP port 80. It is a simulated castle
network, not a radio or cellular capture.

## 2. Find the unauthorized tower

Use this Wireshark display filter:

```text
udp.port == 41842
```

The first control broadcast is a `WARDEN-REG/3` record. Its `approved` list is:

```text
AST-014,NWT-221,RVN-332,WRP-418
```

The `SPIRE-ANN/2` broadcasts include one ID outside that trusted list:

```text
VLT-707
```

Packets 14 and 15 are its announcements. It is uniquely unauthorized because
the registry is captured in the same broadcast protocol.

## 3. Correlate the affected device

Filter HTTP traffic associated with that identifier:

```text
http.user_agent contains "VLT-707"
```

Packet 149 shows the profile request from the affected device. Its User-Agent
contains these evidence values:

```text
unit=folio-amber
serial=SLT-8B19-ARC
relay=VLT-707
```

The `relay` field matches the unauthorized broadcast identifier.

## 4. Recover the encryption recipe

The response at packet 151 is a normal HTTP JSON response. Filter it with:

```text
http.response && frame contains "key_recipe"
```

It documents the complete recovery method:

```text
cipher=xor-repeat
encoding=base64
key_recipe=sha256_utf8(serial + '|' + tower)[:8]
identifier_order=serial|tower
fragment_order=part ascending
```

This describes an eight-byte raw SHA-256 digest prefix; it does not disclose
the derived key itself.

## 5. Reassemble the transfer

Filter the HTTP POSTs:

```text
http.request.method == "POST" && http.request.uri == "/archive/dispatch"
```

Packets 160, 171, 182, 193, 204, and 215 contain one form-encoded transfer.
Each body includes `transfer=MEM-ORIEL-72`, `part`, `total=6`, and `data`.
Sort by the explicit numeric `part` field and concatenate the six `data`
values. The result is Base64 ciphertext, not plaintext flag data.

An organizer-safe reconstruction check is provided by the private solver:

```bash
python3 organizer/solver.py seventh-spire.pcap
```

## 6. Decode and decrypt

The equivalent core Python operation is:

```python
import base64
import hashlib

serial = "SLT-8B19-ARC"
tower = "VLT-707"
key = hashlib.sha256(f"{serial}|{tower}".encode("utf-8")).digest()[:8]
ciphertext = base64.b64decode(reassembled_data)
plaintext = bytes(value ^ key[index % len(key)] for index, value in enumerate(ciphertext))
print(plaintext.decode("utf-8"))
```

The recovered static flag is:

```text
ACM{spire_registry_breach_unraveled}
```

All teams submit this same flag to CTFd. There is no container, instance, or
freshness token for this challenge.

## Intended flag

```text
ACM{spire_registry_breach_unraveled}
```
