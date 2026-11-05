# tools：封面与拼图脚本（Serenity / vincent 通用）

- `make_cover.py`：封面。底图 `cover_tpl.png`（Serenity）或 `cover_tpl_vincent.png`（vincent），只替换日期行和封面标题，内容缩进 B 站 4:3 安全区并自检。
  用法：`python3 make_cover.py "20261103 18:31" "封面标题" out.png`（要用 vincent 模板时在代码里改 `make_cover.TPL`）。
  依赖字体：Inter-Medium.otf、NotoSansCJK-Medium.ttc（路径见脚本顶部）。
- `collage_example_20261103.py`：拼图最新版实例。每篇写 (名称, 封面时间, 封面标题, 缩放S, 组列表)；
  坐标是手机“显示坐标”（宽 920），脚本乘 截图宽/920。支持 "seam" 无缝对齐两张重叠截图。
  规则：底部留 125px 给字幕、两栏、栏间距 24、统一缩放、只在段落空白处换栏、图/引用框整块不拆、各栏高度均衡。
  **每篇的裁剪坐标要看图后自己定**，这是最需要判断的一步。
- 各 `posts/<日期>/make.py` 是当批实际用的脚本，截图路径需改成自己的。
