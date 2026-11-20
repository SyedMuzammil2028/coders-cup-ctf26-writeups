"""Build the second-stage source from a trusted, validated flag."""

import re


# Keep flags single-line ASCII so they are safe to encode as reversible numeric
# values and cannot influence generated source syntax.
FLAG_PATTERN = re.compile(r"^ACM\{[!-z|~]{1,160}\}$")


def validate_flag(flag):
    """Return *flag* if it is an acceptable team flag, else raise ValueError."""
    if not isinstance(flag, str) or not FLAG_PATTERN.fullmatch(flag):
        raise ValueError("FLAG must match ACM{...} using 1-160 printable ASCII characters")
    return flag


def build_payload(flag):
    """Return a deterministic, valid Python 3.8 second-stage program.

    The flag is represented only as values transformed by a position-dependent
    XOR. It is never interpolated into the generated source as plaintext.
    """
    validate_flag(flag)
    anchor = 45
    stride = 19
    modulus = 67
    runes = [ord(character) ^ (anchor + ((index * stride) % modulus))
             for index, character in enumerate(flag)]
    rune_text = ", ".join(str(value) for value in runes)

    return '''# The castle's archivist used arithmetic, not a spell.
runes = [{runes}]
anchor = {anchor}
stride = {stride}
modulus = {modulus}

flag = ''.join(
    chr(value ^ (anchor + ((index * stride) % modulus)))
    for index, value in enumerate(runes)
)
magic_number = sum(ord(character) for character in flag)

print('The archive stirs. Offer the magic number.')
try:
    offered = int(input('Magic number: ').strip())
except (ValueError, EOFError):
    offered = -1

if offered == magic_number:
    print('The forbidden payload yields:', flag)
else:
    print('The wards remain sealed. Nice try.')
'''.format(runes=rune_text, anchor=anchor, stride=stride, modulus=modulus)
