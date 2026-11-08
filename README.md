<img src="assets/banner.svg" width="100%">

The `template` branch holds everything needed to make my talks: a Markdown template ([Marp](https://marp.app)), its
theme and palettes, the projects of the thesis with their recap videos, and the scripts. The `create-slides` skill of
[VikVador/Claude](https://github.com/VikVador/Claude) reads it. The `main` branch holds only the published talks.

---

| Folder or file   | What                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------ |
| `template.md`    | every slide rule on its own slide, in a yellow box: the reference for every deck                       |
| `palettes.md`    | the four palettes side by side                                                                         |
| `theme/`         | `base.css` (layout and slide classes), one CSS per palette, the Arimo font (SIL OFL), `video-controls.js` |
| `media/`         | shared media: the title animation (credit: Gilles Louppe) and its poster, the figure placeholder       |
| `projects/`      | one folder per project: recap videos, posters, stills (for the PDF) and `project.yaml`                  |
| `logos/`         | university logos of the project slides                                                                 |
| `team/`          | photos of the lab members and `people.yaml`, for the faces on the slides                               |
| `animations/`    | HTML sources of the recap videos, `render.js` (to MP4) and `stills.js` (one image per step)             |
| `scripts/`       | `build.sh` (HTML or PDF), `artifact.sh` (stage a deck as a Claude artifact), `publish.sh` (to `main`), `video-stills.js` (the PDF shows the stills of a video) |
| `assets/`        | the banner of the READMEs and its generator                                                            |

## Make a talk

```bash
npm install
bash scripts/build.sh template.md                          # the template, as template.html
bash scripts/build.sh talks/YYYY-MM-DD-name/talk.md --pdf  # a talk, as a PDF
bash scripts/publish.sh talks/YYYY-MM-DD-name "Talk name"  # publish it on main and GitHub Pages
```

A talk is drafted in `talks/YYYY-MM-DD-name/` (`talk.md` and `figures/`), ignored by git on this branch. It refers to
the shared files as `../../media/…`, `../../projects/…` and `../../logos/…`: the same paths on both branches, so
`publish.sh` copies the talk and the shared files it uses to `main` unchanged. The workflow of `main` builds every
talk with the theme of this branch.

## Change the template

The rules stay general ("whenever a deck presents experiments…", never "in a meeting deck…"). Change `template.md`
together with the theme. A published talk is rebuilt with the latest theme at the next push on `main`: check the
published talks after a change of the theme.
