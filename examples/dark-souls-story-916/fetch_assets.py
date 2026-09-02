"""Commons photos (licences recorded), article screenshots, and trailer frames (fetched at build time, not in git)."""
import os, sys, glob, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import assets

HERE = Path(__file__).resolve().parent; W = HERE / "work"; A = W / "assets"; A.mkdir(parents=True, exist_ok=True)
M = str(W / "manifest.json")
if Path(M).exists(): os.remove(M)

PICS = {
    "miyazaki.jpg": ("Hidetaka Miyazaki", 0),
    "fromsoftware.jpg": ("FromSoftware building Tokyo", 0),
    "ps3.jpg": ("PlayStation 3 console", 0),
    "bonfire.jpg": ("Dark Souls bonfire cosplay", 0),
    "knight_cosplay.jpg": ("Dark Souls cosplay", 0),
    "elden_ring_cosplay.jpg": ("Elden Ring cosplay", 0),
    "arcade_crowd.jpg": ("Tokyo Game Show crowd", 0),
    "sword.jpg": ("medieval longsword museum", 0),
}
for f, (q, pick) in PICS.items():
    assets.commons_fetch(q, str(A / f), M, pick=pick)
assets.attributions(M, str(W / "attributions.txt"))

# portrait-ish captures: narrow viewport so the page reflows tall
assets.capture([
    dict(name="wiki_ds", url="https://en.wikipedia.org/wiki/Dark_Souls", w=900, h=1600, out=str(A / "wiki_ds.png")),
    dict(name="wiki_demons", url="https://en.wikipedia.org/wiki/Demon%27s_Souls", w=900, h=1600, out=str(A / "wiki_demons.png")),
    dict(name="wiki_miyazaki", url="https://en.wikipedia.org/wiki/Hidetaka_Miyazaki", w=900, h=1600, out=str(A / "wiki_miyazaki.png")),
    dict(name="wiki_soulslike", url="https://en.wikipedia.org/wiki/Soulslike", w=900, h=1600, out=str(A / "wiki_soulslike.png")),
    dict(name="wiki_elden", url="https://en.wikipedia.org/wiki/Elden_Ring", w=900, h=1600, out=str(A / "wiki_elden.png")),
    dict(name="wiki_ds_sales", url="https://en.wikipedia.org/wiki/Dark_Souls", w=900, h=1600, scroll="#Sales", out=str(A / "wiki_ds_sales.png")),
], str(W))

# "YOU DIED" card in the game's style: dark red serif on black
from PIL import Image, ImageDraw, ImageFont
im = Image.new("RGB", (1080, 1920), (0, 0, 0)); d = ImageDraw.Draw(im)
try: f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman.ttf", 150)
except OSError: f = ImageFont.load_default()
d.rectangle([0, 860, 1080, 1060], fill=(12, 0, 0))
w = d.textlength("YOU DIED", font=f); d.text(((1080 - w) / 2, 880), "YOU DIED", font=f, fill=(150, 20, 24))
im.save(A / "you_died.png")
print("assets done")
