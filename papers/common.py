"""
Shared geometry primitives for all paper modes.

╔══════════════════════════════════════════════════════════════════════════╗
║  GEOMETRY MODEL — read this before changing anything.                    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Page is WIDTH × HEIGHT pixels at 1000 DPI (8.5" × 11").                 ║
║  A solid header rectangle of HEADER_HEIGHT rows fills the very top       ║
║  (rows 0 .. HEADER_HEIGHT−1). Everything below — rows HEADER_HEIGHT ..   ║
║  HEIGHT−1, full width — is the "usable rectangle" where the pattern      ║
║  lives. EVERY mode and EVERY density places its primitive elements with  ║
║  the SAME MARGIN px gap between element edge and rectangle edge on all   ║
║  four sides. Top, bottom, left, right are exactly equal.                 ║
║                                                                          ║
║  ALL MATH IS EDGE-BASED — we never reason about element "centers". PIL's ║
║  paste() and rectangle() take pixel-aligned coordinates, so edge-math is ║
║  the natural unit and avoids //2 conversion noise.                       ║
║                                                                          ║
║  The "primitive element" is one ELEM_SIZE × ELEM_SIZE pixel box:         ║
║    • Dotted modes → a circular dot occupying that box.                   ║
║    • Lined / graph / cornell → a line of thickness ELEM_SIZE.            ║
║  Keeping ELEM_SIZE shared across modes is what allows every mode to use  ║
║  the SAME LATTICE_W/LATTICE_H and the same allowed SPACING set.          ║
║                                                                          ║
║  Lattice equations. For a chosen SPACING:                                ║
║    element (i,j) top-left pixel =                                        ║
║        ( MARGIN + i·SPACING ,  HEADER_HEIGHT + MARGIN + j·SPACING )      ║
║    n_x = LATTICE_W // SPACING + 1                                        ║
║    n_y = LATTICE_H // SPACING + 1                                        ║
║  where                                                                   ║
║    LATTICE_W = WIDTH      − 2·MARGIN − ELEM_SIZE                         ║
║    LATTICE_H = HEIGHT − HEADER_HEIGHT − 2·MARGIN − ELEM_SIZE             ║
║                                                                          ║
║  For the right/bottom margin to land EXACTLY on MARGIN px (not less),    ║
║  SPACING must divide both LATTICE_W and LATTICE_H. With current values   ║
║  LATTICE_W = 8250 and LATTICE_H = 10500, gcd = 750. Allowed SPACINGs     ║
║  are divisors of 750: 1, 2, 3, 5, 6, 10, 15, 25, 30, 50, 75, 125, 150,   ║
║  250, 375, 750. Every mode uses the canonical {250, 150, 125} for its    ║
║  three densities (regular / extra / super).                              ║
║                                                                          ║
║  Even vs. odd ELEM_SIZE: even sizes have a sub-pixel geometric center;   ║
║  odd sizes have a true center pixel. Either works for our lattice — the  ║
║  offset is uniform — but parity matters for whether MARGIN comes out an  ║
║  integer. With even WIDTH and even MARGIN, even ELEM_SIZE is safe.       ║
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
ELEM_SIZE     = 10    # pixel diameter of dot / pixel thickness of line
SUPERSAMPLE   = 8     # render dots at 8× then downscale for AA
MARGIN        = 120   # empty pixels between element edge and usable-rect edge
HEADER_HEIGHT = 250   # rows occupied by header rect at top of page

LATTICE_W = WIDTH  - 2 * MARGIN - ELEM_SIZE                   # 8250
LATTICE_H = HEIGHT - HEADER_HEIGHT - 2 * MARGIN - ELEM_SIZE   # 10500

# Canonical 3-density set (divisors of gcd(LATTICE_W, LATTICE_H) = 750):
SPACING_REGULAR = 250
SPACING_EXTRA   = 150
SPACING_SUPER   = 125

DENSITIES = {
    "regular": SPACING_REGULAR,
    "extra":   SPACING_EXTRA,
    "super":   SPACING_SUPER,
}

# === Helpers =================================================================

def blank_page():
    """Fresh white canvas."""
    return Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)


def draw_header(img, color=FG_COLOR):
    """Solid header rectangle filling rows 0..HEADER_HEIGHT-1."""
    ImageDraw.Draw(img).rectangle(
        [0, 0, WIDTH - 1, HEADER_HEIGHT - 1], fill=color
    )


def make_dot_template(size=ELEM_SIZE, color=FG_COLOR, ss=SUPERSAMPLE):
    """Antialiased circular dot rendered at ss× then LANCZOS-downscaled."""
    hi = size * ss
    dot_hi = Image.new("RGB", (hi, hi), BG_COLOR)
    ImageDraw.Draw(dot_hi).ellipse([0, 0, hi - 1, hi - 1], fill=color)
    return dot_hi.resize((size, size), Image.LANCZOS)


def grid_counts(spacing):
    """(n_x, n_y) for a given SPACING. Asserts the lattice fits exactly."""
    assert LATTICE_W % spacing == 0 and LATTICE_H % spacing == 0, (
        f"SPACING={spacing} must divide LATTICE_W={LATTICE_W} "
        f"and LATTICE_H={LATTICE_H}"
    )
    return LATTICE_W // spacing + 1, LATTICE_H // spacing + 1


def lattice_x(i, spacing):
    """Pixel column of the left edge of element (i, _)."""
    return MARGIN + i * spacing


def lattice_y(j, spacing):
    """Pixel row of the top edge of element (_, j)."""
    return HEADER_HEIGHT + MARGIN + j * spacing


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
