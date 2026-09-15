"""Erase text strokes from an image using a text schema (two-pass by default).

Usage:
  python inpaint_text.py <schema.json> <source.png> <out_background.png> \
      [--single] [--thresh 90] [--radius 3] [--dilate 3]

Default is TWO-PASS for near-residue-free erasure:
  Pass 1: Otsu-adaptive stroke mask (per text box, on the colour-distance map)
          + dilate 3 + TELEA radius 5. Catches glyph cores + anti-aliased edges.
  Pass 2: detect pixels still close to a text colour after pass 1 (missed cores),
          dilate 2, fill with NS radius 3 (natural fill from clean neighbourhood).

On the KSIA test slide this drops residue from 3.1% (single-pass fixed-threshold)
to 0.72% (two-pass). Use --single to fall back to the old single-pass behaviour.

Schema format: see text_schema.example.json.
- logos entries are SKIPPED (kept intact; re-applied as image crops).
- Whole-bbox masking is NEVER used: text often sits on coloured pills / dark
  bars whose fill must be preserved. Mask = stroke pixels only (by colour).
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np


def imread_unicode(p):
    return cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)


def imwrite_unicode(p, img):
    ok, buf = cv2.imencode(Path(p).suffix, img)
    buf.tofile(str(p))
    return ok


def hex_to_bgr(hexv):
    hexv = hexv.lstrip('#')
    r = int(hexv[0:2], 16)
    g = int(hexv[2:4], 16)
    b = int(hexv[4:6], 16)
    return np.array([b, g, r], dtype=np.float32)  # cv2 is BGR


def iter_boxes(schema):
    sw = schema.get('src_w')
    sh = schema.get('src_h')
    logos = set(schema.get('logos', []))
    for t in schema['texts']:
        if t['text'] in logos:
            continue
        yield t, sw, sh


def build_pass1_mask(src, schema, dilate_iter, fixed_thresh=None):
    h, w = src.shape[:2]
    sw = schema.get('src_w', w)
    sh = schema.get('src_h', h)
    mask = np.zeros((h, w), dtype=np.uint8)
    for t in schema['texts']:
        if t['text'] in set(schema.get('logos', [])):
            continue
        x, y, bw, bh = t['x'], t['y'], t['w'], t['h']
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(w, x + bw), min(h, y + bh)
        if x1 <= x0 or y1 <= y0:
            continue
        c_bgr = hex_to_bgr(t['color'])
        roi = src[y0:y1, x0:x1].astype(np.float32)
        dist = np.linalg.norm(roi - c_bgr, axis=2)
        if fixed_thresh is not None:
            stroke = (dist < fixed_thresh).astype(np.uint8) * 255
        else:
            d8 = dist.astype(np.uint8)
            if d8.max() < 40:
                stroke = (dist < 90).astype(np.uint8) * 255
            else:
                _ret, binv = cv2.threshold(d8, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                stroke = binv
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], stroke)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    return cv2.dilate(mask, kernel, iterations=dilate_iter)


def build_residue_mask(clean, schema, residue_thresh=55, dilate_iter=2):
    h, w = clean.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    for t in schema['texts']:
        if t['text'] in set(schema.get('logos', [])):
            continue
        x, y, bw, bh = t['x'], t['y'], t['w'], t['h']
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(w, x + bw), min(h, y + bh)
        if x1 <= x0 or y1 <= y0:
            continue
        c_bgr = hex_to_bgr(t['color'])
        roi = clean[y0:y1, x0:x1].astype(np.float32)
        dist = np.linalg.norm(roi - c_bgr, axis=2)
        still = (dist < residue_thresh).astype(np.uint8) * 255
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], still)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    return cv2.dilate(mask, kernel, iterations=dilate_iter)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('schema')
    ap.add_argument('source')
    ap.add_argument('out_background')
    ap.add_argument('--single', action='store_true', help='single-pass (old behaviour)')
    ap.add_argument('--thresh', type=float, default=None, help='fixed threshold (disables Otsu)')
    ap.add_argument('--dilate', type=int, default=3)
    ap.add_argument('--radius', type=int, default=5)
    args = ap.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding='utf-8'))
    src = imread_unicode(args.source)
    assert src is not None, f'failed to read source: {args.source}'
    h, w = src.shape[:2]

    fixed = args.thresh if args.thresh is not None else None

    mask1 = build_pass1_mask(src, schema, args.dilate, fixed_thresh=fixed)
    clean1 = cv2.inpaint(src, mask1, args.radius, flags=cv2.INPAINT_TELEA)

    if args.single:
        clean = clean1
        print(f'single-pass: coverage={np.count_nonzero(mask1)/(h*w)*100:.2f}%')
    else:
        mask2 = build_residue_mask(clean1, schema)
        clean = cv2.inpaint(clean1, mask2, 3, flags=cv2.INPAINT_NS)
        print(f'pass1 coverage={np.count_nonzero(mask1)/(h*w)*100:.2f}%  '
              f'pass2 residue_mask={np.count_nonzero(mask2)/(h*w)*100:.2f}%')
        mp = Path(args.out_background).with_name('inpaint_mask_pass2.png')
        imwrite_unicode(mp, cv2.applyColorMap(mask2, cv2.COLORMAP_JET))

    imwrite_unicode(args.out_background, clean)
    mp1 = Path(args.out_background).with_name('inpaint_mask_pass1.png')
    imwrite_unicode(mp1, cv2.applyColorMap(mask1, cv2.COLORMAP_JET))
    print(f'wrote {args.out_background}')


if __name__ == '__main__':
    main()
