"""Serenity 封面：python3 make_cover.py "20261017 06:25" "封面标题" out.png
以用户提供的封面（cover_tpl.png，1584x993）为底：保留头像、名字、第二行“最新信息差”，
只替换日期行和封面标题行，最后缩放并裁成 1273x716。"""
import sys
from PIL import Image, ImageDraw, ImageFont

import os
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "cover_tpl.png")   # 改 make_cover.TPL 可换 cover_tpl_vincent.png / cover_tpl_musk.png
INTER = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"   # 标题用 Bold
W, H = 1273, 716

# 模板中实测位置（1584x993 坐标）
DATE_X, DATE_TOP, DATE_H = 736, 512, 68          # 数字字高
TITLE_CX, TITLE_TOP, TITLE_REF_W = 476.5, 671, 706 * 1.3  # 标题以头像圆心 x 居中  # “戴尔称存储短缺或持续四年”宽度
TITLE_REF = "戴尔称存储短缺或持续四年"
BOTTOM_ROW = 726  # 内容最下沿（模板坐标），用于垂直居中
TITLE_SCALE = 1.3  # 标题大小 = 原版 × 1.3（2026-11-12 定），仍以头像圆心居中
TITLE_MAX_H = None  # 设为数字则启用“大标题”模式（标题字高上限，模板像素）


def fit_font(path, idx, text, target, measure="h"):
    size = 80
    for _ in range(4):
        f = ImageFont.truetype(path, size, index=idx)
        b = f.getbbox(text)
        cur = (b[3] - b[1]) if measure == "h" else (b[2] - b[0])
        size = max(8, round(size * target / cur))
    return ImageFont.truetype(path, size, index=idx)


def draw_top_left(dr, x, top, text, font):
    b = font.getbbox(text)
    dr.text((x - b[0], top - b[1]), text, font=font, fill="white")


def make(stamp, title, out):
    img = Image.open(TPL).convert("RGB")
    dr = ImageDraw.Draw(img)
    # 抹掉原日期和原标题
    dr.rectangle((700, 495, 1584, 600), fill="black")
    dr.rectangle((100, 650, 1584, 760), fill="black")

    f_date = fit_font(INTER, 0, "20261017 06:25", DATE_H, "h")
    draw_top_left(dr, DATE_X, DATE_TOP, stamp, f_date)

    # 标题：先按目标宽度放大，再用最大字高封顶（TITLE_MAX_H=None 时沿用旧逻辑）
    if TITLE_MAX_H:
        f_title = fit_font(CJK, 2, title, TITLE_REF_W, "w")
        b = f_title.getbbox(title)
        if b[3] - b[1] > TITLE_MAX_H:
            f_title = fit_font(CJK, 2, title, TITLE_MAX_H, "h")
            b = f_title.getbbox(title)
        tw, th = b[2] - b[0], b[3] - b[1]
        tx = TITLE_CX - tw / 2 - b[0]
        dr.text((tx, TITLE_TOP - b[1]), title, font=f_title, fill="white")
        L_over, bottom_row = TITLE_CX - max(tw, 706) / 2, TITLE_TOP + th
    else:
        f_title = fit_font(CJK, 2, TITLE_REF, TITLE_REF_W, "w")
        rb = f_title.getbbox(TITLE_REF)
        b = f_title.getbbox(title)
        max_w = TITLE_REF_W
        if b[2] - b[0] > max_w:
            f_title = fit_font(CJK, 2, title, max_w, "w")
            b = f_title.getbbox(title)
            print("WARN 标题过长，已缩小字号:", title)
        tx = TITLE_CX - (b[2] - b[0]) / 2 - b[0]
        dr.text((tx, TITLE_TOP - rb[1]), title, font=f_title, fill="white")
        L_over, bottom_row = None, BOTTOM_ROW
        if TITLE_SCALE != 1.0:  # 标题放大 k 倍；整体缩放只随标题实际宽度变化（≤706 时与原版完全一致）
            L_over = TITLE_CX - max(b[2] - b[0], 706) / 2
            bottom_row = TITLE_TOP + (rb[3] - rb[1])

    # B站封面安全区：部分场景按 4:3 显示，只保留中间 955px 宽（x 159–1114）。
    # 把整块内容（标题最左 123.5 → 日期最右 1436，模板坐标）等比缩小放进安全区，左右各留 20px。
    SAFE_L, SAFE_R = (W - H * 4 / 3) / 2 + 20, (W + H * 4 / 3) / 2 - 20
    L, R = (L_over if L_over is not None else TITLE_CX - TITLE_REF_W / 2), 1436
    f = (SAFE_R - SAFE_L) / (R - L)
    ox = SAFE_L - f * L
    oy = H / 2 - f * (230 + bottom_row) / 2
    small = img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "black")
    canvas.paste(small, (round(ox), round(oy)))
    # 自检：所有非黑像素必须在安全区内
    import numpy as np
    a = np.array(canvas.convert("L")) > 40
    xs = np.where(a.any(0))[0]
    if xs[0] < SAFE_L - 20 or xs[-1] > SAFE_R + 20:
        print(f"WARN 超出安全区: x={xs[0]}–{xs[-1]}", title)
    canvas.save(out)


if __name__ == "__main__":
    make(*sys.argv[1:4])


def make_pc(stamp, title, out, max_w=900, max_h_tpl=104):
    """标题相对整个页面居中（x=W/2）；头像+三行字整体居中放进 4:3 安全区。"""
    import numpy as np
    img = Image.open(TPL).convert("RGB")
    dr = ImageDraw.Draw(img)
    dr.rectangle((700, 495, 1584, 600), fill="black")
    dr.rectangle((100, 650, 1584, 760), fill="black")      # 擦掉原标题
    f_date = fit_font(INTER, 0, "20261017 06:25", DATE_H, "h")
    draw_top_left(dr, DATE_X, DATE_TOP, stamp, f_date)
    SAFE_L, SAFE_R = (W - H * 4 / 3) / 2 + 20, (W + H * 4 / 3) / 2 - 20
    L, R = 277, 1436                                        # 头像左缘 → 日期右缘
    f = (SAFE_R - SAFE_L) / (R - L)
    ox = SAFE_L - f * L
    bottom = 671 + max_h_tpl
    oy = H / 2 - f * (230 + bottom) / 2
    small = img.resize((round(img.width * f), round(img.height * f)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), "black")
    canvas.paste(small, (round(ox), round(oy)))
    # 标题直接画在画布上：先按宽度，再按字高封顶
    dr2 = ImageDraw.Draw(canvas)
    ft = fit_font(CJK, 2, title, max_w, "w")
    b = ft.getbbox(title)
    if b[3] - b[1] > max_h_tpl * f:
        ft = fit_font(CJK, 2, title, max_h_tpl * f, "h"); b = ft.getbbox(title)
    tw = b[2] - b[0]
    tx = W / 2 - tw / 2 - b[0]
    ty = oy + f * 671 - b[1]
    dr2.text((tx, ty), title, font=ft, fill="white")
    a = np.array(canvas.convert("L")) > 40
    xs = np.where(a.any(0))[0]; ys = np.where(a.any(1))[0]
    if xs[0] < SAFE_L - 20 or xs[-1] > SAFE_R + 20:
        print(f"WARN 超出安全区: x={xs[0]}–{xs[-1]}", title)
    print("f=%.3f x=%d–%d y=%d–%d" % (f, xs[0], xs[-1], ys[0], ys[-1]))
    canvas.save(out)
