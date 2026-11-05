# 配音声音：曼波（Fish Audio）

- 模型 ID（reference_id）：`0f08cacd3e354471a4b94dd00b4cc4a3`
- 页面：https://fish.audio/m/0f08cacd3e354471a4b94dd00b4cc4a3/
- 类型：TTS，普通话，年轻男声，语速快、有表现力，适合社媒解说
- 公开可见（public）
- 样音：`manbo_sample.mp3`

## API 调用示例
```bash
curl -X POST https://api.fish.audio/v1/tts \
  -H "Authorization: Bearer $FISH_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"配音稿文本","reference_id":"0f08cacd3e354471a4b94dd00b4cc4a3","format":"mp3"}' \
  -o out.mp3
```
Serenity 配音默认用这个声音。
