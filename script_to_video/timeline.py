"""Anchor-phrase timeline: shots start when a phrase is spoken, so re-recording the voice never breaks the sync.

    tl = Timeline("work/words.json", w=1920, h=1080)
    tl.shot("I'm Isa", layers=[tl.T("HI.", 560, 420)])          # shot starts when "I'm Isa" is spoken
    tl.shot("a pixel knight", bg=tl.bg("assets/knight.png", kb="zin"))
    tl.shot("Every body part", bg=tl.clip("knight"), flash=0)     # clip frames in gifframes/knight/
    tl.write("work/timeline.js")

Two cursors: shot() anchors move the search cursor forward (monotonic); tl.at() looks up a phrase from the
current shot's anchor without moving it (for layer `in` times). "a|b" = transcription alternatives.
"""
from __future__ import annotations
import json, re
from pathlib import Path
from PIL import Image


class Timeline:
    def __init__(self, words_json: str, w: int = 1920, h: int = 1080, tail: float = 1.2, assets: str = "assets/"):
        words = json.load(open(words_json))
        self.norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower().replace("'", "")).split()
        self.W = [(self.norm(w)[0] if self.norm(w) else "", s, e) for w, s, e in words]
        self.w, self.h, self.pos, self.missing, self.S = w, h, 0, [], []
        self.portrait = h > w      # 9:16: images fill the phone screen. 16:9: images are protected, whole and centred.
        self.end = round(self.W[-1][2] + tail, 2)
        self.A = assets
        self.work = Path(words_json).resolve().parent     # image sizes are read from here for pic()

    # ---------- lookup
    def _find(self, phrase, start):
        for alt in phrase.split("|"):
            p = self.norm(alt); n = len(p)
            if not n: continue
            for i in range(start, len(self.W) - n + 1):
                if [self.W[i + k][0] for k in range(n)] == p:
                    return i
        return None

    def at(self, phrase: str, off: float = 0.0) -> float:
        """time a phrase is spoken, searched forward from the current shot (cursor unchanged)."""
        i = self._find(phrase, self.pos)
        if i is None: i = self._find(phrase, 0)
        if i is None: self.missing.append(phrase); i = min(self.pos + 3, len(self.W) - 1)
        return round(self.W[i][1] + off, 2)

    def rel(self, phrase: str) -> str:
        """a layer `in` that means "when this phrase is spoken, inside THIS shot". Returns a marker that shot()
        resolves against the shot it ends up in (Python evaluates the layers before shot() runs, so a number
        computed here would be relative to the previous shot: text a second late)."""
        return "@" + phrase

    # ---------- layers
    def T(self, text, x, y, fs=150, rot=0, i=0.0, **k): return dict(type="text", text=text, x=x, y=y, fs=fs, rot=rot, **{"in": i}, **k)
    def words(self, text, ins=None, fs=170, rot=-2, y=None, **k):
        """A line that appears WORD BY WORD, each word on its own spoken word, centred on the stage.
        ins: one anchor per word, e.g. ["@everything", "@falling", "@apart"]; default = each word anchors to itself.
        Pair with shot(..., shake="@apart") to jolt the whole picture on the hit word."""
        ws = text.split(" ")
        if ins is None: ins = ["@" + w.strip(".,!?").lower() for w in ws]
        assert len(ins) == len(ws), "one anchor per word"
        d = dict(type="words", text=text, ins=list(ins), fs=fs, rot=rot, **k)
        if y is not None: d["y"] = y
        return d

    def C(self, text, x, y, i=0.0, **k): return dict(type="chip", text=text, x=x, y=y, **{"in": i}, **k)
    def _src(self, src):
        """paths are relative to the work dir; anything not already under assets/ or gifs/ (or absolute/http) gets the assets prefix."""
        return src if src.startswith(("assets/", "gifs/", "gifframes/", "/", "http")) else self.A + src

    def I(self, src, x, y, w, i=0.0, **k): return dict(type="img", src=self._src(src), x=x, y=y, w=w, **{"in": i}, **k)

    def pic(self, src, i=0.0, safe=None, anim="slideU", plain=True, cx=None, cy=None, zoomTo=None, origin="50% 50%", **k):
        """A WHOLE image, centred, fitted inside `safe` × the stage so nothing bleeds off the edges.
        Size is computed from the file, so wide diagrams and tall pages both fit. A zoomTo push into a detail is a deliberate crop and is not capped."""
        path = self.work / self._src(src)
        iw, ih = Image.open(path).size
        maxw, maxh = self.w * safe, self.h * safe
        k_ = min(maxw / iw, maxh / ih); w, h = int(iw * k_), int(ih * k_)
        x = int((self.w - w) / 2 if cx is None else cx - w / 2); y = int((self.h - h) / 2 if cy is None else cy - h / 2)
        d = dict(type="img", src=self._src(src), x=x, y=y, w=w, plain=plain, anim=anim, **{"in": i}, **k)
        if zoomTo:
            d["zoomTo"] = zoomTo; d["origin"] = origin      # a push into a detail is a deliberate crop, not bleeding
        return d
    def G(self, name, x, y, w, i=0.0, **k): return dict(type="img", src=f"gifs/{name}.gif", x=x, y=y, w=w, plain=True, **{"in": i}, **k)
    def bg(self, src, kb="zin", dark=0.0, fit=None, shake=False, blur=True):
        """Full-frame background. 16:9 default fit='contain': the WHOLE image centred over a blurred copy of itself
        (protection padding, nothing bleeds off). 9:16 default fit='cover': the image fills the phone screen.
        Pass fit explicitly to override either."""
        if fit is None: fit = "cover" if self.portrait else "contain"
        return dict(src=self._src(src), kb=kb, dark=dark, fit=fit, shake=shake, blur=blur)
    def clip(self, name, kb="zin", dark=0.0, fit="contain", offset=0.0):
        """A clip as the background. offset = seconds into the clip to start from (pick the moment that matches the words,
        e.g. the jump, not whatever happens to be at the top of the file). fit='contain' keeps the whole frame; the push is gentle."""
        d = dict(src=f"gifs/{name}.gif", kb=kb, dark=dark, fit=fit)
        if offset: d["offset"] = offset
        return d

    # ---------- shots
    def shot(self, anchor, off: float = 0.0, see: str | None = None, **sh):
        """anchor: phrase (moves the cursor) or a float time. see: what the viewer should SEE here (printed in the plan)."""
        if see: sh["see"] = see
        if isinstance(anchor, (int, float)):
            t0 = float(anchor)
        else:
            i = self._find(anchor, self.pos)
            if i is None: i = self._find(anchor, 0)
            if i is None: self.missing.append(anchor); i = min(self.pos + 3, len(self.W) - 1)
            self.pos = i; t0 = round(self.W[i][1] + off, 2)
        backdrop = sh.pop("backdrop", True)
        lys = sh.get("layers") or []
        if backdrop and "bg" not in sh and lys and lys[0].get("type") == "img" and (lys[0].get("in") or 0) < 0.3:
            # an image-only shot: put the same image, blurred, behind it from frame one so the cut never drops to black
            sh["bg"] = dict(src=lys[0]["src"], kb="still", dark=0.0, fit="contain", blur=True, backdropOnly=True)
        def _res(v):                                          # "@phrase" -> seconds after this shot's start
            if not (isinstance(v, str) and v.startswith("@")): return v
            j = self._find(v[1:], self.pos)
            if j is None: self.missing.append(v[1:]); return 0.0
            return round(max(0.0, self.W[j][1] - t0), 2)
        for L in lys:                                          # resolve "@phrase" ins relative to this shot
            L["in"] = _res(L.get("in", 0.0))
            if "ins" in L: L["ins"] = [_res(v) for v in L["ins"]]; L["in"] = min(L["ins"]) if L["ins"] else 0.0
        if "shake" in sh: sh["shakeAt"] = _res(sh.pop("shake"))
        self.S.append([t0, sh])
        return t0

    def black(self, anchor, off=0.0): return self.shot(anchor, off)

    # ---------- continuity: a move on an image that is already on screen continues, it does not restart
    def _continue_moves(self):
        def END(kb, s0, gentle):
            if kb == "zin": return ((s0 or 1.0) + 0.06) if gentle else ((s0 or 1.02) + 0.10)
            if kb == "zout": return ((s0 or 1.06) - 0.06) if gentle else ((s0 or 1.12) - 0.10)
            if kb == "still": return s0 or 1.0
            if kb == "punch": return 1.02
            return 1.14
        for i in range(1, len(self.S)):
            prev, cur = self.S[i - 1][1], self.S[i][1]
            pb, cb = prev.get("bg"), cur.get("bg")
            if pb and cb and pb.get("src") == cb.get("src") and not pb.get("backdropOnly") and not cb.get("backdropOnly"):
                if cb.get("kb", "zin") in ("zin", "zout", "still"):
                    cb["s0"] = round(END(pb.get("kb", "zin"), pb.get("s0"), pb.get("fit") == "contain"), 3)
            for L in cur.get("layers") or []:
                if L.get("type") != "img" or not L.get("zoomTo") or L.get("anim") != "none": continue
                for P in prev.get("layers") or []:
                    if P.get("type") == "img" and P.get("src") == L["src"]:
                        L["zoomFrom"] = P.get("zoomTo") or 1.0
                        if P.get("zoomTo") and P.get("origin", "50% 50%") != L.get("origin", "50% 50%"): L["originFrom"] = P.get("origin", "50% 50%")
                        break

    # ---------- output + report
    def write(self, path: str):
        self._continue_moves()
        out = [f"const META = {json.dumps(dict(w=self.w, h=self.h, dur=self.end))};", "const TL = ["]
        problems = []
        for i, (t0, sh) in enumerate(self.S):
            t1 = self.S[i + 1][0] if i + 1 < len(self.S) else self.end
            if t1 <= t0: problems.append(f"shot {i} at {t0} is not after the previous shot"); t1 = round(t0 + 0.05, 2)
            d = {"t0": t0, "t1": t1}; d.update(sh); out.append(json.dumps(d, ensure_ascii=False) + ",")
        out.append("];")
        Path(path).write_text("\n".join(out))
        text_t = sum((self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0 for i, (t0, sh) in enumerate(self.S)
                     if any(l.get("type") in ("text", "words") for l in sh.get("layers", [])))
        long = [(i, round((self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0, 1)) for i, (t0, _) in enumerate(self.S)
                if (self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0 > 8]
        # reuse check: the same image twice is a smell (one image per idea)
        used = {}
        for i, (t0, sh) in enumerate(self.S):
            for src in ([sh["bg"]["src"]] if sh.get("bg") else []) + [l.get("src") for l in sh.get("layers", []) if l.get("src")]:
                if src and not src.startswith("gifs/") and i not in used.setdefault(src, []): used[src].append(i)
        # a continuation (same image in the very next shot, different move) is fine; a comeback later is not
        reused = {k: v for k, v in used.items() if any(b - a > 1 for a, b in zip(v, v[1:]))}
        print(f"timeline: {'9:16 full-bleed' if self.portrait else '16:9 protected'}, {len(self.S)} shots, {self.end}s, word slams {100 * text_t / self.end:.0f}% of runtime (aim ≤10%)")
        if reused: print("  REUSED images:", {k.split('/')[-1]: v for k, v in reused.items()})
        if long: print("  shots over 8 s:", long)
        if self.missing: print("  MISSING anchors:", self.missing)
        for p in problems: print("  ORDER:", p)
        return path
