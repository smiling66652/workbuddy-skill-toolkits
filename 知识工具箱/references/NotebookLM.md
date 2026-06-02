---
name: 二级：NotebookLM
---

# 二级：NotebookLM

**适用场景**：生成学习材料（播客/测验/抽认卡/思维导图）、学习内容交互

---

## 工具对比

| 工具 | 生成内容 | 速度 | 推荐场景 |
|------|---------|------|------------|
| **NotebookLM API** | 播客/测验/抽认卡 | 中 | 程序化生成（推荐） |
| **NotebookLM Web** | 手动生成 | 慢 | 一次性操作 |

---

## 三级执行：NotebookLM API（推荐）

**触发词**：生成播客、生成测验、学习内容、NotebookLM

### 前置条件

需要 `NOTEBOOKLM_API_KEY`，在 [NotebookLM](https://notebooklm.google.com/) 获取。

### 生成播客

```python
import requests

api_key = "YOUR_NOTEBOOKLM_API_KEY"
headers = {"Authorization": f"Bearer {api_key}"}

# 生成播客（基于上传的文档）
response = requests.post(
    "https://notebooklm.googleapis.com/v1/generate_podcast",
    headers=headers,
    json={
        "document_ids": ["doc_123", "doc_456"],
        "duration_minutes": 10,
        "style": "conversational",
    },
)
print(f"播客生成任务ID：{response.json()['task_id']}")
```

### 生成测验

```python
# 生成测验（基于文档内容）
response = requests.post(
    "https://notebooklm.googleapis.com/v1/generate_quiz",
    headers=headers,
    json={
        "document_ids": ["doc_123"],
        "num_questions": 10,
        "question_types": ["multiple_choice", "true_false"],
    },
)
quiz = response.json()
for question in quiz["questions"]:
    print(f"Q: {question['question_text']}")
    for option in question["options"]:
        print(f"  {option['label']}. {option['text']}")
```

### 生成抽认卡

```python
# 生成抽认卡（用于记忆）
response = requests.post(
    "https://notebooklm.googleapis.com/v1/generate_flashcards",
    headers=headers,
    json={
        "document_ids": ["doc_123"],
        "num_cards": 20,
    },
)
flashcards = response.json()
for card in flashcards["cards"]:
    print(f"Front: {card['front']}")
    print(f"Back: {card['back']}")
```

---

## 三级执行：NotebookLM Web

**触发词**：手动生成学习材料、NotebookLM网页版

### 使用

1. 访问 https://notebooklm.google.com/
2. 上传文档（PDF/Word/TXT）
3. 选择生成内容类型：
   - 播客（Podcast）
   - 测验（Quiz）
   - 抽认卡（Flashcards）
   - 思维导图（Mind Map）
4. 等待生成完成
5. 下载或分享生成的内容

---

## 使用建议

1. **程序化生成** → NotebookLM API
2. **一次性生成** → NotebookLM Web界面
3. **批量生成** → Python脚本 + NotebookLM API
4. **学习内容交互** → NotebookLM Web界面（支持问答）
5. **多语言支持** → 检查官方文档是否支持中文

---

## 注意事项

- **API Key 保护**：不要将 API Key 写入代码或上传到 Git
- **文档格式支持**：检查官方文档支持的文件格式
- **生成内容审核**：生成的内容可能需要人工审核
- **速率限制**：API 有调用频率限制，批量操作注意间隔
