"""Render, sfx, encode, audit."""
from __future__ import annotations
import json, os, re, shutil, subprocess, sys, time, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"


def prepare_work(work: str):
    """Copy the engine page into the work dir (assets/, gifframes/, timeline.js, gifmeta.js live there)."""
    w = Path(work); w.mkdir(parents=True, exist_ok=True)
    shutil.copy(ENGINE / "stage.html", w / "stage.html")
    if not (w / "gifmeta.js").exists(): (w / "gifmeta.js").write_text("const GIFMETA = {};\n")
    return w


def free_port() -> int:
    import socket
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def render(work: str, start: int | None = None, end: int | None = None, port: int | None = None):
    """Serve `work` on a free port and render frames into work/render_frames. Partial: start/end frame numbers (30 fps)."""
    w = prepare_work(work); port = port or free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port)], cwd=str(w), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    env = dict(os.environ, PORT=str(port), OUT=str(w / "render_frames"))
    if start is not None: env["START_F"] = str(start)
    if end is not None: env["END_F"] = str(end)
    try:
        subprocess.run(["node", str(ENGINE / "render.js")], env=env, cwd=str(ROOT), check=True)
    finally:
        srv.terminate()
    return str(w / "render_frames")


def shots(work: str) -> list[dict]:
    tl = Path(work, "timeline.js").read_text()
    return [json.loads(l.rstrip(",")) for l in tl.splitlines() if l.startswith("{")]


def frames_for(work: str, indices: list[int]) -> tuple[int, int]:
    S = shots(work); t0 = min(S[i]["t0"] for i in indices); t1 = max(S[i]["t1"] for i in indices)
    return int(t0 * 30), int(t1 * 30) + 1


def sfx(work: str, out: str = None):
    """Soft low booms on flash cuts and black beats, aligned to the timeline. No pops, no whooshes."""
    S = shots(work); dur = max(s["t1"] for s in S); SR = 44100
    def boom():
        n = int(0.55 * SR); t = np.arange(n) / SR; f = 75 * np.exp(-t * 5) + 35
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.arange(n) / (SR * 0.18)) * 0.5
    track = np.zeros(int((dur + 0.5) * SR))
    for s in S:
        if s["t0"] == 0: continue
        hit = 1.0 if s.get("flash") == 0 else (0.55 if not s.get("bg") and not s.get("layers") else None)
        if hit:
            i = int((s["t0"] - 0.02) * SR); b = boom() * hit
            if 0 <= i and i + len(b) <= len(track): track[i:i + len(b)] += b
    out = out or str(Path(work) / "sfx.wav")
    w = wave.open(out, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes()); w.close(); return out


def encode(work: str, narration_mp3: str, out_mp4: str, music: str | None = None, music_vol: float = 0.07, sfx_wav: str | None = None):
    frames = Path(work) / "render_frames"; S = shots(work); dur = max(s["t1"] for s in S)
    meta = json.loads(re.search(r"const META = (\{.*?\});", Path(work, "timeline.js").read_text()).group(1))
    inputs = ["-framerate", "30", "-i", str(frames / "f%05d.jpg"), "-i", narration_mp3]; fc = []; mix = ["[1:a]"]; idx = 2
    if music:
        inputs += ["-stream_loop", "-1", "-i", music]; fc.append(f"[{idx}:a]volume={music_vol},afade=t=out:st={max(0, dur - 4):.2f}:d=3.7[m]"); mix.append("[m]"); idx += 1
    if sfx_wav:
        inputs += ["-i", sfx_wav]; fc.append(f"[{idx}:a]volume=0.85[s]"); mix.append("[s]"); idx += 1
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:dropout_transition=0:normalize=0[a]")
    cmd = ["ffmpeg", "-y", "-v", "error"] + inputs + ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]",
           "-vf", f"scale={meta['w']}:{meta['h']}", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "224k", "-movflags", "+faststart", "-shortest", out_mp4]
    subprocess.run(cmd, check=True); print("encoded", out_mp4); return out_mp4


def audit(work: str, out_prefix: str, cols: int = 5):
    """Contact sheets: 2 frames per shot (25% and 75%), labelled with shot index and start time."""
    S = shots(work); frames = Path(work) / "render_frames"; cells = []
    for i, s in enumerate(S):
        for q in (0.25, 0.75):
            f = int((s["t0"] + (s["t1"] - s["t0"]) * q) * 30); p = frames / f"f{f:05d}.jpg"
            if p.exists(): cells.append((f"{i:02d} {s['t0']:.1f}s", p))
    im0 = Image.open(cells[0][1]); k = 384 / im0.width; cw, ch = 384, int(im0.height * k) + 22
    per = cols * 8; sheets = []
    for page in range(0, len(cells), per):
        chunk = cells[page:page + per]; rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * cw, rows * ch), (20, 20, 20)); d = ImageDraw.Draw(sheet)
        for j, (lab, p) in enumerate(chunk):
            im = Image.open(p).resize((cw, ch - 22)); x, y = (j % cols) * cw, (j // cols) * ch
            sheet.paste(im, (x, y)); d.text((x + 4, y + ch - 20), lab, fill=(230, 230, 230))
        out = f"{out_prefix}_{page // per + 1}.jpg"; sheet.save(out, quality=85); sheets.append(out)
    print("audit sheets:", sheets); return sheets
