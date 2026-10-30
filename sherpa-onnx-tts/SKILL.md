---
name: sherpa-onnx-tts
version: "1.0.0"
display_name: "语音合成（sherpa-onnx-tts）"
display_name_en: "text-to-speech synthesis (sherpa-onnx-tts)"
description: "text-to-speech synthesis capability in the creative, voice and multimedia domain. Use when the user wants to 完全离线的文字转语音. Triggers: sherpa-onnx-tts, openai-whisper. Not for requests unrelated to text-to-speech synthesis. Risk level L0. 中文触发：sherpa-onnx-tts、openai-whisper。"
description_zh: "完全离线的文字转语音。（类别：六、创意、语音与多媒体类；风险等级：低）当用户需要语音合成相关能力、或提到 sherpa-onnx-tts、openai-whisper 时使用；与语音合成无关的请求不要触发。"
description_en: "text-to-speech synthesis capability in the creative, voice and multimedia domain. Use when the user wants to 完全离线的文字转语音. Triggers: sherpa-onnx-tts, openai-whisper. Not for requests unrelated to text-to-speech synthesis. Risk level L0."
agent_created: true
---

# 语音合成（sherpa-onnx-tts）

## 用途

完全离线的文字转语音。

> 分类：六、创意、语音与多媒体类（creative, voice and multimedia）  
> 技能类型：语音合成  
> 风险等级：低  
> 门禁档位：**L0** — 只读 / 无副作用，可直接执行；仍遵守“先确认再改生产”的通用原则。

## 触发条件

- 用户提到 `sherpa-onnx-tts`、需要语音合成能力，或提出对应诉求时触发。
- 典型触发词：sherpa-onnx-tts、完全离线的文字转语音。
- 关联技能：openai-whisper。

## 何时不要使用

- 与语音合成无关的请求：不要触发，交给更合适的技能或直接回答。
- 前置依赖未就绪（未授权 / 缺 CLI / 缺网络）时：**停下并报告**，不要降级为让用户粘贴明文凭据。
- 超出本技能声明范围的目标（其他系统、其他账号）：不越权操作。

## 功能清单

- 完全离线运行
- 文字转语音
- 无网络依赖，保护隐私

## 标准操作流程

1. 确认输入素材的版权与授权状态，不使用无授权的内容。
2. 明确输出格式/质量/语言等参数，必要时先出小样。
3. 调用外部付费模型（图像/语音/视频）前确认成本与额度。
4. 本地可离线完成的优先本地执行，敏感音频不外传。
5. 交付产物路径与播放/查看方式说明清楚。

## 外部依赖与前置检查

- 依赖：本地模型（离线）。开箱即用，无需额外配置。

## 典型使用场景

1. 隐私敏感的语音播报
2. 离线环境下的 TTS

## 使用提示

与 openai-whisper 搭配可组成离线语音方案。

## 备注

- 关联技能：openai-whisper。
- 本技能由规划规格 README 自动落地生成，操作细节（具体 API/CLI/连接）应在接入真实运行时补全。
- 通用铁律：先验证现状 → 列影响面 → 取得确认 → 再执行；不可逆或涉钱/涉密的动作用最高门禁。
