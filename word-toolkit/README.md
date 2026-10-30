# Word 文档创作与美化（workbuddy-docx）

一个面向开放平台的、**自包含、可离线运行**的 Word（.docx）创作与美化技能。

## 为什么是这一版

原 WorkBuddy 内置的 `workbuddy-docx` 是一个大型复合技能，含深度 4–5 级的嵌套目录、
上百处内部引用，以及一个只在宿主机器运行时现场构建、不随包分发的 Node 预构建二进制
`dist/cli.cjs`。该结构无法满足开放平台「两级目录 + 被引用资源必须存在」的校验，且无法
在平台环境重建缺失二进制。本版据此**重做为干净的两级结构、纯 python-docx 实现**，
既能通过平台校验，也能真实生成/美化标准 .docx。

## 目录结构（严格两级）

```
workbuddy-docx/
├── SKILL.md                 # 技能说明与方法论（含 frontmatter）
├── README.md                # 本文件
├── scripts/
│   └── make_docx.py         # python-docx 大纲渲染器（可执行）
└── assets/
    ├── style-guide.md        # 版式与配色规范
    └── cover-template.md     # 封面模板说明
```

## 快速开始

```bash
# 1) 安装依赖（仅 python-docx）
pip install python-docx

# 2) 生成示例文档，验证脚本可用
python scripts/make_docx.py --demo --out demo.docx

# 3) 用你自己的大纲生成
python scripts/make_docx.py --json outline.json --out report.docx
```

## 适用范围

- 从零生成：研报、论文、公文、合同、方案、会议纪要等结构化 .docx
- 已有文档排版美化与风格统一（用 python-docx 批量重设样式）
- 不负责内容的事实准确性与合规（由调用方/用户把关）
