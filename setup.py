"""Build hook: filter merman-cli binaries to current platform, then delegate to setuptools.

Run via:
    pip install --no-build-isolation .

This keeps the installed package at ~33MB instead of ~150MB by only shipping
the binary that matches the build host's platform.

Without --no-build-isolation, pip's isolated build environment cannot execute
this script, so all platform binaries would be included.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path

from setuptools import setup

# Platform → generic merman-cli binary filename
_PLATFORM_GENERIC_NAME = {
    ("linux", "x86_64"): "merman-cli",
    ("linux", "aarch64"): "merman-cli",
    ("darwin", "arm64"): "merman-cli",
    ("darwin", "x86_64"): "merman-cli",
    ("win32", "AMD64"): "merman-cli.exe",
    ("win32", "x86_64"): "merman-cli.exe",
}

# Generic name → (os, machine) → source binary name
_PLATFORM_SOURCE_NAME = {
    "merman-cli": {
        ("linux", "x86_64"): "merman-cli-linux-x86_64",
        ("linux", "aarch64"): "merman-cli-linux-aarch64",
        ("darwin", "arm64"): "merman-cli-darwin-arm64",
        ("darwin", "x86_64"): "merman-cli-darwin-x86_64",
    },
    "merman-cli.exe": {
        ("win32", "AMD64"): "merman-cli-windows-x64.exe",
        ("win32", "x86_64"): "merman-cli-windows-x64.exe",
    },
}


def _detect_platform() -> tuple[str, str]:
    return (sys.platform, platform.machine())


def _get_source_name(os_name: str, machine: str) -> str | None:
    generic = _PLATFORM_GENERIC_NAME.get((os_name, machine))
    if generic is None:
        return None
    return _PLATFORM_SOURCE_NAME[generic].get((os_name, machine))


def _filter_binaries(source_dir: Path) -> None:
    """Keep only the platform-matching binary, rename to generic name.

    Idempotent: if the generic binary already exists, the filter has already
    run and we just need to clean up non-matching platform binaries.
    """
    os_name, machine = _detect_platform()
    generic_name = _PLATFORM_GENERIC_NAME.get((os_name, machine))
    source_name = _get_source_name(os_name, machine)

    bin_dir = source_dir / "mdutil" / "export" / "_merman_binaries"
    if not bin_dir.is_dir():
        print(f"Warning: {bin_dir} not found", file=sys.stderr)
        return

    # Idempotent: if generic binary already exists, skip the copy step
    # (it was already done by a prior run). We still clean up non-matching binaries.
    generic_path = bin_dir / generic_name if generic_name else None
    if generic_name and generic_path and generic_path.exists():
        # Clean up non-matching platform binaries
        for f in bin_dir.iterdir():
            if f.name in ("__init__.py", "sha256sums", "__pycache__"):
                continue
            if f.name == generic_name:
                continue
            f.unlink()
        print(f"Binary already filtered: {generic_name}")
        return

    if source_name is None:
        print(
            f"Warning: unsupported platform {os_name}/{machine}. "
            f"No merman-cli binary will be included.",
            file=sys.stderr,
        )
        for f in bin_dir.iterdir():
            if f.name not in ("__init__.py", "sha256sums", "__pycache__"):
                f.unlink()
        return

    source_path = bin_dir / source_name
    generic_path = bin_dir / generic_name

    # Remove any existing generic binary (from prior runs)
    if generic_path.exists():
        generic_path.unlink()

    if not source_path.exists():
        print(
            f"Warning: source binary {source_name} not found in {bin_dir}",
            file=sys.stderr,
        )
        # Remove all binaries — can't ship without a working binary
        for f in bin_dir.iterdir():
            if f.name not in ("__init__.py", "sha256sums", "__pycache__"):
                f.unlink()
        return

    # Copy matching binary to generic name
    shutil.copy2(source_path, generic_path)

    # Preserve executable bit on Unix
    if os_name != "win32":
        generic_path.chmod(generic_path.stat().st_mode | 0o111)

    # Remove all other platform-specific binaries
    for f in bin_dir.iterdir():
        if f.name in ("__init__.py", "sha256sums", "__pycache__"):
            continue
        if f.name == generic_name:
            continue
        f.unlink()

    print(f"Kept binary: {generic_name} ({os_name}/{machine})")


# Run the filter BEFORE setuptools does anything
_filter_binaries(Path(__file__).resolve().parent)

setup()
