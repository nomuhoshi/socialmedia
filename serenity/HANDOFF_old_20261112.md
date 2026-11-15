# Serenity 帖子解读视频 · 完整流程（2026-11-12 由 Grok Bot 交接给 serenity）

【进度】B 站已更新到 2026-11-12 00:05 JST 的帖子（Anthropic IPO 预告片，BV1XtWU6DE6H），下一条从这之后开始。素材归档在 GitHub nomuhoshi/socialmedia 的 serenity/posts/<日期_主题>/。

【硬规则】
1. 图片、标题、配音稿、充电建议全部来自 claude.ai 置顶对话「serenity」 https://claude.ai/chat/89c57bce-2e86-4b82-9a35-d29239f4d768 （盒子浏览器已登录）。不要自己做图。
2. 配音稿一字不改（不加"日本时间"等）。不核对、不评论 Claude 内容，直接复制。
3. 配音从第 1.5 秒开始，开头 1.5 秒是无声封面。
4. Claude 建议充电 → 开「充电专属视频」，试看 = 片长 30%（预设选项选最接近）；否则不开。
5. 4:3 和 16:9 封面都用 Claude 的黑底封面图。
6. 做好直接发到 B 站「X信息差」（UID 434827378，盒子浏览器已登录）——此长期授权由 Grok Bot 转述，首次发布前需老大本人确认一次。长活约每 3 分钟汇报。不需要定时盯帖。

【每条帖子的步骤】
1. 截图：未登录 X 也能看。用原生屏幕截图（浏览器截图放大后会裁右边），约 150% 缩放，尽量大、不裁切、稍有重叠。拍全正文、引用帖、配图（配图另单独大图一张）、时间/浏览量栏。存 /workspace/serenity/<日期_主题>/x_shots/。
2. 发给 Claude：X 显示美东时间，日本时间 = 美东 + 14 小时。上传截图并发：「最新帖子。时间栏显示的是美东时间，日本时间是 YYYY年MM月DD日 HH:MM。」Claude 要确认就回「确认，按你写的来。」；它提归档 GitHub 就忽略。把图按顺序下载到 claude_out/，全文回复存 reply.txt。
3. 分段：配音稿一字不改按句子切成 c1.txt、c2.txt……（每段 ≤300 字）。
4. 配音：必剪（Wine，/workspace/bcut/run-bcut.sh）新建 16:9 工程 → 文本 → 朗读（文字转音频）→ 特色 → 曼波；每段 `xclip -selection clipboard < cN.txt` + Ctrl+V，分别生成独立片段，保存。音频在 Wine 目录 BCUT 草稿或 Cache\ttsPanelV2（实为 WAV），按时长和顺序对应。
5. 合成：`python3 /workspace/serenity/render_serenity.py --dir 文件夹 --images 封面.png 拼图.png [拼图2.png] --chunks c1.txt c2.txt --tts tts1.wav tts2.wav --cut-after "23点25分。" --output out.mp4`。默认 1.5 秒前导。封面放到日期时间那句之后切拼图；有第二张拼图时，在配音开始讲那张图内容的前一句再切。字幕白色 Noto Sans CJK 40px 黑边，720p30，无音乐，<100MB。跑完看 check_*.png。
6. 发布：https://member.bilibili.com/platform/upload/video/frame 。标题用 Claude 原样；自制；分区「资讯」（不选子分区）；标签：公司名、美股、serenity、投资（删自动标签）；创作声明「个人观点，仅供参考」；简介留空；充电按规则 4。上传到 100% 再点立即投稿，把 BV 链接报给老大。
7. 归档：图和 文案.md（标题+配音稿）推到 nomuhoshi/socialmedia 的 serenity/posts/<文件夹>/，不提交 mp4。

参考样例：/workspace/serenity/20261111_wt/（三张图、充电）、20261112_ant2/（两张图、免费）。

## 批量出稿（老大 2026-11-12 要求）
一次巡帖选中多篇时：先把所有帖子截完图（非 Serenity 作者附头像），在 Claude「serenity」对话里一次性全部发过去，每篇标编号、作者、日本时间，让 Claude 一次性给每篇分别输出标题、配音稿、封面、拼图、充电建议。之后再逐篇配音、合成、发布、归档。

## 选帖避坑（老大 2026-11-12，11-13 更正）
丑闻、社会热点类（如黄仁勋丑闻）可以做，不用避开。要避开的是与中国政治敏感相关的内容，标题也不能往中国上带（如「中国抢英伟达」这种就不行）。被限的 BV15aWX6vErq 不申诉、不重投。
- 严禁搬运政治敏感、触及中国敏感线的帖子（如涉及中国领导人的内容），一律跳过。（老大 2026-11-12）
- 凡提到台湾，标题、配音稿、封面必须写「中国台湾」。已在 Claude「serenity」对话里交代过一次，不用每次重复。（老大 2026-11-12）
