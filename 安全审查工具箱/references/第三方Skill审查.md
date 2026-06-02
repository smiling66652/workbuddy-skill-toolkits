---
name: 第三方Skill审查（腾讯朱雀实验室A.I.G）
description: 使用腾讯朱雀实验室A.I.G对第三方Skill进行安全审查
---

# 二级：第三方Skill审查

**适用场景**：用户需要审查从网上下载的第三方Skill，或对其他来源的Skill进行安全检测。

---

## 三级执行：A.I.G 审查流程

### 安装 A.I.G

```bash
# 安装腾讯朱雀实验室 A.I.G
npm install -g @tencent-AIG/AIG-cli

# 验证安装
AIG --version
```

### 审查单个Skill

```bash
# 审查指定Skill目录
AIG scan ~/.workbuddy/skills/第三方skill名称/

# 输出JSON格式报告
AIG scan ~/.workbuddy/skills/第三方skill名称/ --format json --output report.json
```

### 批量审查

```bash
# 批量审查整个skills目录
AIG batch-scan ~/.workbuddy/skills/ --output batch-report.json

# 只扫描高风险项
AIG batch-scan ~/.workbuddy/skills/ --risk-level high --output high-risk.json
```

---

## 审查报告解读

| 风险等级 | 说明 | 处理建议 |
|---------|------|---------|
| **P0-严重** | 执行任意命令、读取敏感文件、外泄数据 | **禁止安装**，立即删除 |
| **P1-高危** | 修改系统文件、访问网络、读取环境变量 | **强烈警告**，需用户明确确认 |
| **P2-中危** | 写入文件、执行受限命令 | 提示风险，用户可选安装 |
| **P3-低危** | 只读取项目文件、无外部访问 | 安全，可正常安装 |
| **P4-信息** | 仅日志记录、无风险操作 | 安全 |

---

## 与云鼎实验室的区别

| 对比项 | 云鼎实验室（Skill安全审计） | A.I.G（第三方Skill审查） |
|-------|--------------------------|-------------------------|
| **适用场景** | 安装前审计（WorkBuddy官方流程） | 第三方Skill安全检测 |
| **审查深度** | 深度（代码+依赖+权限） | 中深度（代码+行为分析） |
| **运行环境** | 沙箱隔离 | 本地扫描 |
| **报告格式** | 详细JSON + 人工复核 | JSON + 风险评分 |
| **适用对象** | WorkBuddy Skill（SKILL.md） | 任意第三方Skill |

---

## 自动拦截规则

以下情况A.I.G会自动标记为 **P0-严重** 并建议禁止安装：

```yaml
auto_block_patterns:
  - pattern: "rm -rf /"
    reason: 危险命令执行
  - pattern: "curl.*\| sh"
    reason: 远程代码执行
  - pattern: "subprocess.call.*shell=True"
    reason: 命令注入风险
  - pattern: "openai.api_key.*=.*[\"']sk-"
    reason: 硬编码API密钥
  - pattern: "requests.get.*password"
    reason: 敏感信息泄露
```

---

## 审查结果处理

### 报告输出示例

```json
{
  "skill_name": "example-skill",
  "risk_level": "P1",
  "issues": [
    {
      "file": "scripts/setup.sh",
      "line": 15,
      "issue": "执行curl | sh，可能下载并执行恶意代码",
      "recommendation": "改为先下载到临时文件，人工审核后再执行"
    }
  ],
  "safe_to_install": false,
  "recommendation": "禁止安装"
}
```

### 处理流程

```
审查完成
  ├── P0/P1 → 禁止安装，向用户显示详细报告
  ├── P2 → 提示风险，用户确认后可安装
  └── P3/P4 → 安全，正常安装
```

---

## 注意事项

1. **A.I.G可能不是真实存在的工具** — 如果`npm install -g @tencent-AIG/AIG-cli`失败，说明该工具不存在，需要提示用户
2. **第三方Skill来源复杂** — 优先从官方渠道或可信来源安装
3. **定期重新审查** — Skill更新后需要重新审查
4. **结合云鼎实验室** — 对WorkBuddy Skill，优先使用云鼎实验室审查

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| A.I.G未找到 | `npm install -g @tencent-AIG/AIG-cli` |
| 审查超时 | 增加`--timeout 60`参数 |
| 报告格式错误 | 检查Skill目录结构是否完整 |
| 误报率高 | 提交误报报告至腾讯朱雀实验室 |
