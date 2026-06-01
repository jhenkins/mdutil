"""Command-line interface for mdutil."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__
from .display import run_interactive_viewer
from .parser import parse_markdown
from .reader import read_input
from .renderer import render
from .themes import DEFAULT_THEME, theme_names


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the mdutil command-line parser."""
    arg_parser = argparse.ArgumentParser(
        prog="mdutil",
        description="Terminal Markdown viewer with ANSI rendering.",
    )
    arg_parser.add_argument(
        "files",
        nargs="*",
        help="Markdown files to read. Use '-' or omit files to read stdin.",
    )
    arg_parser.add_argument(
        "--theme",
        default=DEFAULT_THEME,
        choices=theme_names(),
        help="Choose built-in theme",
    )
    arg_parser.add_argument("--theme-file", help="Path to JSON/TOML theme file")
    arg_parser.add_argument("--line-numbers", action="store_true", help="Show line numbers")
    arg_parser.add_argument("--quiet", action="store_true", help="Suppress rendered output")
    arg_parser.add_argument(
        "--version",
        action="version",
        version=f"mdutil {__version__}",
        help="Show version",
    )
    return arg_parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the mdutil CLI and return a process exit code."""
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args(argv)

    if not args.files and sys.stdin.isatty():
        arg_parser.print_usage(sys.stderr)
        print("mdutil: error: provide a file path or pipe Markdown on stdin", file=sys.stderr)
        return 2

    files = args.files or [None]
    for file_path in files:
        try:
            content = read_input(file_path)
            parsed = parse_markdown(content)
            output = render(
                parsed,
                theme=args.theme,
                theme_file=args.theme_file,
                line_numbers=args.line_numbers,
                quiet=args.quiet,
            )
            if _should_run_interactive(file_path, args.quiet):
                run_interactive_viewer(output.splitlines())
            elif not args.quiet and output:
                print(output)
        except KeyboardInterrupt:
            return 130
        except (OSError, UnicodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    return 0


def _should_run_interactive(file_path: str | None, quiet: bool) -> bool:
    """Return True when a real file should open in the interactive TTY viewer."""
    return bool(
        not quiet
        and file_path not in (None, "-")
        and sys.stdout.isatty()
    )


def run() -> str:
    """Backward-compatible helper that renders argv[1] or stdin and returns output."""
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    content = read_input(file_path)
    parsed = parse_markdown(content)
    output = render(parsed)
    print(output)
    return output


if __name__ == "__main__":
    raise SystemExit(main())
