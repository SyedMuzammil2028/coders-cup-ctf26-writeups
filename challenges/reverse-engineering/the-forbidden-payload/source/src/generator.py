"""Generate the team-specific bytecode artifact at trusted-container startup."""

import argparse
import base64
import os
import py_compile
from pathlib import Path

from .bytecode_builder import compile_loader
from .payload_builder import build_payload, validate_flag


FRAGMENT_NAMES = (
    "owl_ink", "moon_salt", "quiet_ash", "raven_quill", "dusk_thread",
    "mirror_dust", "tower_chalk", "amber_wax", "frosted_vellum",
    "cinder_key", "starless_seal",
)


def split_fragments(encoded_payload, count=len(FRAGMENT_NAMES)):
    """Split Base64 evenly and deterministically into a fixed number of pieces."""
    if count < 2:
        raise ValueError("at least two fragments are required")
    base, remainder = divmod(len(encoded_payload), count)
    return [encoded_payload[index * base + min(index, remainder):
                            (index + 1) * base + min(index + 1, remainder)]
            for index in range(count)]


def build_loader(payload_source):
    """Wrap a second-stage script in an intentionally readable obfuscated loader."""
    encoded = base64.b64encode(payload_source.encode("utf-8")).decode("ascii")
    fragments = split_fragments(encoded)
    assignments = "\n".join(
        "{name} = {piece!r}".format(name=name, piece=piece)
        for name, piece in zip(FRAGMENT_NAMES, fragments)
    )
    joined = " +\n    ".join(FRAGMENT_NAMES)
    return '''# Recovered from a restricted shelf. No network, files, or commands involved.
import base64

{assignments}

# Ink stains from an unrelated inventory calculation.
cauldron_count = (17 * 23) - 390
catalogue_note = 'do not wake the portraits; inventory only'
if cauldron_count == 1 and catalogue_note:
    print('The archive notices your presence...')

sealed_scroll = (
    {joined}
)
hidden_words = base64.b64decode(sealed_scroll.encode('ascii')).decode('utf-8')
exec(compile(hidden_words, '<forbidden-payload>', 'exec'))
'''.format(assignments=assignments, joined=joined)


def trusted_flag(environment=None, development_flag=None, development=False):
    """Read FLAG safely; dev input is explicit and cannot override production."""
    environment = os.environ if environment is None else environment
    production_flag = environment.get("FLAG")
    if production_flag is not None:
        if development_flag is not None:
            raise ValueError("refusing --flag while FLAG is set")
        return validate_flag(production_flag)
    if development and development_flag is not None:
        return validate_flag(development_flag)
    raise ValueError("FLAG is required; use --dev --flag only for local development")


def generate_artifact(flag, output_path):
    """Build a pyc from *flag* without retaining plaintext source files."""
    payload = build_payload(validate_flag(flag))
    loader = build_loader(payload)
    return compile_loader(loader, output_path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a team-specific malware.pyc")
    parser.add_argument("--output", type=Path, required=True, help="target malware.pyc path")
    parser.add_argument("--dev", action="store_true", help="allow an explicit dummy --flag only when FLAG is absent")
    parser.add_argument("--flag", help="dummy development flag; never use in production")
    arguments = parser.parse_args(argv)
    try:
        flag = trusted_flag(development_flag=arguments.flag, development=arguments.dev)
        artifact = generate_artifact(flag, arguments.output)
    except (OSError, ValueError, RuntimeError, py_compile.PyCompileError) as error:
        # Never interpolate a flag into an error or startup log.
        parser.error(str(error))
    print("generated {} bytes at {}".format(artifact.stat().st_size, artifact))


if __name__ == "__main__":
    main()
