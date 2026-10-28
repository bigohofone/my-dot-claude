---
name: paper-figure
description: Style rules for academic paper figures made with matplotlib or seaborn (size, fonts, colors, axes, legends, saving), plus a required delivery step - a `figures/` folder in the user's project holds a copy of the style files and `figures.ipynb`, where every figure is one self-contained cell, with a paper-style caption above it, so the user can run, edit, and re-export it (PDF/PNG) themselves. Always use this skill when creating or editing any figure, plot, graph, chart, heatmap, or visualization intended for a paper, even if no venue (ICML, CVPR, ACL, NeurIPS, ICLR) is mentioned, and even if the user asks only for the plotting code.
---

# Paper Figure Rules

Apply every rule unless the user says otherwise. Order: size → style → plot type → color → legend → save → caption → notebook → check. A figure is not delivered until its cell is in the notebook with its caption and has run.

## 1. Size

### Width

| Venue | Single column | 1.5 column | Double column |
|---|---|---|---|
| ICML | 3.25 in | 5.0625 in | 6.75 in |
| CVPR | 3.25 in | 5.15625 in | 6.875 in |
| ACL (ARR) | 3 in | 4.6875 in | 6.25 in |
| NeurIPS | – | – | 5.5 in |
| ICLR | – | – | 5.5 in |

- No venue: ICML single column. Venue without column type: single column (NeurIPS/ICLR: 5.5 in).
- 1.5 column is 0.75 × double column: a `figure*` that does not need the full text width. Use it only when the user asks or when single column is too narrow and double column leaves the content sparse.

### Grid and panel aspect

Choose the grid (rows × cols) and the panel aspect together, by judgment, for what this data needs to show. Use 4:3 (0.75) unless the content needs another aspect. The aspect (width : height) is per panel, not for the whole figure, and is one of four:

| Aspect | `aspect=` | Typical fit |
|---|---|---|
| 8 : 3 | 0.375 | a single panel at double-column width (curves, bars) |
| 4 : 3 | 0.75 | curves, bars, histograms (default) |
| 1 : 1 | 1.0 | heatmap, confusion matrix, embedding |
| 3 : 4 | 1.333 | content that is taller than wide (e.g. many horizontal bars) |

- Ask what the reader must see: slopes and gaps between curves need height, many x categories need width, matrices need square cells.
- Compare a few layouts before choosing. E.g. two line plots in one column: side by side gives ~1.3 in-wide panels that flatten the curves; stacked 2×1 at 0.75 gives each panel the full width and enough height, so it is better.
- Spread panels evenly; turn off unused cells.
- Turn on `sharex` / `sharey` when panels plot the same quantity on that axis (`plt.subplots(..., sharex=True, sharey=True)`); inner tick labels hide automatically, and axis labels go on the outer panels only.
- After rendering, if curves look flattened or labels crowd, change the grid or aspect and re-render.

### Height

Don't compute it. Create the figure at the target width with any height, draw everything (labels, legend, colorbar), then call `fit_height` last. It changes only the height so every panel matches the chosen aspect.

```python
fig, axes = plt.subplots(1, 2, figsize=(3.25, 2))  # after the §2 setup
...  # plot, labels, fig.legend, colorbar
fit_height(fig, axes, aspect=0.75)
fig.savefig(...)  # never bbox_inches="tight"
```

- `ax` may be one Axes, an array, a list, or the `subplot_mosaic` dict; hidden cells and colorbars are skipped.
- `ValueError` (fixed aspect): use `imshow(..., aspect="auto")` instead of `set_aspect`.
- "different widths" warning: give all panels the same width (no spanning cells or `width_ratios`), or accept and tell the user.

## 2. Base style

Always start with the bundled style, copied into the project's `figures/` (§9); don't set or override its rcParams by hand. In the notebook, which runs from `figures/`:

```python
import tol_colors as tc
from paper import fit_height  # importing paper also registers the bundled Inter font
plt.style.use("paper.mplstyle")
```

It needs `tol-colors` (Paul Tol's own palette package; Python 3.10+) in the project's Python; if it is missing, tell the user and ask before installing it.

It sets fonts (Inter for all text and math, STIX Sans for math symbols Inter lacks: labels 9, ticks 8, legend 7, titles 10 pt bold), left+bottom spines, 0.5 pt axes and ticks, horizontal #DDDDDD gridlines, lines and markers, the `bright` color cycle and `tol.iridescent` colormap (§4), legend frame defaults, constrained layout, 300 dpi, and fonttype 42 (PDF text stays text with Inter embedded, so it renders the same anywhere).

- If text renders in DejaVu Sans, `paper` was not imported before plotting; fix that.
- No figure title. Panel identifiers (dataset, setting) go in the axes title, never as text inside the axes.
- Subsampled markers: at x major tick positions (mask by x value, not index step).
- Don't set axis limits exactly at the first or last data point (e.g. `set_xlim(0, 1)` for x in [0, 1]); markers there get cut in half. Keep the default margin.
- Reference lines (max/min, regression, threshold): color of related data, `--`, `alpha` 0.5, behind data.
- Text tick labels (model names, keywords, categories): `fontsize=7`, one step below the 8 pt numeric ticks.
- Category axes (bar charts, text tick labels): no tick marks, `ax.tick_params(axis="x", length=0)` (or `axis="y"` for horizontal bars); the label under each bar already marks it. With shared axes, apply it to every panel, including those whose labels are hidden.
- Value labels (numbers on bars or points, e.g. `bar_label`): `fontsize=6`; the proposed method's ("Ours") labels bold.

## 3. Plot-type overrides

| Plot type | Frame | Gridlines | Other |
|---|---|---|---|
| Line | Base | Horizontal | – |
| Vertical bar, histogram | Base | Horizontal | `linewidth=0` (no outline) |
| Horizontal bar | Base | Vertical | `linewidth=0` (no outline) |
| Scatter | Full | Horizontal | `edgecolors="none"`, `alpha` 0.5 |
| Embedding (t-SNE, UMAP) | Full | None | No ticks; markers as scatter |
| Heatmap, confusion matrix | Full | None | No tick marks; cell text by cell luminance: `"white" if np.dot(im.cmap(im.norm(v))[:3], [0.299, 0.587, 0.114]) < 0.5 else "black"` |

## 4. Color

Paul Tol's color-blind-safe schemes, from `tol_colors` (imported as `tc`). Pick colors by name from a set (`cset = tc.colorsets["bright"]`, then `cset.red`) and colormaps by `cmap="tol.<name>"`.

### Qualitative sets

| Set | Colors (in order) | Use |
|---|---|---|
| `bright` | blue, red, green, yellow, cyan, purple, grey | Default |
| `vibrant` | orange, blue, cyan, magenta, red, teal, grey | Same use as bright, more saturated; user's choice |
| `muted` | rose, indigo, sand, green, cyan, wine, teal, olive, purple, pale_grey | 7–9 series |
| `high_contrast` | blue, yellow, red (+ black, white) | ≤ 3 series that must survive grayscale printing |
| `medium_contrast` | light/dark blue, yellow, red (+ black, white) | Paired series, e.g. train/test per method |
| `light` | light_blue, orange, light_yellow, pink, light_cyan, mint, pear, olive, pale_grey | Filled areas with text on top |
| `pale`, `dark` | pale_* / dark_* blue, red, green, yellow, cyan, grey | Backgrounds / text only |

- Use `bright` unless the user names another set or the case above fits better. One set per figure; the same set across a paper.

### Rules

| Case | Color |
|---|---|
| Categorical | the set's colors in order, skipping grey, black and white; never reorder |
| "Ours" | the set's red (`muted`: rose); others take the rest in order |
| Neutral / de-emphasized | the set's grey (`pale_grey`; `high_contrast`: `tc.colorsets["bright"].grey`) |
| Grouped (sizes, sweeps) | one set color per group; within group blend with white at 40 / 70 / 100 %, light → dark |
| Sequential | `tol.iridescent` (style default); also `tol.YlOrBr`, `tol.WhOrBr`, `tol.incandescent` |
| Signed | `tol.sunset`, centered at 0 (symmetric `vmin/vmax` or `TwoSlopeNorm`); also `tol.BuRd`, `tol.PRGn`, `tol.nightfall` |

- Few levels (e.g. a 5-step heatmap): the `_discrete` version of the map (`tol.sunset_discrete`).

- If series could be confused (grayscale, many series, shades), also vary marker or line style.
- Emphasis, only when the user names what to emphasize (bars, lines, any chart): that series keeps color (the set's red) and every other series is the same gray (the set's grey, also for bands and markers). If several gray lines must be told apart, vary line style or marker, not shade. Without such a request, use the set colors above.
- Bar charts: name the bars on the x-axis instead of in a legend; for several groups (benchmarks, datasets), use one panel per group, titled with the group, rather than grouped bars.
- Never use fill patterns (hatching, dots, `hatch=`) to tell series apart; use color only.

## 5. Legend

| Case | Rule |
|---|---|
| Single panel | inside, explicit `loc` (never `"best"`) |
| Multiple panels, same series | one shared `fig.legend`, `loc="outside upper center"` (above the panels), `ncol` = entries; no per-panel legends |
| Multiple panels, different series per panel | one legend per panel, above its title: `ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1), borderaxespad=2, frameon=False, fontsize=8)`; never merge them into one legend |
| Grouped series | rows = groups, columns = variants |

- Inside legends use the style defaults (7 pt). Outside legends add `frameon=False, borderaxespad=0, fontsize=8`.

## 6. Save

| Item | Rule |
|---|---|
| Files | `{id}.pdf` + `{id}.png`, id in kebab-case |
| PDF fonts | Embedded TrueType only (Type 1 is also accepted); never Type 3 or unembedded fonts, which venues reject. The style's `pdf.fonttype: 42` guarantees this: never override it, and never turn text into paths or images. |
| Folder | the project's `figures/` (§9); save with relative paths `"{id}.pdf"` |
| LaTeX (one line in reply) | single column → `figure`, `width=\columnwidth`; 1.5 column → `figure*`, `width=0.75\textwidth`; double → `figure*`, `width=\textwidth` |

## 7. Check

After the notebook cell has run (§9), look at the PNG; fix the cell and re-run if any fails:

- Width equals target; `fit_height` raised no warning.
- PDF fonts are embedded TrueType: `pdffonts {id}.pdf` lists every font as `CID TrueType` with emb `yes` (without pdffonts: `grep -ac /Type3 {id}.pdf` prints 0).
- No clipped or overlapping text; legend covers no data or labels.
- Panel spacing visible; subsampled markers on ticks.
- Font is Inter, not DejaVu.
- Colors follow §4.
- Caption matches the figure.

## 8. Caption

Written as it appears under the figure in the paper; must stand alone. Paper's language (default English).

| Part | Content |
|---|---|
| Lead (bold) | What the figure shows, one short sentence |
| Reading guide | Encodings not obvious from axes/legend: error bars/bands (±1 std over N seeds), dashed lines, panels (by title), log scale |
| Takeaway | Main observation, with a number computed from the plotted data |

- 2–4 sentences, present tense. No "This figure shows…", no restating legend or axis labels.
- Unknown details → `[TODO: …]`, report in reply. Never invent.
- Plain text with Unicode (±, ×, α), no `$...$`.

> **Figure 1: Test accuracy versus training steps on CIFAR-10.** Shaded bands show ±1 std over 3 seeds; the dashed line marks the best baseline's final accuracy. Ours reaches it after 12k steps, 2.1× faster.

## 9. Notebook (required)

All figure work happens in `figures/` at the root of the project the user is working in (e.g. the paper repo), even for a single figure or a script-only request. The user runs, edits, and re-exports figures from there, so it must work without this skill installed and each cell must be plain, readable code they can change.

```
figures/
├── paper.py, paper.mplstyle, Inter-*.ttf, Inter-LICENSE.txt   # copied from {skill-dir}/assets/
├── figures.ipynb
└── {id}.pdf, {id}.png
```

- `{skill-dir}` is this skill's base directory. Copy with `cp -n {skill-dir}/assets/{paper.py,paper.mplstyle,Inter-*} figures/` so copies already in the project are kept.
- Never reference `{skill-dir}` from the notebook; it uses only the copies in `figures/`.

| Cell | Content |
|---|---|
| First (code, once) | Setup: `%matplotlib inline`, `%config InlineBackend.print_figure_kwargs = {"bbox_inches": None}` (inline preview at the saved size, not cropped), `%config InlineBackend.figure_formats = ["retina"]` (sharp preview; the inline default is 100 dpi), imports, the §2 setup |
| Per figure (markdown) | `## {id}` then the §8 caption |
| Per figure (code) | Everything for that figure: load data, plot, `fit_height`, save `{id}.pdf` + `{id}.png`, `plt.show()` |

- Each figure cell runs on its own after the setup cell: no variables shared between figure cells.
- Load data from the project's result files (paths relative to `figures/`) when they exist; write numbers inline only when there is no file.
- Same `id` replaces its two cells; a new id appends two cells at the end. Edit with `NotebookEdit`; create `figures/figures.ipynb` with `Write` if it does not exist.
- Run it with the project's Python: `jupyter nbconvert --to notebook --execute --inplace figures/figures.ipynb` (it runs with `figures/` as the working directory). The outputs stay in the notebook and the PDF/PNG land in `figures/`. If jupyter is missing, tell the user and ask before installing it.
- **Reply**: changes, LaTeX line, any `[TODO]`.
