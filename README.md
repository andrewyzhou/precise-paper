# paper-generation

Pixel-perfect paper templates for personal notes, cheatsheets, study sheets, etc. Every page is rendered at **8.5" × 11" @ 1000 DPI** (8500 × 11000 px) with the same usable rectangle, header, and exactly equal 120 px margins on all four sides — across every mode and every density.

## Modes

Each mode comes in three densities: **regular** (250 px spacing), **extra** (150 px), and **super** (125 px). 250 / 150 / 125 are the only integer spacings in that range that fit the lattice exactly — see [`papers/common.py`](papers/common.py) for the geometry derivation.

| mode | description | output |
|---|---|---|
| [dotted](papers/dotted.ipynb) | dot grid | [`output/dotted/`](output/dotted/) |
| [lined](papers/lined.ipynb) | horizontal rules | [`output/lined/`](output/lined/) |
| [graph](papers/graph.ipynb) | full grid (lines both directions) | [`output/graph/`](output/graph/) |
| [cornell](papers/cornell.ipynb) | lined + cue column + summary band | [`output/cornell/`](output/cornell/) |

## Layout

```
paper-generation/
├── papers/
│   ├── common.py        # WIDTH, HEIGHT, MARGIN, HEADER_HEIGHT, lattice helpers
│   ├── dotted.ipynb
│   ├── lined.ipynb
│   ├── graph.ipynb
│   └── cornell.ipynb
└── output/
    ├── dotted/{dotted,extra-dotted,super-dotted}.png
    ├── lined/...
    ├── graph/...
    └── cornell/...
```

Every notebook is the same shape: `import common`, define a `render_<mode>(spacing)` function, loop over the three densities, save + display. All math is edge-based (PIL paste/rectangle take corners, not centers) — `common.py` documents the model in detail.

## Running

```bash
python3 -m venv venv && source venv/bin/activate
pip install pillow jupyter
jupyter nbconvert --to notebook --execute papers/<mode>.ipynb --output <mode>.ipynb
```

Outputs go to `output/<mode>/`.

## Future modes (not yet implemented)

- **isometric** / **hex** — 60° lattices need irrational vertical spacing; can't have both exact angles AND integer 120 px margins on this canvas. Would require a separate design.
- **storyboard** / **music staff** — don't naturally map to "three densities," would need a different parameterization.
