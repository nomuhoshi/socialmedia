"""第九批（2026-11-02）：20:43 充电篇、21:17 收购篇、22:59 激光厂篇"""
import math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/work"); import make_cover
A = "/mnt/user-data/attachments/a4464ac6-ea71-5dc8-9737-36e4cce7c493/"
OUT = "/home/claude/work/batch9/out/"
K = 1206 / 920; CW = 1180
W, H, TOP, BOTTOM, GAP, PGAP = 1273, 716, 20, 125, 24, 50

POSTS = [  # 名称, 封面时间, 封面标题, S, 组（组内可在段落处分栏，组与组不混栏）
    ("01_对冲基金十年最猛去杠杆", "20261102 20:43", "对冲基金去杠杆十年最猛", 0.38,
     [[("be18cf23", 245, 1682), ("0d1d2238", 680, 1475), ("9b6730ed", 665, 1625), ("c5066954", 640, 1125)],
      [("cdf0e5f2", 262, 1396)]]),
    ("02_迈威尔收购Lumentum", "20261102 21:17", "迈威尔买下Lumentum", 0.38,
     [[("3e57f77a", 245, 1290), ("7bca500e", 400, 1345)]]),
    ("03_独立激光厂身价上涨", "20261102 22:59", "独立激光厂身价要涨了", 0.38,
     [[("c0f1f2ca", 245, 1650), ("fad52333", 930, 1630), ("c6249394", 870, 1640),
       ("e70d833f", 765, 1465), ("b6a1e259", 400, 1375)],
      [("84fc2eab", 700, 1275)]]),
]

def split(strip, COL_H, name):
    """先用最大栏高贪心算出最少栏数，再二分找能保持同样栏数的最小栏高，让各栏均衡；只在段落空白（≥40 行）处切。"""
    blank = (np.array(strip.convert("L")) > 30).sum(1) == 0
    def greedy(L):
        segs, start = [], 0
        while strip.height - start > L:
            cut = start + L
            while cut > start + 40 and not blank[cut - 40:cut].all(): cut -= 1
            if cut <= start + 40: return None
            segs.append((start, cut)); start = cut
            while start < strip.height and blank[start]: start += 1
        segs.append((start, strip.height)); return segs
    best = greedy(COL_H)
    if best is None: print("WARN 无法分栏", name); best = [(0, strip.height)]
    lo, hi = strip.height // len(best), COL_H
    while lo < hi:
        mid = (lo + hi) // 2; g = greedy(mid)
        if g is not None and len(g) <= len(best): hi = mid
        else: lo = mid + 1
    segs = greedy(hi)
    return [strip.crop((0, a, CW, b)) for a, b in segs]

only = sys.argv[1:]
for name, stamp, title, S, groups in POSTS:
    if only and not any(name.startswith(o) for o in only): continue
    COL_H = int((H - TOP - BOTTOM) / S)
    cols = []
    for gi, shots in enumerate(groups):
        parts = [Image.open(A + f + "-image.png").convert("RGB").crop((0, round(t * K), CW, round(b * K))) for f, t, b in shots]
        st = Image.new("RGB", (CW, sum(p.height for p in parts) + PGAP * (len(parts) - 1)), "black"); y = 0
        for p in parts: st.paste(p, (0, y)); y += p.height + PGAP
        st.save(f"{OUT}_{name}_长图{gi}.png")
        cols += split(st, COL_H, name)
    pages = [cols[i:i + 2] for i in range(0, len(cols), 2)]
    for n, pg in enumerate(pages, 1):
        ims = [im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS) for im in pg]
        c = Image.new("RGB", (W, H), "black")
        x = (W - sum(i.width for i in ims) - GAP * (len(ims) - 1)) // 2
        y0 = TOP + max(0, (H - TOP - BOTTOM - max(i.height for i in ims)) // 2)
        for im in ims: c.paste(im, (x, y0)); x += im.width + GAP
        c.save(f"{OUT}{name}_拼图_{n}.png")
    make_cover.TPL = "/home/claude/work/cover_tpl.png"
    make_cover.make(stamp, title, f"{OUT}{name}_封面.png")
    print(name, len(cols), "栏", len(pages), "页", [c.height for c in cols], "COL_H", COL_H)
