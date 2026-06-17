"""
PIL-based smart board visual card generator for ShikshAI.
Creates high-resolution (1200px wide) cards optimised for classroom projectors.
Emoji characters are avoided in PIL draws to maximise cross-platform compatibility.
"""
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap
import functools

# ── Pre-load bundled font bytes at import time ─────────────────────────────────
# Tries __file__-relative AND cwd-relative paths so it works on every platform.
def _read_font_file(filename: str) -> bytes | None:
    candidates = []
    try:
        _d = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(_d, "..", "assets", "fonts", filename))
    except Exception:
        pass
    try:
        candidates.append(os.path.join(os.getcwd(), "assets", "fonts", filename))
    except Exception:
        pass
    for p in candidates:
        try:
            with open(os.path.normpath(p), "rb") as f:
                return f.read()
        except Exception:
            continue
    return None

_NOTO_BYTES  = _read_font_file("NotoSansDevanagari-Regular.ttf")
_DEJAVU_BYTES = _read_font_file("DejaVuSans.ttf")

# ── Colour palette ────────────────────────────────────────────────────────────
BG            = (10,  14,  39)
CARD_BG       = (22,  28,  60)
INDIGO        = (99,  102, 241)
PURPLE        = (139,  92, 246)
EMERALD       = (16,  185, 129)
AMBER         = (251, 191,  36)
TEAL          = (20,  184, 166)
TEXT_PRIMARY  = (226, 232, 240)
TEXT_SECONDARY= (148, 163, 184)
WHITE         = (255, 255, 255)


@functools.lru_cache(maxsize=64)
def _load_font(size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    """Load Latin/ASCII font — DejaVuSans first (full Latin coverage)."""
    # 1. Bundled DejaVuSans (Latin, full coverage)
    if _DEJAVU_BYTES:
        try:
            return ImageFont.truetype(io.BytesIO(_DEJAVU_BYTES), size)
        except Exception:
            pass
    # 2. Windows system fonts
    for path in [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\Nirmala.ttc",
    ]:
        try:
            return ImageFont.truetype(path, size, index=index)
        except Exception:
            continue
    # 3. Linux system fonts
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


@functools.lru_cache(maxsize=64)
def _load_font_deva(size: int) -> ImageFont.FreeTypeFont:
    """Load Devanagari font — NotoSansDevanagari first (Hindi support)."""
    # 1. Bundled NotoSansDevanagari
    if _NOTO_BYTES:
        try:
            return ImageFont.truetype(io.BytesIO(_NOTO_BYTES), size)
        except Exception:
            pass
    # 2. Windows — Nirmala supports Devanagari
    for path in [
        "C:\\Windows\\Fonts\\Nirmala.ttc",
        "C:\\Windows\\Fonts\\NirmalaUI.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    # 3. Linux Noto Devanagari
    for path in [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    # 4. Fall back to Latin font (Hindi won't render but at least no crash)
    return _load_font(size)


def _is_truetype(font) -> bool:
    return isinstance(font, ImageFont.FreeTypeFont)


def _has_devanagari(text: str) -> bool:
    return any(0x0900 <= ord(c) <= 0x097F for c in text)


def _text_width(font, text: str) -> int:
    """Return rendered pixel width of text for the given font."""
    try:
        return int(font.getlength(text))
    except Exception:
        try:
            bb = font.getbbox(text)
            return bb[2] - bb[0]
        except Exception:
            return len(text) * 12


def _split_script_runs(text: str) -> list:
    """Split text into (segment, is_devanagari) runs by character script."""
    runs = []
    cur, cur_deva = "", None
    for c in text:
        is_d = 0x0900 <= ord(c) <= 0x097F
        if cur_deva is None:
            cur_deva = is_d
        if is_d != cur_deva:
            if cur:
                runs.append((cur, cur_deva))
            cur, cur_deva = c, is_d
        else:
            cur += c
    if cur:
        runs.append((cur, cur_deva))
    return runs


def _mixed_line_width(text: str, size: int) -> int:
    """Pixel width of mixed-script text across both fonts."""
    f_deva = _load_font_deva(size)
    f_lat  = _load_font(size)
    total  = 0
    for seg, is_d in _split_script_runs(text):
        font    = f_deva if is_d else f_lat
        seg_out = seg if is_d else _sci_ascii(seg)
        total  += _text_width(font, seg_out)
    return total


def _draw_mixed_line(draw, x: int, y: int, text: str, fill, size: int):
    """Left-aligned per-segment renderer for mixed Devanagari+Latin text.

    NotoSansDevanagari has no Latin glyphs, so 'CO2 अवशोषित' needs
    each run rendered with its own font.
    """
    f_deva = _load_font_deva(size)
    f_lat  = _load_font(size)
    for seg, is_d in _split_script_runs(text):
        font    = f_deva if is_d else f_lat
        seg_out = seg if is_d else _sci_ascii(seg)
        try:
            draw.text((x, y), seg_out, fill=fill, font=font)
            x += _text_width(font, seg_out)
        except Exception:
            pass


def _draw_content(draw, pos, text: str, fill, size: int, anchor=None):
    """Smart content renderer: per-segment font selection for mixed scripts."""
    text     = str(text)
    has_deva = _has_devanagari(text)
    if not has_deva:
        _draw_sci(draw, pos, text, fill, _load_font(size), anchor)
    elif anchor is None:
        # Left-aligned: render segment by segment
        _draw_mixed_line(draw, pos[0], pos[1], text, fill, size)
    elif anchor == "mm":
        # Centred: measure total width, then position so ink centre = pos
        total_w = _mixed_line_width(text, size)
        f_ref   = _load_font_deva(size) if _has_devanagari(text) else _load_font(size)
        try:
            sample = text[:20] if len(text) > 20 else text
            bb     = f_ref.getbbox(sample)
            draw_y = pos[1] - (bb[1] + bb[3]) // 2
        except Exception:
            draw_y = pos[1] - int(size * 0.45)
        _draw_mixed_line(draw, pos[0] - total_w // 2, draw_y, text, fill, size)
    else:
        # Other anchors: use Devanagari font directly
        _draw_text_safe(draw, pos, text, fill, _load_font_deva(size), anchor)


# Common Unicode → ASCII substitutions for scientific/math text
_UNICODE_MAP = str.maketrans({
    "—": "--", "–": "-",  # em-dash, en-dash
    "’": "'",  "‘": "'",  # curly single quotes
    "“": '"',  "”": '"',  # curly double quotes
    "→": "->", "←": "<-", "↑": "^", "↓": "v", "↔": "<->",
    "²": "^2", "³": "^3", "⁴": "^4", "⁰": "^0", "¹": "^1",
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
    "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9",
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
    "π": "pi",   "Δ": "Delta", "Σ": "Sigma", "μ": "mu",
    "λ": "lambda","ω": "omega","θ": "theta","φ": "phi",
    "×": "x",    "÷": "/",    "√": "sqrt", "∞": "inf",
    "≈": "~",    "≠": "!=",   "≤": "<=",   "≥": ">=",
    "°": " deg", "·": ".",    "±": "+/-",  "∑": "sum",
    "∫": "int",  "∂": "d",    "∇": "del",
})


def _sci_ascii(text: str) -> str:
    """Convert common scientific/math Unicode to ASCII, keep Latin-1."""
    text = text.translate(_UNICODE_MAP)
    return "".join(c if ord(c) < 256 else "?" for c in text)


def _draw_text_safe(draw, pos, text: str, fill, font, anchor=None):
    """Draw text safely — handles anchor failure for bitmap/non-TrueType fonts."""
    for use_anchor in [True, False]:
        try:
            a = anchor if (anchor and use_anchor) else None
            if a:
                draw.text(pos, text, fill=fill, font=font, anchor=a)
            else:
                draw.text(pos, text, fill=fill, font=font)
            return
        except Exception:
            continue


def _draw_sci(draw, pos, text: str, fill, font, anchor=None):
    """Draw scientific text — always converts Unicode math/chem symbols to ASCII first."""
    _draw_text_safe(draw, pos, _sci_ascii(str(text)), fill, font, anchor)


def _rr(draw, xy, r, fill, outline=None, w=2):
    """Draw a rounded rectangle."""
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)


def _gradient_bg(img: Image.Image, top: tuple, bot: tuple):
    """Fill image with a vertical gradient."""
    draw  = ImageDraw.Draw(img)
    W, H  = img.size
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


# ── Feature 1: Concept Card ───────────────────────────────────────────────────

def create_concept_card(data: dict) -> bytes:
    W = 1200

    is_hindi   = _has_devanagari(
        data.get("title", "") + data.get("explanation", "")
    )
    wrap_expl  = 48 if is_hindi else 44
    wrap_panel = 22 if is_hindi else 26
    wrap_kp    = 46 if is_hindi else 54

    formula = data.get("formula") or data.get("key_equation") or ""
    if not formula:
        for pt in data.get("key_points", []):
            if any(c in str(pt) for c in ["=", "^", "²", "³", "∑", "∆"]):
                formula = str(pt)
                break

    HDR_H   = 134
    FML_TOP = HDR_H + 4
    FML_BOT = HDR_H + 118   # 114px tall formula box

    expl_y     = FML_BOT + 14 if formula else HDR_H + 10
    expl_lines = textwrap.wrap(data.get("explanation", ""), width=wrap_expl)[:5]
    expl_h     = 62 + max(len(expl_lines), 2) * 64 + 14
    mid_y      = expl_y + expl_h + 16
    PANEL_H    = 252
    kp_y       = mid_y + PANEL_H + 16
    kpts       = data.get("key_points", [])[:3]
    kp_h       = 62 + max(len(kpts), 1) * 68 + 12
    H          = kp_y + kp_h + 96

    img  = Image.new("RGB", (W, H), BG)
    _gradient_bg(img, (6, 10, 30), (18, 24, 62))
    draw = ImageDraw.Draw(img)

    f_lbl    = _load_font(25)
    f_lbl_sm = _load_font(22)
    f_badge  = _load_font(19)

    # ── HEADER ────────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, HDR_H], fill=(20, 28, 96))
    draw.rectangle([0, 0, 7, HDR_H], fill=INDIGO)
    draw.rectangle([W-7, 0, W, HDR_H], fill=PURPLE)
    draw.rectangle([0, HDR_H-5, W, HDR_H], fill=INDIGO)

    _rr(draw, [14, 14, 154, 46], 8, INDIGO, None)
    _draw_sci(draw, (84, 30), "ShikshAI", WHITE, f_badge, anchor="mm")

    title_text  = data.get("title", "Concept")
    title_wrap  = 36
    title_lines = textwrap.wrap(title_text, width=title_wrap)[:2]
    if len(title_lines) == 1:
        _draw_content(draw, (W // 2, HDR_H // 2), title_lines[0], WHITE, 74, anchor="mm")
    else:
        _draw_content(draw, (W // 2, 38), title_lines[0], WHITE, 58, anchor="mm")
        _draw_content(draw, (W // 2, 98), title_lines[1], (215, 220, 255), 50, anchor="mm")

    # ── FORMULA BOX ──────────────────────────────────────────────────────────
    if formula:
        _rr(draw, [32, FML_TOP, W-32, FML_BOT], 14, (24, 20, 6), AMBER, w=2)
        _rr(draw, [50, FML_TOP, 174, FML_TOP+24], 8, AMBER, None)
        _draw_sci(draw, (112, FML_TOP+12), "FORMULA", BG, f_badge, anchor="mm")
        _draw_sci(draw, (W//2, (FML_TOP+FML_BOT)//2), str(formula)[:85],
                  AMBER, _load_font(52), anchor="mm")

    # ── EXPLANATION ──────────────────────────────────────────────────────────
    _rr(draw, [32, expl_y, W-32, expl_y+expl_h], 14, (14, 18, 55), INDIGO, w=1)
    draw.rectangle([32, expl_y+16, 36, expl_y+expl_h-16], fill=INDIGO)
    _draw_sci(draw, (52, expl_y+17), "EXPLANATION", (120, 125, 255), f_lbl)
    draw.line([(52, expl_y+40), (268, expl_y+40)], fill=(70, 75, 200), width=1)
    for i, line in enumerate(expl_lines):
        _draw_content(draw, (52, expl_y+52+i*64), line, TEXT_PRIMARY, 50)

    # ── EXAMPLE + FUN FACT (two-column) ──────────────────────────────────────
    _rr(draw, [32, mid_y, 576, mid_y+PANEL_H], 14, (10, 20, 50), EMERALD, w=2)
    draw.rectangle([32, mid_y+16, 36, mid_y+PANEL_H-16], fill=EMERALD)
    _draw_sci(draw, (52, mid_y+17), "EXAMPLE", EMERALD, f_lbl)
    draw.line([(52, mid_y+40), (258, mid_y+40)], fill=EMERALD, width=1)
    for i, line in enumerate(textwrap.wrap(data.get("example", ""), width=wrap_panel)[:4]):
        _draw_content(draw, (52, mid_y+50+i*52), line, TEXT_PRIMARY, 40)

    _rr(draw, [624, mid_y, W-32, mid_y+PANEL_H], 14, (22, 16, 50), AMBER, w=2)
    draw.rectangle([624, mid_y+16, 628, mid_y+PANEL_H-16], fill=AMBER)
    _draw_sci(draw, (644, mid_y+17), "FUN FACT", AMBER, f_lbl)
    draw.line([(644, mid_y+40), (848, mid_y+40)], fill=AMBER, width=1)
    for i, line in enumerate(textwrap.wrap(data.get("fun_fact", ""), width=wrap_panel)[:4]):
        _draw_content(draw, (644, mid_y+50+i*52), line, TEXT_PRIMARY, 40)

    # ── KEY POINTS ────────────────────────────────────────────────────────────
    _rr(draw, [32, kp_y, W-32, kp_y+kp_h], 14, (14, 16, 54), PURPLE, w=1)
    draw.rectangle([32, kp_y+16, 36, kp_y+kp_h-16], fill=PURPLE)
    _draw_sci(draw, (52, kp_y+15), "KEY POINTS", (180, 140, 255), f_lbl)
    draw.line([(52, kp_y+38), (240, kp_y+38)], fill=(100, 60, 200), width=1)
    dot_colors = [INDIGO, EMERALD, AMBER]
    for i, pt in enumerate(kpts):
        cy  = kp_y + 50 + i * 68
        col = dot_colors[i % 3]
        draw.ellipse([52, cy, 90, cy+38], fill=col)
        _draw_sci(draw, (71, cy+19), str(i+1), WHITE, f_lbl_sm, anchor="mm")
        pt_lines = textwrap.wrap(str(pt), width=wrap_kp)
        _draw_content(draw, (104, cy+2), pt_lines[0] if pt_lines else str(pt), TEXT_PRIMARY, 40)

    # ── HINDI SUMMARY STRIP ───────────────────────────────────────────────────
    draw.rectangle([0, H-82, W, H], fill=(14, 20, 62))
    draw.line([(0, H-82), (W, H-82)], fill=INDIGO, width=2)
    hindi = str(data.get("hindi_summary", ""))[:100]
    _draw_content(draw, (W//2, H-38), hindi, AMBER, 36, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Feature 2: Quiz Card ──────────────────────────────────────────────────────

def create_quiz_card(q_data: dict, q_num: int, total: int) -> bytes:
    W, H = 1200, 560
    img  = Image.new("RGB", (W, H), BG)
    _gradient_bg(img, (10, 14, 39), (18, 22, 55))
    draw = ImageDraw.Draw(img)

    f_lg = _load_font(40)
    f_md = _load_font(32)
    f_sm = _load_font(28)

    # Header
    draw.rectangle([0, 0, W, 68], fill=PURPLE)
    _draw_sci(draw, (W // 2, 34), f"Question  {q_num}  of  {total}", WHITE, f_lg, anchor="mm")

    # Question box
    _rr(draw, [28, 80, W - 28, 200], 14, CARD_BG, PURPLE)
    for i, line in enumerate(textwrap.wrap(q_data.get("question", ""), width=55)[:3]):
        _draw_content(draw, (52, 96 + i * 36), line, TEXT_PRIMARY, 32)

    # Options (2x2 grid)
    opts   = q_data.get("options", {})
    colors = {"A": INDIGO, "B": EMERALD, "C": AMBER, "D": (239, 68, 68)}
    pos    = [(28, 215), (620, 215), (28, 345), (620, 345)]
    for i, (key, val) in enumerate(opts.items()):
        x1, y1 = pos[i]
        c = colors.get(key, INDIGO)
        _rr(draw, [x1, y1, x1 + 565, y1 + 115], 12, CARD_BG, c)
        _draw_sci(draw, (x1 + 20, y1 + 16), f"{key})", c, f_lg)
        for j, line in enumerate(textwrap.wrap(str(val), width=30)[:2]):
            _draw_content(draw, (x1 + 72, y1 + 16 + j * 36), line, TEXT_PRIMARY, 28)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Feature 3: Translation Card ───────────────────────────────────────────────

def create_translation_card(data: dict) -> bytes:
    W, H = 1200, 460
    img  = Image.new("RGB", (W, H), BG)
    _gradient_bg(img, (10, 14, 39), (16, 22, 50))
    draw = ImageDraw.Draw(img)

    f_lg   = _load_font(38)
    f_md   = _load_font(30)
    f_sm   = _load_font(24)
    f_deva = _load_font_deva(28)

    # Header
    draw.rectangle([0, 0, W, 64], fill=TEAL)
    _draw_sci(draw, (W // 2, 32), "Bilingual Translation  |  ShikshAI", WHITE, f_lg, anchor="mm")

    # Original text panel
    _rr(draw, [18, 76, 576, 280], 14, CARD_BG, TEAL)
    _draw_sci(draw, (40, 86), "[ Original ]", TEAL, f_sm)
    for i, line in enumerate(textwrap.wrap(_sci_ascii(data.get("original", "")), width=44)[:4]):
        _draw_sci(draw, (40, 116 + i * 38), line, TEXT_PRIMARY, f_md)

    # Translation panel — uses Devanagari font for Hindi rendering
    _rr(draw, [624, 76, W - 18, 280], 14, CARD_BG, INDIGO)
    _draw_sci(draw, (644, 86), "[ Translation ]", INDIGO, f_sm)
    for i, line in enumerate(textwrap.wrap(data.get("translation", ""), width=44)[:4]):
        _draw_text_safe(draw, (644, 116 + i * 38), line, TEXT_PRIMARY, f_deva)

    # Key words strip — render English part with Latin font, Hindi with Devanagari font
    _rr(draw, [18, 292, W - 18, 400], 12, CARD_BG, AMBER)
    _draw_sci(draw, (40, 302), "Key Words:", AMBER, f_sm)
    kws = data.get("key_words", [])[:5]
    for i, kw in enumerate(kws):
        x = 40 + i * 232
        if isinstance(kw, dict):
            vals = list(kw.values())[:2]
            part1 = str(vals[0])[:10] if vals else ""
            part2 = str(vals[1])[:10] if len(vals) > 1 else ""
            _draw_sci(draw, (x, 334), part1, TEXT_PRIMARY, f_sm)
            _draw_sci(draw, (x + 75, 334), "->", TEXT_SECONDARY, f_sm)
            _draw_text_safe(draw, (x + 100, 334), part2, TEXT_PRIMARY, f_deva)
        else:
            _draw_text_safe(draw, (x, 334), str(kw)[:22], TEXT_PRIMARY, f_deva)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Feature 4: Activity Guide Card ───────────────────────────────────────────

def create_activity_card(data: dict) -> bytes:
    """PIL smart board visual for Feature 4 — Hands-Free Activity Guide."""
    W, H   = 1200, 590
    ORANGE = (234, 88,  12)
    img    = Image.new("RGB", (W, H), BG)
    _gradient_bg(img, BG, (18, 25, 60))
    draw   = ImageDraw.Draw(img)

    f_xl = _load_font(40)
    f_lg = _load_font(32)
    f_md = _load_font(26)
    f_sm = _load_font(22)

    # Header bar
    draw.rectangle([0, 0, W, 68], fill=ORANGE)
    title = _sci_ascii(data.get("title", "Classroom Activity")[:55])
    _draw_sci(draw, (W // 2, 34), f"Activity  |  {title}",
              WHITE, f_xl, anchor="mm")

    # Objective strip
    _rr(draw, [18, 78, W - 18, 132], 10, CARD_BG, AMBER)
    _draw_sci(draw, (36, 88), "[ Objective ]", AMBER, f_sm)
    obj = data.get("objective", "")
    for i, ln in enumerate(textwrap.wrap(_sci_ascii(obj), width=100)[:2]):
        _draw_sci(draw, (36, 106 + i * 22), ln, TEXT_PRIMARY, f_sm)

    # Steps — up to 4 in a 2 x 2 grid
    steps  = data.get("steps", [])[:4]
    s_clrs = [INDIGO, EMERALD, AMBER, PURPLE]
    for idx, step in enumerate(steps):
        row, col = divmod(idx, 2)
        x1 = 18  + col * 594
        y1 = 142 + row * 195
        x2, y2 = x1 + 574, y1 + 180
        sc = s_clrs[idx % 4]

        _rr(draw, [x1, y1, x2, y2], 12, CARD_BG, sc)
        draw.ellipse([x1 + 14, y1 + 14, x1 + 50, y1 + 50], fill=sc)
        _draw_sci(draw, (x1 + 32, y1 + 32), str(step.get("step", idx + 1)),
                  WHITE, f_md, anchor="mm")
        instr = step.get("instruction", "")
        for j, ln in enumerate(textwrap.wrap(_sci_ascii(instr), width=36)[:3]):
            _draw_sci(draw, (x1 + 62, y1 + 14 + j * 30), ln, TEXT_PRIMARY, f_sm)
        if step.get("duration_min"):
            _draw_sci(draw, (x1 + 62, y1 + 112),
                      f"Duration: {step['duration_min']} min",
                      sc, f_sm)

    # Footer: group size + materials
    draw.rectangle([0, 548, W, H], fill=(20, 25, 65))
    group = _sci_ascii(str(data.get("group_size", "")))
    mats  = " | ".join(_sci_ascii(str(m)) for m in data.get("materials", [])[:3])
    _draw_sci(draw, (W // 2, 568),
              f"Group: {group}   --   Materials: {mats}",
              TEXT_SECONDARY, f_sm, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ── Diagram label translations ────────────────────────────────────────────────

_DIAG_LABELS = {
    "en": {
        # Right Triangle
        "LEGEND": "LEGEND", "Perpendicular": "Perpendicular", "Base": "Base",
        "Hypotenuse": "Hypotenuse", "Formula": "Formula", "(Pythagoras)": "(Pythagoras)",
        # Circle
        "r (radius)": "r (radius)", "d (diameter)": "d (diameter)", "Key Facts": "Key Facts",
        # Photosynthesis
        "Photosynthesis": "Photosynthesis",
        "Sunlight": "Sunlight", "Water (H2O)": "Water (H2O)", "CO2": "CO2",
        "Chlorophyll": "Chlorophyll", "Glucose": "Glucose", "Oxygen O2": "Oxygen O2",
        "Energy source": "Energy source", "From roots": "From roots", "From air": "From air",
        "Green pigment": "Green pigment", "Food / energy": "Food / energy", "Released out": "Released out",
        "photo_eq": "6CO2 + 6H2O + light  ->  C6H12O6 + 6O2",
        # Water Cycle
        "Water Cycle": "Water Cycle", "Ocean/River": "Ocean/River",
        "Evaporation": "Evaporation", "Condensation": "Condensation",
        "Clouds": "Clouds", "Precipitation": "Precipitation",
        # Heart
        "Human Heart -- Anatomy": "Human Heart -- Anatomy",
        "Right": "Right", "Left": "Left", "Atrium": "Atrium", "Ventricle": "Ventricle",
        "Septum": "Septum", "Aorta": "Aorta",
        "Pulmonary Vein": "Pulmonary Vein", "Pulmonary Artery": "Pulmonary Artery",
        "Superior Vena Cava": "Superior Vena Cava", "Inferior Vena Cava": "Inferior Vena Cava",
        "Aorta (to body)": "Aorta (to body)",
        "deoxy_blood": "Deoxygenated blood (body->heart->lungs)",
        "oxy_blood":   "Oxygenated blood (lungs->heart->body)",
        "Heart Facts": "Heart Facts",
        "heart_beats": "~72 beats/min | 5L blood/min",
        "heart_size":  "Size of your fist | Beats 2.5B times",
        # Food Chain
        "Food Chain": "Food Chain", "Sun": "Sun",
        "Producers": "Producers", "Herbivores": "Herbivores",
        "Carnivores": "Carnivores", "Decomposers": "Decomposers",
        "Energy Source": "Energy Source", "Plants / Grass": "Plants / Grass",
        "Rabbit / Deer": "Rabbit / Deer", "Fox / Lion": "Fox / Lion",
        "Fungi / Bacteria": "Fungi / Bacteria",
        "food_flow": "Energy flows: Sun->Producers->Consumers->Decomposers",
        # Cell
        "Animal Cell Structure": "Animal Cell Structure",
        "Nucleus": "Nucleus", "(DNA here)": "(DNA here)",
        "Mitochondria": "Mitochondria", "Mito\nchondria": "Mito\nchondria",
        "ORGANELLES": "ORGANELLES", "Cell Membrane": "Cell Membrane",
        "ctrl_enter": "Controls what enters/exits",
        "brain_dna":  "Brain of the cell, has DNA",
        "powerhouse": "Powerhouse, makes energy",
        "cytoplasm":  "Cytoplasm", "cytoplasm_desc": "Jelly-like fluid inside",
        # Newton
        "Newton's Laws": "Newton's Laws",
        "1st_title": "1st Law - Inertia",
        "1st_l1": "Object stays at rest or in motion",
        "1st_l2": "unless an external force acts on it.",
        "2nd_title": "2nd Law - F = ma",
        "2nd_l1": "Force = Mass x Acceleration",
        "2nd_l2": "More force = more acceleration.",
        "3rd_title": "3rd Law - Action-Reaction",
        "3rd_l1": "Every action has an equal and",
        "3rd_l2": "opposite reaction.",
        "Force (Newton, N)": "Force (Newton, N)",
        "Mass (kg)": "Mass (kg)",
        "Acceleration (m/s^2)": "Acceleration (m/s^2)",
        # Shared
        "footer": "ShikshAI  |  Smart Board Visual",
    },
    "hi": {
        # Right Triangle
        "LEGEND": "विवरण", "Perpendicular": "लम्ब", "Base": "आधार",
        "Hypotenuse": "कर्ण", "Formula": "सूत्र", "(Pythagoras)": "(पाइथागोरस)",
        # Circle
        "r (radius)": "r (त्रिज्या)", "d (diameter)": "d (व्यास)", "Key Facts": "मुख्य तथ्य",
        # Photosynthesis
        "Photosynthesis": "प्रकाश संश्लेषण",
        "Sunlight": "सूर्य प्रकाश", "Water (H2O)": "पानी (H2O)", "CO2": "CO2",
        "Chlorophyll": "क्लोरोफिल", "Glucose": "ग्लूकोज", "Oxygen O2": "ऑक्सीजन O2",
        "Energy source": "ऊर्जा स्रोत", "From roots": "जड़ों से", "From air": "हवा से",
        "Green pigment": "हरा वर्णक", "Food / energy": "भोजन/ऊर्जा", "Released out": "बाहर निकलती",
        "photo_eq": "6CO2 + 6H2O + प्रकाश  ->  C6H12O6 + 6O2",
        # Water Cycle
        "Water Cycle": "जल चक्र", "Ocean/River": "समुद्र/नदी",
        "Evaporation": "वाष्पीकरण", "Condensation": "संघनन",
        "Clouds": "बादल", "Precipitation": "वर्षा",
        # Heart
        "Human Heart -- Anatomy": "मानव हृदय -- शरीर रचना",
        "Right": "दायाँ", "Left": "बायाँ", "Atrium": "अलिंद", "Ventricle": "निलय",
        "Septum": "पट", "Aorta": "महाधमनी",
        "Pulmonary Vein": "फुफ्फुस शिरा", "Pulmonary Artery": "फुफ्फुस धमनी",
        "Superior Vena Cava": "उच्च महाशिरा", "Inferior Vena Cava": "निम्न महाशिरा",
        "Aorta (to body)": "महाधमनी (शरीर को)",
        "deoxy_blood": "अशुद्ध रक्त (शरीर->हृदय->फेफड़े)",
        "oxy_blood":   "शुद्ध रक्त (फेफड़े->हृदय->शरीर)",
        "Heart Facts": "हृदय तथ्य",
        "heart_beats": "~72 धड़कन/मिनट | 5L रक्त/मिनट",
        "heart_size":  "मुट्ठी के बराबर | 2.5 अरब बार धड़कता है",
        # Food Chain
        "Food Chain": "खाद्य श्रृंखला", "Sun": "सूर्य",
        "Producers": "उत्पादक", "Herbivores": "शाकाहारी",
        "Carnivores": "मांसाहारी", "Decomposers": "अपघटक",
        "Energy Source": "ऊर्जा स्रोत", "Plants / Grass": "पौधे/घास",
        "Rabbit / Deer": "खरगोश/हिरण", "Fox / Lion": "लोमड़ी/शेर",
        "Fungi / Bacteria": "कवक/जीवाणु",
        "food_flow": "ऊर्जा: सूर्य->उत्पादक->उपभोक्ता->अपघटक",
        # Cell
        "Animal Cell Structure": "जंतु कोशिका संरचना",
        "Nucleus": "केंद्रक", "(DNA here)": "(DNA यहाँ)",
        "Mitochondria": "माइटोकॉन्ड्रिया", "Mito\nchondria": "माइटो\nकॉन्ड्रिया",
        "ORGANELLES": "कोशिकांग", "Cell Membrane": "कोशिका झिल्ली",
        "ctrl_enter": "क्या प्रवेश/निकास नियंत्रित",
        "brain_dna":  "कोशिका मस्तिष्क, DNA युक्त",
        "powerhouse": "शक्तिगृह, ऊर्जा बनाता है",
        "cytoplasm":  "कोशिकाद्रव्य", "cytoplasm_desc": "जेली जैसा तरल पदार्थ",
        # Newton
        "Newton's Laws": "न्यूटन के नियम",
        "1st_title": "प्रथम नियम - जड़त्व",
        "1st_l1": "वस्तु विराम या गति में रहती है",
        "1st_l2": "जब तक बाह्य बल न लगे।",
        "2nd_title": "द्वितीय नियम - F = ma",
        "2nd_l1": "बल = द्रव्यमान x त्वरण",
        "2nd_l2": "अधिक बल = अधिक त्वरण।",
        "3rd_title": "तृतीय नियम - क्रिया-प्रतिक्रिया",
        "3rd_l1": "प्रत्येक क्रिया की समान व",
        "3rd_l2": "विपरीत प्रतिक्रिया होती है।",
        "Force (Newton, N)": "बल (न्यूटन, N)",
        "Mass (kg)": "द्रव्यमान (kg)",
        "Acceleration (m/s^2)": "त्वरण (m/s^2)",
        # Shared
        "footer": "ShikshAI  |  स्मार्ट बोर्ड विज़ुअल",
    },
}


def _L(key: str, lang: str) -> str:
    """Get translated diagram label. Falls back to English if key missing."""
    return _DIAG_LABELS.get(lang, _DIAG_LABELS["en"]).get(key, _DIAG_LABELS["en"].get(key, key))


def _draw_lbl(draw, pos, key: str, fill, size: int, lang: str, anchor=None):
    """Draw a translated diagram label using the correct script font."""
    _draw_content(draw, pos, _L(key, lang), fill, size, anchor)


# ── Concept Diagram (PIL-based, replaces Mermaid for visual accuracy) ─────────

def _detect_diagram_type(data: dict) -> str:
    title   = (data.get("title") or "").lower()
    formula = (data.get("formula") or "").lower()
    mermaid = (data.get("mermaid") or "").lower()
    text    = title + formula + mermaid

    if any(k in text for k in ["pythagoras", "right triangle", "hypotenuse",
                                "a² + b²", "a^2 + b^2",
                                "पाइथागोरस", "समकोण त्रिभुज", "कर्ण"]):
        return "right_triangle"
    if any(k in text for k in ["circle", "circumference", "diameter", "radius",
                                "pi r", "2pi", "πr",
                                "वृत्त", "त्रिज्या", "व्यास", "परिधि"]):
        return "circle"
    if any(k in text for k in ["photosynthesis", "sunlight", "chlorophyll",
                                "glucose", "co2", "carbon dioxide",
                                "प्रकाश संश्लेषण", "क्लोरोफिल", "ग्लूकोज"]):
        return "photosynthesis"
    if any(k in text for k in ["water cycle", "evaporation", "condensation",
                                "precipitation", "hydrological",
                                "जल चक्र", "वाष्पीकरण", "संघनन", "वर्षा"]):
        return "water_cycle"
    if any(k in text for k in ["heart", "cardiac", "atrium", "ventricle",
                                "heartbeat", "blood pump", "circulatory",
                                "हृदय", "अलिंद", "निलय", "रक्त"]):
        return "heart"
    if any(k in text for k in ["food chain", "food web", "producer", "consumer",
                                "herbivore", "carnivore", "decomposer",
                                "खाद्य श्रृंखला", "उत्पादक", "शाकाहारी", "मांसाहारी"]):
        return "food_chain"
    if any(k in text for k in ["cell", "nucleus", "mitochondria", "membrane",
                                "cytoplasm", "organelle",
                                "कोशिका", "केंद्रक", "माइटोकॉन्ड्रिया", "कोशिकांग"]):
        return "cell"
    if any(k in text for k in ["newton", "force", "motion", "acceleration",
                                "f = ma", "friction", "gravity", "inertia",
                                "न्यूटन", "बल", "त्वरण", "जड़त्व", "गुरुत्व"]):
        return "newton"
    return "flowchart"


def create_concept_diagram(data: dict, lang: str = "en") -> bytes:
    dtype = _detect_diagram_type(data)
    if dtype == "right_triangle":
        return _diagram_right_triangle(data, lang)
    if dtype == "circle":
        return _diagram_circle(data, lang)
    if dtype == "photosynthesis":
        return _diagram_photosynthesis(data, lang)
    if dtype == "water_cycle":
        return _diagram_water_cycle(data, lang)
    if dtype == "heart":
        return _diagram_heart(data, lang)
    if dtype == "food_chain":
        return _diagram_food_chain(data, lang)
    if dtype == "cell":
        return _diagram_cell(data, lang)
    if dtype == "newton":
        return _diagram_newton(data, lang)
    return _diagram_flowchart(data, lang)


def _diagram_right_triangle(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 580
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)

    f_big  = _load_font(32)
    f_med  = _load_font(24)
    f_sm   = _load_font(18)
    f_tiny = _load_font(15)

    # Header
    draw.rectangle([0, 0, W, 56], fill=(28, 36, 100))
    formula = data.get("formula") or "a^2 + b^2 = c^2"
    _draw_content(draw, (W // 2, 28), formula, AMBER, 32, anchor="mm")

    # Triangle vertices  (right angle at bottom-left)
    Ax, Ay = 160, 480   # right angle
    Bx, By = 600, 480   # bottom right
    Cx, Cy = 160, 140   # top

    # Draw filled triangle
    draw.polygon([(Ax, Ay), (Bx, By), (Cx, Cy)],
                 fill=(18, 28, 72), outline=INDIGO)
    draw.line([(Ax, Ay), (Bx, By)], fill=INDIGO, width=3)
    draw.line([(Ax, Ay), (Cx, Cy)], fill=EMERALD, width=3)
    draw.line([(Bx, By), (Cx, Cy)], fill=AMBER, width=3)

    # Right-angle marker
    m = 28
    draw.line([(Ax, Ay - m), (Ax + m, Ay - m)], fill=WHITE, width=2)
    draw.line([(Ax + m, Ay - m), (Ax + m, Ay)], fill=WHITE, width=2)

    # Side labels
    _draw_sci(draw, (Ax - 44, (Ay + Cy) // 2), "a", EMERALD, f_big, anchor="mm")
    _draw_sci(draw, ((Ax + Bx) // 2, Ay + 36), "b", INDIGO,  f_big, anchor="mm")
    # Hypotenuse label (perpendicular to line BC)
    hx = (Bx + Cx) // 2 + 36
    hy = (By + Cy) // 2 - 10
    _draw_sci(draw, (hx, hy), "c", AMBER, f_big, anchor="mm")

    # Small squares on each side (visual proof)
    sq = 60
    # Square on side a (left of vertical)
    draw.rectangle([Ax - sq - 4, Cy, Ax - 4, Ay], outline=EMERALD, width=2)
    _draw_sci(draw, (Ax - sq // 2 - 4, (Cy + Ay) // 2), "a^2", EMERALD, f_sm, anchor="mm")
    # Square on side b (below horizontal)
    draw.rectangle([Ax, Ay + 4, Bx, Ay + sq + 4], outline=INDIGO, width=2)
    _draw_sci(draw, ((Ax + Bx) // 2, Ay + sq // 2 + 4), "b^2", INDIGO, f_sm, anchor="mm")

    # Legend box
    _rr(draw, [640, 120, 875, 330], 12, (16, 22, 58), PURPLE)
    _draw_lbl(draw, (757, 140), "LEGEND", PURPLE, 18, lang, anchor="mm")
    items = [("a", EMERALD, "Perpendicular"), ("b", INDIGO, "Base"),
             ("c", AMBER, "Hypotenuse")]
    for i, (lbl, col, name) in enumerate(items):
        y = 168 + i * 52
        draw.ellipse([660, y, 690, y + 30], fill=col)
        _draw_sci(draw, (676, y + 15), lbl, WHITE, f_sm, anchor="mm")
        _draw_lbl(draw, (705, y + 15), name, TEXT_PRIMARY, 17, lang, anchor="lm")

    # Formula box bottom
    _rr(draw, [640, 350, 875, 480], 12, (20, 28, 80), AMBER)
    _draw_lbl(draw, (757, 375), "Formula", AMBER, 15, lang, anchor="mm")
    _draw_sci(draw, (757, 415), "a^2 + b^2 = c^2", WHITE, f_med, anchor="mm")
    _draw_lbl(draw, (757, 455), "(Pythagoras)", TEXT_SECONDARY, 15, lang, anchor="mm")

    # Footer
    _draw_lbl(draw, (W // 2, H - 16), "footer", (60, 70, 130), 15, lang, anchor="mm")

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_circle(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 500
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(28); f_med = _load_font(22); f_sm = _load_font(17)

    draw.rectangle([0, 0, W, 52], fill=(28, 36, 100))
    _draw_content(draw, (W // 2, 26), data.get("formula") or "C = 2*pi*r  |  A = pi*r^2",
                  AMBER, 28, anchor="mm")

    cx, cy, r = 280, 270, 170
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=INDIGO, width=4)
    draw.line([(cx, cy), (cx + r, cy)], fill=EMERALD, width=3)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=AMBER, width=2)
    draw.ellipse([cx-6, cy-6, cx+6, cy+6], fill=WHITE)
    _draw_lbl(draw, (cx + r // 2, cy - 20), "r (radius)", EMERALD, 17, lang)
    _draw_lbl(draw, (cx - 10, cy - 20), "d (diameter)", AMBER, 17, lang)

    _rr(draw, [560, 100, 860, 440], 12, (16, 22, 58), PURPLE)
    _draw_lbl(draw, (710, 130), "Key Facts", PURPLE, 22, lang, anchor="mm")
    for i, pt in enumerate(data.get("key_points", [])[:3]):
        _draw_content(draw, (580, 170 + i * 70), f"* {str(pt)[:32]}", TEXT_PRIMARY, 17)

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_photosynthesis(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 520
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(26); f_med = _load_font(20); f_sm = _load_font(16)

    draw.rectangle([0, 0, W, 52], fill=(16, 80, 40))
    _draw_lbl(draw, (W // 2, 26), "Photosynthesis", WHITE, 26, lang, anchor="mm")

    boxes = [
        (60,  100, "Sunlight",    AMBER,   "Energy source"),
        (60,  220, "Water (H2O)", TEAL,    "From roots"),
        (60,  340, "CO2",         INDIGO,  "From air"),
        (380, 220, "Chlorophyll", EMERALD, "Green pigment"),
        (680, 130, "Glucose",     AMBER,   "Food / energy"),
        (680, 310, "Oxygen O2",   TEAL,    "Released out"),
    ]
    for x, y, lbl, col, sub in boxes:
        _rr(draw, [x, y, x+240, y+68], 10, (16, 24, 55), col)
        _draw_lbl(draw, (x+120, y+22), lbl, col,           20, lang, anchor="mm")
        _draw_lbl(draw, (x+120, y+50), sub, TEXT_SECONDARY, 16, lang, anchor="mm")

    # Arrows: inputs -> chlorophyll -> outputs
    for sx, sy in [(180,168),(180,288),(180,408)]:
        draw.line([(sx, sy), (380, 254)], fill=WHITE, width=1)
    draw.line([(620, 254), (680, 164)], fill=AMBER, width=2)
    draw.line([(620, 254), (680, 344)], fill=TEAL,  width=2)

    _draw_lbl(draw, (W//2, H-16), "photo_eq", AMBER, 16, lang, anchor="mm")

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_water_cycle(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 500
    img  = Image.new("RGB", (W, H), (6, 10, 30))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(26); f_med = _load_font(20); f_sm = _load_font(15)

    draw.rectangle([0, 0, W, 52], fill=(10, 60, 100))
    _draw_lbl(draw, (W//2, 26), "Water Cycle", WHITE, 26, lang, anchor="mm")

    stages = [
        (120, 380, "Ocean/River",  TEAL),
        (120, 200, "Evaporation",  AMBER),
        (380, 100, "Condensation", INDIGO),
        (640, 100, "Clouds",       PURPLE),
        (750, 300, "Precipitation",TEAL),
    ]
    for x, y, lbl, col in stages:
        _rr(draw, [x-10, y-20, x+160, y+40], 10, (14, 20, 55), col)
        _draw_lbl(draw, (x+75, y+10), lbl, col, 20, lang, anchor="mm")

    arrows = [(230,360,130,240),(230,180,380,120),(530,110,640,110),
              (780,120,800,280),(720,340,280,390)]
    for ax,ay,bx,by in arrows:
        draw.line([(ax,ay),(bx,by)], fill=TEXT_SECONDARY, width=2)

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_heart(data: dict, lang: str = "en") -> bytes:
    W, H = 1000, 640
    img  = Image.new("RGB", (W, H), (245, 245, 250))
    draw = ImageDraw.Draw(img)
    f_big  = _load_font(26)
    f_med  = _load_font(18)
    f_sm   = _load_font(14)
    f_tiny = _load_font(12)

    RED        = (200, 40,  40)
    BLUE       = (40,  70,  200)
    LIGHT_RED  = (240, 160, 160)
    LIGHT_BLUE = (160, 180, 240)
    DARK       = (30,  30,  50)
    OUTLINE    = (60,  60,  80)

    # Header
    draw.rectangle([0, 0, W, 48], fill=(60, 10, 10))
    _draw_lbl(draw, (W//2, 24), "Human Heart -- Anatomy", (255,220,220), 26, lang, anchor="mm")

    # ── Heart body (approximate shape using overlapping ellipses) ─────────────
    hx, hy = 420, 360   # heart centre

    # Outer heart shape — two ellipses for top bumps + bottom point
    draw.ellipse([hx-190, hy-200, hx+10,  hy+20],  fill=LIGHT_RED, outline=OUTLINE, width=2)  # left bump
    draw.ellipse([hx-40,  hy-200, hx+160, hy+20],  fill=LIGHT_RED, outline=OUTLINE, width=2)  # right bump
    # Bottom triangle/point
    draw.polygon([(hx-190, hy-60), (hx+160, hy-60), (hx, hy+220)],
                 fill=LIGHT_RED, outline=OUTLINE)

    # ── Internal chambers ─────────────────────────────────────────────────────
    # Right Atrium (viewer's left top) — blue (deoxygenated)
    draw.ellipse([hx-175, hy-175, hx-30, hy-30], fill=LIGHT_BLUE, outline=BLUE, width=2)
    _draw_lbl(draw, (hx-102, hy-112), "Right",   BLUE, 14, lang, anchor="mm")
    _draw_lbl(draw, (hx-102, hy-96),  "Atrium",  BLUE, 14, lang, anchor="mm")

    # Left Atrium (viewer's right top) — red (oxygenated)
    draw.ellipse([hx+20, hy-175, hx+155, hy-30], fill=LIGHT_RED, outline=RED, width=2)
    _draw_lbl(draw, (hx+87, hy-112), "Left",   RED, 14, lang, anchor="mm")
    _draw_lbl(draw, (hx+87, hy-96),  "Atrium", RED, 14, lang, anchor="mm")

    # Right Ventricle (viewer's left bottom) — blue
    draw.polygon([(hx-175, hy-35), (hx-10, hy-35), (hx-55, hy+175), (hx-185, hy+80)],
                 fill=LIGHT_BLUE, outline=BLUE, width=2)
    _draw_lbl(draw, (hx-105, hy+60),  "Right",     BLUE, 14, lang, anchor="mm")
    _draw_lbl(draw, (hx-105, hy+76),  "Ventricle", BLUE, 14, lang, anchor="mm")

    # Left Ventricle (viewer's right bottom) — red, thick wall
    draw.polygon([(hx+10, hy-35), (hx+155, hy-35), (hx+100, hy+100), (hx-50, hy+175)],
                 fill=LIGHT_RED, outline=RED, width=3)
    _draw_lbl(draw, (hx+80, hy+45),  "Left",      RED, 14, lang, anchor="mm")
    _draw_lbl(draw, (hx+80, hy+61),  "Ventricle", RED, 14, lang, anchor="mm")

    # Septum line
    draw.line([(hx-10, hy-175), (hx-30, hy+170)], fill=OUTLINE, width=3)

    # ── Blood vessels ──────────────────────────────────────────────────────────
    # Superior Vena Cava (top-left, blue)
    draw.rectangle([hx-155, hy-280, hx-115, hy-170], fill=LIGHT_BLUE, outline=BLUE, width=2)
    # Inferior Vena Cava (bottom-left, blue)
    draw.rectangle([hx-185, hy+175, hx-145, hy+280], fill=LIGHT_BLUE, outline=BLUE, width=2)
    # Pulmonary Artery (top, blue → lungs)
    draw.rectangle([hx-60, hy-280, hx-20, hy-165], fill=LIGHT_BLUE, outline=BLUE, width=2)
    # Pulmonary Vein (top-right, red ← lungs)
    draw.rectangle([hx+60, hy-280, hx+100, hy-165], fill=LIGHT_RED, outline=RED, width=2)
    # Aorta (top-right, red → body)
    draw.rectangle([hx+110, hy-280, hx+155, hy-170], fill=LIGHT_RED, outline=RED, width=2)
    # Bottom Aorta
    draw.rectangle([hx-30, hy+175, hx+10, hy+270], fill=LIGHT_RED, outline=RED, width=2)

    # ── Leader lines + Labels (right side) ────────────────────────────────────
    def label_line(x1, y1, x2, y2, txt, col, right=True):
        draw.line([(x1, y1), (x2, y2)], fill=col, width=1)
        anchor = "lm" if right else "rm"
        _draw_content(draw, (x2 + (6 if right else -6), y2), txt, col, 14, anchor=anchor)

    # Right labels
    label_line(hx+155, hy-225, 610, hy-260, _L("Aorta",           lang), RED)
    label_line(hx+100, hy-225, 610, hy-220, _L("Pulmonary Vein",  lang), RED)
    label_line(hx+155, hy-80,  610, hy-180, _L("Left",  lang) + " " + _L("Atrium",    lang), RED)
    label_line(hx+155, hy+30,  610, hy-140, _L("Left",  lang) + " " + _L("Ventricle", lang), RED)

    # Left labels
    label_line(hx-135, hy-225, 220, hy-260, _L("Superior Vena Cava", lang), BLUE, right=False)
    label_line(hx-40,  hy-225, 220, hy-220, _L("Pulmonary Artery",   lang), BLUE, right=False)
    label_line(hx-175, hy-100, 220, hy-180, _L("Right", lang) + " " + _L("Atrium",    lang), BLUE, right=False)
    label_line(hx-175, hy+30,  220, hy-140, _L("Right", lang) + " " + _L("Ventricle", lang), BLUE, right=False)
    label_line(hx-165, hy+225, 220, hy-100, _L("Inferior Vena Cava",  lang), BLUE, right=False)
    label_line(hx-10,  hy+230, 610, hy-100, _L("Aorta (to body)",     lang), RED)

    # Septum label
    _draw_lbl(draw, (hx+10, hy-10), "Septum", OUTLINE, 12, lang, anchor="lm")

    # ── Legend ─────────────────────────────────────────────────────────────────
    lx, ly = 20, 540
    draw.rectangle([lx, ly, lx+460, ly+80], fill=(230,230,240), outline=OUTLINE, width=1)
    draw.rectangle([lx+10, ly+14, lx+36, ly+34], fill=LIGHT_BLUE, outline=BLUE, width=1)
    _draw_lbl(draw, (lx+44, ly+24), "deoxy_blood", BLUE, 12, lang, anchor="lm")
    draw.rectangle([lx+10, ly+44, lx+36, ly+64], fill=LIGHT_RED, outline=RED, width=1)
    _draw_lbl(draw, (lx+44, ly+54), "oxy_blood",   RED,  12, lang, anchor="lm")

    # Fun fact strip
    draw.rectangle([500, 540, W-10, 620], fill=(230,230,240), outline=OUTLINE, width=1)
    _draw_lbl(draw, (750, 560), "Heart Facts",  DARK, 14, lang, anchor="mm")
    _draw_lbl(draw, (750, 580), "heart_beats",  RED,  12, lang, anchor="mm")
    _draw_lbl(draw, (750, 598), "heart_size",   DARK, 12, lang, anchor="mm")

    # Remove reference image
    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_food_chain(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 500
    img  = Image.new("RGB", (W, H), (6, 14, 30))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(26); f_med = _load_font(20); f_sm = _load_font(16); f_tiny = _load_font(13)

    draw.rectangle([0, 0, W, 52], fill=(10, 60, 20))
    _draw_lbl(draw, (W//2, 26), "Food Chain", WHITE, 26, lang, anchor="mm")

    levels = [
        (70,  200, 160, "Sun",          AMBER,       "Energy Source"),
        (230, 160, 200, "Producers",    EMERALD,     "Plants / Grass"),
        (430, 160, 200, "Herbivores",   TEAL,        "Rabbit / Deer"),
        (630, 160, 200, "Carnivores",   (220,80,80), "Fox / Lion"),
        (730, 320, 160, "Decomposers",  PURPLE,      "Fungi / Bacteria"),
    ]
    for x, y, w, lbl, col, sub in levels:
        _rr(draw, [x, y, x+w, y+110], 12, (14,22,50), col, w=2)
        _draw_lbl(draw, (x+w//2, y+42), lbl, col,           20, lang, anchor="mm")
        _draw_lbl(draw, (x+w//2, y+70), sub, TEXT_SECONDARY, 16, lang, anchor="mm")

    # Arrows between adjacent level boxes
    for ax, bx in [(230, 430), (430, 630)]:
        draw.line([(ax, 255), (bx, 255)], fill=WHITE, width=2)
        draw.polygon([(bx-8, 249), (bx-8, 261), (bx+2, 255)], fill=WHITE)

    _draw_lbl(draw, (W//2, H-20), "food_flow", AMBER, 13, lang, anchor="mm")
    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_cell(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 520
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(24); f_med = _load_font(18); f_sm = _load_font(14); f_tiny = _load_font(12)

    draw.rectangle([0, 0, W, 50], fill=(20, 30, 80))
    _draw_lbl(draw, (W//2, 25), "Animal Cell Structure", WHITE, 24, lang, anchor="mm")

    cx, cy = 300, 290
    # Cell membrane (outer)
    draw.ellipse([cx-210, cy-185, cx+210, cy+185], outline=EMERALD, width=3)
    _draw_lbl(draw, (cx, cy-200), "Cell Membrane", EMERALD, 14, lang, anchor="mm")
    # Cytoplasm fill
    draw.ellipse([cx-205, cy-180, cx+205, cy+180], fill=(14, 20, 55))
    draw.ellipse([cx-210, cy-185, cx+210, cy+185], outline=EMERALD, width=3)
    # Nucleus
    draw.ellipse([cx-70, cy-60, cx+70, cy+60], fill=(30, 20, 70), outline=PURPLE, width=3)
    _draw_lbl(draw, (cx, cy),     "Nucleus",    PURPLE,       18, lang, anchor="mm")
    _draw_lbl(draw, (cx, cy+22),  "(DNA here)", (180,150,230),14, lang, anchor="mm")
    # Mitochondria
    draw.ellipse([cx+90, cy-40, cx+170, cy], fill=(40,20,10), outline=AMBER, width=2)
    _draw_lbl(draw, (cx+130, cy-20), "Mitochondria", AMBER, 12, lang, anchor="mm")

    # Labels on right
    lx = 560
    _rr(draw, [lx, 60, lx+310, 460], 12, (14,20,54), INDIGO)
    _draw_lbl(draw, (lx+155, 85), "ORGANELLES", INDIGO, 18, lang, anchor="mm")
    items = [
        ("Cell Membrane", EMERALD, "ctrl_enter"),
        ("Nucleus",       PURPLE,  "brain_dna"),
        ("Mitochondria",  AMBER,   "powerhouse"),
        ("cytoplasm",     TEAL,    "cytoplasm_desc"),
    ]
    for i, (name_key, col, desc_key) in enumerate(items):
        y = 115 + i * 82
        draw.ellipse([lx+18, y, lx+34, y+16], fill=col)
        _draw_lbl(draw, (lx+45, y+8),  name_key, col,           14, lang, anchor="lm")
        _draw_lbl(draw, (lx+45, y+26), desc_key, TEXT_SECONDARY, 12, lang, anchor="lm")

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_newton(data: dict, lang: str = "en") -> bytes:
    W, H = 900, 500
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(28); f_med = _load_font(21); f_sm = _load_font(16); f_tiny = _load_font(14)

    formula = data.get("formula") or "F = ma"
    draw.rectangle([0, 0, W, 55], fill=(28, 36, 100))
    _draw_content(draw, (W//2, 27), _L("Newton's Laws", lang) + f"  |  {formula}", AMBER, 28, anchor="mm")

    laws = [
        (40,  75, INDIGO,  "1st_title", "1st_l1", "1st_l2"),
        (40, 220, EMERALD, "2nd_title", "2nd_l1", "2nd_l2"),
        (40, 365, AMBER,   "3rd_title", "3rd_l1", "3rd_l2"),
    ]
    for x, y, col, tk, l1k, l2k in laws:
        _rr(draw, [x, y, x+520, y+120], 14, (16,22,58), col, w=2)
        _draw_lbl(draw, (x+20, y+22), tk,  col,           21, lang)
        _draw_lbl(draw, (x+20, y+58), l1k, TEXT_PRIMARY,  16, lang)
        _draw_lbl(draw, (x+20, y+82), l2k, TEXT_SECONDARY, 16, lang)

    # Formula visual
    _rr(draw, [600, 75, 870, 480], 14, (16,22,58), AMBER, w=2)
    _draw_sci(draw, (735, 105), "F = m x a", AMBER, f_big, anchor="mm")
    draw.line([(620, 125), (850, 125)], fill=AMBER, width=1)
    pairs = [("F", "Force (Newton, N)", AMBER),
             ("m", "Mass (kg)",         EMERALD),
             ("a", "Acceleration (m/s^2)", INDIGO)]
    for i, (sym, desc_key, col) in enumerate(pairs):
        y = 148 + i * 80
        draw.ellipse([625, y, 665, y+40], fill=col)
        _draw_sci(draw, (645, y+20), sym, WHITE, f_med, anchor="mm")
        _draw_lbl(draw, (675, y+20), desc_key, TEXT_PRIMARY, 16, lang, anchor="lm")

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


def _diagram_flowchart(data: dict, lang: str = "en") -> bytes:
    """Generic PIL flowchart — fallback for non-specific concepts."""
    W, H = 900, 500
    img  = Image.new("RGB", (W, H), (8, 12, 35))
    draw = ImageDraw.Draw(img)
    f_big = _load_font(26); f_med = _load_font(20); f_sm = _load_font(16)

    title = data.get("title", "Concept")
    draw.rectangle([0, 0, W, 56], fill=(28, 36, 100))
    _draw_content(draw, (W//2, 28), title[:50], WHITE, 26, anchor="mm")

    pts = data.get("key_points", [])[:4]
    cols = [INDIGO, EMERALD, AMBER, PURPLE]
    node_w, node_h = 720, 72
    start_y = 90
    for i, pt in enumerate(pts):
        y = start_y + i * (node_h + 20)
        _rr(draw, [(W - node_w)//2, y, (W + node_w)//2, y + node_h],
            12, (16, 22, 60), cols[i % 4])
        _draw_content(draw, (W//2, y + node_h//2), str(pt)[:65],
                      TEXT_PRIMARY, 20, anchor="mm")
        if i < len(pts) - 1:
            arr_x = W // 2
            draw.line([(arr_x, y + node_h), (arr_x, y + node_h + 20)],
                      fill=cols[i % 4], width=2)

    buf = io.BytesIO(); img.save(buf, "PNG"); return buf.getvalue()


# ── Dynamic matplotlib diagram executor ──────────────────────────────────────

def execute_diagram_code(code: str) -> bytes | None:
    """Execute AI-generated matplotlib code and return PNG bytes."""
    if not code or len(code) < 30:
        return None
    import tempfile, subprocess, os, sys
    script_path = None
    out_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as out_f:
            out_path = out_f.name

        code_fixed = code.replace("_OUTPUT_PATH", repr(out_path))

        with tempfile.NamedTemporaryFile(suffix=".py", delete=False,
                                         mode="w", encoding="utf-8") as script_f:
            script_f.write("import warnings; warnings.filterwarnings('ignore')\n")
            script_f.write("import matplotlib; matplotlib.use('Agg')\n")
            script_f.write(code_fixed)
            script_path = script_f.name

        result = subprocess.run(
            [sys.executable, script_path],
            timeout=20, capture_output=True, text=True
        )
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            with open(out_path, "rb") as f:
                data = f.read()
            return data
        return None
    except Exception:
        return None
    finally:
        for p in [script_path, out_path]:
            try: os.unlink(p)
            except Exception: pass


# ── Human body parts diagram ──────────────────────────────────────────────────

def create_body_parts_diagram(grade: str, lang: str = "en") -> bytes:
    """Labeled human body figure — external parts for LKG-5, internal organs for Class 6+."""
    W, H = 1000, 680
    BG_COL    = (245, 248, 255)
    SKIN      = (255, 213, 178)
    SKIN_LINE = (195, 145, 105)
    HAIR_COL  = (55,  32,  12)

    img  = Image.new("RGB", (W, H), BG_COL)
    draw = ImageDraw.Draw(img)

    f_title = _load_font(26)
    f_label = _load_font(17)
    f_sm    = _load_font(13)
    # Use Devanagari font when language is Hindi
    if lang == "hi":
        f_title = _load_font_deva(26)
        f_label = _load_font_deva(17)

    show_organs = grade not in ("LKG", "UKG", "1", "2", "3", "4", "5")
    bx = 390   # body centre X

    # Header
    if lang == "hi":
        title = "मानव शरीर -- आंतरिक अंग" if show_organs else "मानव शरीर के अंग"
    else:
        title = "Human Body -- Internal Organs" if show_organs else "Parts of the Human Body"
    draw.rectangle([0, 0, W, 52], fill=(25, 55, 140))
    _draw_text_safe(draw, (W // 2, 26), title, (255, 255, 255), f_title, anchor="mm")

    # ── Draw body ─────────────────────────────────────────────────────────────
    # Hair
    draw.ellipse([bx - 65, 62, bx + 65, 172], fill=HAIR_COL)
    # Head
    draw.ellipse([bx - 58, 76, bx + 58, 192], fill=SKIN, outline=SKIN_LINE, width=2)
    # Ears
    draw.ellipse([bx - 76, 108, bx - 55, 150], fill=SKIN, outline=SKIN_LINE, width=2)
    draw.ellipse([bx + 55, 108, bx + 76, 150], fill=SKIN, outline=SKIN_LINE, width=2)
    # Eyes
    draw.ellipse([bx - 36, 116, bx - 14, 134], fill=(40, 90, 200))
    draw.ellipse([bx + 14, 116, bx + 36, 134], fill=(40, 90, 200))
    # Nose
    draw.ellipse([bx - 5, 148, bx + 5, 158], fill=SKIN_LINE)
    # Mouth
    draw.arc([bx - 18, 162, bx + 18, 180], start=10, end=170, fill=(180, 40, 40), width=3)
    # Neck
    draw.rectangle([bx - 18, 192, bx + 18, 230], fill=SKIN, outline=SKIN_LINE, width=1)
    # Torso
    draw.rounded_rectangle([bx - 86, 230, bx + 86, 452], radius=18, fill=SKIN, outline=SKIN_LINE, width=2)
    # Arms
    draw.rounded_rectangle([bx - 136, 230, bx - 86, 394], radius=16, fill=SKIN, outline=SKIN_LINE, width=2)
    draw.rounded_rectangle([bx + 86,  230, bx + 136, 394], radius=16, fill=SKIN, outline=SKIN_LINE, width=2)
    # Hands
    draw.ellipse([bx - 152, 394, bx - 72, 432], fill=SKIN, outline=SKIN_LINE, width=2)
    draw.ellipse([bx + 72,  394, bx + 152, 432], fill=SKIN, outline=SKIN_LINE, width=2)
    # Legs
    draw.rounded_rectangle([bx - 76, 452, bx - 18, 618], radius=14, fill=SKIN, outline=SKIN_LINE, width=2)
    draw.rounded_rectangle([bx + 18,  452, bx + 76, 618], radius=14, fill=SKIN, outline=SKIN_LINE, width=2)
    # Feet
    draw.ellipse([bx - 94, 618, bx + 2,   650], fill=SKIN, outline=SKIN_LINE, width=2)
    draw.ellipse([bx - 2,  618, bx + 94,  650], fill=SKIN, outline=SKIN_LINE, width=2)

    # ── Internal organs (Class 6+) ────────────────────────────────────────────
    if show_organs:
        BRAIN_C  = ((255, 200, 200), (200,  50,  50))
        LUNG_C   = ((255, 170, 140), (200,  80,  60))
        HEART_C  = ((255,  80,  80), (180,  20,  20))
        LIVER_C  = ((180, 100,  60), (130,  55,  18))
        STOM_C   = ((180, 220, 255), ( 60, 100, 200))
        KID_C    = ((200, 255, 160), ( 80, 180,  60))
        INT_C    = ((220, 200, 255), (100,  60, 180))

        draw.ellipse([bx - 36,  84, bx + 36, 142], fill=BRAIN_C[0], outline=BRAIN_C[1], width=2)
        draw.ellipse([bx - 82, 246, bx - 22, 350], fill=LUNG_C[0],  outline=LUNG_C[1],  width=2)
        draw.ellipse([bx + 22, 246, bx + 82, 350], fill=LUNG_C[0],  outline=LUNG_C[1],  width=2)
        draw.ellipse([bx - 46, 266, bx -  4, 306], fill=HEART_C[0], outline=HEART_C[1], width=2)
        draw.ellipse([bx + 10, 342, bx + 84, 406], fill=LIVER_C[0], outline=LIVER_C[1], width=2)
        draw.ellipse([bx - 58, 348, bx -  4, 412], fill=STOM_C[0],  outline=STOM_C[1],  width=2)
        draw.ellipse([bx - 74, 374, bx - 42, 422], fill=KID_C[0],   outline=KID_C[1],   width=2)
        draw.ellipse([bx + 42, 374, bx + 74, 422], fill=KID_C[0],   outline=KID_C[1],   width=2)
        draw.ellipse([bx - 62, 412, bx + 62, 450], fill=INT_C[0],   outline=INT_C[1],   width=2)

    # ── Leader line helpers ───────────────────────────────────────────────────
    LEFT_X  = 150   # text right edge (left side labels)
    RIGHT_X = 618   # text left edge (right side labels)

    def leader_left(bx_pt, by_pt, label_y, text, col=(20, 50, 180)):
        draw.line([(bx_pt, by_pt), (LEFT_X, label_y)], fill=col, width=1)
        draw.ellipse([bx_pt - 4, by_pt - 4, bx_pt + 4, by_pt + 4], fill=col)
        _draw_text_safe(draw, (LEFT_X - 4, label_y), text, col, f_label, anchor="rm")

    def leader_right(bx_pt, by_pt, label_y, text, col=(130, 30, 150)):
        draw.line([(bx_pt, by_pt), (RIGHT_X, label_y)], fill=col, width=1)
        draw.ellipse([bx_pt - 4, by_pt - 4, bx_pt + 4, by_pt + 4], fill=col)
        _draw_text_safe(draw, (RIGHT_X + 4, label_y), text, col, f_label, anchor="lm")

    L = (20,  50, 180)   # blue  — left-side labels
    R = (130, 30, 150)   # purple — right-side labels
    G = (20, 130,  60)   # green  — leg/foot labels

    # ── External labels (LKG–Class 5) ────────────────────────────────────────
    if not show_organs:
        if lang == "hi":
            leader_left (bx - 30, 125, 108, "आँखें",      L)
            leader_left (bx - 67, 129, 138, "कान",         L)
            leader_left (bx - 111, 295, 270, "हाथ",        L)
            leader_left (bx - 112, 413, 395, "उँगलियाँ",   L)
            leader_left (bx - 47,  535, 505, "पैर",         G)
            leader_left (bx - 48,  634, 622, "पंजे",        G)
            leader_right(bx,        68,  90, "बाल",          R)
            leader_right(bx + 4,   155, 132, "नाक",          R)
            leader_right(bx + 14,  171, 162, "मुँह",         R)
            leader_right(bx + 15,  211, 205, "गर्दन",        R)
            leader_right(bx + 86,  242, 242, "कंधे",         R)
            leader_right(bx + 84,  320, 318, "छाती",         R)
            leader_right(bx + 84,  395, 390, "पेट",          R)
            leader_right(bx + 47,  535, 480, "पैर",          G)
            leader_right(bx + 48,  634, 608, "पंजे",         G)
        else:
            leader_left (bx - 30, 125, 108, "Eyes",        L)
            leader_left (bx - 67, 129, 138, "Ears",        L)
            leader_left (bx - 111, 295, 270, "Arms",       L)
            leader_left (bx - 112, 413, 395, "Fingers",    L)
            leader_left (bx - 47,  535, 505, "Legs",       G)
            leader_left (bx - 48,  634, 622, "Feet",       G)
            leader_right(bx,        68,  90, "Hair",        R)
            leader_right(bx + 4,   155, 132, "Nose",        R)
            leader_right(bx + 14,  171, 162, "Mouth",       R)
            leader_right(bx + 15,  211, 205, "Neck",        R)
            leader_right(bx + 86,  242, 242, "Shoulders",   R)
            leader_right(bx + 84,  320, 318, "Chest",       R)
            leader_right(bx + 84,  395, 390, "Stomach",     R)
            leader_right(bx + 47,  535, 480, "Legs",        G)
            leader_right(bx + 48,  634, 608, "Feet",        G)

    # ── Organ labels (Class 6+) ───────────────────────────────────────────────
    else:
        BRAIN_L = (200, 50,  50)
        HEART_L = (180, 20,  20)
        LUNG_L  = (200, 80,  60)
        LIVER_L = (130, 55,  18)
        STOM_L  = ( 60, 100, 200)
        KID_L   = ( 80, 180,  60)
        INT_L   = (100,  60, 180)

        if lang == "hi":
            leader_left (bx - 34, 113,  72, "मस्तिष्क",   BRAIN_L)
            leader_left (bx - 55, 298, 265, "फेफड़े",       LUNG_L)
            leader_left (bx - 25, 286, 295, "हृदय",         HEART_L)
            leader_left (bx - 31, 380, 352, "आमाशय",        STOM_L)
            leader_left (bx - 58, 398, 382, "गुर्दे",       KID_L)
            leader_left (bx - 30, 431, 420, "बड़ी आँत",     INT_L)
            leader_right(bx + 55, 298, 265, "फेफड़े",        LUNG_L)
            leader_right(bx + 47, 374, 332, "यकृत",          LIVER_L)
            leader_right(bx + 58, 398, 362, "गुर्दे",        KID_L)
        else:
            leader_left (bx - 34, 113,  72, "Brain",        BRAIN_L)
            leader_left (bx - 55, 298, 265, "Lungs",        LUNG_L)
            leader_left (bx - 25, 286, 295, "Heart",        HEART_L)
            leader_left (bx - 31, 380, 352, "Stomach",      STOM_L)
            leader_left (bx - 58, 398, 382, "Kidneys",      KID_L)
            leader_left (bx - 30, 431, 420, "Intestines",   INT_L)
            leader_right(bx + 55, 298, 265, "Lungs",         LUNG_L)
            leader_right(bx + 47, 374, 332, "Liver",         LIVER_L)
            leader_right(bx + 58, 398, 362, "Kidneys",       KID_L)

    # Footer
    draw.rectangle([0, H - 26, W, H], fill=(25, 55, 140))
    footer = "ShikshAI | Smart Board Visual" if lang == "en" else "ShikshAI | Smart Board Visual (Hindi)"
    _draw_text_safe(draw, (W // 2, H - 13), footer, (200, 220, 255), f_sm, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ── Utility ───────────────────────────────────────────────────────────────────

def img_to_display(img_bytes: bytes) -> str:
    """Return a base64 data-URL for embedding in HTML."""
    import base64
    return "data:image/png;base64," + base64.b64encode(img_bytes).decode()
