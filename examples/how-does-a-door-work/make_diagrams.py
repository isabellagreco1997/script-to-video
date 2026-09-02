"""Diagrams drawn in code for the lines a photo can't explain: the hinge axis, what a tilted axis does,
the latch as a 3-state clip (bolt out → riding the strike → snapped in), the shear line, a row of doors."""
import sys, glob
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import assets

HERE = Path(__file__).resolve().parent; W = HERE / "work"; A = W / "assets"
PAPER, INK, RED, GREY, BLUE = (247, 244, 236), (30, 30, 34), (220, 50, 60), (150, 150, 150), (60, 110, 200)
def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    return ImageFont.load_default()
F = font(64); F2 = font(46)

# ---- 1. the axis: a door seen from above, swinging around the hinge line
def axis(tilt_deg=0, name="axis.png", caption="one line: the hinge pin"):
    im = Image.new("RGB", (1600, 900), PAPER); d = ImageDraw.Draw(im)
    hx, hy = 400, 450
    d.rectangle([hx - 12, 120, hx + 12, 780], fill=INK)                              # frame post
    # the door leaf rotated about the hinge
    import math
    for ang, col, wdt in ((0, GREY, 6), (35, INK, 14)):
        a = math.radians(ang); ex, ey = hx + 900 * math.cos(a), hy - 900 * math.sin(a)
        d.line([(hx, hy), (ex, ey)], fill=col, width=wdt)
    d.arc([hx - 300, hy - 300, hx + 300, hy + 300], start=-35, end=0, fill=RED, width=8)
    d.ellipse([hx - 26, hy - 26, hx + 26, hy + 26], fill=RED)
    d.text((hx - 150, 810), caption, font=F, fill=INK)
    if tilt_deg:
        d.text((900, 140), f"axis {tilt_deg}° off vertical", font=F, fill=RED)
        d.text((900, 200), "→ the door swings on its own", font=F2, fill=RED)
    im.save(A / name)
axis(); axis(1, "axis_tilted.png", "same hinge, leaning")

# ---- 2. the latch, side view, three states → a clip
def latch(state, name):
    im = Image.new("RGB", (1600, 900), PAPER); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 700, 900], fill=(225, 218, 200))                             # door edge (left)
    d.rectangle([900, 0, 1600, 900], fill=(200, 192, 176))                            # frame (right)
    d.rectangle([930, 330, 1000, 570], fill=(120, 120, 125)); d.text((940, 600), "strike plate", font=F2, fill=INK)
    d.rectangle([1000, 400, 1140, 500], fill=(90, 90, 95))                             # keeper hole
    d.rectangle([540, 380, 700, 520], fill=(110, 110, 115))                            # latch body
    bx = {0: 850, 1: 760, 2: 1120}[state]                                              # bolt tip x
    d.polygon([(700, 400), (bx - 60, 400), (bx, 450), (bx - 60, 500), (700, 500)], fill=(210, 170, 60))
    for i in range(6):                                                                  # spring
        x0 = 560 + i * 22 * (1 if state != 1 else 0.6)
        d.line([(x0, 430), (x0 + 11, 470)], fill=RED, width=6); d.line([(x0 + 11, 470), (x0 + 22, 430)], fill=RED, width=6)
    d.text((80, 80), ["1. bolt out, door swinging shut", "2. angled face rides over the strike", "3. spring shoves it into the keeper"][state], font=F, fill=INK)
    if state == 1: d.line([(760, 300), (700, 300)], fill=RED, width=8); d.polygon([(700, 300), (730, 282), (730, 318)], fill=RED)
    im.save(name)
frames = []
for i, st in enumerate([0, 0, 1, 1, 2, 2, 2]):
    p = W / f"latch_{i}.png"; latch(st, p); frames.append(p)
d = W / "gifframes" / "latch"; d.mkdir(parents=True, exist_ok=True)
for i, p in enumerate(frames): Image.open(p).save(d / f"f{i + 1:03d}.png"); p.unlink()
latch(2, A / "latch_closed.png"); latch(0, A / "latch_open.png")
(W / "gifmeta.js").write_text('const GIFMETA = {"latch": {"n": 7, "fps": 2.5, "hold": true}};\n')   # plays once, holds on state 3

# ---- 3. the shear line, drawn over the with-key diagram
src = Image.open(A / "pin_with_key.png").convert("RGB"); d = ImageDraw.Draw(src)
y = int(src.height * 0.52)
for x in range(0, src.width, 40): d.line([(x, y), (x + 22, y)], fill=RED, width=8)
d.text((40, y - int(src.height * 0.07) - 16), "shear line", font=font(int(src.height * 0.07)), fill=RED)
src.save(A / "pin_shear.png")

# ---- 4. no key: the same line drawn over the no-key diagram, pins crossing it
src = Image.open(A / "pin_no_key.png").convert("RGB"); d = ImageDraw.Draw(src)
for x in range(0, src.width, 40): d.line([(x, y), (x + 22, y)], fill=RED, width=8)
d.text((40, y - int(src.height * 0.06) - 16), "pins cross the line", font=font(int(src.height * 0.06)), fill=RED)
src.save(A / "pin_blocked.png")

# ---- 4. a row of doors for "a hundred times a day"
doors = [p for p in sorted(glob.glob(str(A / "wp" / "door_*.png"))) if "glossary" not in p][:6]
row = Image.new("RGB", (1800, 620), PAPER); x = 10
for p in doors:
    im = Image.open(p).convert("RGB"); k = 600 / im.height; im = im.resize((int(im.width * k), 600))
    im = im.crop((0, 0, min(im.width, 290), 600)); row.paste(im, (x, 10)); x += im.width + 10
row.crop((0, 0, min(x, 1800), 620)).save(A / "doors_row.png")
print("diagrams ok")
