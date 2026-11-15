# 必剪（Bcut）在 Wine 下的可用配置（serenity 旧电脑，2026-11-15 导出）

## 1. 版本
- `wine --version` → `wine-10.0 (Debian 10.0~repack-6)`（只装了 64 位，提示缺 wine32 可以忽略）
- `dpkg -l | grep -i wine`：
  ```
  ii  fonts-wine  10.0~repack-6  all    Windows API implementation - fonts
  ii  libwine:amd64  10.0~repack-6  amd64  Windows API implementation - library
  ii  wine  10.0~repack-6  all    Windows API implementation - standard suite
  ii  wine64  10.0~repack-6  amd64  Windows API implementation - 64-bit binary loader
  ```
  系统是 Debian 13。apt 镜像走不通代理时，用 curl 下这几个 Debian 的 .deb，再 `dpkg -i` 装。
- 相关包：xvfb 2:21.1.16-1.3+deb13u4，mesa 25.0.7（libgl1-mesa-dri、libglx-mesa0、libegl-mesa0、libosmesa6、mesa-libgallium），cabextract。

## 2. 必剪
- 版本：**3.11.25**（Windows 版）。安装包 `Bcut-Win-3.11.25-23679089.exe` 有 241MB，超过 GitHub 单文件 100MB 的上限，所以没推上来，请从官方地址下载：
  https://boss.hdslb.com/bcut_pc_pkg/static/7a3aa83aa894dc242c0fec493a0521a7/Bcut-Win-3.11.25-23679089.exe
- WINEPREFIX：`/home/box/.wine-bcut`（win64）
- 安装路径：`C:\Bcut\BCUT.exe`，即 `/home/box/.wine-bcut/drive_c/Bcut/`
- 启动脚本：`run-bcut.sh`（就在本文件夹里），里面设置了：
  `WINEARCH=win64`、`LANG/LC_ALL=zh_CN.UTF-8`、`WINEDLLOVERRIDES="mscoree,mshtml="`（关掉 Mono 和 Gecko 的安装弹窗）
- 我的启动命令：`cd /workspace/bcut && DISPLAY=:34 nohup ./run-bcut.sh >/tmp/bcut.log 2>&1 &`

## 3. 装过的东西和改过的设置
- winetricks：**vcrun2019**（它会连带装 ucrtbase2019）、**d3dcompiler_47**，日志见 `winetricks.log`。
- **没有 DXVK**。d3d11/dxgi/d3d9 都是 Wine 自带的 wined3d，走 Xvfb 里 mesa 的软件 OpenGL（llvmpipe）。
- 注册表 DllOverrides：只有 winetricks 自动写进去的那些（vcrun 的 msvcp140/vcruntime140/ucrtbase 等设为 native,builtin，d3dcompiler_47 设为 native），没有手动改过。完整的注册表在 `wine-prefix-reg/` 里。
- 没有动过 winecfg。
- 中文字体：把 NotoSansCJK、NotoSerifCJK、wqy-microhei、wqy-zenhei 的 .ttc 复制进了 `drive_c/windows/Fonts/`。没有中文字体的话，界面字会变成方块或者空白。
- `bcut-run.stderr` 里那些 `SwapChain11 ... 0x80004001` 报错一直都有，不影响使用。

## 4. 显示器 :34
是 Xvfb 加 x11vnc，box 系统给每个 bot 桌面自动开的，不是我手动起的：
```
Xvfb :34 -screen 0 1920x1200x24 -ac +extension GLX +render -noreset
x11vnc -display :34 -localhost -nopw -shared -forever -noxdamage -norc -rfbport 5934
```
分辨率 1920x1200，色深 24。

## 5. 窗口全黑时先查这几项
1. Xvfb 有没有带 `+extension GLX +render`，色深是不是 24（16 位或者没有 GLX，ANGLE 和 wined3d 会黑屏）。
2. `DISPLAY=:N glxinfo -B` 能不能看到 llvmpipe；需要装 `libgl1-mesa-dri` 和 `libglx-mesa0`。
3. 是否装了 d3dcompiler_47 和 vcrun2019。
4. 有没有误装 DXVK。软件渲染环境下 DXVK 跑不起来，会黑屏，删掉它恢复 wined3d。
5. 黑屏也可能只是还没画出来：等 30 到 60 秒，或者拖一下窗口、换个大小试试。

## 6. 配音用法
新建 16:9 工程 → 文本 → 朗读（文字转音频）→ 特色 → 曼波。每一段文字 `xclip -selection clipboard < cN.txt` 后按 Ctrl+V，分别生成。mp3 在 `drive_c/users/box/Documents/Bcut Drafts/<uuid>/`。
