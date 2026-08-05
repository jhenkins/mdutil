"""Verify SHA256 checksums of bundled merman-cli binaries.

Usage:
    python mdutil/export/_verify_binaries.py [--output-dir DIR]

Checks each binary in _merman_binaries/ against sha256sums.
Exits with code 0 if all match, 1 if any fail.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def load_sha256sums(bin_dir: Path) -> dict[str, str]:
    """Load SHA256 checksums from sha256sums file."""
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


def verify_sha256(binary_path: Path, expected_sha256: str) -> bool:
    """Verify SHA256 checksum of a binary file."""
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify merman-cli binary checksums")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Binary directory (default: mdutil/export/_merman_binaries)",
    )
    args = parser.parse_args()

    if args.output_dir:
        bin_dir = Path(args.output_dir)
    else:
        bin_dir = Path(__file__).resolve().parent / "_merman_binaries"

    if not bin_dir.is_dir():
        print(f"Error: Directory not found: {bin_dir}", file=sys.stderr)
        return 1

    expected_sums = load_sha256sums(bin_dir)
    if not expected_sums:
        print("No sha256sums file found.", file=sys.stderr)
        return 1

    errors = 0
    for filename, expected_sha256 in expected_sums.items():
        binary_path = bin_dir / filename
        if not binary_path.exists():
            print(f"  ✗ Missing: {filename}")
            errors += 1
            continue

        try:
            verify_sha256(binary_path, expected_sha256)
            print(f"  ✓ {filename}")
        except RuntimeError as e:
            print(f"  ✗ {filename}: {e}")
            errors += 1

    if errors:
        print(f"\n{errors} verification failure(s).")
        return 1

    print(f"\nAll {len(expected_sums)} binaries verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
