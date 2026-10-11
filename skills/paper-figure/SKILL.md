---
name: paper-figure
description: Style rules for academic paper figures made with matplotlib or seaborn (size, fonts, colors, axes, legends, saving), plus a required delivery step - every figure gets a paper-style caption and is published to a `{project-name}-figures` artifact gallery where it can be previewed and downloaded (PDF/PNG) with a copy-caption button. Always use this skill when creating or editing any figure, plot, graph, chart, heatmap, or visualization intended for a paper, even if no venue (ICML, CVPR, ACL, NeurIPS, ICLR) is mentioned, and even if the user asks only for the plotting code.
---

# Paper Figure Rules

Apply every rule unless the user says otherwise. Order: size → style → plot type → color → legend → save → check → caption → gallery. A figure is not delivered until it is in the gallery with its caption.

## 1. Size

### Width

| Venue | Single column | Double column |
|---|---|---|
| ICML | 3.25 in | 6.75 in |
| CVPR | 3.25 in | 6.875 in |
| ACL (ARR) | 3 in | 6.25 in |
| NeurIPS | – | 5.5 in |
| ICLR | – | 5.5 in |

- No venue: ICML single column. Venue without column type: single column (NeurIPS/ICLR: 5.5 in).

### Grid

- One row if every panel is ≥ 1 in wide; otherwise add rows, spread evenly (4 → 2×2). Turn off unused cells.

### Height (inches; compute, don't guess)

| Step | Formula |
|---|---|
| Usable width | figure width − 0.8 if a colorbar is attached |
| Panel width | (usable width − 0.35 − 0.25 × (ncols − 1)) / ncols |
| Panel height | panel width × 0.618 (1.0 for heatmap, confusion matrix, embedding) |
| Figure height | nrows × (panel height + 0.35 + 0.25 if titled) + 0.05 + 0.2 × outside legend rows |

### Layout

| Setting | Value |
|---|---|
| `layout` | `"constrained"`, `w_pad = h_pad = 0.01` |
| `wspace` | 0.25 × (ncols − 1) / figure width |
| `hspace` | 0.25 × (nrows − 1) / figure height |
| `bbox_inches` | never set |

## 2. Base style

### Fonts

| Setting | Value |
|---|---|
| `font.family` | serif |
| `font.serif` | Times New Roman, TeX Gyre Termes, Nimbus Roman, STIX Two Text, DejaVu Serif (tell the user if DejaVu is used) |
| `mathtext.fontset` | stix |

### Font sizes (pt)

| Element | rcParam | Size |
|---|---|---|
| Base / annotations | `font.size` | 9 |
| Axis labels | `axes.labelsize` | 9 |
| Tick labels | `xtick.labelsize`, `ytick.labelsize` | 8 |
| Legend | `legend.fontsize` | 8 |
| Panel title | `axes.titlesize` | 12 (`titleweight` normal, `titlepad` 3) |

- No figure title. Panel identifiers (dataset, setting) go in the axes title, never as text inside the axes.

### Axes

| Setting | Value |
|---|---|
| Spines | left and bottom only |
| `axes.linewidth` | 0.5 |
| Tick width (x, y, major, minor) | 0.5 |
| `axes.grid` / `axes.grid.axis` | True / y |
| `axes.axisbelow` | True |
| `grid.color` / `grid.linewidth` | #DDDDDD / 0.5 |

### Lines and markers

| Setting | Value |
|---|---|
| `lines.linewidth` | 1.0 |
| `lines.markersize` | 4 |
| `lines.markeredgecolor` | #FFFFFF |
| `lines.markeredgewidth` | 0.5 |
| Subsampled markers | at x major tick positions (mask by x value, not index step) |
| Reference lines (max/min, regression, threshold) | color of related data, `--`, `alpha` 0.5, behind data |

## 3. Plot-type overrides

| Plot type | Frame | Gridlines | Other |
|---|---|---|---|
| Line | Base | Horizontal | – |
| Vertical bar, histogram | Base | Horizontal | Bar edge black 0.5; `hatch.linewidth` 0.5 |
| Horizontal bar | Base | Vertical | Bar edge black 0.5 |
| Scatter | Full | Horizontal | `edgecolors="none"`, `alpha` 0.5 |
| Embedding (t-SNE, UMAP) | Full | None | No ticks; markers as scatter |
| Heatmap, confusion matrix | Full | None | No tick marks; colorbar outline 0.5; cell text white if \|v\| > 0.6 × max, else black |

## 4. Color

### Okabe-Ito cycle (this order)

| # | Name | Hex |
|---|---|---|
| O1 | orange | #E69F00 |
| O2 | sky blue | #56B4E9 |
| O3 | bluish green | #009E73 |
| O4 | yellow | #F0E442 |
| O5 | blue | #0072B2 |
| O6 | vermillion | #D55E00 |
| O7 | reddish purple | #CC79A7 |
| O8 | gray | #999999 |
| O9 | black | #000000 |

```python
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=[
    "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2",
    "#D55E00", "#CC79A7", "#999999", "#000000"])
```

### Rules

| Case | Color |
|---|---|
| Categorical | O1 → O9 in order; never reorder or skip |
| "Ours" | O6; others take the rest in order |
| Neutral / de-emphasized | O8; drop O8 from the cycle for the rest |
| Grouped (sizes, sweeps) | one cycle color per group; within group blend with white at 40 / 70 / 100 %, light → dark |
| Sequential | `viridis` |
| Signed | O5 → white → O6, centered at 0 (symmetric `vmin/vmax` or `TwoSlopeNorm`) |

- If series could be confused (grayscale, many series, shades), also vary marker or line style.

## 5. Legend

| Case | Rule |
|---|---|
| Single panel | inside, explicit `loc` (never `"best"`) |
| Multiple panels | one shared `fig.legend`, `loc="outside lower center"`, `ncol` = entries; no per-panel legends |
| Grouped series | rows = groups, columns = variants |

| Setting | All | Inside | Outside |
|---|---|---|---|
| `handlelength` / `handletextpad` | 1.5 / 0.25 | | |
| `columnspacing` / `labelspacing` | 1.0 / 0.25 | | |
| Frame | | square (`fancybox` False), edge #DDDDDD, width 0.5, fill white, `framealpha` 1 | none |
| `borderpad` | | 0.5 | 0.5 |
| `borderaxespad` | | 0.75 | 0 |

## 6. Save

| Item | Rule |
|---|---|
| Files | `{id}.pdf` + `{id}.png` (300 dpi), id in kebab-case |
| Folder | `/mnt/user-data/outputs/{project-name}-figures/` |
| Font embedding | `pdf.fonttype` 42, `ps.fonttype` 42, `svg.fonttype` none |
| LaTeX (one line in reply) | single column → `figure`, `width=\columnwidth`; double → `figure*`, `width=\textwidth` |

## 7. Check

Look at the PNG; fix and re-render if any fails:

- Width equals target.
- No clipped or overlapping text; legend covers no data or labels.
- Panel spacing visible; subsampled markers on ticks.
- Font is Times-family, not DejaVu.
- Colors follow §4.
- Caption matches the figure.

## 8. Caption

Written as it appears under the figure in the paper; must stand alone. Paper's language (default English).

| Part | Field | Content |
|---|---|---|
| Lead (bold) | `caption_lead` | What the figure shows, one short sentence |
| Reading guide | `caption_body` | Encodings not obvious from axes/legend: error bars/bands (±1 std over N seeds), dashed lines, panels (by title), log scale |
| Takeaway | `caption_body` | Main observation, with a number computed from the plotted data |

- 2–4 sentences, present tense. No "This figure shows…", no restating legend or axis labels.
- Unknown details → `[TODO: …]`, report in reply. Never invent.
- Plain text with Unicode (±, ×, α), no `$...$`.

> **Figure 1: Test accuracy versus training steps on CIFAR-10.** Shaded bands show ±1 std over 3 seeds; the dashed line marks the best baseline's final accuracy. Ours reaches it after 12k steps, 2.1× faster.

## 9. Gallery (required)

Always publish all project figures to one artifact, `{project-name}-figures`, even for a single figure or a script-only request. If the Artifact tool is unavailable, `present_files` the PDF/PNG and put the caption in the reply.

The page comes from `assets/gallery_template.html` via the script below (paper-style 2-column layout, actual size, caption, PDF/PNG buttons). Don't hand-write or restyle it.

1. **Name**: user's project name → repo/folder name → topic slug; lowercase kebab-case.
2. **Existing gallery**: reuse its url if published in this conversation; otherwise `Artifact` `list`, find the exact title, `read` it, and pass its `index.html` as `--merge`.
3. **Manifest** `/mnt/user-data/outputs/{project-name}-figures/figures.json` (same `id` replaces):

   ```json
   {"project": "sparse-moe",
    "figures": [{"id": "accuracy-curve", "pdf": ".../accuracy-curve.pdf", "png": ".../accuracy-curve.png",
                 "caption_lead": "...", "caption_body": "..."}]}
   ```
4. **Build**:

   ```bash
   python /mnt/skills/plugins/paper-figure/scripts/build_gallery.py --manifest <figures.json> \
     --out /mnt/user-data/outputs/{project-name}-figures.html [--merge <index.html>]
   ```
5. **Publish**: `Artifact` with `file_path`, `title` = `{project-name}-figures`, `favicon` 📊, `capabilities` `{"downloads": true}`, `url` if existing.
6. **Reply**: changes, LaTeX line, any `[TODO]`, DejaVu fallback. No `present_files` for the HTML.
