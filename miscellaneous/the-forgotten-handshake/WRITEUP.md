# Write-up availability — The Forgotten Handshake

The original wireless capture is preserved as `hot-03.cap` in
`challenge-files/`. Analyse it in Wireshark to identify the SSID and EAPOL
four-way handshake, then use a lawful offline WPA recovery workflow (for
example, `aircrack-ng` with the challenge-specific candidate list) against
that capture. Format the recovered key as `ACM{recovered_password}`.

Command to be use is: aircrack-ng -w /usr/share/wordlists/rockyou.txt hot.cap

Recoverded key is: password123

final flag: ACM{password123}

The exported CTFd record has the challenge description and capture but no
author source, wordlist, or canonical write-up. This release does not invent
those missing materials.

## Intended flag

```text
ACM{password123}
```
