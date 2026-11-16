# Serenity 帖子解读视频 · 继承文件（2026-11-15 19:45 JST，serenity → 下一个 Grok Bot）

对老大称「老大」，用中文。主线：把 Serenity（X @aleabitoreddit）的帖子做成解读视频，发到老大的 B 站「X信息差」（UID 434827378）。

## 一、当前进度（接手从这里开始）
- Serenity 已扫到 **2026-11-15 17:10 JST**。下一次只看这之后的帖子。
- 11-15 两次巡帖都没发：11:00 没有新帖；17:00 只有一条 15:27 JST（西方媒体报道 NVDA/黄仁勋 vs 中共官媒），属于中国政治敏感，已跳过。
- 最近发布：
  | 日期 | 标题 | BV | 充电 |
  |---|---|---|---|
  | 11-14 11:00 | 三星洽购散热商，已买光子专利：并购将加速 | BV1pZWC6dESG | 充电，试看30s |
  | 11-14 11:00 | 传云厂商不再怕黄仁勋，他不看好克雷斯掌舵 | BV1PoWC64Erp | 免费 |
  | 11-14 11:00 | 30人排队走5人也没桌：他仍看多算力 | BV1WoWC64EfE | 免费 |
  | 11-14 11:00 | 两大基金致信董事会：别急着换黄仁勋 | BV1wcWy69E6e | 免费 |
  | 11-14 16:49 | 从洗碗工到5万亿美元公司，他说被逼辞职（Be Jensen） | BV1UJsG65Ega | 免费 |
  | 11-14 19:42 | 快2.5倍还更聪明，谷歌说它是日常主力（非 Serenity：Gemini 4 Hydrogen） | BV1Trs363EgT | 免费 |
- 待老大决定：要不要补一期 Gemini 4 Carbon（11-10 发布）。老大没回，不要自己做。
- 全部历史记录：GitHub nomuhoshi/socialmedia → serenity/posts/<日期_主题>/文案.md（含 BV）。

## 二、硬规则
1. 图片、标题、配音稿、充电建议全部来自 claude.ai 置顶对话「serenity」 https://claude.ai/chat/89c57bce-2e86-4b82-9a35-d29239f4d768 （盒子浏览器已登录）。**不要自己做图。**
2. 配音稿一字不改，不核对、不评论 Claude 内容。
3. Claude 额度用完时**绝不点「Use reset」**，告诉老大什么时候恢复。
4. Claude 建议充电 → 开「充电专属视频」，试看约片长 30%（选最接近的预设）；否则不开。
5. 老大已长期授权：做好直接发 B 站，不用问。
6. 长活约每 3 分钟向老大汇报一次进度。
7. 选帖避坑：
   - 丑闻、热点可以做（如黄仁勋丑闻）。
   - 跳过一切中国政治敏感内容、涉及中国领导人的帖子；标题也不能往中国上带（「中国抢英伟达」这种不行）。
   - 提到台湾一律「中国台湾」（Claude 已知，不用每次说）。
   - 被限的 BV15aWX6vErq 不申诉、不重投。
   - 低信息量的（投票结果、短回复）跳过。
8. 2026-11-13 起只做 Serenity，不再主动找其他账号的热点。老大点名的非 Serenity 帖子照做：把该账号头像发给 Claude 替换封面上的 Serenity 头像。

## 三、每条帖子的步骤
1. **找帖**：可用 X 公开读取（search_posts_all, from:aleabitoreddit）列出新帖；媒体/头像从 pbs.twimg.com 下载。
2. **截图**：未登录 X 也能看。用原生屏幕截图（不要浏览器截图），约 150% 缩放，拍全正文、引用帖、配图（配图另存大图）、时间/浏览量栏。存 /workspace/serenity/<日期_主题>/x_shots/。
3. **批量发 Claude**：所有选中的帖子一次性发到「serenity」对话，每篇标编号、作者、日本时间（X 显示美东时间，日本 = 美东 + 14 小时）。例：「最新帖子。时间栏显示的是美东时间，日本时间是 YYYY年MM月DD日 HH:MM。」Claude 要确认就回「确认，按你写的来。」；它提归档 GitHub 就忽略。图按顺序下载到 claude_out/，全文回复存 reply.txt。
4. **分段**：配音稿一字不改，按句子拼成每段 ≤290 字，存 v/c1.txt、c2.txt……
5. **配音（必剪，Wine）**：
   - 启动：`cd /workspace/bcut && DISPLAY=:34 nohup ./run-bcut.sh >/tmp/bcut.log 2>&1 &`（在 :34 上开，先关掉 :2 上的旧实例）。
   - 新建 16:9 工程 → 文本 → 朗读（文字转音频）→ 特色 → **曼波**（小心别点到别的声音，如激昂张飞）。
   - 每段 `xclip -selection clipboard < cN.txt` 后 Ctrl+V，每段生成独立片段，保存。
   - mp3 在 `/home/box/.wine-bcut/drive_c/users/box/Documents/Bcut Drafts/<uuid>/`，按顺序 ffmpeg 转成 v/tts1.wav、tts2.wav……
   - Wine 若从盒子消失：apt 镜像过不了代理，用 curl 下 wine-10.0 的 deb 再 dpkg 安装。
6. **合成**（路径相对 --dir）：
   `cd <帖子文件夹> && python3 /workspace/serenity/render_serenity.py --dir v --images 01_cover.png 02_collage.png --chunks c1.txt c2.txt --tts tts1.wav tts2.wav --cut-after "<日期时间那一句>" --output X.mp4`
   - 1.5 秒无声封面前导；`--cut-after` 必须是完整的逗号/句号分隔短句；有第二张拼图时在开始讲它的前一句切。
   - 跑完看 check_*.png。
   - 上传前必须压缩：`ffmpeg -i X.mp4 -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 128k X_small.mp4`（约 3-4MB；~99MB 的原片会卡在 100% 上传中）。
7. **发布**：https://member.bilibili.com/platform/upload/video/frame （盒子浏览器已登录）。
   - 标题用 Claude 原样（B 站标题 ≤20 字）。
   - 封面用 Claude 的封面图，勾「双比例同步改动」。
   - 分区「资讯」（会偶尔跳成 vlog，提交前再确认）。页面上没有「自制」选项，跳过。
   - 标签：公司名、美股、serenity、投资（删自动标签；检查 serenity 有没有被截成 nity）。
   - 创作声明「个人观点，仅供参考」；简介留空；充电按规则 4。
   - 上传到 100% 再点立即投稿，把 BV 链接报给老大。
8. **归档**：
   `cd /workspace/socialmedia && git checkout -- serenity/__pycache__; git pull --rebase`
   把封面、拼图、文案.md（标题、来源链接、配音稿、充电、BV）放到 serenity/posts/<文件夹>/，
   `git -c user.name=nomuhoshi -c user.email=nomuhoshi@users.noreply.github.com commit` 后 push。不提交 mp4。

## 四、定时巡帖
原来在 serenity 里有一个每天 11:00、17:00（JST）的定时任务「Serenity 帖子巡查搬运」，步骤同上；没有新帖或没有值得搬的就安静结束，有发布就列出标题和 BV 链接。接手后请在你那边建同样的定时任务，并确认 serenity 那边的已暂停，避免重复发。

## 五、参考
- 本机文件：/workspace/serenity/（每篇一个文件夹；示例 20261111_wt 三张图充电、20261112_ant2 两张图免费、20261114_batch6 批量四篇）。
- 渲染脚本：/workspace/serenity/render_serenity.py；封面工具 nomuhoshi/socialmedia serenity/cover.py（一般用不到，图都由 Claude 出）。
- 旧版交接：/workspace/serenity/HANDOFF_old_20261112.md。

## 六、怎么选 Serenity 以外的帖子（老大 2026-11-11 定，2026-11-16 补充）
现状：2026-11-13 起定时巡帖只扫 Serenity。别的账号只在老大点名时做（例：11-14 的 Gemini 4 Hydrogen）。哪天老大说恢复找热点，就按下面这套来。

**看哪些号（固定名单）**
- 马斯克及其公司：@elonmusk、@SpaceX、@Tesla、@xAI
- AI 公司和大佬：@OpenAI、@AnthropicAI、@GoogleDeepMind、@sundarpichai、@sama、@karpathy
- 美股和财经：@unusual_whales、@KobeissiLetter，以及类似的大 V
- 热点新闻：X 热门和 news

**怎么挑（尽量省额度）**
1. 先粗筛，这一步不用 AI：用 X 公开读取（search_posts_all），只看过去约 24 小时、或者上次巡帖之后发的帖子，按浏览、点赞、转发排序。
2. 只把排在前十几条的拿来判断，选 3 篇左右；没有够格的就不搬，不要凑数。
3. 判断标准有三条：
   - 有用：观众看完能学到东西，或者能拿来参考投资决定。
   - 有流量：浏览量高（例子里的帖子多在几十万到几百万）、话题新。
   - 有信息量：有具体的数字、事实、发布内容。纯情绪、梗、投票结果、短回复都跳过。
   方向是科技、美股、资讯、热点新闻。
4. 优先选这两类：新模型或新产品发布当天的官方帖，当天美股的大新闻（比如英伟达暴跌）。和已经发过的视频重复的不选。
5. 同一件事有多篇帖子时，可以合成一个视频。比如 Gemini 那期用的是 DeepMind 的发布帖加 Sundar Pichai 的说明帖。
6. 避坑规则和 Serenity 一样：丑闻、热点可以做；中国政治敏感、涉及中国领导人的帖子一律跳过，标题也不能往中国上带；台湾写「中国台湾」。

**做的时候和 Serenity 的区别**
- 截图时把作者头像也下载下来（pbs.twimg.com），和截图一起发给 Claude，请它把封面上的 Serenity 头像和名字换成这个作者的。Claude 那边已经有马斯克和 DeepMind 的封面模板。
- 标签换成相关的公司名或人名，再加上美股、投资等，不写 serenity。
- 其余流程一样：批量发给 Claude，用它原样给的稿子，必剪配音，合成，直接发布，归档到 serenity/posts/。
