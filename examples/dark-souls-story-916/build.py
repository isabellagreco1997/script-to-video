"""Shot list for "The story of Dark Souls" — a 9:16 reel. Run: script-to-video build examples/dark-souls-story-916/build.py
Gameplay clips are trailer segments fetched by fetch_assets.py (not in git). Stills: Wikipedia article images + captures."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from script_to_video import Timeline

HERE = Path(__file__).resolve().parent; W = HERE / "work"
BUILD = dict(work=str(W), narration=str(W / "narration.mp3"), out=str(HERE / "out/dark-souls-story-916.mp4"), music=None)
(HERE / "out").mkdir(exist_ok=True)
P = "wp/"
MIYA = P + "ds_Hidetaka_Miyazaki_The_Game_Awards_2022_cropped_p.png"

tl = Timeline(str(W / "words.json"), w=1080, h=1920)
tl.shot("Dark Souls", bg=tl.clip("gp4", kb="zin", fit="cover"), layers=[tl.I(P + "ds_Dark_Souls_logo_black_svg.png", 90, 700, 900, 0.05, anim="slideU")])
tl.shot("2011", bg=tl.clip("gp4", kb="zin", fit="cover", dark=0.2), layers=[tl.C("2011", 440, 1500, 0.05)])
tl.shot("almost nobody", bg=tl.clip("gp1", kb="zin", fit="cover", dark=0.3))
# ---- demon's souls
tl.shot("spiritual sequel", layers=[tl.I(P + "demons_Demon_Souls_Screenshot_jpg.png", 40, 560, 1000, 0.05, anim="slideU"), tl.C("DEMON'S SOULS, 2009", 300, 1200, 0.4)])
tl.shot("Sony", layers=[tl.I("ps3.jpg", 90, 560, 900, 0.05, rot=-3)])
tl.shot("outside Japan", bg=tl.bg("wiki_demons.png", kb="panD", dark=0.2))
tl.shot("too hard", bg=tl.bg("wiki_demons.png", kb="zin", dark=0.65), layers=[tl.T("TOO HARD TO SELL.", 60, 880, fs=120, rot=-2, i=0.05, wrap=960)])
# ---- miyazaki
tl.shot("The director", layers=[tl.I(MIYA, 140, 300, 800, 0.05, rot=-2), tl.C("HIDETAKA MIYAZAKI", 250, 1330, tl.rel("Miyazaki|Haidtaka|director"))])
tl.shot("wanted one thing", bg=tl.bg("wiki_miyazaki.png", kb="zin", dark=0.4))
tl.shot("A world where dying", bg=tl.clip("gp5", kb="punch", fit="cover"), flash=0)
tl.shot("You keep", bg=tl.clip("gp2", kb="zin", fit="cover"))
tl.shot("You lose", bg=tl.clip("gp1", kb="zout", fit="cover", dark=0.3))
tl.shot("one chance", bg=tl.clip("gp3", kb="zin", fit="cover"))
tl.shot("reclaim", bg=tl.clip("gp3", kb="zin", fit="cover", dark=0.2), layers=[tl.I(P + "soulslike_Dark_Souls_Bonfire_png.png", 90, 1180, 900, 0.05, anim="slideU")])
# ---- the rules
tl.shot("no difficulty", layers=[tl.I("options_card.png", 90, 560, 900, 0.05, anim="slideU", plain=True)])
tl.shot("no pause", layers=[tl.I("options_card.png", 90, 560, 900, 0.0, plain=True, zoomTo=1.6, origin="50% 70%")])
tl.shot("the map", bg=tl.clip("gp4", kb="panL", fit="cover"))
tl.shot("every shortcut", bg=tl.clip("gp2", kb="zout", fit="cover"))
tl.shot("discovered", bg=tl.clip("gp2", kb="zin", fit="cover", dark=0.35))
# ---- legacy
tl.shot("It sold", bg=tl.bg("wiki_ds_sales.png", kb="zin", dark=0.55), layers=[dict(type="counter", to=2000000, x=60, y=820, fs=140, rot=-2, d=1.8, **{"in": tl.rel("2 million|two million|million")})])
tl.shot("two sequels", layers=[tl.I(P + "ds3_Dark_Souls_III_gameplay_screenshot_jpg.png", 40, 620, 1000, 0.05, anim="slideU")])
tl.shot("Bloodborne", layers=[tl.I(P + "bb_Bloodborne_Alpha_PlayStation_4_gameplay_screensh.png", 40, 620, 1000, 0.05, anim="slideL")])
tl.shot("Sekiro", layers=[tl.I(P + "sekiro_Sekiro_Shadows_Die_Twice_pre_release_gameplay_sc.png", 40, 620, 1000, 0.05, anim="slideR")])
tl.shot("Elden Ring", layers=[tl.I(P + "elden_Elden_Ring_gameplay_png.png", 40, 620, 1000, 0.05, anim="slideU")])
tl.shot("entire genre", bg=tl.bg("wiki_soulslike.png", kb="zin", dark=0.3), layers=[tl.C("SOULSLIKE", 380, 1500, tl.rel("genre"))])
# ---- the message
tl.shot("The message you see", bg=tl.clip("gp6", kb="zin", fit="cover", dark=0.3))
tl.shot("you died", bg=tl.bg("you_died.png", kb="punch"), flash=0)
tl.shot("The message it", bg=tl.clip("gp6", kb="zin", fit="cover"))
tl.shot("try again", bg=tl.clip("gp6", kb="zin", fit="cover", dark=0.55), layers=[tl.T("TRY AGAIN.", 180, 880, fs=150, rot=-2, i=0.05)])
tl.shot("You know more")
tl.write(str(W / "timeline.js"))
