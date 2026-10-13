#!/usr/bin/env python3
"""Build the `{project}-figures` gallery page for the paper-figure skill.

Usage:
    python build_gallery.py --manifest figures.json --out /mnt/user-data/outputs/<project>-figures.html \
        [--merge previously_published_index.html]

Manifest (JSON):
{
  "project": "my-project",
  "figures": [
    {
      "id": "accuracy-curve",              # kebab-case; used as the download filename
      "pdf": "/abs/path/accuracy-curve.pdf",
      "png": "/abs/path/accuracy-curve.png",
      "caption_lead": "Test accuracy versus training steps on CIFAR-10.",
      "caption_body": "Shaded bands show ±1 std over 3 seeds. Ours converges ..."
    }
  ]
}

With --merge, figures already in the previously published page are kept; a figure with the same
id is replaced by the new one, and new ids are appended in manifest order.

The page previews the PDF at its printed size; PDF and PNG are offered as downloads.
"""
import argparse
import base64
import html
import json
import os
import re
import sys

DATA_RE = re.compile(
    r'<script id="gallery-data" type="application/json">(.*?)</script>', re.S
)
SIZE_LIMIT = 16 * 1024 * 1024

def b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def load_existing(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        m = DATA_RE.search(f.read())
    if not m:
        sys.exit(f"--merge: no gallery data found in {path}")
    return json.loads(m.group(1).replace("<\\/", "</"))["figures"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--merge", help="previously published gallery HTML to keep figures from")
    a = ap.parse_args()

    with open(a.manifest, encoding="utf-8") as f:
        man = json.load(f)
    project = man["project"]

    new = []
    for fig in man["figures"]:
        for key in ("id", "pdf", "png", "caption_lead"):
            if not fig.get(key):
                sys.exit(f"figure missing '{key}': {fig}")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fig["id"]):
            sys.exit(f"id must be kebab-case: {fig['id']}")
        new.append({
            "id": fig["id"],
            "caption_lead": fig["caption_lead"].strip(),
            "caption_body": fig.get("caption_body", "").strip(),
            "pdf_b64": b64(fig["pdf"]),
            "png_b64": b64(fig["png"]),
        })

    figures = load_existing(a.merge) if a.merge else []
    index = {f["id"]: i for i, f in enumerate(figures)}
    for fig in new:
        if fig["id"] in index:
            figures[index[fig["id"]]] = fig
        else:
            index[fig["id"]] = len(figures)
            figures.append(fig)

    data = {"project": project, "figures": figures}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    with open(os.path.join(os.path.dirname(__file__), "..", "assets", "gallery_template.html"),
              encoding="utf-8") as f:
        page = f.read()
    page = DATA_RE.sub(lambda m: f'<script id="gallery-data" type="application/json">{blob}</script>', page, count=1)
    page = page.replace("<title>figures</title>", f"<title>{html.escape(project)}-figures</title>", 1)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    size = os.path.getsize(a.out)
    print(f"wrote {a.out}: {len(figures)} figure(s), {size / 1e6:.2f} MB")
    if size > SIZE_LIMIT * 0.9:
        print("WARNING: close to the 16 MB artifact limit; split the gallery or reduce PNG size.")


if __name__ == "__main__":
    main()
