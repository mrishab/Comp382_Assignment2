# COMP382 Assignment-2

A Python based app to simulate Super PDA that shows intersection of a CFL and Regular Language is a CFL

View [Youtube VLOG]()

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
