# trailpad

`trailpad` is an offline note trail manager with tags, pinning, search, and export.

It stores everything in a local JSON vault under `~/.trailpad/`.

## Why this exists

- Fast local note capture from the terminal
- Easy tag filtering
- Pinned items stay at the top
- Export to Markdown or JSON
- Can be bundled into a standalone binary with PyInstaller

## Install

### From source

```bash
python -m pip install .
trailpad --help
```

### Build a binary

```bash
python -m pip install pyinstaller
pyinstaller --onefile --name trailpad main.py
```

## Usage

```bash
trailpad init
trailpad add "Ship release notes" -t release -t github
trailpad pin 1
trailpad list
trailpad find release
trailpad export trailpad.md
trailpad stats
```

## Release files

- Linux/macOS: `trailpad`
- Windows: `trailpad.exe`

## Release

- Current release: `v0.1.0`
- Changelog: [`CHANGELOG.md`](./CHANGELOG.md)
- Release workflow: [`.github/workflows/release.yml`](./.github/workflows/release.yml)
