#!/usr/bin/env python3
"""Generate the 1997-style graphics for the site (flags, banners, buttons).

Everything here is drawn from scratch with Pillow, so there are no
licensing questions. Run from the repo root:

    python3 tools/make_retro_assets.py
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "..", "img", "retro")
os.makedirs(OUT, exist_ok=True)

RED = (178, 34, 52)
WHITE = (255, 255, 255)
BLUE = (60, 59, 110)
NAVY = (0, 0, 102)
GOLD = (255, 204, 0)
BLACK = (0, 0, 0)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = f"{FONT_DIR}/liberation/LiberationSerif-Bold.ttf"
SANS_BOLD = f"{FONT_DIR}/dejavu/DejaVuSans-Bold.ttf"
SANS = f"{FONT_DIR}/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def star_points(cx, cy, r_out, r_in=None, rot=-math.pi / 2):
    r_in = r_in if r_in is not None else r_out * 0.382
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def to_p(rgba, palette_src=None):
    """RGBA -> paletted image with index 255 transparent (hard-edged, like 1997)."""
    rgb = rgba.convert("RGB")
    alpha = np.array(rgba.split()[3])
    if palette_src is None:
        p = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    else:
        p = rgb.quantize(palette=palette_src, dither=Image.Dither.NONE)
    pal = (p.getpalette() or [])[: 255 * 3]
    pal += [0] * (255 * 3 - len(pal))
    p.putpalette(pal + [255, 0, 255])
    arr = np.array(p)
    arr[alpha < 128] = 255
    out = Image.fromarray(arr, mode="P")
    out.putpalette(pal + [255, 0, 255])
    out.info["transparency"] = 255
    return out


def save_anim(frames, name, duration, transparent=True):
    path = os.path.join(OUT, name)
    if transparent:
        # Build one shared palette from all frames so colours don't flicker.
        w, h = frames[0].size
        sheet = Image.new("RGB", (w, h * len(frames)))
        for i, f in enumerate(frames):
            sheet.paste(f.convert("RGB"), (0, h * i))
        pal_src = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        pframes = [to_p(f, pal_src) for f in frames]
        pframes[0].save(path, save_all=True, append_images=pframes[1:], duration=duration,
                        loop=0, transparency=255, disposal=2, optimize=False)
    else:
        pframes = [f.convert("RGB").quantize(colors=256) for f in frames]
        pframes[0].save(path, save_all=True, append_images=pframes[1:], duration=duration,
                        loop=0, optimize=False)
    print("wrote", path)


# --------------------------------------------------------------------------
# US flag (correct 1.9:1 proportions, 50 stars)
# --------------------------------------------------------------------------
def draw_flag(h):
    w = int(round(h * 1.9))
    img = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(img)
    sh = h / 13
    for i in range(13):
        if i % 2 == 0:
            d.rectangle([0, round(i * sh), w, round((i + 1) * sh) - 1], fill=RED)
    cw, ch = h * 0.76, h * 7 / 13
    d.rectangle([0, 0, round(cw) - 1, round(ch) - 1], fill=BLUE)
    r = h * 0.0616 / 2
    for row in range(1, 10):
        cols = range(1, 12, 2) if row % 2 == 1 else range(2, 12, 2)
        for col in cols:
            d.polygon(star_points(cw * col / 12, ch * row / 10, r), fill=WHITE)
    return img


def waving_flag(name, flag_h, frames=12, pole=True, amp_frac=0.07):
    scale = 3
    base = draw_flag(flag_h * scale)
    fw, fh = base.size
    amp = fh * amp_frac
    pole_w = (6 * scale) if pole else 0
    pad_top = (10 * scale) if pole else int(amp) + scale
    W = pole_w + fw + int(amp)
    H = fh + int(amp * 2) + pad_top + (8 * scale if pole else 0)
    src = np.array(base).astype(np.float32)
    out_frames = []
    lam = fw * 0.8
    for k in range(frames):
        ph = 2 * math.pi * k / frames
        canvas = np.zeros((H, W, 4), dtype=np.float32)
        for x in range(fw):
            t = x / fw
            env = t ** 0.9
            dy = amp * math.sin(2 * math.pi * x / lam - ph) * env
            shade = 1.0 + 0.28 * math.cos(2 * math.pi * x / lam - ph) * env
            y0 = int(round(pad_top + amp + dy))
            col = np.clip(src[:, x, :] * shade, 0, 255)
            canvas[y0:y0 + fh, pole_w + x, :3] = col
            canvas[y0:y0 + fh, pole_w + x, 3] = 255
        img = Image.fromarray(canvas.astype(np.uint8), "RGBA")
        if pole:
            d = ImageDraw.Draw(img)
            px = pole_w // 2
            d.rectangle([px - 2 * scale, 4 * scale, px + 1 * scale, H - 1], fill=(150, 150, 150, 255))
            d.rectangle([px - 2 * scale, 4 * scale, px - 1 * scale, H - 1], fill=(220, 220, 220, 255))
            d.ellipse([px - 4 * scale, 0, px + 3 * scale, 7 * scale], fill=(230, 180, 30, 255))
        img = img.resize((W // scale, H // scale), Image.LANCZOS)
        out_frames.append(img)
    save_anim(out_frames, name, duration=90)


# --------------------------------------------------------------------------
# WordArt-style logo banner
# --------------------------------------------------------------------------
def gradient(w, h, stops):
    """Vertical gradient through a list of RGB stops."""
    arr = np.zeros((h, w, 3), dtype=np.float32)
    n = len(stops) - 1
    for y in range(h):
        t = y / max(h - 1, 1) * n
        i = min(int(t), n - 1)
        f = t - i
        c = np.array(stops[i]) * (1 - f) + np.array(stops[i + 1]) * f
        arr[y, :, :] = c
    return Image.fromarray(arr.astype(np.uint8), "RGB")


def wordart(text, size, path, stops, extrude=8, extrude_color=(10, 10, 40),
            outline=WHITE, pad=24, letter_spacing=2):
    f = font(SERIF_BOLD, size)
    # measure with spacing
    widths = [f.getbbox(ch)[2] for ch in text]
    tw = sum(widths) + letter_spacing * (len(text) - 1)
    asc, desc = f.getmetrics()
    th = asc + desc
    W, H = tw + pad * 2 + extrude, th + pad * 2 + extrude
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def text_mask(dx, dy, stroke=0):
        m = Image.new("L", (W, H), 0)
        dm = ImageDraw.Draw(m)
        x = pad + dx
        for ch, cw in zip(text, widths):
            dm.text((x, pad + dy), ch, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
            x += cw + letter_spacing
        return m

    # 3D extrusion
    for i in range(extrude, 0, -1):
        layer = Image.new("RGBA", (W, H), extrude_color + (255,))
        img.paste(layer, (0, 0), text_mask(i, i, stroke=2))
    # outline
    img.paste(Image.new("RGBA", (W, H), outline + (255,)), (0, 0), text_mask(0, 0, stroke=3))
    # gradient face
    face = gradient(W, H, stops).convert("RGBA")
    img.paste(face, (0, 0), text_mask(0, 0))
    bbox = img.getbbox()
    img = img.crop(bbox)
    img.save(path)
    print("wrote", path)
    return img


def logo_banner():
    stops = [(255, 60, 60), (200, 0, 20), (255, 255, 255), (90, 120, 255), (20, 30, 160)]
    word = wordart("AMERICAN CHAIRS", 78, os.path.join(OUT, "_logo_word.png"), stops)
    W = word.width + 140
    H = word.height + 46
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(word, (70, 4), word)
    d = ImageDraw.Draw(img)
    # stars flanking the word
    for cx in (32, W - 32):
        d.polygon(star_points(cx, word.height / 2 + 4, 26), fill=GOLD, outline=(120, 80, 0))
        d.polygon(star_points(cx, word.height / 2 + 4, 12), fill=WHITE)
    tag = "PROUDLY AMERICAN-OWNED  *  EST. 2026  *  LIVE U.S. SUPPORT"
    tf = font(SANS_BOLD, 17)
    tw = d.textlength(tag, font=tf)
    x0 = (W - tw) / 2
    y0 = word.height + 14
    # draw the '*' as little stars instead of asterisks
    parts = tag.split("*")
    x = x0
    for i, part in enumerate(parts):
        d.text((x, y0), part, font=tf, fill=GOLD)
        x += d.textlength(part, font=tf)
        if i < len(parts) - 1:
            sw = d.textlength("*", font=tf)
            d.polygon(star_points(x + sw / 2, y0 + 10, 7), fill=WHITE)
            x += sw
    path = os.path.join(OUT, "logo.png")
    img.save(path)
    os.remove(os.path.join(OUT, "_logo_word.png"))
    print("wrote", path)


# --------------------------------------------------------------------------
# 88x31 buttons
# --------------------------------------------------------------------------
def bevel(d, w, h, light=(255, 255, 255), dark=(64, 64, 64)):
    d.line([(0, 0), (w - 1, 0)], fill=light)
    d.line([(0, 0), (0, h - 1)], fill=light)
    d.line([(0, h - 1), (w - 1, h - 1)], fill=dark)
    d.line([(w - 1, 0), (w - 1, h - 1)], fill=dark)


def button(name, draw_fn, frames=1, duration=500):
    out = []
    for k in range(frames):
        img = Image.new("RGB", (88, 31), (192, 192, 192))
        d = ImageDraw.Draw(img)
        draw_fn(img, d, k)
        out.append(img)
    path = os.path.join(OUT, name)
    if frames == 1:
        out[0].quantize(colors=64).save(path)
        print("wrote", path)
    else:
        save_anim(out, name, duration, transparent=False)


def centered(d, box, text, f, fill):
    x0, y0, x1, y1 = box
    tw = d.textlength(text, font=f)
    bb = f.getbbox(text)
    th = bb[3] - bb[1]
    d.text((x0 + (x1 - x0 - tw) / 2, y0 + (y1 - y0 - th) / 2 - bb[1]), text, font=f, fill=fill)


def btn_american_owned(img, d, k):
    d.rectangle([0, 0, 87, 30], fill=WHITE)
    d.rectangle([0, 0, 30, 30], fill=BLUE)
    d.polygon(star_points(15.5, 16, 11), fill=WHITE)
    for i in range(0, 31, 6):
        d.rectangle([31, i, 87, i + 2], fill=(255, 225, 225))
    f = font(SANS_BOLD, 9)
    centered(d, (31, 3, 87, 15), "AMERICAN", f, RED)
    centered(d, (31, 15, 87, 28), "OWNED", f, BLUE)
    d.rectangle([0, 0, 87, 30], outline=BLACK)


def btn_buy_american(img, d, k):
    d.rectangle([0, 0, 87, 30], fill=NAVY)
    f = font(SANS_BOLD, 12)
    colors = [(RED, WHITE), (WHITE, RED)][k % 2]
    centered(d, (0, 1, 88, 16), "BUY", f, colors[1])
    centered(d, (0, 15, 88, 30), "AMERICAN!", f, colors[0])
    bevel(d, 88, 31)


def btn_800x600(img, d, k):
    d.rectangle([0, 0, 87, 30], fill=BLACK)
    f = font(SANS_BOLD, 8)
    centered(d, (0, 2, 88, 14), "BEST VIEWED AT", f, (0, 255, 0))
    f2 = font(SANS_BOLD, 11)
    centered(d, (0, 14, 88, 29), "800 x 600", f2, (255, 255, 0))
    d.rectangle([0, 0, 87, 30], outline=(0, 160, 0))


def btn_freedom(img, d, k):
    d.rectangle([0, 0, 87, 30], fill=(192, 192, 192))
    for i in range(7):
        d.rectangle([2, 2 + i * 4, 26, 3 + i * 4], fill=RED if i % 2 == 0 else WHITE)
    d.rectangle([2, 2, 13, 13], fill=BLUE)
    f = font(SANS_BOLD, 8)
    centered(d, (28, 3, 87, 14), "POWERED BY", f, BLACK)
    f2 = font(SANS_BOLD, 10)
    centered(d, (28, 14, 87, 28), "FREEDOM", f2, RED)
    bevel(d, 88, 31)


def btn_poc(img, d, k):
    d.rectangle([0, 0, 87, 30], fill=(255, 255, 0) if k % 2 == 0 else (255, 160, 0))
    f = font(SANS_BOLD, 9)
    centered(d, (0, 2, 88, 15), "PROOF OF", f, BLACK)
    centered(d, (0, 15, 88, 29), "CONCEPT", f, BLACK)
    d.rectangle([0, 0, 87, 30], outline=BLACK)


# --------------------------------------------------------------------------
# Under construction strip (468x60, the classic banner size)
# --------------------------------------------------------------------------
def under_construction():
    W, H = 468, 60
    frames = []
    n = 8
    for k in range(n):
        img = Image.new("RGB", (W, H), (255, 214, 0))
        d = ImageDraw.Draw(img)
        off = k * (40 / n)
        for x in range(-80, W + 80, 40):
            x0 = x + off
            d.polygon([(x0, H), (x0 + 20, H), (x0 + 20 + H, 0), (x0 + H, 0)], fill=BLACK)
        d.rectangle([70, 9, W - 71, H - 10], fill=BLACK)
        d.rectangle([72, 11, W - 73, H - 12], fill=(255, 214, 0))
        f = font(SANS_BOLD, 15)
        centered(d, (72, 12, W - 72, 31), "PARDON OUR DUST!", f, BLACK)
        f2 = font(SANS, 11)
        centered(d, (72, 30, W - 72, 48), "This site is a proof of concept - no orders accepted yet", f2, BLACK)
        frames.append(img)
    save_anim(frames, "under_construction.gif", 110, transparent=False)


# --------------------------------------------------------------------------
# Little animated bits
# --------------------------------------------------------------------------
def spinning_star(name="star_spin.gif", size=22, color=GOLD):
    s = 4
    frames = []
    n = 12
    for k in range(n):
        big = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        sx = abs(math.cos(math.pi * k / n))
        sx = max(sx, 0.08)
        c = size * s / 2
        pts = [(c + (x - c) * sx, y) for x, y in star_points(c, c + s, size * s * 0.48)]
        shade = tuple(int(v * (0.7 + 0.3 * sx)) for v in color)
        d.polygon(pts, fill=shade + (255,), outline=(90, 60, 0, 255))
        frames.append(big.resize((size, size), Image.LANCZOS))
    save_anim(frames, name, 70)


def new_burst():
    frames = []
    for k in range(2):
        s = 4
        W, H = 46 * s, 28 * s
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        pts = []
        for i in range(24):
            r = (H * 0.5 if i % 2 == 0 else H * 0.34)
            a = i * math.pi / 12
            pts.append((W / 2 + r * 1.6 * math.cos(a), H / 2 + r * math.sin(a)))
        d.polygon(pts, fill=(RED if k == 0 else GOLD) + (255,))
        f = font(SANS_BOLD, 11 * s)
        centered(d, (0, 0, W, H), "NEW!", f, (GOLD if k == 0 else RED) + (255,))
        frames.append(big.resize((46, 28), Image.LANCZOS))
    save_anim(frames, "new.gif", 400)


def bars():
    # red-white-blue rule
    img = Image.new("RGB", (600, 9), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 599, 2], fill=RED)
    d.rectangle([0, 6, 599, 8], fill=BLUE)
    img.save(os.path.join(OUT, "rwb_bar.gif"))
    # star bar
    s = 3
    W, H = 600, 18
    big = Image.new("RGBA", (W * s, H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    n = 25
    for i in range(n):
        cx = (i + 0.5) * W * s / n
        col = [RED, BLUE, GOLD][i % 3]
        d.polygon(star_points(cx, H * s / 2 + s, 8 * s), fill=col + (255,))
    to_p(big.resize((W, H), Image.LANCZOS)).save(os.path.join(OUT, "star_bar.gif"), transparency=255)
    print("wrote bars")


def background_tile():
    W = 96
    img = Image.new("RGB", (W, W), (8, 18, 70))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(1776)
    for _ in range(6):
        x, y = rng.integers(4, W - 4, size=2)
        r = rng.uniform(1.2, 2.6)
        d.polygon(star_points(float(x), float(y), r * 1.6), fill=(150, 160, 210))
    for _ in range(14):
        x, y = rng.integers(0, W, size=2)
        d.point((int(x), int(y)), fill=(90, 100, 160))
    img.save(os.path.join(OUT, "bg_stars.gif"))
    print("wrote bg tile")


def mini_flag():
    # small static flag used as a bullet / in the footer
    f = draw_flag(48).resize((46, 24), Image.LANCZOS)
    img = Image.new("RGB", (48, 26), BLACK)
    img.paste(f, (1, 1))
    img.save(os.path.join(OUT, "flag_small.gif"))
    print("wrote flag_small")


def coming_soon():
    W, H = 400, 400
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    for i in range(0, W, 20):
        d.line([(i, 0), (i, H)], fill=(235, 235, 245))
        d.line([(0, i), (W, i)], fill=(235, 235, 245))
    # camera
    d.rounded_rectangle([110, 120, 290, 240], radius=14, fill=(90, 90, 90), outline=BLACK, width=3)
    d.rectangle([150, 100, 210, 122], fill=(90, 90, 90), outline=BLACK, width=3)
    d.ellipse([160, 135, 240, 215], fill=(40, 40, 60), outline=WHITE, width=5)
    d.ellipse([185, 160, 215, 190], fill=(120, 150, 220))
    d.rectangle([255, 132, 278, 146], fill=GOLD)
    f = font(SERIF_BOLD, 40)
    centered(d, (0, 262, W, 310), "PHOTO", f, RED)
    centered(d, (0, 308, W, 356), "COMING SOON!", f, BLUE)
    d.rectangle([0, 0, W - 1, H - 1], outline=(128, 128, 128), width=4)
    img.save(os.path.join(OUT, "coming_soon.gif"))
    print("wrote coming_soon")


if __name__ == "__main__":
    coming_soon()
    waving_flag("flag_wave.gif", flag_h=64)
    waving_flag("flag_wave_big.gif", flag_h=110)
    logo_banner()
    button("btn_american_owned.gif", btn_american_owned)
    button("btn_buy_american.gif", btn_buy_american, frames=2, duration=600)
    button("btn_800x600.gif", btn_800x600)
    button("btn_freedom.gif", btn_freedom)
    button("btn_poc.gif", btn_poc, frames=2, duration=500)
    under_construction()
    spinning_star()
    new_burst()
    bars()
    background_tile()
    mini_flag()
