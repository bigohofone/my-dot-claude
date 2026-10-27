import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

ASSETS = Path(__file__).parent / "assets"
sys.path.insert(0, str(ASSETS))
from paper import fit_height

STYLE = ASSETS / "paper.mplstyle"
WIDTH = 3.25


@pytest.fixture(autouse=True)
def style():
    with plt.style.context(STYLE):
        yield
    plt.close("all")


def check(fig, ratios, aspect, tol=0.005):
    assert fig.get_figwidth() == WIDTH
    for r in ratios:
        assert abs(r - aspect) / aspect < tol


def test_single_line():
    fig, ax = plt.subplots(figsize=(WIDTH, 3))
    ax.plot([0, 1], [0, 1])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    check(fig, fit_height(fig, ax), 0.618)


def test_two_panels_shared_legend():
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3))
    for ax in axes:
        ax.plot([0, 1], [0, 1], label="a")
        ax.plot([0, 1], [1, 0], label="b")
        ax.set_title("T")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="outside lower center", ncol=2,
               frameon=False, borderaxespad=0)
    check(fig, fit_height(fig, axes), 0.618)


def test_grid_with_empty_cell():
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 3))
    for ax in axes.flat[:3]:
        ax.plot([0, 1], [0, 1])
    axes[1, 1].axis("off")
    ratios = fit_height(fig, axes)
    assert len(ratios) == 3
    check(fig, ratios, 0.618)


def test_heatmap_colorbar():
    fig, ax = plt.subplots(figsize=(WIDTH, 3))
    im = ax.imshow(np.random.rand(5, 5), aspect="auto")
    fig.colorbar(im, ax=ax)
    check(fig, fit_height(fig, fig.axes, aspect=1.0), 1.0)


def test_imshow_default_aspect_raises():
    fig, ax = plt.subplots(figsize=(WIDTH, 3))
    ax.imshow(np.random.rand(5, 5))
    with pytest.raises(ValueError, match="aspect='auto'"):
        fit_height(fig, ax, aspect=1.0)


def test_mosaic_different_widths_warns():
    fig, axd = plt.subplot_mosaic("AAB", figsize=(WIDTH, 3), layout="constrained")
    with pytest.warns(UserWarning, match="different widths"):
        fit_height(fig, axd)


def test_long_labels_converge():
    fig, ax = plt.subplots(figsize=(WIDTH, 3))
    ax.plot([0, 1], [0, 1_000_000])
    ax.set_yticks([0, 500_000, 1_000_000], ["0", "500,000", "1,000,000"], fontsize=12)
    ax.set_ylabel("A very long y-axis label\nthat spans two lines")
    check(fig, fit_height(fig, ax), 0.618)


def test_aspect_options():
    for aspect in (1.0, 1.618):
        fig, ax = plt.subplots(figsize=(WIDTH, 3))
        ax.plot([0, 1], [0, 1])
        check(fig, fit_height(fig, ax, aspect=aspect), aspect)


def test_ticks_that_change_with_height_converge():
    fig, ax = plt.subplots(figsize=(3.0, 2))
    ax.bar(np.arange(3), [84, 92, 89], edgecolor="black")
    ax.set_ylabel("Accuracy (%)")
    ax.set_ylim(78, 95)
    ratios = fit_height(fig, ax)
    assert fig.get_figwidth() == 3.0
    assert abs(ratios[0] - 0.618) / 0.618 < 0.005
    assert ax.get_ylim() == (78, 95)


def test_shared_axes():
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 3), sharex=True, sharey=True)
    for i, ax in enumerate(axes.flat):
        ax.plot([0, 1], [0, i + 1])
    check(fig, fit_height(fig, axes), 0.618)


def test_pdf_embeds_inter_as_text(tmp_path):
    fig, ax = plt.subplots(figsize=(WIDTH, 2))
    ax.plot([0, 1], [0, 1])
    ax.set_title(r"$\alpha=0.1$, $\sum_i x_i \leq \sqrt{2}$")
    ax.set_xlabel(r"FLOPs ($\times 10^{18}$)")
    fig.savefig(tmp_path / "f.pdf")
    pdf = (tmp_path / "f.pdf").read_bytes()
    assert b"Inter" in pdf and b"DejaVu" not in pdf
    assert b"/Type3" not in pdf
    assert pdf.count(b"/FontFile2") == pdf.count(b"/CIDFontType2") > 0
    assert b"/ToUnicode" in pdf
