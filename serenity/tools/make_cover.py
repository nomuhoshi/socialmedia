"""Serenity 封面：python3 make_cover.py "20261017 06:25" "封面标题" out.png
以用户提供的封面（cover_tpl.png，1584x993）为底：保留头像、Serenity、最新帖子解读，
只替换日期行和封面标题行，最后缩放并裁成 1273x716。"""
import sys
from PIL import Image, ImageDraw, ImageFont

TPL = "cover_tpl.png"
INTER = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
W, H = 1273, 716

# 模板中实测位置（1584x993 坐标）
DATE_X, DATE_TOP, DATE_H = 736, 512, 68          # 数字字高
TITLE_CX, TITLE_TOP, TITLE_REF_W = 476.5, 671, 706  # 标题以头像圆心 x 居中  # “戴尔称存储短缺或持续四年”宽度
TITLE_REF = "戴尔称存储短缺或持续四年"


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

    # 标题字号按参考标题宽度标定，保持与原图一致的字大小
    f_title = fit_font(CJK, 2, TITLE_REF, TITLE_REF_W, "w")
    rb = f_title.getbbox(TITLE_REF)
    b = f_title.getbbox(title)
    # 标题过长时缩小字号，保证以圆心居中后左右都不出画面（左右至少留 60px）
    max_w = TITLE_REF_W  # 最宽不超过参考标题，超出就缩小字号
    if b[2] - b[0] > max_w:
        f_title = fit_font(CJK, 2, title, max_w, "w")
        b = f_title.getbbox(title)
        print("WARN 标题过长，已缩小字号:", title)
    tx = TITLE_CX - (b[2] - b[0]) / 2 - b[0]
    dr.text((tx, TITLE_TOP - rb[1]), title, font=f_title, fill="white")

    # B站封面安全区：部分场景按 4:3 显示，只保留中间 955px 宽（x 159–1114）。
    # 把整块内容（标题最左 123.5 → 日期最右 1436，模板坐标）等比缩小放进安全区，左右各留 20px。
    SAFE_L, SAFE_R = (W - H * 4 / 3) / 2 + 20, (W + H * 4 / 3) / 2 - 20
    L, R = TITLE_CX - TITLE_REF_W / 2, 1436
    f = (SAFE_R - SAFE_L) / (R - L)
    ox = SAFE_L - f * L
    oy = H / 2 - f * (230 + 726) / 2
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
