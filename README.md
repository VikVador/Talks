<img src="assets/banner.svg" width="100%">

My talks, written in Markdown ([Marp](https://marp.app)) from the template of this repository and published by
GitHub Pages at each push. The `create-slides` skill of [VikVador/Claude](https://github.com/VikVador/Claude) makes
them.

## Talks

- 2026-11-13: [Progress meeting: Heimdall, Neptune and Poseidon](https://vikvador.github.io/Talks/talks/2026-11-13-progress-meeting/talk.html)
- 2026-11-08: [Heimdall: seven encoders trained, latents on Torch](https://vikvador.github.io/Talks/talks/2026-11-08-encoders/talk.html)
- 2026-11-08: [Poseidon: three changes for a better prior](https://vikvador.github.io/Talks/talks/2026-11-08-poseidon-three-changes/talk.html)

## Make a talk

| Folder or file   | What                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| `template.md`    | every slide rule on its own slide, in a yellow box: the reference for every deck                       |
| `palettes.md`    | the four palettes side by side                                                                         |
| `theme/`         | `base.css` (layout and slide classes), one CSS per palette, the Arimo font (SIL OFL), `video-controls.js` |
| `media/`         | shared media: the title animation (credit: Gilles Louppe) and its poster, the figure placeholder       |
| `projects/`      | one folder per project: recap videos, posters, stills (for the PDF) and `project.yaml` (title, university, logo, paper, code repository, videos) |
| `logos/`         | university logos of the project slides                                                                 |
| `team/`          | photos of the lab members and `people.yaml`, for the faces on the slides                               |
| `animations/`    | HTML sources of the recap videos, `render.js` (to MP4) and `stills.js` (one image per step)             |
| `scripts/`       | `build.sh` (HTML or PDF), `artifact.sh` (stage a deck as a Claude artifact), `publish.sh` (a draft to `talks/`), `video-stills.js` (the PDF shows the stills of a video) |
| `drafts/`        | the talks being written, `YYYY-MM-DD-name/` (`talk.md` and `figures/`), ignored by git                  |
| `talks/`         | the published talks, same layout, built by the `Pages` workflow at each push on `main`                 |
| `assets/`        | the banner of the READMEs and its generator                                                            |

```bash
npm install
bash scripts/build.sh template.md                            # the template, as template.html
bash scripts/build.sh drafts/YYYY-MM-DD-name/talk.md         # a draft, as talk.html next to it (--pdf for a PDF)
bash scripts/publish.sh drafts/YYYY-MM-DD-name "Talk name"   # move it to talks/, list it above, push main
```

A talk refers to the shared files as `../../media/…`, `../../projects/…`, `../../logos/…` and `../../team/…`: the
same paths in `drafts/` and in `talks/`, so publishing moves the folder and changes nothing in it.

## Change the template

The rules stay general ("whenever a deck presents experiments…", never "in a meeting deck…"). Change `template.md`
together with the theme. Every published talk is rebuilt with the latest theme at the next push on `main`: check them
after a change of the theme.
