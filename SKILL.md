---
name: script-to-video
description: Turn a script into a narrated, word-synced explainer video (16:9 YouTube or 9:16 Reels/Shorts) with a free local voice, images and articles from the web, clips, and browser-rendered motion. Use when asked to make an explainer, a fast-paced editorial video, a "Fireship-style" video, a reel from a script, or to animate a narration with pictures.
---

# script-to-video — playbook

Tools: `script_to_video/` (Python: Pillow, numpy; Kokoro TTS; whisper for word timings), `engine/` (Chrome-rendered stage + puppeteer renderer), ffmpeg. Read this whole file before starting a video. Every rule below was paid for with a bad cut.

## 0a. Expectations

The first build is a draft the user directs, not a deliverable. Say so when you hand it over, then ask for notes on style, assets, timing and alignment, and iterate: swap images, change a shot to a diagram, nudge an anchor, re-render just the frames that changed. Two or three rounds is normal. Never present a first render as final.

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
* **Protection padding depends on the format.** 16:9 (YouTube): every image and illustration sits whole and centred with a margin, over a blurred copy of itself; nothing touches the edge. That is the default for `tl.pic()` (86% safe box) and `tl.bg()` (contain + backdrop). Use `fit="cover"` only for wide photos and clips that can lose their edges. 9:16 (Reels, Shorts, TikTok): the opposite. No padding, images fill the phone screen edge to edge; `tl.bg()` defaults to cover and `tl.pic()` to the full width. A letterboxed picture on a phone looks like a mistake. The Timeline picks the mode from its size (`h > w` = portrait) and prints it in the report; override per shot with `fit=` or `safe=`. A slow `zoomTo` push into a detail (a row of the dump, one frame of a sheet) is deliberate and welcome; a wide strip or a tall column left small in the middle of the frame for ten seconds is not. Don't crop into a small image in either mode; a 600 px photo blown up to 1080p is a glitch.
* **No black holes between shots.** A cut that drops to black for a quarter second while the next image fades in reads as a glitch. An image-only shot automatically gets its own blurred copy as a backdrop from frame one (`backdrop=False` on the shot to opt out), so every cut lands on something. Cuts are hard, moves are soft: slide/pop in 0.3 s, never a long fade on a new image.
* A continuation (same image, next shot, new camera move) uses `anim="none"`. The move then **continues** instead of restarting: a push that ended at 1.6× carries on from 1.6×, a new origin is glided to, a background `zin` on the same still keeps pushing. `write()` does this automatically; a zoom that snaps back to 1× on the same picture every few seconds is a tell. A fade or slide on an image that is already on screen reads as a flicker.
* Text appears within a tenth of a second of its word, and it is big: slams ≥ 150 px, chips ≥ 56 px. A word the viewer can't read is worse than no word.
* **The sentence test, shot by shot.** Put the transcript next to the dense sheet and, for every sentence, answer four questions out loud: *Is the thing I am naming on screen right now?* (she says "she jumps": is the character in frame, jumping, not the level scenery). *Is it there at the moment the word is said, not two seconds later?* *Is it whole: not cropped by a push, not hidden at the edge of a clip, not too small to see?* *Would someone with the sound off guess roughly what this sentence is about?* One "no" is a bug, fix it before anyone watches. Miscast pictures (a lock-picking diagram for "the lock", the good walk for "the walk looked wrong", the wrong frames of a clip) are the most common way a video stops making sense, and no report catches them; only this pass does.
* Watch it as a viewer, at speed, once, before showing anyone. The dense sheet (a frame every half second) catches what the two-per-shot audit misses: a pop-in that flashes, a diagram with its labels cut off, a photo held for five seconds.

## 0c. Fun behaviours (use one or two per video, on the lines that earn it)

* **Word by word.** `tl.words("IT FELL APART.", ins=["@everything", "@falling", "@apart"])` puts the line dead centre and pops each word on its own spoken word. No x/y maths: the engine centres the whole line.
* **The hit.** `tl.shot("the animation", shake="@apart", layers=[...])` jolts the entire picture (background and all) on that word, decaying over half a second. Pair it with the last word of a word-by-word line, a "YOU DIED", a number landing. Never on an ordinary cut.
* **Counter** counting up live to the number as it is said; **flash** (`flash=0`) on a punch cut; **replace-slams** for escalation ("1 YEAR" then "WEEKS."); a **chip** under a face.
* These are punctuation. Three of them in a minute and the viewer stops feeling any of them.

## 1. Script

Write for the ear: short sentences, one idea each, numbers as words, no parentheses. Spell out things the voice will fluff (`C L I`, `G P U`). Keep the tone dry and specific; a joke must survive with no music under it. End with the thesis, then stop. 150 words ≈ 1 minute.

## 1a. Retention (the shape that keeps people watching)

YouTube tests every upload on a small audience first; if early retention is poor the test stops. The steepest drop in almost every retention curve is between second 10 and 20, and 20 to 35% of viewers are gone by second 30. So the opening is not an intro, it is the gate. Rules, in order:

**The first 30 seconds**
1. **0 to 5 s: result first.** Open on the finished thing (the game running, the render done, the number on screen), not the title card, not the history, not "hey guys". A cold open of the best moment works the same way.
2. **5 to 15 s: the specific promise.** One concrete claim with a number or a name in it: "it took thirteen tries to make her walk" beats "there were some problems". Count the specifics in the first 15 seconds; fewer than three is a weak hook, four or more is strong.
3. **15 to 30 s: the open loop.** Plant one question the body will close (the fail you'll explain, the thing that broke). Then start.
4. **Never:** a greeting, a logo bumper, "in this video we're going to", an apology or disclaimer, a like-and-subscribe before any value, more than 10 seconds of setup.

**The rest**
5. **Pattern interrupt every 20 to 40 seconds.** A cut, a before/after, a fail clip, a number card. A devlog's compares are made for this; a flat stretch of talking head is where the second drop happens.
6. **Teaser at the start AND payoff at the end.** Showing the finished result only at the end makes the viewer wait the whole runtime for what the title promised. Show it in the first five seconds as proof, tell the story, then give the full tour at the end as the payoff.
7. **Chapters.** Every beat in the shot plan is a chapter marker; skippers still count as watch time.
8. **End on the payoff, then stop.** The link on screen and said aloud, a few seconds of the result, no outro talk.

**Test the opening before recording:** read only the first 15 seconds of the script; if no specific value claim has landed, rewrite. Read it with no visuals; if it needs the b-roll to make sense, it is brittle.

Sources: PrePublish, "The first 30 seconds of a YouTube video" (2025); 1of10, "How to hook viewers in the first 30 seconds" (2025); Narration Box, "Why viewers drop off after 30 seconds" (2026).

## 2. Voice

`script-to-video voice script.txt work/narration.wav --voice am_puck` (male) / `af_bella` (female). Kokoro is free, local, MIT. **Tempo is part of the edit**: the dead air Kokoro leaves before and after every sentence is trimmed, sentences are 0.12 s apart, paragraphs 0.30 s, speed 1.06. That is what makes the clip feel fast-paced; a picture per idea over a slow, gappy voice still drags. Loosen (`--gap 0.3 --pgap 0.6 --speed 1.0`) only for a calm, documentary read. If the user brings their own recording, run it through a silence trim too (ffmpeg `silenceremove`, or cut the gaps in the timeline by shot). Normalised to −1 dB. Listen to a paragraph before committing to a voice. If the user has their own recording, use that instead, the pipeline doesn't care.

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
* **A clip must show the moment the words describe.** `tl.clip("play1", offset=1.0)` starts the clip 1 s in, so "when she jumps" lands on the jump, not on whatever is at the top of the file. Look at the clip's contact sheet and pick the second. If the subject is near the edge of the frame, `kb="still"`: a contained clip is never cropped by more than 6%, but 6% is enough to lose a sprite at the border.
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
* When the user says "transitions look glitchy": look for cuts to black between shots (missing backdrop), a fade on an image already on screen (use `anim="none"`), a clip that loops instead of holding, a pop on a huge image (use slideU), or a flash on an ordinary cut.
* When the user says "too many words": they are right. Replace slams with pictures until the share is ≤ 5–10%.
