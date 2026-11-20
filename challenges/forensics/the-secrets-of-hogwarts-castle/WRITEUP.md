
# Organizer write-up — The Secrets of Hogwarts Castle

> Keep this document organizer-only. It contains the plaintext flag and both
> keys. Do not make `docs/`, `scripts/`, or `challenge.yml` web-accessible.

## Intended solution

1. Visit **Hogwarts Castle Archives** and open the photograph gallery.
2. Download the four original files as `castle1.jpg`, `castle2.jpg`,
   `castle3.jpg`, and `castle4.jpg`.
3. Inspect Castle Image 1:

   ```bash
   exiftool castle1.jpg
   ```

   Its `Image Description` contains `archive_pass=oldcastlekey2026`. The same
   description notes that early keys may predate the last restoration. This is
   a plausible but deliberately outdated key.
4. Examine Castle Image 2:

   ```bash
   binwalk castle2.jpg
   binwalk -e castle2.jpg
   ```

   Binwalk identifies a ZIP archive after the ordinary JPEG data. Depending on
   the extractor configuration, it may carve the archive automatically. The
   recovered ZIP holds one encrypted member: `secret.txt`.
5. Try the old key and observe the failure:

   ```bash
   unzip -P oldcastlekey2026 recovered.zip
   ```

6. Inspect Castle Image 3:

   ```bash
   exiftool castle3.jpg
   ```

   Its `Image Description` says the vault credentials changed after the fourth
   tower was restored and directs the reader to the final watchtower record.
7. Inspect Castle Image 4:

   ```bash
   exiftool castle4.jpg
   ```

   Its `Copyright` field contains the current key:
   `archive_pass=castleward2026`.
8. Unlock the recovered archive and read the flag:

   ```bash
   unzip -P castleward2026 recovered.zip
   sed -n '1p' secret.txt
   ```

   The result is:

   ```text
   ACM{n1ne_l1ves_0ne_h1dden_s3cret}
   ```

9. Submit that value to CTFd.

## Alternative when `binwalk -e` cannot carve

Some Binwalk builds report an appended ZIP without automatic extraction. Carve
from the ZIP local-file header using standard Python and `unzip`:

```bash
OFFSET=$(python3 -c "from pathlib import Path; print(Path('castle2.jpg').read_bytes().find(b'PK\\x03\\x04'))")
python3 -c "from pathlib import Path; import sys; p=Path('castle2.jpg').read_bytes(); Path('recovered.zip').write_bytes(p[int(sys.argv[1]):])" "$OFFSET"
unzip -P castleward2026 recovered.zip
sed -n '1p' secret.txt
```

The image remains valid because the ZIP starts after the JPEG `FF D9`
end-of-image marker.

## Intended flag

```text
ACM{m3t4d4t4_4rch1v3_<hash>}
```
