"""Template-matching OCR for the bitmap font, with a per-character confidence.

Each cell is downsampled by majority vote over its SCALE x SCALE block, then compared to every glyph.
Confidence = 1 - (Hamming distance to the best glyph / 35). A cell that is close to two glyphs gets a
lower confidence too, because the margin to the runner-up is folded in.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from .font import GLYPHS, H, W
from .invoices import LINE, PITCH, SCALE

_BITS = {ch: [int(b) for row in g for b in row] for ch, g in GLYPHS.items()}


@dataclass
class Line:
    text: str
    conf: list[float]

    @property
    def min_conf(self) -> float:
        return min(self.conf) if self.conf else 0.0


def _cell_bits(px, w: int, h: int, x0: int, y0: int) -> list[int]:
    bits = []
    for gy in range(H):
        for gx in range(W):
            dark = 0
            for dy in range(SCALE):
                for dx in range(SCALE):
                    x, y = x0 + gx * SCALE + dx, y0 + gy * SCALE + dy
                    if x < w and y < h and px[x, y] < 128:
                        dark += 1
            bits.append(1 if dark * 2 > SCALE * SCALE else 0)
    return bits


def read_cell(bits: list[int]) -> tuple[str, float]:
    scored = sorted((sum(a != b for a, b in zip(bits, g, strict=True)), ch) for ch, g in _BITS.items())
    (d1, ch), (d2, _) = scored[0], scored[1]
    n = W * H
    conf = max(0.0, 1 - d1 / n) * min(1.0, 0.5 + (d2 - d1) / 4)
    return ch, round(conf, 4)


def read(img: Image.Image, n_lines: int, cols: int) -> list[Line]:
    g = img.convert("L")
    px, (w, h) = g.load(), g.size
    out = []
    for row in range(n_lines):
        chars, confs = [], []
        for col in range(cols):
            x0, y0 = (1 + col * PITCH) * SCALE, (1 + row * LINE) * SCALE
            ch, c = read_cell(_cell_bits(px, w, h, x0, y0))
            chars.append(ch)
            if ch != " ":
                confs.append(c)
        out.append(Line("".join(chars).rstrip(), confs))
    return out
