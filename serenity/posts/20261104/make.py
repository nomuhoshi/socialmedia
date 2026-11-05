"""第十一批（2026-11-04 发帖）三篇：AEHR/FN、AAOI 云南锗业长单、选举夜 AI。
沿用 tools/collage_example_20261103.py 的拼图逻辑；坐标是手机"显示坐标"（宽 920），乘 1206/920 得像素。
用法（在 serenity 目录下）：python3 posts/20261104/make.py [名称前缀]
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
    ("01_Aehr与Fabrinet财报大涨", "20261104 00:27", "财报暴涨，杠杆党还在吗", 0.50,
     [[("4477d454", 245, 1380)]]),
    ("02_AAOI磷化铟长单", "20261104 02:06", "AAOI签下磷化铟长单", 0.345,
     [[("99772b63", 245, 1685), ("74910ea7", 508, 1690, "seam"),
       ("1a53bc6e", 995, 1690, "seam"), ("f706e544", 610, 1585, "seam")]]),
    ("03_选举夜AI末日论", "20261104 13:25", "选举夜的AI末日论", 0.50,
     [[("66c47523", 245, 1685), ("5ea412dd", 796, 1690, "seam"),
       ("a7c28a0e", 1060, 1440, "seam")]]),
]


GW = {"02": 62}  # 分栏要求的最小空白行数；02 的引用框与时间/互动栏间隙只有 49–60px，要连在一起


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
        if how == "seam":
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
        pages = [cols[i:i + 2] for i in range(0, len(cols), 2)]
        for n, pg in enumerate(pages, 1):
            ims = [im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS) for im in pg]
            c = Image.new("RGB", (W, H), "black")
            x = (W - sum(i.width for i in ims) - GAP * (len(ims) - 1)) // 2
            y0 = TOP + max(0, (H - TOP - BOTTOM - max(i.height for i in ims)) // 2)
            for im in ims: c.paste(im, (x, y0)); x += im.width + GAP
            c.save(f"{OUT}{name}_拼图_{n}.png")
        make_cover.make(stamp, title, f"{OUT}{name}_封面.png")
        print(name, len(cols), "栏", len(pages), "页", [c.height for c in cols], "COL_H", COL_H)
