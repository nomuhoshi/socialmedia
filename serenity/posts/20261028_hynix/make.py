# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W,H=1273,716
FD='/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc'
def font(w,sz,idx=2): return ImageFont.truetype(FD%w,sz,index=idx)

# ---------- stitched long image ----------
off=[0,1338,1799,2499,3934]; S=[335,1668,2129,2829,4264,3934+2215]
parts=[]
for k in range(5):
    im=Image.open(f'src/s{k+1}.png').convert('RGB')
    parts.append(im.crop((0,S[k]-off[k],1206,S[k+1]-off[k])))
long=Image.new('RGB',(1206,sum(p.height for p in parts)))
y=0
for p in parts: long.paste(p,(0,y)); y+=p.height
long.paste((0,0,0),(1186,0,1206,long.height)); long.save('long.png'); print('long',long.size)

# ---------- blank-row cut points ----------
g=np.asarray(long.convert('L'))[:,:1170]; blank=(g.max(axis=1)<70)
def nearest_blank(t,r=330):
    for d in range(0,r):
        for y in (t-d,t+d):
            if 0<y<len(blank)-5 and blank[y-2:y+3].all(): return y
    return t
SC=0.495; colh=int(520/SC); n=6
cuts=[0]
for i in range(1,n): cuts.append(nearest_blank(int(i*long.height/n)))
cuts.append(long.height); print(cuts)
cols=[long.crop((0,cuts[i],1206,cuts[i+1])) for i in range(n)]
for pg in range(3):
    cv=Image.new('RGB',(W,H),(0,0,0)); ims=[]
    for c in cols[pg*2:pg*2+2]:
        sc=min(SC,520/c.height); ims.append(c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS))
    gap=24; tot=sum(i.width for i in ims)+gap; x=(W-tot)//2
    for i in ims: cv.paste(i,(x,24)); x+=i.width+gap
    cv.save(f'拼图_{pg+1}_1273x716.png')

# ---------- cover ----------
T=Image.open('../../references/封面模板_1273x716.png').convert('RGB')   # 2292x1434
cx,cy,r=690,620,286
av=T.crop((cx-r,cy-r,cx+r,cy+r)).resize((318,318),Image.LANCZOS)
m=Image.new('L',(318,318),0); ImageDraw.Draw(m).ellipse((0,0,317,317),fill=255)
cov=Image.new('RGB',(W,H),(0,0,0)); AX,AY=383,300
cov.paste(av,(AX-159,AY-159),m); d=ImageDraw.Draw(cov)
TX=592
d.text((TX,AY-86),'Serenity',font=font('Medium',66),fill='white',anchor='ls')
d.text((TX,AY+10),'最新帖子解读',font=font('Medium',66),fill='white',anchor='ls')
d.text((TX,AY+106),'20261028 11:11',font=font('Medium',66),fill='white',anchor='ls')
d.text((AX,AY+159+70),'海力士：产能卖到2029年',font=font('Bold',50),fill='white',anchor='mm')
cov.save('封面_1273x716.png')
