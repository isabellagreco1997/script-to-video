"""script-to-video CLI

  script-to-video setup                                   # download the Kokoro voice model (once)
  script-to-video voice  script.txt work/narration.wav --voice am_puck [--speed 1.0] [--say "CLI=C L I"]
  script-to-video align  work/narration16.wav work/       # → work/words.json + work/sentences.txt
  script-to-video timeline build.py                       # runs your shot script (it writes work/timeline.js)
  script-to-video render work/ [--start F --end F]        # frames → work/render_frames
  script-to-video sfx    work/
  script-to-video encode work/ work/narration.mp3 out.mp4 [--music bed.mp3] [--sfx work/sfx.wav]
  script-to-video audit  work/ out/sheet                  # contact sheets, 2 frames per shot
  script-to-video build  build.py                         # timeline + render + sfx + encode + audit (reads BUILD in build.py)
"""
from __future__ import annotations
import argparse, runpy, sys
from pathlib import Path
from . import voice as V, align as AL, pipeline as P


def main(argv=None):
    p = argparse.ArgumentParser(prog="script-to-video"); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup")
    a = sub.add_parser("voice"); a.add_argument("script"); a.add_argument("out_wav"); a.add_argument("--voice", default="am_puck"); a.add_argument("--speed", type=float, default=1.0); a.add_argument("--say", action="append", default=[])
    a = sub.add_parser("align"); a.add_argument("wav16"); a.add_argument("work"); a.add_argument("--model", default="small")
    a = sub.add_parser("timeline"); a.add_argument("build_py")
    a = sub.add_parser("render"); a.add_argument("work"); a.add_argument("--start", type=int); a.add_argument("--end", type=int); a.add_argument("--port", type=int)
    a = sub.add_parser("sfx"); a.add_argument("work")
    a = sub.add_parser("encode"); a.add_argument("work"); a.add_argument("narration_mp3"); a.add_argument("out_mp4"); a.add_argument("--music"); a.add_argument("--music-vol", type=float, default=0.07); a.add_argument("--sfx")
    a = sub.add_parser("audit"); a.add_argument("work"); a.add_argument("out_prefix"); a.add_argument("--every", type=float, help="seconds between frames (e.g. 0.5) instead of 2 per shot")
    a = sub.add_parser("build"); a.add_argument("build_py")
    args = p.parse_args(argv)

    if args.cmd == "setup": V.setup()
    elif args.cmd == "voice":
        say = dict(s.split("=", 1) for s in args.say); V.synthesize(args.script, args.out_wav, voice=args.voice, speed=args.speed, say=say)
    elif args.cmd == "align": AL.align(args.wav16, args.work, model=args.model)
    elif args.cmd == "timeline": runpy.run_path(args.build_py, run_name="__main__")
    elif args.cmd == "render": P.render(args.work, args.start, args.end, args.port)
    elif args.cmd == "sfx": P.sfx(args.work)
    elif args.cmd == "encode": P.encode(args.work, args.narration_mp3, args.out_mp4, args.music, args.music_vol, args.sfx)
    elif args.cmd == "audit": P.audit(args.work, args.out_prefix, every=args.every)
    elif args.cmd == "build":
        g = runpy.run_path(args.build_py, run_name="__main__"); b = g.get("BUILD")
        if not b: raise SystemExit("build.py must define BUILD = dict(work=, narration=, out=, music=None)")
        P.render(b["work"]); s = P.sfx(b["work"]); P.encode(b["work"], b["narration"], b["out"], b.get("music"), b.get("music_vol", 0.07), s)
        P.audit(b["work"], str(Path(b["out"]).with_suffix("")) + "_audit"); P.audit(b["work"], str(Path(b["out"]).with_suffix("")) + "_dense", every=0.5)


if __name__ == "__main__":
    main()
