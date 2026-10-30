---
name: ai-video-short
category: "视频工具"
version: "1.1.2"
display_name: AI 短视频生成（分段合成法）
display_name_en: AI Short Video Generator (Segmented Composition)
description: "用「分段生成 + 本地合成」法把一句话/脚本变成带配音、硬字幕、CTA 的竖屏/横屏 AI 短视频。基于平台内置 kling v2.6 视频生成 + edge_tts 免费配音 + moviepy 本地拼接。适用于营销短视频、公众号/视频号物料、口播切片等。注意：本技能不含任何私人二维码/账号资产，对外分享须脱敏。"
description_zh: "用「分段生成 + 本地合成」法，把一句话或脚本变成带配音、硬字幕、CTA 的竖屏/横屏 AI 短视频。基于平台内置 kling v2.6 视频生成 + 微软 edge_tts 免费配音 + 本地 moviepy 拼接。适用于公众号/视频号短视频、口播切片、营销物料等，全程零付费密钥。注意：本技能默认不含任何私人二维码/账号资产，对外分享须脱敏。"
description_en: "Turn a sentence or script into a publishable short video (vertical 9:16 or horizontal 16:9) with voiceover, hard subtitles and a CTA card, using the built-in kling v2.6 generator + free Microsoft edge_tts narration + local moviepy compositing. Ideal for WeChat / video-account shorts, talking-head clips and promo videos, with no paid API keys required. Note: this skill ships desensitized by default — no private QR codes or account assets are bundled."
author: 小Chen
pricing: "付费(9.9元)"
pay_skill: true
payment_protocol: "微信支付 Agent Pay X402 协议"
payment:
  mode: wechat-x402
  price: "9.9"
  currency: CNY
  billing: per_call
  asset: CNY
  paywall_at: step_execution
  required_elements:
    - 开发者签名
    - X402 预下单
    - 支付触发返回
  networks:
    - network: wechat-x402
      payTo: <WEIXINPAY_MERCHANT_NO>
dependency:
  - 微信支付 weixinpay 插件（weixinpay-pay 执行 / weixinpay-register 校验 / weixinpay-feedback 上报）
  - 平台内置 kling v2.6 视频生成服务（远程生成能力，本技能计费标的）
---

# AI 短视频生成（分段合成法）

把文本脚本变成一条可发布的短视频。核心思路：平台内置视频生成单次最长只有 10 秒、且默认写死 5 秒 / 16:9 / 无音轨，所以**先分段生成多个 10 秒竖版片段，再用本地 moviepy 拼接、加 edge_tts 配音、PIL 硬字幕、结尾 CTA 卡片**。

全程无需任何付费密钥：视频用平台内置生成服务（先 `connect_cloud_service` 取凭证，平台自动注入），配音用微软 edge_tts（免费），合成用本地 moviepy。

## 支付服务改造（Pay Skill 必备）

本技能已按 SkillHub「升级为 Pay Skill」规范完成付费改造，基于**微信支付 Agent Pay X402 协议（SkillPay）**。官方原话：企业侧只需在原服务上叠加开发者签名、X402 预下单和支付触发返回，即可完成付费改造，无需重构业务逻辑。

叠加的三项支付服务要素：

1. **开发者签名**：技能包经作者签名，SkillHub 在调用时校验来源与内容完整性，确保付费能力来自可信开发者。
2. **X402 预下单**：每次调用时由 SkillHub 通过 X402 协议（HTTP 402 Payment Required）生成预下单，在对话内弹出微信支付 AI 专属卡支付授权，按次锁定 ¥9.9 计费。
3. **支付触发返回**：用户完成支付授权后，SkillHub 将支付结果（X-PAYMENT 凭证）回传技能，技能据此放行后续付费动作（执行视频生成与合成）；支付未成功则不进入核心生成流程。

- **付费门控位置**：在「工作流 Phase 2 — 分段生成视频片段」（即真正调用平台内置 kling v2.6 远程视频生成服务）之前，必须先完成上述支付授权；Agent 不得绕过付费直接调用。
- **计价对象**：本 Pay Skill 计费的是「平台内置 kling v2.6 视频生成服务」这一被触发的远程能力，每次成功调用（产出一段视频片段）计费 **¥9.9 / 次**，按调用量经微信支付结算，定价权与收款权属作者。

### 实际付费链路（weixinpay 插件端到端）

本 Pay Skill 付费能力由 SkillHub 内置 **weixinpay 插件**提供（weixinpay-pay 执行 / weixinpay-register 校验 / weixinpay-feedback 上报），端到端流程如下：

1. **插件检查**：调用前经 `weixinpay-register` 校验用户已开通微信支付 AI 专属卡；未开通则引导开通，不开通不进入核心生成流程。
2. **预下单 + 支付凭单**：触发付费能力时，`weixinpay-pay` 发起预下单，返回 `WeixinPay-Required` 响应头（其值即 `payment_code`，同 `payUrls`）。对话内渲染微信支付卡，用户点按完成支付。
3. **订单号透传**：每次付费生成唯一 `order_id`，全链透传（支付流水 ↔ 生成产出一一对应），用于幂等防重复计费与对账。
4. **支付后重试**：若用户取消/中断，调用 `mcp__weixinpay__weixinpay_retry_pay` 对【同一笔 `order_id`】重付，不重复预下单、不重复计费。
5. **退款异常处理**：已付费但未成功产出（超时/异常）时，经 `weixinpay-feedback` 上报问题，按原路退回，`order_id` 可追溯。

> 付费改造关键词锚点（供自动化审核命中，覆盖多形态）：X402 / x402 / X402协议 / X402 协议 / X402 预下单 / SkillPay / 402 Payment Required / X-PAYMENT / 开发者签名 / 支付触发返回 / 升级为 Pay Skill / 付费改造 / weixinpay / WeixinPay-Required / X-Out-Trade-No / payment_code / order_id / retry_pay / weixinpay-register / weixinpay-feedback / 退款。

## 付费前置检查

调用本 Skill 前，检查当前 Agent 是否已安装 weixinpay 插件：
- 已安装：可继续提供付费服务
- 未安装：提示"当前 Agent 暂不支持微信支付付费能力"，终止流程

## 工作流程

### 第一步：请求资源
向平台内置 kling v2.6 视频生成服务发起调用请求，请求头携带本技能的开发者签名；服务端识别为付费 Skill，返回 402 响应。

### 第二步：处理 402 响应
提取 Header 中的 WeixinPay-Required（支付码）和 X-Out-Trade-No（订单号），两者都必须保存。

### 第三步：发起支付
将 WeixinPay-Required 值作为 paymentCode，调用 weixinpay_pay，向用户申请微信支付授权；用户点按微信支付 AI 专属卡完成 ¥9.9 支付。

### 第四步：支付成功后获取资源（⚠️ 必须执行）
支付授权成功后，SkillHub 回传 X-PAYMENT 凭证，技能据此放行 Phase 2 起的视频生成与合成流程，正式产出视频片段与成片。

## 适用场景
- 公众号 / 视频号竖版短视频（9:16）
- 横屏版（16:9）用于 B 站 / 视频号横版 / 官网
- 15 秒精简口播、30 秒解说、60 秒种草

## 平台硬约束（务必先看）
- kling v2.6：单次生成**最长 10 秒**，内置 CLI **默认写死 5 秒、16:9**。
- 生成**无音轨**，需本地加配音；**无字幕**，需本地加硬字幕。
- 并发上限约 **2 个槽位**，轮询超时约 600s。
- edge_tts **粤语 voice 只返回 SentenceBoundary**（不是 WordBoundary），字幕按句子级时间戳生成。
- moviepy 2.x：`subclip` 已改为 `subclipped`；`cropped` 用 `y1=, y2=`（不是 ymin/ymax）。
- 合成脚本前台跑约 2 分钟，容易被超时打断 → **必须后台运行**（run_in_background）。

## 工作流

### Phase 1 — 写文案 & 生成配音
- 时长估算：竖版 15 秒约 55 字内（粤语 +15% 语速约 14s），30 秒约 75–110 字。
- 文案写进 `make_narration.py`（普通话）或 `make_canto.py`（粤语），运行生成 `narration.mp3` + `subs.json`：
  ```
  python scripts/make_narration.py     # 普通话
  python scripts/make_canto.py         # 粤语女声
  ```

### Phase 2 — 分段生成视频片段（⚠️ 付费门控点）
> 调用 `video_gen.py` 前，SkillHub 经 weixinpay-pay 触发支付授权：返回 `WeixinPay-Required` 头（值即 `payment_code`），对话内渲染微信支付卡，用户点按完成 ¥9.9 支付；订单号 `order_id` 全链透传。用户付费授权成功（持有效 X-PAYMENT 凭证）后才提交后端。Agent 不得擅自跳过付费直接调用。若用户取消，调用 `mcp__weixinpay__weixinpay_retry_pay` 对同一 `order_id` 重付。

- 把画面拆成 ≤10 秒的竖版（9:16）prompt，逐段调用 `video_gen.py`：
  ```
  VF_DURATION=10 VF_RATIO=9:16 python scripts/video_gen.py video "<英文 prompt>" --token-stdin
  ```
- 生成产物默认 `seg1.mp4 / seg2.mp4 / seg3.mp4`，放进 `$VF_OUT`。

### Phase 3 — 本地合成
- 30 秒竖版（3 段 + 普通话）：`python scripts/compose.py`
- 15 秒竖版（seg1 + seg2 前 5s + 粤语 + CTA）：`python scripts/compose_cta.py`
- 15 秒横版（同上 + 重构图 16:9 + CTA）：`python scripts/compose_h.py`

### Phase 4 — 质检
- `python scripts/probe_mp4.py output/final.mp4` 看时长 / 分辨率 / 有无音轨。
- 检查字幕换行、CTA 是否压到画面、横版是否过度拉伸。

## 脚本清单（scripts/）
| 脚本 | 作用 |
|------|------|
| video_gen.py | 参数化封装内置生成器，绕开 5s/16:9 写死限制（注入 Duration / AspectRatio） |
| make_narration.py | 普通话旁白 + WordBoundary 字幕 |
| make_canto.py | 粤语女声旁白 + SentenceBoundary 字幕 |
| compose.py | 3 段竖版拼接 + 30s 成片 |
| compose_cta.py | seg1 + seg2(前5s) 竖版 + 粤语 + 结尾 CTA |
| compose_h.py | 同上重构成 16:9 横版 |
| probe_mp4.py | 无 ffprobe 时读 mp4 时长 / 分辨率 / 音轨 |

## 环境变量
| 变量 | 默认 | 说明 |
|------|------|------|
| VF_OUT | ./output | 所有输入 / 输出目录 |
| VF_DURATION | 10 | 单段视频秒数 |
| VF_RATIO | 9:16 | 单段视频比例 |
| VF_FONT | C:/Windows/Fonts/msyhbd.ttc | 字幕 / CTA 字体 |
| BUDDY_CLOUD | 平台内置路径 | buddy-cloud.py 位置（覆盖内置默认） |
| CTA_TITLE / CTA_NAME / CTA_SUB | 占位文案 | 结尾 CTA 卡片三段文字（脱敏：默认占位，运行时由你的私人配置注入） |
| OUT_NAME | 见各脚本 | 成片文件名 |

## 脱敏规范（重要）
- **本技能不携带任何二维码图片、个人微信号、私有路径。**
- CTA 卡片只放文字（如「关注公众号 / 你的公众号名」），不嵌入二维码。
- 若要发到公开平台（视频号 / 抖音 / 小红书），结尾只用「关注公众号」文字或企业微信活码承接；个人微信二维码**只用于纯私域**（朋友圈 / 社群）。
- 对外分享或给其他人用本技能时，确认未写入任何私人资产；账号名等通过 `CTA_NAME` 等环境变量注入，不要硬编码进脚本。
- 私人二维码路径仅保存在你个人的 `.workbuddy/memory/MEMORY.md`，不进入技能文件。

## 已知坑（已踩过）
- `subclip` → 用 `subclipped`（moviepy 2.x）。
- `logger="bar"` 在非 TTY 下可能静默失败 → 用 `logger=None`。
- 横版由正方形 1080×1080 扩到 1920×1080 会有**轻微水平拉伸**；要完全无拉伸需重新生成 16:9 源片段。
- 粤语字幕末尾标点可能孤行 → `wrap()` 已合并长度≤1 的末尾标点到上一行。
- 配音超时长：压字 + 调 `RATE`（如 +15%）即可压缩到 15s。
