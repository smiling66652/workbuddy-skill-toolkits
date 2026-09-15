"""Visual QA: compare the source image with a rendered PPTX preview.

Outputs (under outputs/qa_v2/):
  side_by_side.png   source | preview, side by side
  blend.png          50/50 blend of source and preview
  diff_heatmap.png   amplified absolute-diff heatmap
  absdiff.png        raw absolute diff (not amplified)
  metrics.json       SSIM, mean abs diff, changed-pixel ratio

Usage:
  python work/qa_compare.py <source.png> <preview.png> [out_dir]
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def imread_unicode(p: Path):
    return cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)


def imwrite_unicode(p: Path, img):
    ok, buf = cv2.imencode(p.suffix, img)
    buf.tofile(str(p))
    return ok


def main(src_path: str, prev_path: str, out_dir: str):
    src = imread_unicode(Path(src_path))
    prev = imread_unicode(Path(prev_path))
    assert src is not None and prev is not None, 'failed to read images'
    h, w = src.shape[:2]
    if prev.shape[:2] != (h, w):
        prev = cv2.resize(prev, (w, h), interpolation=cv2.INTER_AREA)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    # --- Side by side ---
    sbs = np.hstack([src, prev])
    imwrite_unicode(out / 'side_by_side.png', sbs)

    # --- Blend ---
    blend = cv2.addWeighted(src, 0.5, prev, 0.5, 0)
    imwrite_unicode(out / 'blend.png', blend)

    # --- Raw abs diff ---
    diff = cv2.absdiff(src, prev)
    imwrite_unicode(out / 'absdiff.png', diff)

    # --- Heatmap (amplified) ---
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    heat = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    imwrite_unicode(out / 'diff_heatmap.png', heat)

    # --- Metrics ---
    gray_src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    gray_prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    ssim_val = float(ssim(gray_src, gray_prev, data_range=255))
    mean_abs = float(diff.mean())
    max_abs = float(diff.max())
    # "changed" pixels: any channel differs by more than 24
    changed = float(np.count_nonzero(diff.max(axis=2) > 24)) / (h * w) * 100.0

    metrics = {
        'source': src_path,
        'preview': prev_path,
        'size': [w, h],
        'ssim_gray': round(ssim_val, 4),
        'mean_abs_diff_BGR': round(mean_abs, 3),
        'max_abs_diff': round(max_abs, 3),
        'changed_pixel_pct_threshold24': round(changed, 3),
    }
    (out / 'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')

    print(json.dumps(metrics, indent=2))
    print(f'wrote QA artefacts to {out}')


if __name__ == '__main__':
    src = sys.argv[1]
    prev = sys.argv[2]
    odir = sys.argv[3] if len(sys.argv) > 3 else 'outputs/qa_v2'
    main(src, prev, odir)
