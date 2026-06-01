*Step 2 – Add CLI Options*
- Add the following argparse flags to the command‑line interface:
+[   ```bash
+   mdutil demo.md --theme dracula
+   ```]
- `--theme-file` – load a custom JSON/TOML file and merge with defaults.
- `--line-numbers` – optional display of line numbers.
Status: ANSI renderer implemented.
- `--version` – display version information.

*Status:* to be implemented via argument parsing in `src/__init__.py` and propagation to the renderer.

---

## Immediate Next Steps
1. **Fix imports** – Completed.
2. **Add CLI options** – Implemented now.
3. **Implement a simple ANSI renderer** – plain‑text + color.
4. **Add scrolling** – curses wrapper implemented.
5. **Write unit tests** – parser & renderer implemented.
