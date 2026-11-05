# 曼波音色本地合成（沙盒无法访问 Fish Audio 时的备选）
- 样音 `references/voice/manbo_sample.mp3`（16 秒）作参考音；模型 sherpa-onnx ZipVoice（distill int8）+ vocos 声码器 + SenseVoice 转写参考文本，均来自 github.com/k2-fsa/sherpa-onnx releases。
- ZipVoice 会吞掉英文单词和部分阿拉伯数字：配音文本先过 `zspeak.py`（英文→中文音译，日期/金额→汉字读法），字幕仍用原文。
- 合成后用 SenseVoice 转写回听，对照原文检查有没有漏字。合成约 9 倍慢于实时。
- 效果不如 Fish Audio 原模型；有 API key 且能联网时，优先用 references/voice/fish_audio_manbo.md 的 API。
