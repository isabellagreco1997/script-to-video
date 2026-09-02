"""Narration with Kokoro (free, local, MIT). Sentence by sentence with natural gaps; paragraph gaps longer.

Model files (~330 MB) are fetched once into ~/.cache/script-to-video/kokoro/ by `script-to-video setup`,
or point SCRIPT_TO_VIDEO_KOKORO_DIR at a folder that already has kokoro-v1.0.onnx + voices-v1.0.bin.
Good voices: af_bella / af_heart (female), am_puck / am_michael / bm_george (male). Speed 0.9–1.1.
"""
from __future__ import annotations
import os, re, subprocess, wave
from pathlib import Path
import numpy as np

CACHE = Path(os.environ.get("SCRIPT_TO_VIDEO_KOKORO_DIR", Path.home() / ".cache/script-to-video/kokoro"))
URLS = {"kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
        "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"}


def setup():
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, url in URLS.items():
        p = CACHE / name
        if not p.exists():
            print("downloading", name); subprocess.run(["curl", "-L", "-o", str(p), url], check=True)
    print("kokoro ready in", CACHE)


def _model():
    from kokoro_onnx import Kokoro
    m, v = CACHE / "kokoro-v1.0.onnx", CACHE / "voices-v1.0.bin"
    if not (m.exists() and v.exists()):
        raise SystemExit(f"Kokoro model files missing in {CACHE}. Run: script-to-video setup")
    return Kokoro(str(m), str(v))


# pronunciation fixes that the model otherwise fluffs; extend per script with --say "X=Y"
DEFAULT_SAY = {"CLI": "C L I", "GPU": "G P U", "API": "A P I", "UI": "U I", "URL": "U R L", "SKILL.md": "skill dot M D"}


def trim_silence(a: np.ndarray, sr: int, thresh: float = 0.012, keep: float = 0.03) -> np.ndarray:
    """cut the dead air Kokoro leaves before and after every sentence (keeps `keep` seconds each side)."""
    loud = np.flatnonzero(np.abs(a) > thresh)
    if len(loud) == 0: return a
    k = int(sr * keep); return a[max(0, loud[0] - k): min(len(a), loud[-1] + k)]


def synthesize(script_path: str, out_wav: str, voice: str = "am_puck", speed: float = 1.06, say: dict | None = None,
               sentence_gap: float = 0.12, paragraph_gap: float = 0.30):
    """Tempo defaults are deliberately tight: no dead air between sentences, slightly faster than Kokoro's natural
    pace. A fast-paced clip is the point; loosen the gaps for a calm documentary voice."""
    text = Path(script_path).read_text()
    subs = dict(DEFAULT_SAY); subs.update(say or {})
    for k, v in subs.items():
        text = text.replace(k, v)
    m = _model(); sr = 24000; parts = []
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    for pi, para in enumerate(paras):
        for s in [s.strip() for s in re.split(r"(?<=[.!?:])\s+", para) if s.strip()]:
            samples, sr = m.create(s, voice=voice, speed=speed, lang="en-us")
            parts.append(trim_silence(np.asarray(samples, np.float32), sr)); parts.append(np.zeros(int(sr * sentence_gap), np.float32))
        parts.append(np.zeros(int(sr * paragraph_gap), np.float32))
        print(f"  para {pi + 1}/{len(paras)}", flush=True)
    audio = np.concatenate(parts); audio = audio / max(1e-6, np.abs(audio).max()) * 0.9
    w = wave.open(out_wav, "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((audio * 32767).astype(np.int16).tobytes()); w.close()
    base = Path(out_wav).with_suffix("")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", out_wav, "-ar", "16000", "-ac", "1", f"{base}16.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", out_wav, "-c:a", "libmp3lame", "-q:a", "2", f"{base}.mp3"], check=True)
    print("narration", round(len(audio) / sr, 1), "s →", out_wav)
    return len(audio) / sr
