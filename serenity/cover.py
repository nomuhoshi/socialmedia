# -*- coding: utf-8 -*-
# 用法: python3 cover.py 20261028 11:11 "海力士：产能卖到2029年" out.png
# 安全区：B站 4:3 首页推荐裁切约保留中间 x∈[197,1076], y∈[29,688]（1273×716 画布），所有文字留在 x 215–1058 内
import sys
from PIL import Image, ImageDraw, ImageFont
W,H=1273,716; FD='/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc'
font=lambda w,s:ImageFont.truetype(FD%w,s,index=2)
def make(date,tm,title,out,safe_preview=False):
    T=Image.open('references/封面模板_1273x716.png').convert('RGB'); cx,cy,r=690,620,286
    D=250; av=T.crop((cx-r,cy-r,cx+r,cy+r)).resize((D,D),Image.LANCZOS)
    m=Image.new('L',(D,D),0); ImageDraw.Draw(m).ellipse((0,0,D-1,D-1),fill=255)
    cov=Image.new('RGB',(W,H)); AX,AY=470,285; cov.paste(av,(AX-D//2,AY-D//2),m); d=ImageDraw.Draw(cov); TX=630
    for dy,t in ((-62,'Serenity'),(20,'最新帖子解读'),(102,f'{date} {tm}')): d.text((TX,AY+dy),t,font=font('Medium',56),fill='white',anchor='ls')
    d.text((AX,AY+D//2+68),title,font=font('Bold',44),fill='white',anchor='mm')
    bb=d.textbbox((AX,AY+D//2+68),title,font=font('Bold',44),anchor='mm'); print('title x',bb[0],bb[2]); cov.save(out)
    if safe_preview:
        p=cov.copy(); ImageDraw.Draw(p).rectangle((197,29,1076,688),outline=(255,60,60),width=3); p.save('/tmp/claude-0/safe.png')
if __name__=='__main__': make(*sys.argv[1:5])
