import sys, subprocess, numpy as np, soundfile as sf, re, os
sys.path.insert(0,"/tmp/tts")
import sherpa_onnx
from PIL import Image, ImageDraw, ImageFont
D="/tmp/tts/vits-melo-tts-zh_en/"; P="/home/claude/socialmedia/serenity/posts/20261104/"
OUT="/tmp/claude-0/vid/"
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=D+"model.onnx",lexicon=D+"lexicon.txt",tokens=D+"tokens.txt",dict_dir=D+"dict"),num_threads=4),rule_fsts=f"{D}phone.fst,{D}date.fst,{D}number.fst")
tts=None
# (页, 显示字幕, 朗读文本)
S=[
(1,"Serenity说，第一家美国纯人形机器人公司，11月5日开始交易。",None),
(1,"2026年11月4日，00点06分。",None),
(1,"她说，Agility Robotics的合并，今天获批了。",None),
(1,"股票代码AGLT，预计11月4日完成交割，11月5日开始交易。",None),
(1,"她称它是美国第一家纯人形机器人公司。",None),
(1,"她说，公司背后的支持者有英伟达、亚马逊、富士康、软银等等，",None),
(1,"目标是在仓库和制造业里，替代人类的工作。",None),
(1,"这次走的是SPAC，也就是先上市的空壳公司，再去收购一家真正的企业。",None),
(1,"她给出的赎回数据是：4140万股公众股里，约61.48%被赎回，约2545万股，",None),
(1,"剩下约1595万股可以交易。",None),
(1,"她提醒，股数大幅减少，股价可能出现剧烈波动。",None),
(1,"她还披露，今天看到消息后买了CCXI的股票，目前持仓，并说这不是投资建议。",None),
(2,"她附了CCXI的行情截图：美东11月3日上午9点59分，报10.26美元，涨10.44%。",None),
(2,"另一张是Agility官方的帖子：",None),
(2,"Churchill Capital Corp XI的股东今天批准了合并，预计11月4日交割。",None),
(2,"再看公司公告。投票中超过84%赞成，",None),
(2,"信托账户约1.64亿美元，富士康领投的私募融资约2.01亿美元，每股10美元。",None),
(2,"算上合并宣布后已经到账的1亿美元股权融资，总融资约4.65亿美元。",None),
(2,"AGLT和认股权证AGLTW，从11月5日起在纳斯达克交易。",None),
(2,"Agility的主打产品是Digit人形机器人，总部在俄勒冈州塞勒姆。",None),
(2,"赎回的数字出自Serenity，公司公告里没有列出。",None),
]
fix={"AGLTW":"A G L T W","AGLT":"A G L T","CCXI":"C C X I","SPAC":"S P A C","10.44%":"百分之十点四四","61.48%":"百分之六十一点四八","84%":"百分之八十四","4140万":"四千一百四十万","2545万":"两千五百四十五万","1595万":"一千五百九十五万","1.64亿":"一点六四亿","2.01亿":"二点零一亿","4.65亿":"四点六五亿","10.26美元":"十点二六美元","每股10美元":"每股十美元","1亿美元":"一亿美元","00点06分":"零点零六分"}
def speak(t):
    for k in sorted(fix,key=len,reverse=True): t=t.replace(k,fix[k])
    return t

import soundfile as sf
GAP=0.30; wavs=[]
for i in range(len(S)):
    w,sr=sf.read(f"/tmp/claude-0/vid/zvwav/{i:02d}.wav",dtype="float32"); wavs.append(w)
OUT="/tmp/claude-0/vid/zvout/"; os.makedirs(OUT,exist_ok=True)
FONT=ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",38,index=2)
pages={1:Image.open(P+"04_AGLT人形机器人新股_拼图_1.png").convert("RGB"),2:Image.open(P+"04_AGLT人形机器人新股_拼图_2.png").convert("RGB")}
def frame(pg,chunk):
    im=pages[pg].copy(); d=ImageDraw.Draw(im)
    b=d.textbbox((0,0),chunk,font=FONT); w=b[2]-b[0]
    x=(im.width-w)/2-b[0]; y=640-b[1]
    for dx in(-2,0,2):
        for dy in(-2,0,2): d.text((x+dx,y+dy),chunk,font=FONT,fill="black")
    d.text((x,y),chunk,font=FONT,fill="white"); 
    out=Image.new("RGB",(1274,716),"black"); out.paste(im,(0,0)); return out
audio=[]; concat=[]; n=0
for (pg,sub,_),w in zip(S,wavs):
    dur=len(w)/sr+GAP; audio.append(w); audio.append(np.zeros(int(GAP*sr),dtype=np.float32))
    chunks=[c for c in re.split(r"(?<=[，：、])",sub) if c]
    # 过长的块再按字数均分
    chunks=[c.rstrip("，：、。") for c in chunks]; tot=sum(len(c) for c in chunks)
    for c in chunks:
        c=c.rstrip("，：、。"); 
        fn=f"{OUT}f{n:03d}.png"; frame(pg,c).save(fn)
        concat.append(f"file '{fn}'\nduration {dur*len(c)/max(tot,1):.3f}"); n+=1
concat.append(f"file '{fn}'")
open(OUT+"list.txt","w").write("\n".join(concat))
sf.write(OUT+"vo.wav",np.concatenate(audio),sr)
print("total",sum(len(x) for x in audio)/sr)
