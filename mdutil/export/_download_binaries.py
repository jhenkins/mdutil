"""Download pre-built merman-cli binaries for all supported platforms.

Usage:
    python mdutil/export/_download_binaries.py [--release-url URL] [--output-dir DIR]

Downloads are from GitHub Releases. Each platform gets its own binary in
mdutil/export/_merman_binaries/ with the name expected by MermanRenderer.

Release: https://github.com/Latias94/merman/releases/tag/v0.7.0

SHA256 checksums are verified against sha256sums file after download.
"""

from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

# Maps (os, machine) → (release asset filename, final binary filename)
# Release assets: https://github.com/Latias94/merman/releases/tag/v0.7.0
PLATFORMS = [
    # (release asset, final binary name)
    ("linux", "x86_64", "merman-cli-x86_64-unknown-linux-gnu.tar.xz", "merman-cli-linux-x86_64"),
    ("linux", "aarch64", "merman-cli-aarch64-unknown-linux-gnu.tar.xz", "merman-cli-linux-aarch64"),
    ("darwin", "arm64", "merman-cli-aarch64-apple-darwin.tar.xz", "merman-cli-darwin-arm64"),
    ("darwin", "x86_64", "merman-cli-x86_64-apple-darwin.tar.xz", "merman-cli-darwin-x86_64"),
    ("win32", "AMD64", "merman-cli-x86_64-pc-windows-msvc.zip", "merman-cli-windows-x64.exe"),
    ("win32", "x86_64", "merman-cli-x86_64-pc-windows-msvc.zip", "merman-cli-windows-x64.exe"),
]


def extract_tar_xz(archive: Path, dest_dir: Path) -> Path:
    """Extract a .tar.xz archive, return path to the merman-cli binary inside."""
    with tarfile.open(archive, "r:xz") as tf:
        tf.extractall(dest_dir)
    # Find the binary (first file that looks like it)
    for f in dest_dir.rglob("*"):
        if f.is_file() and "merman-cli" in f.name and not f.name.endswith((".md", ".txt", ".json")):
            return f
    raise FileNotFoundError("merman-cli binary not found in archive")


def extract_zip(archive: Path, dest_dir: Path) -> Path:
    """Extract a .zip archive, return path to the merman-cli binary inside."""
    with zipfile.ZipFile(archive, "r") as zf:
        zf.extractall(dest_dir)
    for f in dest_dir.rglob("*"):
        if f.is_file() and "merman-cli" in f.name and not f.name.endswith((".md", ".txt", ".json")):
            return f
    raise FileNotFoundError("merman-cli binary not found in archive")


def verify_sha256(binary_path: Path, expected_sha256: str) -> bool:
    """Verify SHA256 checksum of a binary file.

    Args:
        binary_path: Path to the binary file.
        expected_sha256: Expected SHA256 hash.

    Returns:
        True if checksum matches.

    Raises:
        RuntimeError: If checksum does not match.
    """
    import hashlib

    sha256 = hashlib.sha256()
    with open(binary_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    actual_sha256 = sha256.hexdigest()
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            f"SHA256 mismatch for {binary_path.name}:\n"
            f"  Expected: {expected_sha256}\n"
            f"  Actual:   {actual_sha256}"
        )
    return True


def download_binary(url: str, dest: Path, archive_format: str) -> None:
    """Download and extract a merman-cli binary from a release URL.

    Args:
        url: Download URL for the archive.
        dest: Destination directory for the extracted binary.
        archive_format: 'tar.xz' or 'zip'.
    """
    import urllib.request

    print(f"  Downloading: {url}")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        urllib.request.urlretrieve(url, tmp / "archive")

        if archive_format == "tar.xz":
            binary = extract_tar_xz(tmp / "archive", tmp / "extracted")
        elif archive_format == "zip":
            binary = extract_zip(tmp / "archive", tmp / "extracted")
        else:
            raise ValueError(f"Unknown archive format: {archive_format}")

        # Copy binary to destination
        shutil.copy2(binary, dest)

        # Make executable on Unix
        if sys.platform != "win32":
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Clean up extracted directory
        if (tmp / "extracted").exists():
            shutil.rmtree(tmp / "extracted")


def load_sha256sums(bin_dir: Path) -> dict[str, str]:
    """Load SHA256 checksums from sha256sums file.

    Returns:
        Dict mapping filename → expected SHA256 hash.
    """
    sums_file = bin_dir / "sha256sums"
    if not sums_file.exists():
        return {}

    sums = {}
    with open(sums_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                sha256, filename = parts
                sums[filename] = sha256
    return sums


def main() -> None:
    parser = argparse.ArgumentParser(description="Download merman-cli binaries")
    parser.add_argument(
        "--release-url",
        default="https://github.com/Latias94/merman/releases/download/v0.7.0",
        help="Base URL for release assets (default: GitHub v0.7.0)",
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

    # Load expected checksums
    expected_sums = load_sha256sums(bin_dir)

    for os_name, machine, asset_name, final_name in PLATFORMS:
        final_path = bin_dir / final_name
        expected_sha256 = expected_sums.get(final_name)

        if final_path.exists() and expected_sha256:
            try:
                verify_sha256(final_path, expected_sha256)
                print(f"  Skipping (verified): {final_name}")
                continue
            except RuntimeError as e:
                print(f"  ⚠ Checksum mismatch for {final_name}: {e}")
                print(f"    Re-downloading...")
                final_path.unlink()

        url = f"{args.release_url}/{asset_name}"
        try:
            if asset_name.endswith(".tar.xz"):
                archive_format = "tar.xz"
            elif asset_name.endswith(".zip"):
                archive_format = "zip"
            else:
                archive_format = "tar.xz"

            download_binary(url, final_path, archive_format)

            # Verify checksum
            if expected_sha256:
                verify_sha256(final_path, expected_sha256)
                print(f"  ✓ Downloaded and verified: {final_name}")
            else:
                print(f"  ✓ Downloaded: {final_name}")
        except Exception as e:
            print(f"  ✗ Failed: {final_name} — {e}")


if __name__ == "__main__":
    main()
