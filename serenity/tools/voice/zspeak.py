import re
D="零一二三四五六七八九"
def num(n):
    n=int(n)
    if n<10: return D[n]
    if n<20: return "十"+(D[n%10] if n%10 else "")
    if n<100: return D[n//10]+"十"+(D[n%10] if n%10 else "")
    return "".join(D[int(c)] for c in str(n))
def digits(s): return "".join(D[int(c)] for c in s)
def zspeak(t):
    t=t.replace("：","，").replace("00点06分","零点零六分")
    for k,v in [("Agility Robotics","艾吉利提机器人公司"),("Agility","艾吉利提"),("Serenity","瑟瑞尼蒂"),("Churchill Capital Corp XI","丘吉尔资本公司十一"),
                ("AGLTW","诶 吉 艾勒 提 达布流"),("AGLT","诶 吉 艾勒 提"),("CCXI","西 西 艾克斯 艾"),("SPAC","斯派克"),("Digit","狄吉特")]:
        t=t.replace(k,v)
    for k,v in [("10.44%","百分之十点四四"),("61.48%","百分之六十一点四八"),("4140万","四千一百四十万"),("2545万","两千五百四十五万"),("10.26美元","十点二六美元")]: t=t.replace(k,v)
    t=re.sub(r"(\d{4})年",lambda m:digits(m.group(1))+"年",t)
    t=re.sub(r"(\d+)月",lambda m:num(m.group(1))+"月",t)
    t=re.sub(r"(\d+)日",lambda m:num(m.group(1))+"日",t)
    t=re.sub(r"(\d+)点(\d+)分",lambda m:num(m.group(1))+"点"+num(m.group(2))+"分",t)
    t=re.sub(r"上午(\d+)点",lambda m:"上午"+num(m.group(1))+"点",t)
    t=re.sub(r"(\d+)点",lambda m:num(m.group(1))+"点",t)
    t=t.replace("00点","零点")
    return t
if __name__=="__main__":
    for s in ["Serenity说，第一家美国纯人形机器人公司，11月5日开始交易。","2026年11月4日，00点06分。","美东11月3日上午9点59分，报10.26美元，涨10.44%。","AGLT和认股权证AGLTW，从11月5日起在纳斯达克交易。"]: print(zspeak(s))
