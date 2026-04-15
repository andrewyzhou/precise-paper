# paper-generation

Pixel-perfect paper templates for personal notes, cheatsheets, study sheets, etc. Every page is rendered at **8.5" × 11" @ 1000 DPI** (8500 × 11000 px) with the same usable rectangle, header, and a shared center-margin invariant (125 px from element center to rect edge) across every mode and every density.

See **[SPEC.md](SPEC.md)** for exact pixel numbers, dot/line sizes, density ratios, and the math.

## Modes

Each mode comes in three densities: **regular**, **extra**, **super**. The orthogonal modes (dotted/lined/graph/cornell) use SPACING ∈ {250, 150, 125} px — the only integer spacings in that range that divide the lattice exactly. Modes with non-orthogonal geometry use mode-specific parameters chosen to preserve the same 120 px margins; see each notebook's header comment for the derivation.

| mode | description | output |
|---|---|---|
| [dotted](papers/dotted.ipynb) | dot grid | [`output/dotted/`](output/dotted/) |
| [lined](papers/lined.ipynb) | horizontal rules | [`output/lined/`](output/lined/) |
| [graph](papers/graph.ipynb) | full grid (lines both directions) | [`output/graph/`](output/graph/) |
| [cornell](papers/cornell.ipynb) | lined + cue column + summary band | [`output/cornell/`](output/cornell/) |
| [isometric](papers/isometric.ipynb) | triangular dot lattice (~60°, < 1.2° deviation) | [`output/isometric/`](output/isometric/) |
| [hex](papers/hex.ipynb) | tessellated pointy-top hexagons | [`output/hex/`](output/hex/) |
| [storyboard](papers/storyboard.ipynb) | tiled rectangle frames | [`output/storyboard/`](output/storyboard/) |
| [cheatsheet](papers/cheatsheet.ipynb) | dotted background + 3 column dividers | [`output/cheatsheet/`](output/cheatsheet/) |

**A note on isometric / hex:** true 60° lattices require an irrational `P_y/P_x = sqrt(3)/2`, which can't coexist with both integer pixel coordinates AND exact 120 px margins. The chosen `(P_x, P_y)` pairs deviate from 60° by less than 1.2° per density — visually indistinguishable at 1000 DPI. Hex vertex offsets `P_y/3` are sub-pixel for two of the three densities; floats are passed to PIL so adjacent hexes still share the same vertex (seamless tessellation under anti-aliasing).

## Layout

```
paper-generation/
├── papers/
│   ├── common.py        # WIDTH, HEIGHT, MARGIN, HEADER_HEIGHT, lattice helpers
│   ├── dotted.ipynb
│   ├── lined.ipynb
│   ├── graph.ipynb
│   ├── cornell.ipynb
│   ├── isometric.ipynb
│   ├── hex.ipynb
│   ├── storyboard.ipynb
│   └── cheatsheet.ipynb
└── output/
    ├── dotted/{dotted,extra-dotted,super-dotted}.png
    ├── lined/...
    └── ...        # one folder per mode, three PNGs per folder
```

Every notebook is the same shape: `import common`, define a `render_<mode>(spacing)` function, loop over the three densities, save + display. All math is edge-based (PIL paste/rectangle take corners, not centers) — `common.py` documents the model in detail.

## Running

```bash
python3 -m venv venv && source venv/bin/activate
pip install pillow jupyter
jupyter nbconvert --to notebook --execute papers/<mode>.ipynb --output <mode>.ipynb
```

Outputs go to `output/<mode>/`.

