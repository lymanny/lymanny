#!/usr/bin/env python3
"""
Generate an animated "AI skin analysis" SVG for a GitHub README,
themed on MedicalSkin AI (cosmetic skin analysis powered by YouCam AI).

    python medical_scan.py

Outputs (in ./assets):
    medscan-dark.svg
    medscan-light.svg

A scanner beam sweeps across a field of skin cells. As it passes, each of the
12 skin concerns is tagged with its score, coloured like the app
(80+ good, 60-79 fair, <60 needs care). The counter ticks up to 12/12 and
the run ends with the overall result before looping.

Edit CONCERNS / SUMMARY below to match your own demo data.
"""
import os
import random

# ---- data shown in the animation (sample data from the MedicalSkin AI demo)
CONCERNS = [
    ("ACNE", 88), ("DARK CIRCLES", 79), ("EYE BAGS", 75), ("FIRMNESS", 93),
    ("MOISTURE", 75), ("OILINESS", 69), ("PORES", 63), ("RADIANCE", 95),
    ("REDNESS", 91), ("AGE SPOTS", 98), ("TEXTURE", 88), ("WRINKLES", 91),
]
SUMMARY = [("OVERALL SKIN SCORE", "83.6"), ("SKIN TYPE", "Oily"), ("SKIN AGE", "25")]

W, H = 860, 250
COLS, ROWS = 30, 6
X0, Y0, DX, DY = 44, 70, 26.5, 25
CYCLE = 12.0                 # seconds per loop
SCAN_START, SCAN_END = 0.6, 8.4
SEED = 11

THEMES = {
    "dark": dict(cell="#2DD4BF", nucleus="#60A5FA", hud="#8B949E", text="#E6EDF3",
                 accent="#38BDF8", track="#21262D", beam="#E0FFFF", bg="#0D1117",
                 good="#34D399", fair="#FBBF24", care="#F43F5E"),
    "light": dict(cell="#14B8A6", nucleus="#3B82F6", hud="#57606A", text="#1F2328",
                  accent="#0284C7", track="#E5E7EB", beam="#0EA5E9", bg="#FFFFFF",
                  good="#059669", fair="#D97706", care="#E11D48"),
}

FONT = "font-family=\"'SFMono-Regular',Menlo,Consolas,'Liberation Mono',monospace\""


def band(score, c):
    return c["good"] if score >= 80 else c["fair"] if score >= 60 else c["care"]


def kt(t):
    return round(min(max(t / CYCLE, 0.0), 1.0), 4)


def anim(attr, values, times):
    """Discrete looping animation; every element shares CYCLE so all stay in sync."""
    values, times = list(values), list(times)
    if times[-1] < CYCLE:
        values.append(values[-1])
        times.append(CYCLE)
    ks = [kt(t) for t in times]
    ks[0], ks[-1] = 0, 1
    for i in range(1, len(ks)):
        ks[i] = max(ks[i], ks[i - 1])
    return (f'<animate attributeName="{attr}" dur="{CYCLE}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="{";".join(map(str, values))}" '
            f'keyTimes="{";".join(map(str, ks))}"/>')


def anim_lin(attr, values, times):
    ks = [kt(t) for t in times]
    ks[0], ks[-1] = 0, 1
    return (f'<animate attributeName="{attr}" dur="{CYCLE}s" repeatCount="indefinite" '
            f'values="{";".join(map(str, values))}" keyTimes="{";".join(map(str, ks))}"/>')


X_START = X0 - 20
X_END = X0 + (COLS - 1) * DX + 20


def pass_time(x):
    return SCAN_START + (SCAN_END - SCAN_START) * (x - X_START) / (X_END - X_START)


def build(theme):
    c = THEMES[theme]
    rnd = random.Random(SEED)
    end_hold = CYCLE - 0.35
    n = len(CONCERNS)

    # one target cell per concern, spread left->right, alternating upper/lower rows
    targets = {}
    for i in range(n):
        col = round(1 + i * (COLS - 3) / (n - 1))
        row = 1 if i % 2 == 0 else 4
        targets[(col, row)] = i

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Animated AI skin analysis">',
        "<defs>",
        '<linearGradient id="beam" x1="0" x2="1" y1="0" y2="0">'
        f'<stop offset="0" stop-color="{c["accent"]}" stop-opacity="0"/>'
        f'<stop offset="0.7" stop-color="{c["accent"]}" stop-opacity="0.18"/>'
        f'<stop offset="0.97" stop-color="{c["beam"]}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{c["beam"]}" stop-opacity="0"/>'
        "</linearGradient>",
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="2" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        "</defs>",
    ]

    # ---- HUD
    out.append(
        f'<text x="{X0 - 12}" y="26" {FONT} font-size="12" fill="{c["accent"]}" '
        f'letter-spacing="1">◉ SKIN ANALYSIS</text>'
    )
    out.append(
        f'<text x="{X0 + 120}" y="26" {FONT} font-size="12" fill="{c["hud"]}">'
        "· YouCam AI · sample data</text>"
    )
    blink = [0, 1.2, 2.2, 3.2, 4.2, 5.2, 6.2, 7.2]
    out.append(
        f'<text x="{W - 300}" y="26" {FONT} font-size="12" fill="{c["accent"]}">ANALYZING…'
        + anim("opacity", [1, .25, 1, .25, 1, .25, 1, .25, 0], blink + [SCAN_END]) + "</text>"
    )
    out.append(
        f'<text x="{W - 300}" y="26" {FONT} font-size="12" fill="{c["good"]}" opacity="0">✓ COMPLETE'
        + anim("opacity", [0, 1, 0], [0, SCAN_END + 0.1, end_hold]) + "</text>"
    )

    # counter CONCERNS 00/12 -> 12/12
    tag_times = sorted(pass_time(X0 + col * DX + (DX / 2 if row % 2 else 0))
                       for col, row in targets)
    windows = [0] + tag_times + [end_hold]
    for k in range(n + 1):
        start, stop = windows[k], windows[k + 1]
        vals, times = ([1, 0, 1], [0, stop, end_hold]) if k == 0 else ([0, 1, 0], [0, start, stop])
        colour = c["accent"] if k < n else c["good"]
        out.append(
            f'<text x="{W - 40}" y="26" text-anchor="end" {FONT} font-size="12" '
            f'fill="{colour}" opacity="{1 if k == 0 else 0}">CONCERNS {k:02d}/{n}'
            + anim("opacity", vals, times) + "</text>"
        )

    # ---- skin cells + concern tags
    tags = []
    for row in range(ROWS):
        for col in range(COLS):
            cx = X0 + col * DX + (DX / 2 if row % 2 else 0) + rnd.uniform(-2.5, 2.5)
            if cx > X0 + (COLS - 1) * DX + 4:
                continue
            cy = Y0 + row * DY + rnd.uniform(-2.5, 2.5)
            t = pass_time(cx)
            rx, ry, rot = rnd.uniform(8, 10), rnd.uniform(6.5, 8.5), rnd.uniform(0, 180)
            out.append(
                '<g opacity="0.3">'
                + anim("opacity", [0.3, 0.95, 0.7, 0.3], [0, t, t + 0.4, end_hold])
                + f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
                f'transform="rotate({rot:.0f} {cx:.1f} {cy:.1f})" fill="{c["cell"]}" '
                f'fill-opacity="0.22" stroke="{c["cell"]}" stroke-width="1"/>'
                f'<circle cx="{cx + rnd.uniform(-2, 2):.1f}" cy="{cy + rnd.uniform(-1.5, 1.5):.1f}" '
                f'r="2.4" fill="{c["nucleus"]}"/></g>'
            )
            if (col, row) in targets:
                tags.append((targets[(col, row)], cx, cy, row, t))

    # tags drawn last so they sit on top of all cells
    for i, cx, cy, row, t in tags:
        name, score = CONCERNS[i]
        col = band(score, c)
        s, L = 15, 5
        x1, y1, x2, y2 = cx - s, cy - s, cx + s, cy + s
        d = (f"M{x1:.1f},{y1 + L:.1f} V{y1:.1f} H{x1 + L:.1f} M{x2 - L:.1f},{y1:.1f} H{x2:.1f} V{y1 + L:.1f} "
             f"M{x2:.1f},{y2 - L:.1f} V{y2:.1f} H{x2 - L:.1f} M{x1 + L:.1f},{y2:.1f} H{x1:.1f} V{y2 - L:.1f}")
        ly = y1 - 6 if row < 3 else y2 + 14
        out.append(
            '<g opacity="0">'
            + anim("opacity", [0, 1, 0.4, 1, 0.4, 1, 0],
                   [0, t, t + 0.12, t + 0.24, t + 0.36, t + 0.48, end_hold])
            + f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5" fill="none" stroke="{col}" '
            f'stroke-width="2" filter="url(#glow)"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.8"/>'
            f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" {FONT} font-size="9.5" '
            f'font-weight="700" fill="{col}" stroke="{c["bg"]}" stroke-width="3" '
            f'paint-order="stroke">{name} {score}</text></g>'
        )

    # ---- scanner beam
    beam_w = 90
    bx0, bx1 = X_START - beam_w, X_END - beam_w
    top, bottom = Y0 - 26, Y0 + (ROWS - 1) * DY + 26
    out.append(
        '<g opacity="0">'
        + anim("opacity", [0, 1, 0], [0, SCAN_START, SCAN_END + 0.05])
        + f'<rect y="{top}" width="{beam_w}" height="{bottom - top}" fill="url(#beam)">'
        + anim_lin("x", [bx0, bx0, bx1, bx1], [0, SCAN_START, SCAN_END, CYCLE])
        + "</rect>"
        f'<rect y="{top}" width="2" height="{bottom - top}" fill="{c["beam"]}" filter="url(#glow)">'
        + anim_lin("x", [bx0 + beam_w - 2] * 2 + [bx1 + beam_w - 2] * 2,
                   [0, SCAN_START, SCAN_END, CYCLE])
        + "</rect></g>"
    )

    # ---- progress bar
    py = H - 32
    pw = W - 2 * (X0 - 12)
    out.append(f'<rect x="{X0 - 12}" y="{py}" width="{pw}" height="4" rx="2" fill="{c["track"]}"/>')
    out.append(
        f'<rect x="{X0 - 12}" y="{py}" width="0" height="4" rx="2" fill="{c["accent"]}">'
        + anim_lin("width", [0, 0, pw, pw, 0], [0, SCAN_START, SCAN_END, end_hold, CYCLE])
        + "</rect>"
    )

    # ---- final result line
    parts = []
    for j, (label, value) in enumerate(SUMMARY):
        sep = f'<tspan fill="{c["hud"]}">   ·   </tspan>' if j else ""
        parts.append(f'{sep}<tspan fill="{c["hud"]}">{label} </tspan>'
                     f'<tspan fill="{c["text"]}" font-weight="700">{value}</tspan>')
    out.append(
        f'<text x="{W / 2}" y="{H - 8}" text-anchor="middle" {FONT} font-size="12" opacity="0">'
        + anim("opacity", [0, 1, 0], [0, SCAN_END + 0.25, end_hold])
        + "".join(parts) + "</text>"
    )

    out.append("</svg>")
    return "\n".join(out)


def main():
    os.makedirs("assets", exist_ok=True)
    for theme in THEMES:
        path = os.path.join("assets", f"medscan-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(theme))
        print("wrote", path)


if __name__ == "__main__":
    main()
