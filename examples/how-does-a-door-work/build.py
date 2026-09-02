"""Shot list for "How does a door work" (16:9). Run: script-to-video build examples/how-does-a-door-work/build.py
Assets come from fetch_assets.py (Wikipedia article images + Commons files + article screenshots, licences in work/manifest*.json)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import Timeline

HERE = Path(__file__).resolve().parent; W = HERE / "work"
BUILD = dict(work=str(W), narration=str(W / "narration.mp3"), out=str(HERE / "out/how-does-a-door-work.mp4"), music=None)
(HERE / "out").mkdir(exist_ok=True)
P = "wp/"   # images pulled from the Wikipedia articles

tl = Timeline(str(W / "words.json"), w=1920, h=1080)
tl.shot(0.0)                                                                                   # black until "door"
tl.shot("door", bg=tl.bg(P + "door__Berfrestone_DB_door_and_tympanum_arch_St_Nichol.png", kb="zin", dark=0.1))
tl.shot("opinion", bg=tl.bg(P + "door__Berfrestone_DB_door_and_tympanum_arch_St_Nichol.png", kb="punch", dark=0.55), layers=[tl.T("AN OPINION.", 560, 420, fs=170, rot=-2, i=0.05)])
# ---- the three problems
tl.shot("Every door", bg=tl.bg(P + "door_Chateau_de_Versailles_Vestibule_Haut_11_lighter_.png", kb="zout", dark=0.15))
tl.shot("It has to swing", bg=tl.bg(P + "hinge_Carrollton_New_Orleans_hinge_brass_inside_jpg.png", kb="panR", dark=0.1))
tl.shot("stay shut|stay shot", bg=tl.bg("latch.jpg", kb="zin", dark=0.15))
tl.shot("right people", bg=tl.bg("pin_tumbler_key.jpg", kb="zin", dark=0.15))
tl.shot("That's a hinge", layers=[tl.C("HINGE", 330, 480), tl.C("LATCH", 800, 480, tl.rel("a latch")), tl.C("LOCK", 1300, 480, tl.rel("a lock"))])
# ---- hinge
tl.shot("Start with", bg=tl.bg(P + "hinge_Carrollton_New_Orleans_hinge_brass_inside_jpg.png", kb="zin", dark=0.1))
tl.shot("Two leaves", layers=[tl.I(P + "hinge_Basic_hinge_svg.png", 360, 60, 1200, 0.05, anim="slideU", plain=True)])
tl.shot("a pin", layers=[tl.I(P + "hinge_Basic_hinge_svg.png", 360, 60, 1200, 0.0, plain=True, zoomTo=1.6, origin="85% 55%")])
tl.shot("The leaves screw", bg=tl.bg(P + "hinge_Hamburgerpaumelle_JPG.png", kb="zout", dark=0.1))
tl.shot("rotate around", bg=tl.bg(P + "hinge_Carrollton_New_Orleans_hinge_brass_inside_jpg.png", kb="punch", dark=0.2), flash=0)
tl.shot("That line", bg=tl.bg(P + "hinge_Carrollton_New_Orleans_hinge_brass_inside_jpg.png", kb="zin", dark=0.6), layers=[tl.T("ONE LINE.", 600, 420, fs=190, rot=-2, i=tl.rel("everything"))])
tl.shot("millimeter|millimetre", bg=tl.bg(P + "hinge_Hinge2P2_jpg.png", kb="panL", dark=0.2))
tl.shot("refuses", bg=tl.bg(P + "hinge_Hinge2P3_jpg.png", kb="zin", dark=0.3))
tl.shot("old doors drift", bg=tl.bg(P + "door_Brooklyn_Museum_1994_92_Door_with_Lock_2_jpg.png", kb="zout", dark=0.25))
# ---- pivots
tl.shot("Before hinges", bg=tl.bg(P + "hinge_Haar_hung_doors_99309543_jpg.png", kb="zin", dark=0.15))
tl.shot("A peg", bg=tl.bg(P + "door_Door_Post_Socket_4690606141_jpg.png", kb="panD", dark=0.1))
tl.shot("The Romans", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="zin", dark=0.1))
tl.shot("solid bronze", bg=tl.bg(P + "pantheon_Einblick_Panorama_Pantheon_Rom_jpg.png", kb="panR", dark=0.2))
tl.shot("more than a car", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="zout", dark=0.55), layers=[tl.T("MORE THAN A CAR.", 300, 420, fs=160, rot=2, i=0.05)])
# ---- latch
tl.shot("Then the latch", bg=tl.bg("latch.jpg", kb="zin", dark=0.1))
tl.shot("Push the door", bg=tl.bg("strike_plate.jpg", kb="panR", dark=0.15))
tl.shot("A spring", layers=[tl.I("wiki_latch.png", 160, 40, 1600, 0.05, anim="slideU", plain=True, zoomTo=1.6, origin="50% 40%")])
tl.shot("The handle", bg=tl.bg(P + "hinge_Hinge_03_jpg.png", kb="zin", dark=0.1))
tl.shot("barely changed", bg=tl.bg(P + "hinge_Hinge_01_jpg.png", kb="zout", dark=0.3))
# ---- lock
tl.shot("The lock is", bg=tl.bg("pin_tumbler_key.jpg", kb="punch", dark=0.15), flash=0)
tl.shot("A pin tumbler", layers=[tl.I("pin_no_key.png", 260, 40, 1400, 0.05, anim="slideU", plain=True)])
tl.shot("With no key", layers=[tl.I("pin_no_key.png", 260, 40, 1400, 0.0, plain=True, zoomTo=1.7, origin="50% 45%")])
tl.shot("The right key", layers=[tl.I("pin_with_key.png", 260, 40, 1400, 0.05, anim="slideU", plain=True)])
tl.shot("the shear line", layers=[tl.I("pin_with_key.png", 260, 40, 1400, 0.0, plain=True, zoomTo=1.9, origin="50% 40%")])
tl.shot("That's it", bg=tl.bg("pin_tumbler_key.jpg", kb="zin", dark=0.5))
tl.shot("A lock is", bg=tl.bg("pin_tumbler_key.jpg", kb="zin", dark=0.6), layers=[tl.T("A SHAPE TEST.", 380, 420, fs=170, rot=-2, i=tl.rel("shape test"))])
# ---- yale
tl.shot("Linus Yale", layers=[tl.I("yale.jpg", 700, 60, 520, 0.05, rot=-3), tl.C("LINUS YALE JR.", 770, 880, 0.3)])
tl.shot("1861", layers=[tl.I("wiki_yale.png", 160, 40, 1600, 0.05, anim="slideU", plain=True, zoomTo=1.5, origin="30% 40%")])
tl.shot("front door", bg=tl.bg("front_door.jpg", kb="zin", dark=0.15))
# ---- close
tl.shot("So a door", layers=[tl.C("A ROTATION", 300, 480), tl.C("A SPRING", 800, 480, tl.rel("a spring")), tl.C("A SHAPE TEST", 1250, 480, tl.rel("shape test"))])
tl.shot("Three ideas", bg=tl.bg(P + "door_Bronze_door_Basilica_di_San_Giovanni_2013_jpg.png", kb="zin", dark=0.25))
tl.shot("hundred times", bg=tl.bg(P + "door_3_5_Strada_Icoanei_Bucharest_Romania_1_jpg.png", kb="panL", dark=0.2))
tl.shot("without looking", bg=tl.bg(P + "door_3_5_Strada_Icoanei_Bucharest_Romania_1_jpg.png", kb="zin", dark=0.6))
tl.shot("Next time")
tl.shot("look", bg=tl.bg(P + "door__Berfrestone_DB_door_and_tympanum_arch_St_Nichol.png", kb="still", dark=0.1))
tl.shot("look", off=1.3)                                                                        # ends on black
tl.write(str(W / "timeline.js"))
