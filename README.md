# mdutil

A simple and comfortable Markdown viewer and editor for terminal written in Python.

## The story behind this project

Firstly - a word of warning:

This is a test project that has been created with the help of AI. If you don't like that, then please
ignore this project. If you find the software useful, feel free to use it. Due to the sandbox nature 
of this project, it is unlikely that I will entertain any pull requests (unless there is something to
be learned from it, of course).

Are you still here?  OK, grab a brew and let's carry on! :-D

The following tools and LLM's were used so far (more might be used as time goes on):

* Hermes Agent (https://github.com/NousResearch/hermes-agent)
* GPT 5.5 (via openai-codex)
* Gemma 4 12B (via self-hosted inference server running llama.cpp)

The intention behind this project wasn't neccessarily to create a functional piece of software (although I 
dare say that it is already pretty functional as a Markdown reader), but to learn about doing functional 
coding with AI. I claim no ability as a programmer, program designer or software architect - my background
is physical network infrastructure and server hardware. Therefore this project is purely to see what can be
done with AI and the tools available at the moment. 

While I was playing with this project, I found that I had to use a cloud-based AI provider. The main reason 
for this was that my local Ollama instance did not work so well, and constantly ran out of context space 
causing agent timeouts and loads of time wasted. So, in order to at least get something done and learn the 
ropes with Hermes, I decided to use my ChatGPT Plus account with the GPT 5.5 model. This worked  quite well, 
and I hope to be able to set up a local LLM engine to work as well as this (I'll settle for 60%-80%
as good). I am working at using llama.cpp instead, but that's an adventure for another day. 

## Where we are today

We currently have a functional Markdown reader and editor with syntax highlighting, themes, and a prompt-toolkit
interactive view. File-backed sessions support raw Markdown editing, explicit saves, dirty-buffer protection,
copy/paste helpers, and mode-aware search. We also have a very simple ini-style configuration file that you can
edit to make your choice of theme and a few other things permanent. The (very) rough roadmap is visible in the
mdutil-specification.md document.

## Quick Overview

- Read markdown documents with syntax highlighting
- Edit file-backed Markdown interactively with normal/insert modes
- Search in normal mode with `/`, then navigate matches with `n` and `N`
- Search while editing with `Ctrl-/`; literal `/` remains text input in insert mode
- Highlight visible search matches in the rendered preview
- Multiple theme support (default, dracula, one-dark, etc.)
- ANSI color output for terminal
- Supports file input or stdin

## Interactive controls

When stdout is a TTY and a file path is provided, `mdutil` opens the interactive viewer/editor.

- Normal mode renders the Markdown preview. Use `i` to enter insert/edit mode, `q` to quit when unmodified, and `!q` to discard unsaved changes.
- Insert/edit mode edits the raw Markdown buffer. Use Escape to return to normal mode and Ctrl-S to save file-backed changes explicitly.
- Search keys are mode-aware and shown in the bottom status bar: `/` searches from normal mode, `Ctrl-/` searches while editing, and `n` / `N` move between matches.
- Search matches are highlighted in the rendered preview.

---

## Installation

### Quick Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/mdutil.git
cd mdutil

# Install from source
pip install .

# Or install in editable mode (recommended for development)
pip install -e .
```

### Manual Installation

```bash
# If you have a local copy
cd path/to/mdutil
pip install .
```

### Direct Python Usage (No Installation)

```bash
# Run directly from source directory
python -m mdutil your_file.md
```

---

## Usage Examples

### Display a markdown file

```bash
mdutil your_document.md
```

### Read from stdin

```bash
echo -e "# Hello World\n\nSome *markdown* text." | mdutil -
```

### With syntax highlighting

```bash
mdutil your_document.md  # Shows with colors
```

### Quiet mode

```bash
mdutil your_document.md --quiet
```

---

## Demo

```bash
# Create a test markdown file
mkdir -p target
echo -e "# Hello World\n\nSome *markdown* text.\n\nUse **bold** and `code`." > target/demo.md

# Display the file
cd target
mdutil demo.md
```

Expected output:
```
# Hello World

Some markdown text.

Use bold and code.
```

---

## Requirements
- Python 3.11 or higher
- Runtime dependencies are declared in `pyproject.toml`:
  - `markdown>=3.0`
  - `Pygments>=2.0`
  - `prompt-toolkit>=3.0`

---

## Versioning and Release Strategy

mdutil follows Semantic Versioning 2.0.0 using `MAJOR.MINOR.PATCH` versions, with optional prerelease/build metadata such as `1.0.0-rc.1` or `1.0.0+build.5`.

### Version source of truth

The package version is defined in one place only:

```python
mdutil/version.py
```

`pyproject.toml` reads the package version dynamically from `mdutil.version.__version__`, and the CLI prints the same value via:

```bash
mdutil --version
```

Release tags should use this exact format:

```text
v{version}
```

For example, version `1.2.3` should be tagged as `v1.2.3`.

### What increments each part

- MAJOR: incompatible CLI, theme-file, rendering-contract, Python API, or packaging changes after 1.0.0.
- MINOR: backward-compatible features, new Markdown rendering support, new themes, new CLI options, or additive Python APIs.
- PATCH: backward-compatible bug fixes, documentation fixes, test-only changes, and internal refactors that do not change user-visible behavior.

### Pre-1.0 policy

While mdutil is in the `0.y.z` phase, the public contract is still stabilizing:

- `0.MINOR.0` may include breaking changes.
- `0.MINOR.PATCH` must remain backward compatible within that minor line.
- Breaking changes should still be called out clearly in release notes.
- Once the CLI flags, theme schema, rendered output contract, and packaging workflow are stable, release `1.0.0`.

### Release checklist

1. Decide the next version from the change set using the rules above.
2. Update `mdutil/version.py` only.
3. Run the full verification suite:

   ```bash
   python -m pytest -q
   python -m unittest discover -v
   python -m compileall -q mdutil tests
   python setup.py check
   python -m pip install -e '.[dev]'
   python -m mdutil --version
   ```

4. Ensure `python -m mdutil --version` prints the intended version.
5. Commit the version change and release notes together.
6. Create an annotated tag named `v{version}`.
7. Build/publish artifacts from that tag.

---

## License

MIT License - see LICENSE file for details.

---

## Documentation

Programming specification can be found in the mdutil-specification.md file.
