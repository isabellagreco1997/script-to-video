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


class Timeline:
    def __init__(self, words_json: str, w: int = 1920, h: int = 1080, tail: float = 1.2, assets: str = "assets/"):
        words = json.load(open(words_json))
        self.norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower().replace("'", "")).split()
        self.W = [(self.norm(w)[0] if self.norm(w) else "", s, e) for w, s, e in words]
        self.w, self.h, self.pos, self.missing, self.S = w, h, 0, [], []
        self.end = round(self.W[-1][2] + tail, 2)
        self.A = assets

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

    def rel(self, phrase: str) -> float:
        """seconds from the current shot's anchor to a phrase — the usual value for a layer's `in`."""
        return round(self.at(phrase) - self.W[self.pos][1], 2)

    # ---------- layers
    def T(self, text, x, y, fs=150, rot=0, i=0.0, **k): return dict(type="text", text=text, x=x, y=y, fs=fs, rot=rot, **{"in": i}, **k)
    def C(self, text, x, y, i=0.0, **k): return dict(type="chip", text=text, x=x, y=y, **{"in": i}, **k)
    def I(self, src, x, y, w, i=0.0, **k): return dict(type="img", src=(src if "/" in src else self.A + src), x=x, y=y, w=w, **{"in": i}, **k)
    def G(self, name, x, y, w, i=0.0, **k): return dict(type="img", src=f"gifs/{name}.gif", x=x, y=y, w=w, plain=True, **{"in": i}, **k)
    def bg(self, src, kb="zin", dark=0.0, fit="cover", shake=False): return dict(src=(src if "/" in src else self.A + src), kb=kb, dark=dark, fit=fit, shake=shake)
    def clip(self, name, kb="zin", dark=0.0, fit="contain"): return dict(src=f"gifs/{name}.gif", kb=kb, dark=dark, fit=fit)

    # ---------- shots
    def shot(self, anchor, off: float = 0.0, **sh):
        """anchor: phrase (moves the cursor) or a float time."""
        if isinstance(anchor, (int, float)):
            t0 = float(anchor)
        else:
            i = self._find(anchor, self.pos)
            if i is None: i = self._find(anchor, 0)
            if i is None: self.missing.append(anchor); i = min(self.pos + 3, len(self.W) - 1)
            self.pos = i; t0 = round(self.W[i][1] + off, 2)
        self.S.append([t0, sh])
        return t0

    def black(self, anchor, off=0.0): return self.shot(anchor, off)

    # ---------- output + report
    def write(self, path: str):
        out = [f"const META = {json.dumps(dict(w=self.w, h=self.h, dur=self.end))};", "const TL = ["]
        problems = []
        for i, (t0, sh) in enumerate(self.S):
            t1 = self.S[i + 1][0] if i + 1 < len(self.S) else self.end
            if t1 <= t0: problems.append(f"shot {i} at {t0} is not after the previous shot"); t1 = round(t0 + 0.05, 2)
            d = {"t0": t0, "t1": t1}; d.update(sh); out.append(json.dumps(d, ensure_ascii=False) + ",")
        out.append("];")
        Path(path).write_text("\n".join(out))
        text_t = sum((self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0 for i, (t0, sh) in enumerate(self.S)
                     if any(l.get("type") == "text" for l in sh.get("layers", [])))
        long = [(i, round((self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0, 1)) for i, (t0, _) in enumerate(self.S)
                if (self.S[i + 1][0] if i + 1 < len(self.S) else self.end) - t0 > 8]
        print(f"timeline: {len(self.S)} shots, {self.end}s, word slams {100 * text_t / self.end:.0f}% of runtime (aim ≤10%)")
        if long: print("  shots over 8 s:", long)
        if self.missing: print("  MISSING anchors:", self.missing)
        for p in problems: print("  ORDER:", p)
        return path
