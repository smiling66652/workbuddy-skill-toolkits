"""Build an editable PPTX from a text schema + clean background.

Usage:
  python build_editable_pptx.py <schema.json> <source.png> <background.png> <out.pptx>

Layer order on the single slide:
  1. background.png  (text erased by inpaint_text.py) -- full bleed
  2. logo image crops (cut from the ORIGINAL source at each logo's bbox;
     brand styling preserved 1:1; NOT editable text)
  3. opaque editable Arial text boxes for every non-logo text entry

Slide size keeps the source aspect ratio (13.333in wide by default).
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR


def imread_unicode(p):
    return cv2.imdecode(np.fromfile(str(p), dtype=np.uint8), cv2.IMREAD_COLOR)


def imwrite_unicode(p, img):
    ok, buf = cv2.imencode(Path(p).suffix, img)
    buf.tofile(str(p))
    return ok


ALIGN_MAP = {'left': PP_ALIGN.LEFT, 'center': PP_ALIGN.CENTER, 'right': PP_ALIGN.RIGHT}


def hex_to_rgb(hexv):
    hexv = hexv.lstrip('#')
    return RGBColor(int(hexv[0:2], 16), int(hexv[2:4], 16), int(hexv[4:6], 16))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('schema')
    ap.add_argument('source')
    ap.add_argument('background')
    ap.add_argument('out_pptx')
    ap.add_argument('--slide-width-in', type=float, default=13.333)
    args = ap.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding='utf-8'))
    logos = set(schema.get('logos', []))
    texts = schema['texts']
    sw = schema.get('src_w')
    sh = schema.get('src_h')

    src_arr = imread_unicode(args.source)
    assert src_arr is not None, f'failed to read source: {args.source}'
    h, w = src_arr.shape[:2]
    if sw is None:
        sw = w
    if sh is None:
        sh = h

    slide_w_in = args.slide_width_in
    slide_h_in = slide_w_in * sh / sw

    prs = Presentation()
    prs.slide_width = Inches(slide_w_in)
    prs.slide_height = Inches(slide_h_in)
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank

    # Layer 1: clean background
    slide.shapes.add_picture(args.background, 0, 0,
                             width=prs.slide_width, height=prs.slide_height)

    # Logo crop output dir next to the pptx
    logo_dir = Path(args.out_pptx).parent / (Path(args.out_pptx).stem + '_logos')
    logo_dir.mkdir(exist_ok=True)

    logo_n = 0
    text_n = 0
    for t in texts:
        text = t['text']
        x, y, bw, bh = t['x'], t['y'], t['w'], t['h']
        left = Inches(x / sw * slide_w_in)
        top = Inches(y / sh * slide_h_in)
        width = Inches(bw / sw * slide_w_in)
        height = Inches(bh / sh * slide_h_in)

        if text in logos:
            x0, y0 = max(0, x), max(0, y)
            x1, y1 = min(w, x + bw), min(h, y + bh)
            crop = src_arr[y0:y1, x0:x1]
            safe = ''.join(c if c.isalnum() else '_' for c in text)[:24]
            crop_path = logo_dir / f'logo_{safe}_{x0}_{y0}.png'
            imwrite_unicode(crop_path, crop)
            pic = slide.shapes.add_picture(str(crop_path), left, top, width, height)
            pic.name = 'logo_crop__' + safe
            logo_n += 1
            continue

        box = slide.shapes.add_textbox(left, top, width, height)
        box.name = 'editable__' + text.replace('\n', ' ')[:40]
        tf = box.text_frame
        tf.clear()
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.word_wrap = True
        for i, line in enumerate(text.split('\n')):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = ''
            p.alignment = ALIGN_MAP.get(t.get('align', 'left'), PP_ALIGN.LEFT)
            run = p.add_run()
            run.text = line
            run.font.name = 'Arial'
            run.font.size = Pt(t['size'])
            run.font.bold = t.get('bold', False)
            run.font.color.rgb = hex_to_rgb(t['color'])
        text_n += 1

    prs.save(args.out_pptx)
    print(f'wrote {args.out_pptx}')
    print(f'slide: {slide_w_in:.4f}in x {slide_h_in:.4f}in | logos: {logo_n} | editable text: {text_n}')


if __name__ == '__main__':
    main()
