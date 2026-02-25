# COMP382 Assignment-2

A Python based app to simulate Super PDA that shows intersection of a CFL and Regular Language is a CFL

View [Youtube VLOG](PASTE_VIDEO_LINK_HERE)

## How the Project Works

The project defines a set of Regular Languages and a set of Context-Free Languages (CFLs). For every permutation of one Regular Language and one CFL, there is an intersection language.

The goal of the visualization is to show that an arbitrary intersection of these two language classes produces a CFL. To demonstrate that the intersection is a CFL, we show that a Pushdown Automaton (PDA) can be constructed for that intersection language. In this project, we call that machine a **SuperPDA** because it is the PDA built for the language produced by intersecting the selected Regular Language and CFL.

The interaction flow is:

1. The user selects one Regular Language and one CFL.
2. The user enters any input string.
3. The input is processed through the selected intersection matcher to extract the **longest matching substring**, which represents a string produced by the intersection language.
4. That resulting substring is then checked by the corresponding SuperPDA.

Because the substring is already produced by the selected intersection language, it is expected to be accepted by the SuperPDA constructed for that same intersection. A rejected state refers to a bug in the program.

## Dependencies

- [uv](https://docs.astral.sh/uv/getting-started/installation/) (version 0.9.24)
Easiest way to install is:
    - Mac: `brew install uv`
    - Windows: `winget install --id=astral-sh.uv  -e`
    - Linux: `sudo apt install uv`
    - Manually from the docs.

- [direnv](https://direnv.net/docs/installation.html)
    - Mac: `brew install direnv`
    - Windows: `winget install direnv`
    - Linux: `sudo apt install direnv`
    - Manually from the docs.

## Installation

If you see error about allowing `.envrc` file, like this:

```bash
>> direnv: error /Users/rishabmanocha/Downloads/mynewdir/.envrc is blocked. Run `direnv allow` to approve its content
```

Run `direnv allow`. This is only needed once.

```bash
uv sync
```

## Usage

```bash
uv run main
```

## Testing

```bash
uv run test
```

## References / Citations

- Astral. (2026). *uv documentation*. https://docs.astral.sh/uv/
- Qt Company. (2026). *PySide6 documentation*. https://doc.qt.io/qtforpython-6/
- WestHealth. (2024). *PyVis documentation*. https://pyvis.readthedocs.io/
- pytest-dev. (2026). *pytest documentation*. https://docs.pytest.org/
- NetworkX Developers. (2026). *NetworkX documentation*. https://networkx.org/documentation/

## AI / Tooling Disclosure

- AI service used: GitHub Copilot (GPT-5.3-Codex) for refactoring assistance, code cleanup, and sanity-check command suggestions.
- AI as a research partner included:
    - background research on framework/library usage patterns and compatibility
    - brainstorming implementation options before code changes

- AI-assisted coding included:
    - setting up/refining scaffolding for implementation-driven PDA loading and related project structure cleanup
    - refactoring SuperPDA stack rendering/state handling
    - identifying dead/unreferenced files
    - converting loader paths from JSON configs to class implementations
    - updating README and project health checks
    - executing only well-defined, specific tasks from explicit prompts
    - keeping edits within clearly defined scope without extending beyond requested requirements

