"""
Shared geometry primitives for all paper modes.

╔══════════════════════════════════════════════════════════════════════════╗
║  GEOMETRY MODEL — read this before changing anything.                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Page is WIDTH × HEIGHT pixels at 1000 DPI (8.5" × 11").                 ║
║  A solid header rectangle of HEADER_HEIGHT rows fills the very top       ║
║  (rows 0 .. HEADER_HEIGHT−1). Everything below — rows HEADER_HEIGHT ..   ║
║  HEIGHT−1, full width — is the "usable rectangle" where the pattern      ║
║  lives.                                                                  ║
║                                                                          ║
║  CENTER-BASED MARGIN (the invariant).                                    ║
║  CENTER_MARGIN is the distance from the CENTER of a primitive element    ║
║  (dot / line / frame-edge) to the usable-rect edge. It is the same 125   ║
║  px for every mode and every density. The EDGE-to-rect-edge margin       ║
║  depends on the element's size:                                          ║
║      edge_margin(elem_size) = CENTER_MARGIN − elem_size // 2             ║
║  For the canonical elem_size = 10, edge_margin = 120 px — same as before ║
║  we started varying sizes per density.                                   ║
║                                                                          ║
║  WHY CENTER-BASED? We want to vary element size per density (bigger      ║
║  dots in sparse grids, thinner lines in dense graphs) while keeping the  ║
║  LATTICE itself — where element CENTERS sit — IDENTICAL across every     ║
║  density. Keeping CENTER_MARGIN fixed is what makes that true:           ║
║      LATTICE_W = WIDTH      − 2·CENTER_MARGIN =  8250                    ║
║      LATTICE_H = HEIGHT − HEADER_HEIGHT − 2·CENTER_MARGIN = 10500        ║
║  These depend only on CENTER_MARGIN, NOT on elem_size. So the allowed    ║
║  SPACING set (divisors of gcd(8250,10500) = 750) is density-independent. ║
║                                                                          ║
║  All underlying rasterization is still EDGE-BASED (PIL paste/rectangle   ║
║  take corners, not centers). edge_margin() converts from the center-     ║
║  invariant model back to edge coordinates just-in-time.                  ║
║                                                                          ║
║  Lattice equations. For spacing S and element size E:                    ║
║    element (i,j) top-left pixel =                                        ║
║        ( edge_margin(E) + i·S ,                                          ║
║          HEADER_HEIGHT + edge_margin(E) + j·S )                          ║
║    n_x = LATTICE_W // S + 1                                              ║
║    n_y = LATTICE_H // S + 1                                              ║
║                                                                          ║
║  Parity. For edge_margin(E) = 125 − E//2 to round correctly and for      ║
║  the rightmost/bottommost element to land exactly on the mirror margin,  ║
║  E must be EVEN. Odd E leaves a 1 px asymmetry. (Even CENTER_MARGIN and  ║
║  even WIDTH/HEIGHT/HEADER_HEIGHT are required; they all are.)            ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
from PIL import Image, ImageDraw

# === Page constants ==========================================================
WIDTH  = 8500
HEIGHT = 11000

# === Colors ==================================================================
BG_COLOR = (255, 255, 255)
FG_COLOR = (210, 210, 210)   # dots, lines, header — same color throughout

# === Geometry ================================================================
CENTER_MARGIN = 125   # element-center to usable-rect-edge (INVARIANT across densities)
HEADER_HEIGHT = 250   # rows occupied by header rect at top of page
SUPERSAMPLE   = 8     # render dots at 8× then downscale for AA

# Lattice extent (where element CENTERS can sit). Independent of elem_size.
LATTICE_W = WIDTH  - 2 * CENTER_MARGIN                   # 8250
LATTICE_H = HEIGHT - HEADER_HEIGHT - 2 * CENTER_MARGIN   # 10500

# Canonical 3-density set (divisors of gcd(LATTICE_W, LATTICE_H) = 750):
SPACING_REGULAR = 250
SPACING_EXTRA   = 150
SPACING_SUPER   = 125

DENSITIES = {
    "regular": SPACING_REGULAR,
    "extra":   SPACING_EXTRA,
    "super":   SPACING_SUPER,
}

# Backwards-compatible aliases for modes that use a fixed elem_size:
DEFAULT_ELEM_SIZE = 10
ELEM_SIZE         = DEFAULT_ELEM_SIZE                 # legacy alias
MARGIN            = CENTER_MARGIN - ELEM_SIZE // 2    # legacy edge-margin = 120


# === Helpers =================================================================

def edge_margin(elem_size=DEFAULT_ELEM_SIZE):
    """Empty pixels between element edge and usable-rect edge for this size.
    Equals CENTER_MARGIN − elem_size//2; always integer for even elem_size."""
    return CENTER_MARGIN - elem_size // 2


def blank_page():
    """Fresh white canvas."""
    return Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)


def draw_header(img, color=FG_COLOR):
    """Solid header rectangle filling rows 0..HEADER_HEIGHT-1."""
    ImageDraw.Draw(img).rectangle(
        [0, 0, WIDTH - 1, HEADER_HEIGHT - 1], fill=color
    )


def make_dot_template(size=DEFAULT_ELEM_SIZE, color=FG_COLOR, ss=SUPERSAMPLE):
    """Antialiased circular dot rendered at ss× then LANCZOS-downscaled."""
    hi = size * ss
    dot_hi = Image.new("RGB", (hi, hi), BG_COLOR)
    ImageDraw.Draw(dot_hi).ellipse([0, 0, hi - 1, hi - 1], fill=color)
    return dot_hi.resize((size, size), Image.LANCZOS)


def grid_counts(spacing):
    """(n_x, n_y) for a given SPACING. Asserts the lattice fits exactly.
    Independent of element size — the lattice is center-defined."""
    assert LATTICE_W % spacing == 0 and LATTICE_H % spacing == 0, (
        f"SPACING={spacing} must divide LATTICE_W={LATTICE_W} "
        f"and LATTICE_H={LATTICE_H}"
    )
    return LATTICE_W // spacing + 1, LATTICE_H // spacing + 1


def lattice_x(i, spacing, elem_size=DEFAULT_ELEM_SIZE):
    """Pixel column of the LEFT EDGE of element (i, _) with given size."""
    return edge_margin(elem_size) + i * spacing


def lattice_y(j, spacing, elem_size=DEFAULT_ELEM_SIZE):
    """Pixel row of the TOP EDGE of element (_, j) with given size."""
    return HEADER_HEIGHT + edge_margin(elem_size) + j * spacing


def hline(img, top_y, color=FG_COLOR, thickness=DEFAULT_ELEM_SIZE,
          left=None, right=None):
    """Horizontal line; spans edge-to-edge of the usable rect by default."""
    if left is None:
        left = edge_margin(thickness)
    if right is None:
        right = WIDTH - 1 - edge_margin(thickness)
    ImageDraw.Draw(img).rectangle(
        [left, top_y, right, top_y + thickness - 1], fill=color
    )


def vline(img, left_x, color=FG_COLOR, thickness=DEFAULT_ELEM_SIZE,
          top=None, bottom=None):
    """Vertical line; spans edge-to-edge of the usable rect by default."""
    if top is None:
        top = HEADER_HEIGHT + edge_margin(thickness)
    if bottom is None:
        bottom = HEIGHT - 1 - edge_margin(thickness)
    ImageDraw.Draw(img).rectangle(
        [left_x, top, left_x + thickness - 1, bottom], fill=color
    )


# === Output ==================================================================

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def output_path(mode, variant):
    """Resolve <repo_root>/output/<mode>/<variant>.png and ensure dir exists."""
    out_dir = os.path.join(_REPO_ROOT, "output", mode)
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, f"{variant}.png")


def variant_name(mode, density):
    """e.g. ('dotted', 'regular') → 'dotted'; ('lined', 'extra') → 'extra-lined'."""
    return mode if density == "regular" else f"{density}-{mode}"
