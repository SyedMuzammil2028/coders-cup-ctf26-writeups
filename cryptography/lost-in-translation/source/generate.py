"""Generate the only public runtime data: the instance's encoded ciphertext."""
import argparse
import base64
import codecs
import json
import os
from pathlib import Path
import sys
import tempfile


def validate_flag(flag: str | None) -> str:
    if not flag or not flag.startswith('ACM{') or not flag.endswith('}'):
        raise ValueError('FLAG must use ACM{...} format.')
    if len(flag) <= 5 or len(flag.encode('utf-8')) > 4096:
        raise ValueError('FLAG must have a nonempty payload and be at most 4096 UTF-8 bytes.')
    if any(character.isspace() or ord(character) < 32 or ord(character) == 127 for character in flag):
        raise ValueError('FLAG must not contain whitespace or control characters.')
    return flag


def encode_flag(flag: str) -> str:
    validated = validate_flag(flag)
    rotated = codecs.encode(validated, 'rot_13')
    reversed_base64 = base64.b64encode(rotated.encode('utf-8')).decode('ascii')[::-1]
    return ' '.join(f'{ord(character):08b}' for character in reversed_base64)


def generate(destination: Path) -> None:
    ciphertext = encode_flag(os.environ.get('FLAG'))
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            json.dump({'ciphertext': ciphertext}, temporary, separators=(',', ':'))
        temporary_path.chmod(0o644)
        temporary_path.replace(destination)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('/tmp/ctf-data/ciphertext.json'))
    arguments = parser.parse_args()
    try:
        generate(arguments.output)
    except (ValueError, OSError, UnicodeError):
        print('Startup failed: FLAG is missing/invalid or ciphertext could not be written.', file=sys.stderr)
        sys.exit(1)
