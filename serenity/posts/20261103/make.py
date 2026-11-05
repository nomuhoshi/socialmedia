"""第十批（2026-11-03）五篇。部分支持 ("seam") 无缝拼接：自动对齐两张截图的重叠区。"""
import math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/work"); import make_cover
A = "/mnt/user-data/attachments/a4464ac6-ea71-5dc8-9737-36e4cce7c493/"
OUT = "/home/claude/work/batch10/out/"
K = 1206 / 920; CW = 1180
W, H, TOP, BOTTOM, GAP, PGAP = 1273, 716, 20, 125, 24, 50

POSTS = [  # 名称, 封面时间, 封面标题, S, 组（每组: [(文件, 显示顶, 显示底, 接法)]，接法 None=空50px, "seam"=无缝对齐）
    ("01_LITE股东吃亏", "20261103 01:43", "换股收购让LITE股东吃亏", 0.38,
     [[("bbbfc088", 245, 1580), ("2ba74a97", 590, 1460), ("f670a7a6", 285, 705)],
      [("f670a7a6", 720, 1415)]]),
    ("02_唱衰AI是流量密码", "20261103 11:04", "唱衰AI是流量密码", 0.38,
     [[("433b04d2", 245, 1678), ("ef7857f5", 790, 1075)],
      [("9cd398f3", 205, 905)],
      [("9cd398f3", 905, 1640), ("9bfa4543", 1202, 1470, "seam")]]),
    ("03_晶豪科被错杀", "20261103 14:47", "1.59倍市盈率还被抛售", 0.37,
     [[("4a278245", 245, 1655), ("a70bfb80", 870, 1200)],
      [("3d9de5bb", 330, 1460)]]),
    ("04_POET市值逼近现金", "20261103 17:47", "POET市值逼近现金", 0.37,
     [[("38bb6f59", 245, 1490)],
      [("fde31355", 385, 1180)],
      [("fde31355", 1190, 1685)]]),
    ("05_激光轮盘谁是赢家", "20261103 18:31", "激光轮盘：谁是赢家", 0.37,
     [[("4f474c62", 245, 1580), ("83c97c1c", 650, 1590), ("83e2768c", 1040, 1240)],
      [("871aaf96", 365, 1515)]]),
]

def load(f): return Image.open(A + f + "-image.png").convert("RGB")

def seam_start(prev_f, prev_b, f, approx_t):
    """在新截图里找与上一张底部 60 行最吻合的位置，返回新截图的起始像素行"""
    p = np.asarray(load(prev_f).convert("L"), dtype=np.int16)[:, :CW]
    q = np.asarray(load(f).convert("L"), dtype=np.int16)[:, :CW]
    pb = round(prev_b * K); ref = p[pb - 60:pb]
    best, by = None, None
    for y in range(round(approx_t * K) - 60, round(approx_t * K) + 60):
        d = np.abs(q[y - 60:y] - ref).mean()
        if best is None or d < best: best, by = d, y
    print(f"  seam {prev_f}->{f}: y={by} diff={best:.2f}")
    return by

def build_strip(shots):
    parts, gaps = [], []
    for i, s in enumerate(shots):
        f, t, b = s[:3]; how = s[3] if len(s) > 3 else None
        im = load(f)
        if how == "seam":
            y0 = seam_start(shots[i - 1][0], shots[i - 1][2], f, t)
            parts.append(im.crop((0, y0, CW, round(b * K)))); gaps.append(0)
        else:
            parts.append(im.crop((0, round(t * K), CW, round(b * K)))); gaps.append(PGAP if i else 0)
    st = Image.new("RGB", (CW, sum(p.height for p in parts) + sum(gaps)), "black"); y = 0
    for p, g in zip(parts, gaps):
        y += g; st.paste(p, (0, y)); y += p.height
    return st

def split(strip, COL_H, name):
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
    if best is None: print("WARN 无法分栏/块太高", name, strip.height, COL_H); return [strip]
    lo, hi = strip.height // len(best), COL_H
    while lo < hi:
        mid = (lo + hi) // 2; g = greedy(mid)
        if g is not None and len(g) <= len(best): hi = mid
        else: lo = mid + 1
    return [strip.crop((0, a, CW, b)) for a, b in greedy(hi)]

only = sys.argv[1:]
for name, stamp, title, S, groups in POSTS:
    if only and not any(name.startswith(o) for o in only): continue
    COL_H = int((H - TOP - BOTTOM) / S)
    cols = []
    for gi, shots in enumerate(groups):
        st = build_strip(shots); st.save(f"{OUT}_{name}_长图{gi}.png")
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
