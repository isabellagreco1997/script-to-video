---
name: script-to-video
description: Turn a script into a narrated, word-synced explainer video (16:9 YouTube or 9:16 Reels/Shorts) with a free local voice, images and articles from the web, clips, and browser-rendered motion. Use when asked to make an explainer, a fast-paced editorial video, a "Fireship-style" video, a reel from a script, or to animate a narration with pictures.
---

# script-to-video — playbook

Tools: `script_to_video/` (Python: Pillow, numpy; Kokoro TTS; whisper for word timings), `engine/` (Chrome-rendered stage + puppeteer renderer), ffmpeg. Read this whole file before starting a video. Every rule below was paid for with a bad cut.

## 0. What a good one looks like

* The screen is **black until the first key word**, then every element appears **the second its word is spoken**. Word-sync is the whole trick.
* **Pictures, not words.** Kinetic text on ~5% of the runtime, on the lines that are the thesis. If a line has no picture, find or make a picture, don't slam a word on it.
* **One image per idea, never reused.** The image must literally match what is being said.
* Cuts every 2–4 s, nothing over ~8 s, no two adjacent shots with the same camera move.
* **Deliberate black** on reflective lines. Video ends on plain black. No outro card.
* Music barely there (0.06–0.08), soft low booms only on flash cuts and black beats. No pops, no whooshes.

## 0b. The human test (do this before the shot plan, it is the shot plan)

This is for people, not for a model. A person watching has one question every second: *what am I looking at, and why?* Go through the script sentence by sentence and write, for each, what the viewer should **see**. Pass `see="..."` to `tl.shot()` so the plan prints with it.

* **A thing** (a hinge, a console, a person) → a clear photo of that exact thing, whole, centred.
* **A mechanism or a change** (the bolt slides, the pins lift, the map loops back) → a diagram, and show the **state change**: two or three frames of the same drawing (`latch_open` → `latch_closed`), not one static picture. If you can't find it, draw it in code; a plain drawing that explains beats a beautiful photo that doesn't.
* **A number** → a counter or the number on screen. **A name** → the face and a chip. **A comparison** → both things side by side, same scale.
* **A claim** ("nobody believed in it") → the source: the article, scrolled to the paragraph.
* **A feeling / the thesis** → black, or the single word.
* If the picture only makes sense *because* of the narration, it is the wrong picture. If a stranger could pause on it and guess the sentence, it is right.
* Never show the same image twice. `tl.write()` reports reuse; treat every hit as a bug.
* Whole images, centred, nothing bleeding off the edge: `tl.pic()` for layers, `tl.bg()` (contain + blurred backdrop) for full-frame stills. Use `fit="cover"` only for wide photos and clips that can lose their edges. Don't crop into a small image; a 600 px photo blown up to 1080p is a glitch.
* A continuation (same image, next shot, new camera move) uses `anim="none"`. A fade or slide on an image that is already on screen reads as a flicker.
* Text appears within a tenth of a second of its word, and it is big: slams ≥ 150 px, chips ≥ 56 px. A word the viewer can't read is worse than no word.
* Watch it as a viewer, at speed, once, before showing anyone. The dense sheet (a frame every half second) catches what the two-per-shot audit misses: a pop-in that flashes, a diagram with its labels cut off, a photo held for five seconds.

## 1. Script

Write for the ear: short sentences, one idea each, numbers as words, no parentheses. Spell out things the voice will fluff (`C L I`, `G P U`). Keep the tone dry and specific; a joke must survive with no music under it. End with the thesis, then stop. 150 words ≈ 1 minute.

## 2. Voice

`script-to-video voice script.txt work/narration.wav --voice am_puck` (male) / `af_bella` (female). Kokoro is free, local, MIT. Sentence gaps 0.28 s, paragraph gaps 0.55 s, normalised to −1 dB. Listen to a paragraph before committing to a voice. If the user has their own recording, use that instead, the pipeline doesn't care.

## 3. Align

`script-to-video align work/narration16.wav work/` → `words.json` + `sentences.txt`. Read `sentences.txt` before planning: every shot is anchored to a phrase in there. Whisper misspells things ("Medium" for median, "3" for three); anchors accept alternatives: `"three|3"`.

## 4. Shot plan (on paper, before code)

For every sentence: one visual. Sources, in order of preference:
1. **A clip** (screen recording, gameplay, a demo) → `assets.clip_frames()`.
2. **A real photo or diagram**: Wikimedia Commons via `assets.commons_fetch()` (licence recorded in a manifest, write the attribution file for the description).
3. **An article/page screenshot**: `assets.capture()` (scroll to the paragraph, then `zoomTo` into it in the timeline).
4. **A made image**: `assets.text_card()` for terminal output or a quote, a chart drawn with Pillow, a diagram.
5. **A word** — last resort, for the thesis line.

Plan the joke beats with the user: memes and GIFs are their picks, uncaptioned (the narration is the caption), full-bleed with `fit:"contain"` and a white flash on the cut.

## 5. Timeline

```python
tl = Timeline("work/words.json", w=1920, h=1080)          # or w=1080, h=1920 for reels
tl.shot(0.0)                                                # black until the first word
tl.shot("hinge", bg=tl.bg("hinge.jpg", kb="zin"))           # shot starts when "hinge" is spoken
tl.shot("pin tumbler", layers=[tl.I("lock_diagram.png", 200, 80, 1500, anim="slideU", plain=True,
                                     zoomTo=1.6, origin="60% 40%")])
tl.shot("Linus Yale", layers=[tl.I("yale.jpg", 700, 100, 520, rot=-3), tl.C("LINUS YALE, 1861", 720, 900, i=tl.rel("1861"))])
tl.shot("a shape test", layers=[tl.T("A SHAPE TEST.", 380, 420, fs=170, rot=-2, i=tl.rel("shape test"))])
tl.write("work/timeline.js")
```

* **Two cursors.** `shot(phrase)` moves the search cursor forward (monotonic). `tl.at()` / `tl.rel()` look up from the current shot without moving it. Using one cursor for both once matched a repeated word 100 s later and froze two shots.
* Layer `in` = seconds after the shot start; `tl.rel("word")` gives it. Elements appear on their word. `rel()` returns a marker that `shot()` resolves inside the shot it lands in (the layers are built before `shot()` runs, so a number computed early would be relative to the previous shot and the text lands a second late).
* Camera moves: `kb` = zin / zout / panL / panR / panD / panU / punch / still. `zoomTo` + `origin` = slow push into a paragraph or a detail (never highlight boxes).
* Text: white Impact, thick black stroke, ±2–4° rotation, pop-in with overshoot. Chips: plain black rectangle, white text, for names/dates/sources.
* Clips: `tl.clip("name")` as background, `tl.G("name", x, y, w)` as a layer. Frames are pre-extracted, deterministic. A state sequence (open → closed) gets `"hold": true` in gifmeta so it plays once and stays on the last frame instead of looping.
* `write()` prints the word-slam share, shots over 8 s, missing anchors and order problems. Fix all four before rendering.

## 6. Render, sound, encode, audit

`script-to-video build build.py` does: render → sfx → encode → audit. Or step by step. Partial re-renders: `render work/ --start F --end F` (frame = t × 30), then re-encode.

**Audit before showing anyone**: the contact sheets (2 frames per shot). Look for: frozen images across many shots (a sync bug), overlapping words, an image cut off by the stage edge, a face cropped, a chip over a HUD, a picture too small to read, the same image twice.

**Never overwrite a delivered mp4.** Bump the version. Overwriting a file someone has open kills their playback mid-video and they'll report "it stopped at 1:09".

## 7. Gotchas

* Tall images in a 16:9 stage: fit to height first (w = img_w × 1040 / img_h), then zoom. A tall image at full width gets its bottom cut off.
* Wide text rows overlap: measure. Three words at 150 px need ~1900 px. Drop to 130 and spread.
* `ffmpeg -y` always; without it a chained render hangs on an overwrite prompt.
* Chrome file:// is fine for the stage, but the renderer serves the work dir over http on port 8722 so gif frames preload.
* Puppeteer captures ~8–20 fps in real time; record the real fps into GIFMETA for clips captured live.
* Wikimedia: use curl with a User-Agent; python's urllib has broken certs on some Macs. Record licences.
* Disk: 9,000 JPEG frames ≈ 1.5 GB. Delete superseded render_frames folders, keep the current one for partial re-renders.
* When the user says "it doesn't hit" without specifics, check in order: sound design, pacing, image specificity, sameness of animation.
* When the user says "too many words": they are right. Replace slams with pictures until the share is ≤ 5–10%.
