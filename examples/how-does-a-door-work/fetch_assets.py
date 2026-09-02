"""Images from Wikimedia Commons (licences recorded) + article screenshots. python fetch_assets.py"""
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import assets

HERE = Path(__file__).resolve().parent; A = HERE / "work/assets"; A.mkdir(parents=True, exist_ok=True)
M = str(HERE / "work/manifest.json")
if Path(M).exists(): os.remove(M)

PICS = {  # file: (commons query, which result)
    "old_door.jpg": ("old wooden door medieval", 0),
    "door_ajar.jpg": ("open door doorway", 0),
    "hinge.jpg": ("butt hinge door", 0),
    "hinge_pin.jpg": ("door hinge pin barrel", 0),
    "leaning_door.jpg": ("crooked old door", 0),
    "pivot_socket.jpg": ("pivot door socket ancient stone", 0),
    "pantheon_door.jpg": ("Pantheon bronze doors Rome", 0),
    "latch.jpg": ("door latch bolt", 0),
    "strike_plate.jpg": ("strike plate door", 0),
    "medieval_latch.jpg": ("medieval iron door latch", 0),
    "pin_tumbler.jpg": ("pin tumbler lock diagram", 0),
    "pin_tumbler_key.jpg": ("pin tumbler lock with key inserted", 0),
    "yale.jpg": ("Linus Yale Jr.", 0),
    "yale_patent.jpg": ("Yale lock patent drawing", 0),
    "front_door.jpg": ("front door house entrance", 0),
    "walking_through_door.jpg": ("person walking through doorway", 0),
}
for f, (q, pick) in PICS.items():
    assets.commons_fetch(q, str(A / f), M, pick=pick)
assets.attributions(M, str(HERE / "work/attributions.txt"))

assets.capture([
    dict(name="wiki_door", url="https://en.wikipedia.org/wiki/Door", w=1600, h=1000, out=str(A / "wiki_door.png")),
    dict(name="wiki_hinge", url="https://en.wikipedia.org/wiki/Hinge", w=1600, h=1000, out=str(A / "wiki_hinge.png")),
    dict(name="wiki_latch", url="https://en.wikipedia.org/wiki/Latch", w=1600, h=1000, out=str(A / "wiki_latch.png")),
    dict(name="wiki_pin", url="https://en.wikipedia.org/wiki/Pin_tumbler_lock", w=1600, h=1000, out=str(A / "wiki_pin.png")),
    dict(name="wiki_yale", url="https://en.wikipedia.org/wiki/Linus_Yale_Jr.", w=1600, h=1000, out=str(A / "wiki_yale.png")),
], str(HERE / "work"))
print("assets done")
