"""Generate fictional invoice images with the bitmap font, at chosen noise levels."""

from __future__ import annotations

import random
from dataclasses import dataclass

from PIL import Image

from .font import GLYPHS, H, W

SCALE = 3
PITCH = W + 1  # one blank column between glyphs
LINE = H + 3
VENDORS = ("BIRCHLINE SUPPLY", "COPPERKETTLE FOODS", "NORTHWIND PAPER", "MAPLEFORD TOOLS", "QUILLSTONE PRINT")


@dataclass(frozen=True)
class Invoice:
    number: str
    date: str
    vendor: str
    subtotal: str
    tax: str
    total: str

    def lines(self) -> list[str]:
        return [
            f"VENDOR: {self.vendor}",
            f"INVOICE NO: {self.number}",
            f"DATE: {self.date}",
            f"SUBTOTAL: {self.subtotal}",
            f"TAX: {self.tax}",
            f"TOTAL: {self.total}",
        ]


def make_invoice(i: int, corrupt_total: bool = False) -> Invoice:
    rng = random.Random(500 + i)
    sub = rng.randint(1000, 99999) / 100
    tax = round(sub * 0.08, 2)
    total = round(sub + tax, 2)
    if corrupt_total:
        total = round(total + 10, 2)  # a document whose arithmetic does not add up
    return Invoice(
        number=f"INV-{rng.randint(10000, 99999)}",
        date=f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        vendor=rng.choice(VENDORS),
        subtotal=f"{sub:.2f}",
        tax=f"{tax:.2f}",
        total=f"{total:.2f}",
    )


def render(inv: Invoice, noise: float = 0.0, seed: int = 0) -> Image.Image:
    lines = inv.lines()
    cols = max(len(s) for s in lines)
    img = Image.new("L", ((cols * PITCH + 2) * SCALE, (len(lines) * LINE + 2) * SCALE), 255)
    px = img.load()
    for row, text in enumerate(lines):
        for col, ch in enumerate(text):
            g = GLYPHS[ch]
            for gy in range(H):
                for gx in range(W):
                    if g[gy][gx] == "1":
                        x0, y0 = (1 + col * PITCH + gx) * SCALE, (1 + row * LINE + gy) * SCALE
                        for dy in range(SCALE):
                            for dx in range(SCALE):
                                px[x0 + dx, y0 + dy] = 0
    if noise:
        rng = random.Random(seed)
        w, h = img.size
        for y in range(h):
            for x in range(w):
                if rng.random() < noise:
                    px[x, y] = 255 - px[x, y]
    return img
