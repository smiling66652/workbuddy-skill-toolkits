# 对"页图型"课件做 OCR，产出可搜索文字
# 用法: python ocr-courseware.py [课程关键词]
import os, sys, json, glob, time
from rapidocr_onnxruntime import RapidOCR

ROOT = r"D:/桌面/浏览器/yuketang-research"
CW = os.path.join(ROOT, "courseware")
OUTD = os.path.join(ROOT, "courses")
only = sys.argv[1] if len(sys.argv) > 1 else ""

ocr = RapidOCR()
courses = sorted([d for d in os.listdir(CW) if os.path.isdir(os.path.join(CW, d))])
if only:
    courses = [c for c in courses if only in c]

total_pages = 0
for course in courses:
    cdir = os.path.join(CW, course)
    decks = sorted([d for d in os.listdir(cdir) if os.path.isdir(os.path.join(cdir, d))])
    out_lines = ["# " + course + " · 课件 OCR 文字", "", "> 由 rapidocr 对课件页图识别，可能有误字，供检索与理解用。", ""]
    cpages = 0
    t0 = time.time()
    for deck in decks:
        imgs = sorted(glob.glob(os.path.join(cdir, deck, "p*.jpg")))
        if not imgs:
            continue
        out_lines.append("## " + deck + "（" + str(len(imgs)) + " 页）")
        out_lines.append("")
        for img in imgs:
            page = os.path.basename(img).replace(".jpg", "").replace("p", "")
            txtfile = img.replace(".jpg", ".ocr.txt")
            if os.path.exists(txtfile) and os.path.getsize(txtfile) > 0:
                txt = open(txtfile, encoding="utf-8").read()
            else:
                try:
                    res, _ = ocr(img)
                    txt = "\n".join([r[1] for r in res]) if res else ""
                except Exception as e:
                    txt = ""
                    print("  ! " + img + " " + str(e)[:60])
                open(txtfile, "w", encoding="utf-8").write(txt)
            cpages += 1
            if txt.strip():
                out_lines.append("**" + page + "**")
                out_lines.append("")
                for ln in txt.split("\n"):
                    if ln.strip():
                        out_lines.append("- " + ln.strip())
                out_lines.append("")
    fn = course + "-OCR.md"
    open(os.path.join(OUTD, fn), "w", encoding="utf-8").write("\n".join(out_lines))
    total_pages += cpages
    print("[ok] " + course + " | " + str(cpages) + " 页 | " + str(round(time.time() - t0)) + "s -> courses/" + fn)

print("完成: " + str(total_pages) + " 页")
