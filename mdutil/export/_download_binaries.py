"""Download pre-built merman-cli binaries for all supported platforms.

Usage:
    python mdutil/export/_download_binaries.py [--release-url URL] [--output-dir DIR]

Downloads are from a configurable release URL (default: GitHub Releases).
Each platform gets its own binary in mdutil/export/_merman_binaries/.
"""

from __future__ import annotations

import os
import sys
import stat
import argparse
from pathlib import Path

# Supported (os, machine) → binary filename
PLATFORMS = [
    ("linux", "x86_64", "merman-cli-linux-x86_64"),
    ("linux", "aarch64", "merman-cli-linux-aarch64"),
    ("darwin", "arm64", "merman-cli-darwin-arm64"),
    ("darwin", "x86_64", "merman-cli-darwin-x86_64"),
    ("win32", "AMD64", "merman-cli-windows-x64.exe"),
    ("win32", "x86_64", "merman-cli-windows-x64.exe"),
]


def download_binary(url: str, dest: Path) -> None:
    """Download a binary from URL to dest path.

    Args:
        url: Download URL (GitHub Release asset URL or custom URL).
        dest: Destination file path.
    """
    import urllib.request

    print(f"  Downloading: {url} → {dest}")
    urllib.request.urlretrieve(url, dest)
    # Make executable on Unix
    if sys.platform != "win32":
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download merman-cli binaries")
    parser.add_argument(
        "--release-url",
        default="https://github.com/example/merman-cli/releases/latest/download",
        help="Base URL for release assets (default: GitHub latest download)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for binaries (default: mdutil/export/_merman_binaries)",
    )
    args = parser.parse_args()

    if args.output_dir:
        bin_dir = Path(args.output_dir)
    else:
        bin_dir = Path(__file__).resolve().parent / "_merman_binaries"
    bin_dir.mkdir(parents=True, exist_ok=True)

    for os_name, machine, binary_name in PLATFORMS:
        url = f"{args.release_url}/{binary_name}"
        dest = bin_dir / binary_name
        if dest.exists():
            print(f"  Skipping (exists): {binary_name}")
            continue
        try:
            download_binary(url, dest)
            print(f"  ✓ Downloaded: {binary_name}")
        except Exception as e:
            print(f"  ✗ Failed: {binary_name} — {e}")


if __name__ == "__main__":
    main()
