"""第六批（2026-10-27）：3 篇 → 去重长图 → 统一缩放、段落处分栏 → 每页 2 栏；封面。
截图原图 1184x2576（显示 920 宽，K = 1184/920）；右侧滚动条在 x>1160，裁掉。"""
import math, os, subprocess
import numpy as np
from PIL import Image

A = "/mnt/user-data/attachments/a4464ac6-ea71-5dc8-9737-36e4cce7c493/"
W_ = "/home/claude/work/"
OUT = W_ + "batch7/out/"
os.makedirs(OUT, exist_ok=True)
K = 1206 / 920
CW = 1180
W, H, TOP, BOTTOM, GAP, PGAP = 1273, 716, 20, 125, 24, 50

POSTS = [
    ("01_大盘股尝到高贝塔", "20261030 16:07", "大盘股也尝到高贝塔的痛", 0.38,
     [[("27265bfc-image.png", 245, 750), ("7947be95-image.png", 170, 1295)]]),
]

for name, stamp, title, S, groups in POSTS:
    COL_H = int((H - TOP - BOTTOM) / S)
    cols = []   # 每个元素是一栏的原图
    for gi, shots in enumerate(groups):
        parts = [Image.open(A + f).convert("RGB").crop((0, round(t * K), CW, round(b * K))) for f, t, b in shots]
        strip = Image.new("RGB", (CW, sum(p.height for p in parts) + PGAP * (len(parts) - 1)), "black")
        y = 0
        for p in parts:
            strip.paste(p, (0, y)); y += p.height + PGAP
        strip.save(f"{OUT}_{name}_长图{gi}.png")
        g = np.array(strip.convert("L"))
        blank = (g > 30).sum(1) == 0
        ncols = math.ceil(strip.height / COL_H)
        target = strip.height / ncols
        segs, start = [], 0
        while strip.height - start > COL_H:
            cut = min(start + COL_H, round(start + target * 1.05))
            while cut > start + COL_H // 3 and not blank[cut - 40:cut].all():
                cut -= 1
            if not blank[cut - 40:cut].all():
                print("WARN 没找到段落空白，切在", cut, name)
            segs.append((start, cut)); start = cut
            while start < strip.height and blank[start]:
                start += 1
        segs.append((start, strip.height))
        cols += [strip.crop((0, a, CW, b)) for a, b in segs]
    pages = [cols[i:i + 2] for i in range(0, len(cols), 2)]
    for n, pg in enumerate(pages, 1):
        ims = [im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS) for im in pg]
        canvas = Image.new("RGB", (W, H), "black")
        total = sum(im.width for im in ims) + GAP * (len(ims) - 1)
        x = (W - total) // 2
        y0 = TOP + max(0, (H - TOP - BOTTOM - max(i.height for i in ims)) // 2)
        for im in ims:
            canvas.paste(im, (x, y0)); x += im.width + GAP
        canvas.save(f"{OUT}{name}_拼图_{n}.png")
    subprocess.run(["python3", W_ + "make_cover.py", stamp, title, f"{OUT}{name}_封面.png"], check=True)
    print(name, len(cols), "栏", len(pages), "页")
