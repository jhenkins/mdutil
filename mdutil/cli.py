"""Command-line interface for mdutil."""

from __future__ import annotations

import argparse
import configparser
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TypedDict, cast


class _AlignedHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """HelpFormatter that aligns option names in the options section."""

    def __init__(self, prog: str, indent_increment: int = 2,
                 max_help_position: int = 32):
        super().__init__(prog, indent_increment, max_help_position)

    def _metavar_formatter(self, action, default_metavar):
        """Custom metavar formatter that returns tuples matching argparse's expectations."""
        def formatter(nargs, flag_string=None):
            if nargs == 0:
                return ("",)
            elif nargs == argparse.REMAINDER:
                return ("...",)
            elif nargs == "*":
                return (default_metavar, default_metavar)
            elif nargs == "+":
                return (default_metavar, default_metavar)
            elif nargs == "?":
                return (default_metavar,)
            elif isinstance(nargs, int):
                return (default_metavar,) * nargs
            else:
                return (default_metavar,)
        return formatter

    def _format_args(self, action, default_metavar):
        """Handle nargs==0 case and delegate to parent."""
        if action.nargs == 0:
            return ''
        return super()._format_args(action, default_metavar)

    def _fill_text(self, text, width, indent):
        """Fill text, aligning continuation lines."""
        lines = []
        for paragraph in text.split("\n"):
            lines.append(paragraph)
        return super()._fill_text("\n".join(lines), width, indent)


from . import __version__
from .config import default_config_path, ensure_config_file, load_config
from .display import run_interactive_viewer
from .parser import parse_markdown
from .reader import read_input
from .renderer import render
from .themes import syntax_theme_names, theme_names


class RuntimeOptions(TypedDict):
    theme: str
    theme_file: str | None
    syntax_theme: str
    line_numbers: bool
    quiet: bool
    status_bar_normal: str | None
    status_bar_insert: str | None


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the mdutil command-line parser."""
    arg_parser = argparse.ArgumentParser(
        prog="mdutil",
        description="Terminal Markdown viewer with ANSI rendering.",
        formatter_class=_AlignedHelpFormatter,
    )
    arg_parser.add_argument(
        "files",
        nargs="*",
        help="Markdown files to read. Use '-' or omit files to read stdin.",
    )
    arg_parser.add_argument(
        "--list",
        action="store_true",
        help="List available markdown files in the current directory and exit",
    )
    arg_parser.add_argument(
        "--syntax-theme",
        choices=syntax_theme_names(),
        help="Choose Pygments syntax style for code highlighting",
    )
    arg_parser.add_argument(
        "--theme",
        choices=theme_names(),
        help="Choose built-in theme",
    )
    arg_parser.add_argument("--theme-file", help="Path to JSON/TOML theme file")
    arg_parser.add_argument("--config", help="Path to an alternate INI configuration file")
    arg_parser.add_argument(
        "--generate-config",
        action="store_true",
        help="Create a starter configuration file with current defaults and exit",
    )
    arg_parser.add_argument(
        "--line-numbers",
        action="store_true",
        default=None,
        help="Show line numbers",
    )
    arg_parser.add_argument(
        "--quiet",
        action="store_true",
        default=None,
        help="Suppress rendered output",
    )
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

    if args.list:
        import glob
        md_files = sorted(glob.glob("*.md"))
        if md_files:
            print("Markdown files in current directory:")
            for f in md_files:
                print(f)
        else:
            print("No markdown files found.")
        return 0

    try:
        config_path = Path(args.config) if args.config else default_config_path()
        ensure_config_file(config_path)
        config = load_config(config_path)
    except (OSError, UnicodeError, configparser.Error, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.generate_config:
        print(f"Configuration file ready: {config_path}")
        return 0

    runtime = _resolve_runtime_options(args, config, arg_parser)

    if not args.files and sys.stdin.isatty():
        arg_parser.print_usage(sys.stderr)
        print("mdutil: error: provide a file path or pipe Markdown on stdin", file=sys.stderr)
        return 2

    files = args.files or [None]
    for file_path in files:
        try:
            content = read_input(file_path)
            parsed = parse_markdown(content)
            interactive = _should_run_interactive(file_path, runtime["quiet"])
            output = render(
                parsed,
                theme=runtime["theme"],
                theme_file=runtime["theme_file"],
                syntax_theme=runtime["syntax_theme"],
                line_numbers=runtime["line_numbers"] and not interactive,
                quiet=runtime["quiet"],
            )
            if interactive:
                run_interactive_viewer(
                    content.splitlines(),
                    line_numbers=runtime["line_numbers"],
                    document_name=Path(file_path).name if file_path else None,
                    save_path=file_path,
                    theme=runtime["theme"],
                    theme_file=runtime["theme_file"],
                    status_bar_normal=runtime["status_bar_normal"],
                    status_bar_insert=runtime["status_bar_insert"],
                )
            elif not runtime["quiet"] and output:
                print(output)
        except KeyboardInterrupt:
            return 130
        except (OSError, UnicodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    return 0


def _resolve_runtime_options(
    args: argparse.Namespace,
    config: dict[str, object],
    arg_parser: argparse.ArgumentParser,
) -> RuntimeOptions:
    """Merge built-in/config defaults with explicit CLI options."""
    theme = cast(str, args.theme if args.theme is not None else config["theme"])
    if theme not in theme_names():
        valid = ", ".join(theme_names())
        arg_parser.error(f"invalid theme in configuration: {theme!r} (choose from {valid})")

    syntax_theme = cast(
        str,
        args.syntax_theme if args.syntax_theme is not None else config["syntax_theme"],
    )
    if syntax_theme not in syntax_theme_names():
        valid = ", ".join(syntax_theme_names())
        arg_parser.error(f"invalid syntax theme in configuration: {syntax_theme!r} (choose from {valid})")

    theme_file = cast(
        str | None,
        args.theme_file if args.theme_file is not None else config["theme_file"],
    )
    line_numbers = cast(
        bool,
        args.line_numbers if args.line_numbers is not None else config["line_numbers"],
    )
    quiet = cast(bool, args.quiet if args.quiet is not None else config["quiet"])
    status_bar_normal = cast(str | None, config["status_bar_normal"])
    status_bar_insert = cast(str | None, config["status_bar_insert"])

    return {
        "theme": theme,
        "theme_file": theme_file,
        "syntax_theme": syntax_theme,
        "line_numbers": line_numbers,
        "quiet": quiet,
        "status_bar_normal": status_bar_normal,
        "status_bar_insert": status_bar_insert,
    }


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
