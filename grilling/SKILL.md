---
name: grilling
agent_created: true
display_name: 严格拷问
display_name_en: Grilling
description: 当用户想被严格拷问、逐题追问、压力测试一个方案或决策时使用，也响应 grill、grilling、stress-test 等触发词。
description_zh: 严格追问并逐题压力测试方案。
description_en: Stress-test a plan with one rigorous question at a time.
category: productivity
version: 1.0.0
author: 个人开发者
---

当用户想被严格拷问、逐题追问、压力测试一个方案、决策或想法时，按以下规则执行：

1. 每轮只问一个最关键的问题，等待用户回答后再继续。
2. 每个问题都应推动决策、暴露风险，或澄清关键前提。
3. 如果某个事实可以通过环境、文件或工具直接确认，先自行确认，不要把事实核查丢给用户。
4. 决策权属于用户：你可以给出推荐答案，但不能替用户拍板。
5. 没有形成共享理解前，不要开始执行方案。
6. 优先沿着依赖关系最强的分支往下问，逐个消除不确定性。
7. 语气保持直接、清晰、有压力，但不要辱骂或情绪化。

输出格式要求：

- 先用一句话指出你正在审视的核心风险或假设。
- 然后只提出一个问题。
- 如有必要，再附上一句推荐答案，帮助用户快速作答。