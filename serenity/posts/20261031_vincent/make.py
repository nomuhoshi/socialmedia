"""第八批：vincent（@SPCX100T）。马斯克 10/31 帖 + vincent 回复；vincent 10/8 置顶长帖。"""
import math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/work"); import make_cover
A = "/mnt/user-data/attachments/a4464ac6-ea71-5dc8-9737-36e4cce7c493/"
OUT = "/home/claude/work/batch8/out/"
K = 1206 / 920; CW = 1180
W, H, TOP, BOTTOM, GAP, PGAP = 1273, 716, 20, 125, 24, 50
S = 0.37
COL_H = int((H - TOP - BOTTOM) / S)

def crop(f, t, b):
    im = Image.open(A + f).convert("RGB"); k = im.width / 920
    return im.crop((0, round(t * k), round(1160 * k / (1184 / 920)), round(b * k))).resize((CW, round((b - t) * K)), Image.LANCZOS) if im.width != 1206 else im.crop((0, round(t * K), CW, round(b * K)))
def stack(parts, gaps):
    st = Image.new("RGB", (CW, sum(p.height for p in parts) + sum(gaps)), "black"); y = 0
    for i, p in enumerate(parts):
        st.paste(p, (0, y)); y += p.height + (gaps[i] if i < len(gaps) else 0)
    return st
def split(strip):
    blank = (np.array(strip.convert("L")) > 30).sum(1) == 0
    n = math.ceil(strip.height / COL_H); target = strip.height / n
    segs, start = [], 0
    while strip.height - start > COL_H:
        cut = min(start + COL_H, round(start + target * 1.05))
        while cut > start + COL_H // 3 and not blank[cut - 40:cut].all(): cut -= 1
        if not blank[cut - 40:cut].all(): print("WARN 切在非空白", cut)
        segs.append((start, cut)); start = cut
        while start < strip.height and blank[start]: start += 1
    segs.append((start, strip.height))
    return [strip.crop((0, a, CW, b)) for a, b in segs]

M = "c9e7fdd1-image.png"; P1 = "aa6ab9fd-image.png"; P2 = "c77d7434-image.png"
musk = stack([crop(M, 245, 1040), crop(M, 1475, 1682)], [70])          # 马斯克帖 + vincent 回复
pinned = stack([crop(P1, 255, 1675), crop(P2, 725, 1655)], [0])        # 置顶长帖，两张无缝接
for i, s in enumerate([musk, pinned]): s.save(f"{OUT}_长图{i}.png")
cols = split(musk) + split(pinned)
pages = [cols[i:i + 2] for i in range(0, len(cols), 2)]
for n, pg in enumerate(pages, 1):
    ims = [im.resize((round(im.width * S), round(im.height * S)), Image.LANCZOS) for im in pg]
    c = Image.new("RGB", (W, H), "black")
    x = (W - sum(i.width for i in ims) - GAP * (len(ims) - 1)) // 2
    y0 = TOP + max(0, (H - TOP - BOTTOM - max(i.height for i in ims)) // 2)
    for im in ims: c.paste(im, (x, y0)); x += im.width + GAP
    c.save(f"{OUT}01_马斯克轨道算力_拼图_{n}.png")
print(len(cols), "栏", len(pages), "页")
make_cover.TPL = "/home/claude/work/cover_tpl_vincent.png"
make_cover.make("20261031 11:41", "马斯克：轨道算力碾压地面", f"{OUT}01_马斯克轨道算力_封面.png")
