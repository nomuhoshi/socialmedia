"""第十五批（2026-11-07/08 发帖）：美光长约与软银涡轮、年内收益 594%、新云公司 NBIS、台积电否认 3D DRAM、NASA 月球基地合同。
沿用 tools/collage_example_20261103.py 的拼图逻辑；坐标是手机"显示坐标"（宽 920），乘 1206/920 得像素。
用法（在 serenity 目录下）：python3 posts/20261108/make.py [名称前缀]
截图原件在对话附件目录 A（会话结束后失效，不入库）。"""
import sys, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools")); import make_cover
make_cover.TPL = os.path.join(HERE, "..", "..", "tools", "cover_tpl.png")
A = "/mnt/user-data/attachments/06bc04ff-18a8-5eca-92df-995ff2b81f3a/"
OUT = HERE + "/"
K = 1206 / 920; CW = 1180
W, H, TOP, BOTTOM, GAP, PGAP = 1273, 716, 20, 125, 24, 50

POSTS = [  # 名称, 封面时间, 封面标题, S, 组（每组: [(文件, 显示顶, 显示底, 接法)]，接法 None=空50px, "seam"=无缝对齐）
    ("01_美光长约与软银涡轮", "20261107 20:04", "美光长约不能随便撕", 0.34,
     [[("0265df8c", 280, 1685), ("89e1ca4a", 772, 1608, "seam"), ("cbea176c", 138, 1450, "at")],
      [("bd93243a", 650, 1265)]]),
    ("02_年内收益594", "20261107 21:05", "巴菲特睡得比我安稳", 0.37,
     [[("c8c74371", 280, 1685), ("9c7501e4", 677, 1385, "seam")]]),
    ("03_NBIS新云", "20261107 23:40", "新云股崩了她却看多", 0.34,
     [[("38ca5779", 280, 1685), ("beac0b52", 642, 1685, "seam"), ("73c75dfd", 558, 1685, "seam"),
       ("304fcbcd", 697, 1685, "seam"), ("cf079f96", 800, 1410, "seam")],
      [("742c4a66", 610, 1222)]]),
    ("04_台积电3DDRAM", "20261108 01:01", "台积电否认要做存储", 0.34,
     [[("a9200459", 280, 1685), ("da910669", 709, 1450, "seam")],
      [("8ce31c89", 650, 1260)]]),
    ("05_NASA月球基地", "20261108 13:35", "NASA月球基地来了", 0.34,
     [[("1f6b9347", 280, 1685), ("737b57b1", 674, 1685, "seam"), ("562f1926", 930, 1330, "seam")],
      [("9164a252", 535, 1140)]]),
]


PER = {"01": 3, "02": 2, "03": 3, "04": 3, "05": 3}  # 每页栏数
GW = {"01": 40, "02": 40, "03": 40, "04": 40, "05": 40}  # 分栏要求的最小空白行数


def load(f): return Image.open(A + f + "-image.png").convert("RGB")


def seam_start(prev_f, prev_b, f, approx_t):
    p = np.asarray(load(prev_f).convert("L"), dtype=np.int16)[:, :CW]
    q = np.asarray(load(f).convert("L"), dtype=np.int16)[:, :CW]
    pb = round(prev_b * K); ref = p[pb - 60:pb]
    best, by = None, None
    for y in range(round(approx_t * K) - 90, round(approx_t * K) + 90):
        d = np.abs(q[y - 60:y] - ref).mean()
        if best is None or d < best: best, by = d, y
    print(f"  seam {prev_f}->{f}: y={by} (approx {round(approx_t*K)}) diff={best:.2f}")
    return by


def build_strip(shots):
    parts, gaps = [], []
    for i, s in enumerate(shots):
        f, t, b = s[:3]; how = s[3] if len(s) > 3 else None
        im = load(f)
        if how == "at":  # 空白处直接对接：t 是本张里对应上一张底边的显示坐标（两侧都落在空白行，误差只改空隙）
            parts.append(im.crop((0, round(t * K), CW, round(b * K)))); gaps.append(0)
        elif how == "seam":
            y0 = seam_start(shots[i - 1][0], shots[i - 1][2], f, t)
            parts.append(im.crop((0, y0, CW, round(b * K)))); gaps.append(0)
        else:
            parts.append(im.crop((0, round(t * K), CW, round(b * K)))); gaps.append(PGAP if i else 0)
    st = Image.new("RGB", (CW, sum(p.height for p in parts) + sum(gaps)), "black"); y = 0
    for p, g in zip(parts, gaps):
        y += g; st.paste(p, (0, y)); y += p.height
    return st


def split(strip, COL_H, name, gw=40):
    blank = (np.array(strip.convert("L")) > 30).sum(1) == 0
    def greedy(L):
        segs, start = [], 0
        while strip.height - start > L:
            cut = start + L
            while cut > start + 40 and not blank[cut - gw:cut].all(): cut -= 1
            if cut <= start + gw: return None
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


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, stamp, title, S, groups in POSTS:
        if only and not any(name.startswith(o) for o in only): continue
        COL_H = int((H - TOP - BOTTOM) / S)
        cols = []
        for gi, shots in enumerate(groups):
            st = build_strip(shots); st.save(f"/tmp/claude-0/long_{name}_{gi}.png")
            cols += split(st, COL_H, name, GW.get(name[:2], 40))
        n_per = PER.get(name[:2], 2)
        pages = [cols[i:i + n_per] for i in range(0, len(cols), n_per)]
        for n, pg in enumerate(pages, 1):
            Sp = S
            if len(pg) == 1: Sp = min(0.65, (H - TOP - BOTTOM) / pg[0].height, W / CW)  # 单栏页（轮播图）放大
            ims = [im.resize((round(im.width * Sp), round(im.height * Sp)), Image.LANCZOS) for im in pg]
            c = Image.new("RGB", (W, H), "black")
            x = (W - sum(i.width for i in ims) - GAP * (len(ims) - 1)) // 2
            y0 = TOP + max(0, (H - TOP - BOTTOM - max(i.height for i in ims)) // 2)
            for im in ims: c.paste(im, (x, y0)); x += im.width + GAP
            c.save(f"{OUT}{name}_拼图_{n}.png")
        make_cover.make(stamp, title, f"{OUT}{name}_封面.png")
        print(name, len(cols), "栏", len(pages), "页", [c.height for c in cols], "COL_H", COL_H)
