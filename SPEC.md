# Paper Generation — Specification

Exact pixel-level numbers for every mode and every density. All geometry lives in [papers/common.py](papers/common.py); this document is the human-readable cross-reference.

## Page

| constant | value | notes |
|---|---|---|
| WIDTH | 8500 px | 8.5" × 1000 DPI |
| HEIGHT | 11000 px | 11" × 1000 DPI |
| BG_COLOR | (255, 255, 255) | white |
| FG_COLOR | (210, 210, 210) | very light gray — every mark uses this |

## Header

A solid rectangle at the top of every page. Defines the "usable rectangle" below it.

| constant | value |
|---|---|
| HEADER_HEIGHT | 250 px (rows 0..249) |
| usable rect | rows 250..10999 = 10750 px tall, full 8500 px wide |

## Margin model (the invariant)

Every mode places its primitive elements (dot / line edge / frame edge) such that each element's **CENTER** sits exactly **125 px** from the corresponding usable-rect edge.

| constant | value | meaning |
|---|---|---|
| CENTER_MARGIN | **125 px** | element center → rect edge. Same for every mode and density. |
| edge_margin(E) | 125 − E/2 | element EDGE → rect edge. Varies with element size E. |

The lattice (where element centers sit) depends **only** on CENTER_MARGIN — not on element size:

```
LATTICE_W = WIDTH      − 2·CENTER_MARGIN =  8500 − 250 =  8250
LATTICE_H = HEIGHT − HEADER_HEIGHT − 2·CENTER_MARGIN = 11000 − 250 − 250 = 10500
```

For SPACING to land the last element exactly on the mirror margin, **SPACING must divide both LATTICE_W and LATTICE_H**. `gcd(8250, 10500) = 750`, so allowed SPACINGs are divisors of 750:

```
{1, 2, 3, 5, 6, 10, 15, 25, 30, 50, 75, 125, 150, 250, 375, 750}
```

Canonical three-density set: **{250, 150, 125}** — these are the three consecutive divisors sitting in the "nice for notes" range.

### Density ratios

Density = 1/SPACING² (dots per unit area on an orthogonal lattice).

| step | spacing ratio | density ratio |
|---|---|---|
| regular → extra | 250/150 = 5/3 | (5/3)² ≈ **2.78×** |
| extra → super | 150/125 = 6/5 | (6/5)² = **1.44×** |
| regular → super | 250/125 = 2 | 2² = **4×** |

## Parity rules

For `edge_margin(E) = 125 − E/2` to be integer AND for the mirror-margin to land exactly, even constraints must hold:

- `E` must be **even** (otherwise edge_margin has a 0.5 px remainder).
- `WIDTH`, `HEIGHT`, `HEADER_HEIGHT`, `CENTER_MARGIN` are all even ✓.
- This is why graph's super LINE_WIDTH is 4 (not the "ideal" 5): 5 is odd.

## Mode: dotted

| density | SPACING | DOT_SIZE | edge_margin | dots | dots/cell² |
|---|---|---|---|---|---|
| regular | 250 | **20** | 115 | 34 × 43 = 1462 | 0.50% |
| extra | 150 | **12** | 119 | 56 × 71 = 3976 | 0.50% |
| super | 125 | **10** | 120 | 67 × 85 = 5695 | 0.50% |

Rationale for per-density DOT_SIZE: `DOT_SIZE/SPACING = 8%` across all densities. Super is the visual baseline (10 px at 125 px spacing) — regular/extra scale up so sparse dots remain visible.

## Mode: lined

| density | SPACING | LINE_WIDTH | edge_margin | lines |
|---|---|---|---|---|
| regular | 250 | 10 | 120 | 43 |
| extra | 150 | 10 | 120 | 71 |
| super | 125 | 10 | 120 | 85 |

Lines are full-width (edge-to-edge of usable rect). Thickness fixed at 10 px across densities — lined paper reads cleanest with uniform line weight.

## Mode: graph

| density | SPACING | LINE_WIDTH | edge_margin | grid | lw/S |
|---|---|---|---|---|---|
| regular | 250 | **10** | 120 | 34 × 43 | 4.0% |
| extra | 150 | **6** | 122 | 56 × 71 | 4.0% |
| super | 125 | **4** | 123 | 67 × 85 | 3.2% |

Regular's 10/250 = 4% is the baseline. Extra scales exactly. Super drops to 4 px (3.2%) because 5 is odd and would break pixel parity.

## Mode: cornell

Lined background plus a vertical cue divider and a horizontal summary divider. Same line width (10 px) as lined. Dividers snap to lattice indices chosen to keep ratios consistent.

| density | SPACING | cue_col | cue_width | summary_row | summary_pos |
|---|---|---|---|---|---|
| regular | 250 | 8 | 2000 px (24.2%) | 34 | 80.9% |
| extra | 150 | 14 | 2100 px (25.4%) | 56 | 79.9% |
| super | 125 | 17 | 2125 px (25.7%) | 67 | 79.7% |

## Mode: isometric

Triangular dot lattice, basis vectors `(P_x, 0)` and `(P_x/2, P_y)`. Even rows at `edge_margin + i·P_x`; odd rows offset by `P_x/2`.

| density | P_x | P_y | DOT_SIZE | angle | deviation from 60° | dots |
|---|---|---|---|---|---|---|
| regular | 250 | 210 | 20 | 59.24° | 0.76° | 1709 |
| extra | 150 | 125 | 12 | 59.04° | 0.96° | 4718 |
| super | 110 | 100 | 10 | 61.19° | 1.19° | 8003 |

**Constraint conflict:** a true 60° lattice requires `P_y = P_x·√3/2` (irrational). We pick the integer `P_y` that divides `LATTICE_H` AND is closest to `P_x·√3/2`. Angular deviation < 1.2° per density — visually indistinguishable at 1000 DPI.

Odd-row horizontal margin = `edge_margin(DOT_SIZE) + P_x/2` — mirror-symmetric, larger than even-row by `P_x/2`. This is the natural visual of triangular paper.

## Mode: hex

Pointy-top hexes centered on the iso lattice. Vertex offsets from center:

```
top:    (0,        −2·P_y/3)
ur:     (+P_x/2,   −P_y/3)
lr:     (+P_x/2,   +P_y/3)
bot:    (0,        +2·P_y/3)
ll:     (−P_x/2,   +P_y/3)
ul:     (−P_x/2,   −P_y/3)
```

Derived from the centroid of three mutually adjacent hex centers, so adjacent hexes share vertices algebraically.

### Hex margin math (different from dot/line modes)

A hex extends outward from its center by `P_x/2` horizontally and `2·P_y/3` vertically, plus `LW/2` line thickness. Placing hex **centers** on the dot lattice would overflow: the first hex's leftmost pixel would land at `edge_margin(LW) − P_x/2 − LW/2`, which is negative for every density. Instead, anchor the leftmost **outline pixel** to `M_x` and solve for hex counts:

```
N_x_even = LATTICE_W // P_x            (one fewer than the dot lattice)
N_x_odd  = N_x_even − 1
M_x      = edge_margin(LW)             (exact match with graph/dotted)
N_y      = LATTICE_H // P_y
M_y      = (USABLE_H − (N_y−1)·P_y − 4·P_y/3 − LW) / 2
first_cx = M_x + P_x/2 + LW/2
first_cy = HEADER_HEIGHT + M_y + 2·P_y/3 + LW/2
```

Horizontal margins land exactly on edge_margin. Vertical margins are per-density best-fit (top == bottom) — they come out **smaller than 120 px** because the hex aspect (`4·P_y/(3·P_x) ≈ 1.15`) doesn't match the usable rect aspect (`8260/10750 ≈ 0.77`), so there's less leftover whitespace vertically.

| density | P_x | P_y | LW | N_x_even × N_y | hexes | M_x | M_y |
|---|---|---|---|---|---|---|---|
| regular | 250 | 210 | 10 | 33 × 50 | 1633 | **120** | **85** |
| extra | 150 | 125 | 6 | 55 × 84 | 4578 | **122** | **~101.17** |
| super | 110 | 100 | 4 | 75 × 105 | 7822 | **123** | **~106.33** |

Odd rows have `N_x_odd = N_x_even − 1` hexes (shifted by `P_x/2`). When `P_y` isn't divisible by 3, vertex offsets are fractional floats — but adjacent hexes reference the same float, so tessellation stays seamless under anti-aliasing.

## Mode: storyboard

Grid of rectangle outlines tiled exactly within the usable rectangle (no gutter). Cell partitioning is `cols × rows`, where `cols | USABLE_W` and `rows | USABLE_H`.

```
USABLE_W = WIDTH − 2·MARGIN           = 8260 = 2² · 5 · 7 · 59
USABLE_H = HEIGHT − HEADER_HEIGHT − 2·MARGIN = 10510 = 2 · 5 · 1051
```

Allowed cols: {2, 4, 5, 7, 10, 14, 20, 28, ...}. Allowed rows: {2, 5, 10}.

| density | cols × rows | cell w × h | frames | OUTLINE |
|---|---|---|---|---|
| regular | 2 × 2 | 4130 × 5255 | 4 | 10 px |
| extra | 4 × 5 | 2065 × 2102 | 20 | 5 px |
| super | 5 × 10 | 1652 × 1051 | 50 | 3 px |

OUTLINE scales with cell min-dim: regular 10/4130 ≈ 0.24%; extra and super scale down proportionally.

## Allowed elements summary

For any element of integer size E to use the canonical `{250, 150, 125}` SPACING set, E must be even (for `edge_margin(E)` integer) and fit visually.

Practical even sizes (in current use): `E ∈ {4, 6, 10, 12, 20}`. Each maps to an edge_margin:

| E | edge_margin | used by |
|---|---|---|
| 4 | 123 | graph super, hex super |
| 6 | 122 | graph extra, hex extra |
| 10 | 120 | lined (all), graph regular, hex regular, cornell, super-dotted, super-isometric, storyboard regular |
| 12 | 119 | extra-dotted, extra-isometric |
| 20 | 115 | dotted regular, isometric regular |
