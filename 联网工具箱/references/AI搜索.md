---
name: 二级：AI搜索
---

# 二级：AI搜索

**适用场景**：用户需要AI生成答案的搜索、深度研究、综合话题分析

---

## 工具对比

| 工具 | 速度 | 深度 | 费用 | 推荐场景 |
|------|------|------|------|------------|
| **Tavily** | 快（1-2s basic） | 中 | 免费额度+按量 | 通用AI搜索 |
| **Perplexity** | 中（5-10s） | 高 | API付费 | 深度研究 |
| **WebSearch + LLM** | 快 | 取决于模型 | 模型token费 | 无API key时 |

---

## 三级执行：Tavily（推荐）

**触发词**：AI搜索、深度研究、综合这个话题、Tavily搜一下

**前置条件**：需要 `TAVILY_API_KEY`

```bash
# 安装 Tavily SDK
pip install tavily-python

# 基础搜索（basic模式，快）
python -c "
from tavily import TavilyClient
client = TavilyClient(api_key='tvly-xxx')
result = client.search('query here', search_depth='basic')
print(result)
"

# 深度搜索（advanced模式，慢但全）
python -c "
from tavily import TavilyClient
client = TavilyClient(api_key='tvly-xxx')
result = client.search('query here', search_depth='advanced', max_results=10)
print(result)
"
```

**两种模式**：
- `basic` — 1-2秒，适合简单查询
- `advanced` — 5-10秒，深度覆盖，适合复杂研究

---

## 三级执行：Perplexity（深度研究）

**触发词**：用Perplexity搜一下、深度研究、综合分析

**前置条件**：需要 `PERPLEXITY_API_KEY`

```bash
# 调用 Perplexity API
curl -X POST "https://api.perplexity.ai/chat/completions" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pplx-70b-online",
    "messages": [{"role": "user", "content": "你的问题"}]
  }'
```

---

## 三级执行：WebSearch + LLM（无API key时）

```bash
# 第一步：用 WebSearch 获取搜索结果
# 第二步：将结果交给 LLM 综合总结
# 适用于没有 Tavily/Perplexity API key 的情况
```

---

## 使用建议

- **快速信息查询** → Tavily basic
- **复杂话题综合分析** → Tavily advanced 或 Perplexity
- **无API key** → WebSearch + LLM 组合
