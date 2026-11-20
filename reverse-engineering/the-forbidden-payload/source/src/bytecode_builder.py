"""Compile generated loader source into deterministic CPython 3.8 bytecode."""

import os
import py_compile
import tempfile
from pathlib import Path


def compile_loader(loader_source, output_path):
    """Compile *loader_source* to *output_path*, leaving no source beside it."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    descriptor, temporary_source = tempfile.mkstemp(
        prefix="forbidden-payload-", suffix=".py", text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(loader_source)
        py_compile.compile(
            temporary_source,
            cfile=str(output),
            dfile="forbidden_archive.py",
            doraise=True,
            invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH,
        )
    finally:
        try:
            os.unlink(temporary_source)
        except FileNotFoundError:
            pass

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("bytecode compilation did not produce a non-empty artifact")
    return output
