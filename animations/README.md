# Recap animations

HTML/canvas sources of the project recap videos, in the Reef palette.

| Source | Video in `projects/` |
|---|---|
| `sq-nyu.html` | `what-can-we-predict-from-space/1-questions.mp4` |
| `methodology.html` | `what-can-we-predict-from-space/2-methodology.mp4` |
| `architecture.html` | `what-can-we-predict-from-space/3-architecture.mp4` and `neural-emulator-of-black-sea-dynamics/2-architecture.mp4` |
| `sq-uliege.html` | `neural-emulator-of-black-sea-dynamics/1-questions.mp4` |

Open a file in a browser to preview it (play, pause, scrub).

Render one to 4K MP4 (3840×2160, 30 fps, H.264 CRF 20), one at a time — parallel 4K renders run out of memory:

```bash
npm i -D playwright && npx playwright install chromium   # once
node animations/render.js sq-nyu 30                      # -> animations/out/sq-nyu.mp4
```

Then copy the MP4 into its project folder under its name above, list it in the `videos` of its `project.yaml`
(`file`, `source`), refresh its poster:
`ffmpeg -ss 12 -i projects/P/X.mp4 -vframes 1 -vf scale=1920:-1 -q:v 3 projects/P/X.jpg`,
and cut it into its stills, one per step (the end of each pause), used by the PDF in place of the video:

```bash
node animations/stills.js <project>    # -> projects/<project>/<video>/NN.jpg, listed under `stills` in project.yaml
```

A video whose pauses keep a small looping detail moving gets `same_px` in its entry (see `stills.js`); check the stills.

Style rules for the animations: no title baked in (the project slide carries it), top-right corner free for the university logo,
text 34 px at 1920 px, maths and labels `#457b9d`, lines `#1d3557`, text `#303030`,
1–2 key words per scene sentence in coral `#d0603f` (never in the left column).
