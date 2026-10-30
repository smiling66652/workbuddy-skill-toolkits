# 平台与凭证细节（references）

## 视频生成凭证
- 视频生成依赖平台内置的多模态生成服务，调用前先 `connect_cloud_service` 取凭证，平台自动注入到内置 `buddy-cloud.py`。
- `video_gen.py` 通过 `importlib` 直接加载内置 `buddy-cloud.py` 并 monkey-patch `_build_video_body`，注入 `{"Duration": N, "AspectRatio": "9:16"}` 以绕开 CLI 写死的 5s/16:9。
- `BUDDY_CLOUD` 环境变量可覆盖内置脚本路径；默认指向 `C:\Users\asus\.workbuddy\plugins\marketplaces\workbuddy-builtin\skills\buddy-multimodal-generation\scripts\buddy-cloud.py`。

## kling v2.6 实测参数
- Vendor 字段 base64：`S2xpbmc=` = `kling`。
- Model：`v2.6`。
- 单次最长 `Duration` = 10；`AspectRatio` 支持 `9:16` / `16:9` / `1:1`。
- `LogoAdd: 1` 为平台水印开关。
- 生成任务异步，轮询超时约 600s；并发上限约 2 槽。

## edge_tts 注意
- 普通话 `zh-CN-YunjianNeural` 返回 `WordBoundary`（逐字时间戳）。
- 粤语 `zh-HK-HiuGaaiNeural` 仅返回 `SentenceBoundary`（句子级时间戳）——字幕脚本已据此适配。
- `rate` 参数可调语速（如 `+8%` / `+15%`）用来压缩配音总时长。

## moviepy 2.x 差异
- `clip.subclip(a, b)` → `clip.subclipped(a, b)`
- `clip.crop(ymin=, ymax=)` → `clip.cropped(y1=, y2=)`
- `write_videofile(..., logger="bar")` 在非 TTY（后台/管道）下可能静默中断 → 用 `logger=None`。
