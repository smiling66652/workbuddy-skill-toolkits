# 福和顺·自动剪辑 · 部署与运行说明

本技能是福和顺自研的竖屏口播视频自动剪辑流水线，全程 Python + PIL + ffmpeg，不依赖剪映 GUI。

## 目录

- `SKILL.md` —— 流水线总说明：六步流程、口令对照、参数基线、踩坑速查
- `scripts/` —— 工具脚本（渲前自检、素材目检、水印终检、交付核验）

## 依赖（需自备，不随包分发）

| 依赖 | 用途 | 安装 |
|---|---|---|
| Python 3.10+ | 全部脚本 | — |
| `Pillow` | 图像合成、联系表 | `pip install pillow` |
| `numpy` | 数值计算 | `pip install numpy` |
| `ffmpeg` / `ffprobe` | 解码、抽帧、编码、混音 | 需在 PATH 上 |
| `faster-whisper` | 词级转写 | `pip install faster-whisper`；模型约 460MB，首次运行自动下载 |
| 系统中文字体 | 字幕与花字渲染 | 按 SKILL.md 指示配置字体路径 |

> 网络受限时 faster-whisper 模型可能下载失败（HF 下载中断/401）。此时需自行获取模型权重并放到本地缓存目录，再用 HTTP 断点续传方式加载。

## 脚本清单

| 脚本 | 用途 | 时机 |
|---|---|---|
| `scripts/static_names.py <build.py>` | 静态扫未定义全局名 | 渲染前 |
| `scripts/dryrun_layout.py <build.py>` | 干跑全时间轴排版 + 打印逐句字幕 | 渲染前 |
| `scripts/bar_windows.py <build.py>` | 金句条窗口/锚点自检 | 渲染前 |
| `scripts/debug_component.py <build.py> <fn>` | 单元素出图诊断 | 改组件时 |
| `scripts/assets_sheet.py <assets根>` | 素材联系表 | 抓完素材、定稿前 |
| `scripts/wm_strip_audit.py <assets_dir>` | 水印条带终检 | 定稿后 |
| `scripts/prep_card_aspect.py` | 素材预裁（卡片比例 + 切水印带） | 定稿时 |
| `scripts/verify_full.py <成片>` | 全片核验：运动量 + 虚化连续性 | 交付前 |
| `scripts/contact_sheet.py <成片> out.png` | 接触表 / 首尾细帧 | 交付前目检 |

## 使用方式

这些脚本是**通用工具**，需要与你的渲染脚本配合使用：

- `static_names.py` / `dryrun_layout.py` / `bar_windows.py` / `debug_component.py` 通过 `importlib` 加载你的渲染脚本，并要求它暴露一组约定接口（`SEGMENTS` / `build_units` / `render_subs` / `DUR` / `FPS` / `W` / `H` / `mat_layout` 等）。缺哪个就跳过哪一步。
- `contact_sheet.py` / `verify_full.py` 直接作用于成片 mp4，无接口依赖。
- `assets_sheet.py` / `wm_strip_audit.py` / `prep_card_aspect.py` 直接作用于素材目录。

各脚本头部都有完整的用法注释与参数说明，`python <script> --help` 亦可查看。

```bash
# 典型顺序
python scripts/static_names.py build.py                  # 渲前：扫未定义名
python scripts/dryrun_layout.py build.py                 # 渲前：全时间轴干跑
python scripts/bar_windows.py build.py                   # 渲前：金句条窗口
python scripts/assets_sheet.py assets/ --cols 4 --out _chk.png   # 素材目检
python scripts/verify_full.py out.mp4 --mat "8.62,12.20,15.86"   # 交付前核验
python scripts/contact_sheet.py out.mp4 总览.png --every 4 --cols 6
```

## 交付前三查

```bash
# 1. 时长 ≥ 配音时长
ffprobe -v error -show_entries format=duration -of default=nw=1 成片.mp4
# 2. 运动量核验（结尾不能塌到 0，防定格）
python scripts/verify_full.py 成片.mp4
# 3. 尾部无长静音（有 = 音频被截）
ffmpeg -i 成片.mp4 -af silencedetect=n=-42dB:d=0.25 -f null -
```
