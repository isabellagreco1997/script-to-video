"""Shot list for "How does a door work" (16:9). Run: script-to-video build examples/how-does-a-door-work/build.py
Every shot carries `see=` — what a viewer should be looking at — and no image is used twice.
Assets: fetch_assets.py (Wikipedia article images, Commons files, article captures) + make_diagrams.py (drawn in code)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import Timeline

HERE = Path(__file__).resolve().parent; W = HERE / "work"
BUILD = dict(work=str(W), narration=str(W / "narration.mp3"), out=str(HERE / "out/how-does-a-door-work.mp4"), music=None)
(HERE / "out").mkdir(exist_ok=True)
P = "wp/"

tl = Timeline(str(W / "words.json"), w=1920, h=1080)
tl.shot(0.0, see="black until the first word")
tl.shot("door", see="one old door, whole", bg=tl.bg(P + "door__Berfrestone_DB_door_and_tympanum_arch_St_Nichol.png", kb="zin", dark=0.1))
tl.shot("opinion", see="the word, on the door", bg=tl.bg(P + "door__Berfrestone_DB_door_and_tympanum_arch_St_Nichol.png", kb="punch", dark=0.55), layers=[tl.T("AN OPINION.", 560, 420, fs=170, rot=-2, i=0.05)])
# ---- the three problems: three pictures, one per word
tl.shot("Every door", see="a grand pair of doors", bg=tl.bg(P + "door_Chateau_de_Versailles_Vestibule_Haut_11_lighter_.png", kb="zout", dark=0.1))
tl.shot("It has to swing", see="a hinge", layers=[tl.pic(P + "hinge_Hamburgerpaumelle_JPG.png", safe=0.8, anim="slideU")])
tl.shot("stay shut|stay shot", see="a bolt latch", layers=[tl.pic("latch.jpg", safe=0.8, anim="slideU")])
tl.shot("right people", see="a see-through lock", layers=[tl.pic("pin_tumbler_key.jpg", safe=0.8, anim="slideU")])
tl.shot("That's a hinge", see="the three words, big, each on its word", layers=[tl.C("HINGE", 330, 470, fs=80), tl.C("LATCH", 800, 470, tl.rel("latch"), fs=80), tl.C("LOCK", 1280, 470, tl.rel("lock"), fs=80)])
# ---- hinge
tl.shot("Start with", see="a real brass hinge, close", bg=tl.bg(P + "hinge_Carrollton_New_Orleans_hinge_brass_inside_jpg.png", kb="zin", dark=0.1))
tl.shot("Two leaves", see="the labelled diagram: leaves, knuckles, pin", layers=[tl.pic(P + "hinge_Basic_hinge_svg.png", safe=0.9, anim="slideU")])
tl.shot("The leaves screw", see="same diagram, pushing in on the pin", layers=[tl.pic(P + "hinge_Basic_hinge_svg.png", safe=0.9, anim="none", zoomTo=1.4, origin="80% 55%")])
tl.shot("rotate around", see="top-down drawing: door swinging about the pin", layers=[tl.pic("axis.png", safe=0.9, anim="fade")])
tl.shot("That line|The line", see="the axis dot, pushed in", layers=[tl.pic("axis.png", safe=0.9, anim="none", zoomTo=1.5, origin="25% 50%")])
tl.shot("millimeter|millimetre", see="same drawing, axis tilted, door drifting", layers=[tl.pic("axis_tilted.png", safe=0.9, anim="fade")])
tl.shot("refuses", see="a worn old hinge", bg=tl.bg(P + "hinge_Hinge2P3_jpg.png", kb="zin", dark=0.15))
tl.shot("old doors drift", see="an old wooden door hanging in a stone wall", bg=tl.bg("old_door.jpg", kb="zout", dark=0.15))
# ---- pivots
tl.shot("Before hinges", see="a medieval drawing of a pivot-hung door", layers=[tl.pic(P + "hinge_Haar_hung_doors_99309543_jpg.png", safe=0.9, anim="slideU")])
tl.shot("A peg", see="the stone socket a door pin sat in", bg=tl.bg(P + "door_Door_Post_Socket_4690606141_jpg.png", kb="panD", dark=0.1))
tl.shot("The Romans", see="Roman bronze doors", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="zin", dark=0.1))
tl.shot("solid bronze", see="same doors, slow push", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="zout", dark=0.5))
tl.shot("more than a car", see="the line", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="still", dark=0.65), layers=[tl.T("MORE THAN A CAR.", 300, 420, fs=160, rot=2, i=0.05)])
# ---- latch: drawn, as a state change
tl.shot("Then the latch", see="an iron slide bolt with its keeper", bg=tl.bg(P + "latch_Asso_chiavistello_porta_Magnocavallo_JPG.png", kb="zin", dark=0.1))
tl.shot("Push the door", see="drawing: bolt out, door closing", layers=[tl.pic("latch_open.png", safe=0.9, anim="fade")])
tl.shot("angled face", see="the bolt riding over the strike plate (animated)", bg=tl.clip("latch", kb="still", fit="contain"))
tl.shot("A spring", see="the red spring pushing the bolt into the keeper", layers=[tl.pic("latch_closed.png", safe=0.9, anim="none", zoomTo=1.5, origin="40% 50%")])
tl.shot("The handle", see="a lever handle on a door", bg=tl.bg("handle.jpg", kb="zin", dark=0.1))
tl.shot("barely changed", see="an old green door with an iron latch", bg=tl.bg(P + "latch_Amizmiz_Old_Shop_Door_jpg.png", kb="zout", dark=0.2))
# ---- lock: the diagrams do the explaining
tl.shot("The lock is", see="an old carved door with its wooden lock", layers=[tl.pic(P + "door_Brooklyn_Museum_1994_92_Door_with_Lock_2_jpg.png", safe=0.9, anim="slideU")])
tl.shot("A pin tumbler", see="diagram: the row of pins, no key", layers=[tl.pic("pin_no_key.png", safe=0.9, anim="fade")])
tl.shot("cut in two", see="push in on the split pins", layers=[tl.pic("pin_no_key.png", safe=0.9, anim="none", zoomTo=1.6, origin="50% 45%")])
tl.shot("With no key", see="the line drawn through: pins cross it, nothing turns", layers=[tl.pic("pin_blocked.png", safe=0.9, anim="fade")])
tl.shot("The right key", see="diagram: key in, pins lifted", layers=[tl.pic("pin_with_key.png", safe=0.9, anim="fade")])
tl.shot("the shear line", see="the red dashed shear line drawn on", layers=[tl.pic("pin_shear.png", safe=0.9, anim="none", zoomTo=1.4, origin="50% 50%")])
tl.shot("That's it", see="the wrong key: pins misaligned", layers=[tl.pic("pin_bad_key.png", safe=0.9, anim="fade")])
tl.shot("A lock is|lock is a shape", see="the line", layers=[tl.T("A SHAPE TEST.", 380, 420, fs=170, rot=-2, i=tl.rel("shape test"))])
# ---- yale
tl.shot("Linus Yale", see="his portrait and name", layers=[tl.pic("yale.jpg", safe=0.75, anim="slideU", rot=-2), tl.C("LINUS YALE JR.", 760, 940, 0.3, fs=64)])
tl.shot("1861", see="the article, pushed to the paragraph", layers=[tl.pic("wiki_yale.png", safe=0.92, anim="fade", zoomTo=1.5, origin="30% 40%")])
tl.shot("front door", see="a front door with steps", bg=tl.bg(P + "door_3_5_Strada_Icoanei_Bucharest_Romania_1_jpg.png", kb="zin", dark=0.1))
# ---- close
tl.shot("So a door", see="three pictures again: hinge, spring, key", layers=[tl.I("axis.png", 60, 300, 580, 0.0, plain=True), tl.I("latch_closed.png", 670, 300, 580, tl.rel("a spring"), plain=True), tl.I("pin_shear.png", 1280, 300, 580, tl.rel("shape test"), plain=True)])
tl.shot("Three ideas", see="a row of doors", layers=[tl.pic("doors_row.png", safe=0.92, anim="slideU")])
tl.shot("hundred times", see="same row, slow push", layers=[tl.pic("doors_row.png", safe=0.92, anim="none", zoomTo=1.3, origin="50% 50%")])
tl.shot("without looking", see="black")
tl.shot("look", see="one door, whole, still", bg=tl.bg("door_ajar.jpg", kb="still", dark=0.1))
tl.shot("look", off=1.3, see="black")
tl.write(str(W / "timeline.js"))
