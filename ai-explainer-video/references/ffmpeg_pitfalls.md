# ffmpeg 实测踩坑（数字人讲解短视频流水线）

本文件固化在受限/沙箱 Windows 环境下用 ffmpeg（imageio_ffmpeg 自带）合成视频的真实坑。
ffmpeg 路径一律用 `imageio_ffmpeg.get_ffmpeg_exe()` 取得，不要硬编码；该目录**只有 ffmpeg、没有 ffprobe**，
测时长用 `ffmpeg -i <文件>` 再正则抓 `Duration`。读已完成容器(webm/mp4)正常，读 PNG 序列不稳。

## 1. filter_complex_script 不支持
本环境 `-filter_complex_script <文件>` 会报 Invalid argument。**改用命令行内联 `-filter_complex`**，
用 Python 列表传参即可彻底避开 shell 引号转义地狱（不要手动拼带引号的字符串）。

## 2. 中文 / 引号 / 逗号 字幕会崩
若需要 `drawtext` 叠加中文或含中文引号（“ ” 、 ，），直接把 text 写进滤镜串会崩。
→ 改为 `textfile=<utf8文件>` 读取，文件用 UTF-8 无 BOM 存储。无字幕场景可整体跳过 drawtext。

## 3. 路径反斜杠 `\s` 被当转义
Windows 路径里的 `\` 在滤镜表达式里会被当成转义符（如 `\s` 触发告警）。
→ 先把路径统一成**正斜杠**，再对冒号 `:` 转义为 `\:`（如 `fontfile='C\:/Windows/Fonts/msyhbd.ttc'`）。

## 4. 编码器选择
- **复杂滤镜链（scale+delogo+overlay 等）下，libx264(mp4) 在沙箱会线程崩溃**（报 -22 / received no packets / Nothing was written，哪怕 -threads 1）。
  → 合成阶段用 **libvpx-vp9(webm) + libvorbis(aac 替代 libopus，libopus 在某些封装打不开)**。
- **纯转码（无滤镜链）时，libx264 可用**：webm→mp4 的 H.264+yuv420p+AAC 转码实测成功。
- 若 libx264 仍报 -22，先确认是否处于复杂滤镜场景，改用 webm 预览或把滤镜移到纯转码之前完成。

## 5. 合成与拼接
- 各段背景用 `-stream_loop -1` 循环适配配音时长，避免逐段足量生成（成本差数倍）。
- 背景视频由生成式工具产出时尺寸常为 1924×1076 而非 1920×1080，先 `scale=1920:1080`。
- 生成式工具常在右下角加水印（如“视频由AI生成”），用 `delogo=x=1680:y=1012:w=234:h=60` 去除。
- 段间 concat 用 `concat=n=段数:v=1:a=1` 滤镜重编码（比 demuxer+copy 在中文路径下更稳）。

## 6. 运行权限
- 合成涉及 av(PyAV)/本地 ffmpeg 时，沙箱可能拦截 DLL。**需要关闭沙箱运行**（如 dangerouslyDisableSandbox）。
- 生成式视频/图片工具（VideoGen / ImageGen）通常有任务数上限，超限报 RequestLimitExceeded，隔几分钟重试即可。
