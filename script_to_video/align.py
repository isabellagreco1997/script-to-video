"""Word timestamps for the narration → words.json [[word, start, end], ...] and sentences.txt for planning.
Backends: mlx_whisper (Apple Silicon, fast) → faster_whisper → openai-whisper CLI."""
from __future__ import annotations
import json, shutil, subprocess
from pathlib import Path


def align(wav16: str, out_dir: str, model: str = "small") -> str:
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    words = None
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(wav16, path_or_hf_repo=f"mlx-community/whisper-{model}-mlx", language="en", word_timestamps=True)
        words = [[w["word"].strip(), round(w["start"], 2), round(w["end"], 2)] for s in r["segments"] for w in s.get("words", [])]
    except ImportError:
        try:
            from faster_whisper import WhisperModel
            segs, _ = WhisperModel(model).transcribe(wav16, language="en", word_timestamps=True)
            words = [[w.word.strip(), round(w.start, 2), round(w.end, 2)] for s in segs for w in (s.words or [])]
        except ImportError:
            if shutil.which("whisper"):
                subprocess.run(["whisper", wav16, "--model", model, "--language", "en", "--word_timestamps", "True",
                                "--output_format", "json", "--output_dir", str(out)], check=True)
                r = json.load(open(out / (Path(wav16).stem + ".json")))
                words = [[w["word"].strip(), round(w["start"], 2), round(w["end"], 2)] for s in r["segments"] for w in s.get("words", [])]
    if not words:
        raise SystemExit("no whisper backend: pip install mlx-whisper (Apple) or faster-whisper, or the openai-whisper CLI")
    json.dump(words, open(out / "words.json", "w"))
    # sentence view for shot planning
    lines, cur = [], []
    for w, s, e in words:
        cur.append((w, s, e))
        if w.endswith((".", "?", "!", ":")):
            lines.append(f"{cur[0][1]:7.2f}-{cur[-1][2]:7.2f}  " + " ".join(x[0] for x in cur)); cur = []
    if cur: lines.append(f"{cur[0][1]:7.2f}-{cur[-1][2]:7.2f}  " + " ".join(x[0] for x in cur))
    (out / "sentences.txt").write_text("\n".join(lines))
    print(f"aligned {len(words)} words, ends {words[-1][2]}s →", out / "words.json")
    return str(out / "words.json")
