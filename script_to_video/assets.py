"""Assets: Wikimedia Commons images with licences, text/terminal cards, clips → frames, gifmeta, page captures."""
from __future__ import annotations
import json, os, re, subprocess, shutil, glob, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

UA = "script-to-video/1.0 (https://github.com/isabellagreco1997/script-to-video)"
ENGINE = Path(__file__).resolve().parent.parent / "engine"


# ---------- Wikimedia Commons (curl: some Python builds have broken SSL certs)
def commons_search(query: str, n: int = 4, width: int = 1600) -> list[dict]:
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=" + str(n) +
           "&gsrsearch=" + subprocess.run(["python3", "-c", "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))", f"filetype:bitmap {query}"], capture_output=True, text=True).stdout.strip() +
           "&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=" + str(width))
    raw = subprocess.run(["curl", "-s", "-A", UA, url], capture_output=True, text=True).stdout
    try:
        pages = json.loads(raw).get("query", {}).get("pages", {})
    except json.JSONDecodeError:
        return []
    out = []
    for p in pages.values():
        ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        out.append(dict(title=p.get("title"), url=ii.get("thumburl") or ii.get("url"), page=ii.get("descriptionurl"),
                        license=md.get("LicenseShortName", {}).get("value", "?"), artist=md.get("Artist", {}).get("value", "?"),
                        credit=md.get("Credit", {}).get("value", "")))
    return out


def commons_fetch(query: str, out_path: str, manifest: str, pick: int = 0, n: int = 4) -> dict | None:
    """Search Commons, download result #pick to out_path, append licence info to manifest (json list)."""
    res = commons_search(query, n=n)
    if not res or pick >= len(res): print("  no result for", query); return None
    r = res[pick]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", out_path, r["url"]], check=True)
    try: Image.open(out_path).convert("RGB").save(out_path)          # normalise (webp/jpg/png all fine)
    except Exception as e: print("  bad image for", query, e); return None
    m = json.load(open(manifest)) if Path(manifest).exists() else []
    m.append(dict(file=os.path.basename(out_path), query=query, **r)); json.dump(m, open(manifest, "w"), indent=1)
    print("  +", os.path.basename(out_path), "|", r["license"], "|", r["title"])
    return r


def wikipedia_images(article: str, out_dir: str, manifest: str, limit: int = 10, lang: str = "en", width: int = 1600, prefix: str = "") -> list[str]:
    """Download the images an article actually uses (curated, licensed, SVGs come back as PNG thumbs).
    Skips icons/logos/audio. Returns local paths; licence info appended to the manifest."""
    q = lambda s: subprocess.run(["python3", "-c", "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))", s], capture_output=True, text=True).stdout.strip()
    api = f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=images&imlimit=50&titles={q(article)}"
    raw = subprocess.run(["curl", "-s", "-A", UA, api], capture_output=True, text=True).stdout
    try: pages = json.loads(raw)["query"]["pages"]
    except Exception: return []
    files = [im["title"] for p in pages.values() for im in p.get("images", [])]
    skip = ("Commons-logo", "Wiki letter", "Edit-clear", "Question book", "Symbol ", "OOjs", "Ambox", "Wiktionary", "Wikiquote", "Wikibooks", "Wikisource", "Wikinews", "Wikiversity", "Wikidata", "Wikispecies", "Flag of", "Padlock-", "Crystal Clear", "Nuvola", "Folder Hexagonal", "P vip", "Speaker Icon", "Gnome-", "Star", "Text document", "Cscr-", "Semi-protection", "Lock-", "Video-", "Icon", "Disambig", "Portal", "Blue pencil", "Pictogram", "Loudspeaker", "Sound-icon")
    files = [f for f in files if not any(s.lower() in f.lower() for s in skip) and not f.lower().endswith((".ogg", ".oga", ".mid", ".webm", ".ogv"))]
    out, m = [], (json.load(open(manifest)) if Path(manifest).exists() else [])
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for i, title in enumerate(files[:limit]):
        info = f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth={width}&titles={q(title)}"
        try: ii = list(json.loads(subprocess.run(["curl", "-s", "-A", UA, info], capture_output=True, text=True).stdout)["query"]["pages"].values())[0]["imageinfo"][0]
        except Exception: continue
        md = ii.get("extmetadata", {}); url = ii.get("thumburl") or ii.get("url")
        name = f"{prefix}{re.sub(r'[^A-Za-z0-9]+', '_', title.replace('File:', ''))[:48]}.png"
        path = str(Path(out_dir) / name)
        ok = False
        for attempt in range(3):                                                   # Wikimedia rate-limits bursts (429 → an HTML page saved as .png)
            subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", path, url], check=True)
            try:
                im = Image.open(path).convert("RGBA"); ok = True; break
            except Exception:
                time.sleep(2 + 3 * attempt)
        if not ok:
            if os.path.exists(path): os.remove(path)
            print("  skipped (not an image):", title); continue
        if im.width < 300 or im.height < 200: os.remove(path); continue
        bg = Image.new("RGBA", im.size, (247, 244, 236, 255)); bg.alpha_composite(im); bg.convert("RGB").save(path)   # SVG/PNG alpha → light card
        time.sleep(0.4)                                                            # be polite to the API
        m.append(dict(file=name, article=article, title=title, url=url, page=ii.get("descriptionurl"),
                      license=md.get("LicenseShortName", {}).get("value", "?"), artist=md.get("Artist", {}).get("value", "?")))
        out.append(path); print("  +", name, "|", md.get("LicenseShortName", {}).get("value", "?"))
    json.dump(m, open(manifest, "w"), indent=1)
    return out


def commons_file(title: str, out_path: str, manifest: str, width: int = 1600) -> str | None:
    """Download one named Commons file (e.g. 'File:Pin tumbler with key.svg'); SVGs arrive as PNG thumbs on a light card."""
    q = subprocess.run(["python3", "-c", "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))", title], capture_output=True, text=True).stdout.strip()
    info = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth={width}&titles={q}"
    try: ii = list(json.loads(subprocess.run(["curl", "-s", "-A", UA, info], capture_output=True, text=True).stdout)["query"]["pages"].values())[0]["imageinfo"][0]
    except Exception: print("  not found:", title); return None
    md = ii.get("extmetadata", {}); Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", out_path, ii.get("thumburl") or ii["url"]], check=True)
    im = Image.open(out_path).convert("RGBA"); bg = Image.new("RGBA", im.size, (247, 244, 236, 255)); bg.alpha_composite(im); bg.convert("RGB").save(out_path)
    m = json.load(open(manifest)) if Path(manifest).exists() else []
    m.append(dict(file=os.path.basename(out_path), title=title, page=ii.get("descriptionurl"), license=md.get("LicenseShortName", {}).get("value", "?"), artist=md.get("Artist", {}).get("value", "?")))
    json.dump(m, open(manifest, "w"), indent=1); print("  +", os.path.basename(out_path), "|", md.get("LicenseShortName", {}).get("value", "?")); return out_path


def attributions(manifest: str, out_txt: str):
    m = json.load(open(manifest))
    lines = ["Images from Wikimedia Commons:"] + [f"- {x['title']} — {x['license']} — {x['page']}" for x in m]
    Path(out_txt).write_text("\n".join(lines)); return out_txt


# ---------- cards
def _font(size, bold=True):
    for p, i in (("/System/Library/Fonts/Menlo.ttc", 1 if bold else 0), ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 0), ("C:/Windows/Fonts/consolab.ttf", 0)):
        try: return ImageFont.truetype(p, size, index=i)
        except OSError: continue
    return ImageFont.load_default()


def text_card(text: str, path: str, size: int = 34, fg=(230, 230, 230), bg=(20, 20, 28), pad: int = 40, width: int | None = None) -> Image.Image:
    """Monospace card (terminal output, a quote, a list). Lines separated by \\n."""
    f = _font(size, False); lines = text.splitlines() or [""]
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    cw = max(d.textlength(l, font=f) for l in lines); lh = size + 6
    im = Image.new("RGB", (int(width or cw + 2 * pad), lh * len(lines) + 2 * pad), bg); dd = ImageDraw.Draw(im)
    for i, l in enumerate(lines): dd.text((pad, pad + i * lh), l, font=f, fill=fg)
    im.save(path); return im


def logo_card(logo_path: str, path: str, w: int = 900, h: int = 500, bg=(247, 244, 236)):
    """Transparent/dark logos need a light card behind them (CSS padding clips)."""
    im = Image.open(logo_path).convert("RGBA"); k = min((w - 120) / im.width, (h - 120) / im.height)
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    card = Image.new("RGBA", (w, h), bg + (255,)); card.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
    card.convert("RGB").save(path); return card


# ---------- clips → frames (video, gif) + gifmeta
def clip_frames(src: str, name: str, work: str, fps: float = 12, start: float = 0, dur: float | None = None, width: int = 1280) -> dict:
    """Extract frames of a video/gif into work/gifframes/<name>/f001.png…; returns {n, fps} for gifmeta."""
    d = Path(work) / "gifframes" / name; shutil.rmtree(d, ignore_errors=True); d.mkdir(parents=True)
    if src.lower().endswith(".gif"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vsync", "0", str(d / "f%03d.png")], check=True)
        im = Image.open(src); durs = []
        try:
            while True: durs.append(im.info.get("duration", 100)); im.seek(im.tell() + 1)
        except EOFError: pass
        n = len(list(d.glob("f*.png"))); fps = round(1000 / max(1, sum(durs) / max(1, len(durs))), 2)
    else:
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(start)] + (["-t", str(dur)] if dur else []) + ["-i", src, "-vf", f"fps={fps},scale={width}:-2", str(d / "f%03d.png")]
        subprocess.run(cmd, check=True); n = len(list(d.glob("f*.png")))
    return dict(n=n, fps=fps)


def write_gifmeta(work: str, meta: dict):
    Path(work, "gifmeta.js").write_text("const GIFMETA = " + json.dumps(meta) + ";\n")


# ---------- page captures (screenshots of articles, repos, docs)
def capture(jobs: list[dict], work: str):
    p = Path(work) / "capture_jobs.json"; json.dump(jobs, open(p, "w"))
    subprocess.run(["node", str(ENGINE / "capture.js"), str(p)], check=True, cwd=str(Path(__file__).resolve().parent.parent))


# ---------- contact sheet of any images
def contact(paths: list[str], out: str, cols: int = 5, width: int = 384):
    ims = [Image.open(p).convert("RGB") for p in paths]
    k = width / max(im.width for im in ims); h = int(max(im.height for im in ims) * k)
    rows = (len(ims) + cols - 1) // cols; sheet = Image.new("RGB", (cols * width, rows * (h + 20)), (20, 20, 20)); d = ImageDraw.Draw(sheet)
    for i, (p, im) in enumerate(zip(paths, ims)):
        im = im.resize((int(im.width * k), int(im.height * k))); x, y = (i % cols) * width, (i // cols) * (h + 20)
        sheet.paste(im, (x, y)); d.text((x + 4, y + h + 4), os.path.basename(p)[:40], fill=(220, 220, 220))
    sheet.save(out); return out
