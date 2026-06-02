---
name: MCP开发
description: MCP（Model Context Protocol）服务器开发指南（Python/Node/协议实现）
---

# 二级：MCP开发

**适用场景**：用户需要开发MCP服务器，或让AI Agent能够调用自定义工具。

---

## 什么是 MCP？

**MCP（Model Context Protocol）** 是 Anthropic 推出的协议，用于让 AI 模型（如 Claude）能够调用外部工具、访问本地资源。

```
AI模型 (Claude)  ←→  MCP客户端  ←→  MCP服务器  ←→  外部工具/资源
```

---

## 三级执行：MCP 服务器开发

### 方法1：Python 开发 MCP 服务器

#### 安装

```bash
pip install mcp
```

#### 基本 MCP 服务器

```python
# server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

# 创建服务器实例
server = Server("my-mcp-server")

# 声明工具列表
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_weather",
            description="获取指定城市的天气",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如：北京"
                    }
                },
                "required": ["city"]
            }
        )
    ]

# 处理工具调用
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_weather":
        city = arguments["city"]
        # 这里应该是实际的天气API调用
        weather = f"{city}的天气：晴，25°C"
        return [TextContent(type="text", text=weather)]
    raise ValueError(f"Unknown tool: {name}")

# 启动服务器
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### 运行

```bash
# 测试运行
python server.py

# 在 WorkBuddy 中配置
# 编辑 ~/.workbuddy/mcp.json：
{
  "mcpServers": {
    "my-weather-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {}
    }
  }
}
```

---

### 方法2：Node.js 开发 MCP 服务器

#### 安装

```bash
npm install @modelcontextprotocol/sdk
```

#### 基本 MCP 服务器

```javascript
// server.js
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  ListToolsRequestSchema,
  CallToolRequestSchema
} from "@modelcontextprotocol/sdk/types.js";

// 创建服务器实例
const server = new Server(
  {
    name: "my-mcp-server",
    version: "1.0.0"
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// 声明工具列表
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_weather",
        description: "获取指定城市的天气",
        inputSchema: {
          type: "object",
          properties: {
            city: {
              type: "string",
              description: "城市名称，如：北京"
            }
          },
          required: ["city"]
        }
      }
    ]
  };
});

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === "get_weather") {
    const city = args.city;
    const weather = `${city}的天气：晴，25°C`;
    return {
      content: [
        {
          type: "text",
          text: weather
        }
      ]
    };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server running on stdio");
}

main().catch(console.error);
```

#### 运行

```bash
# 测试运行
node server.js

# 在 WorkBuddy 中配置
# 编辑 ~/.workbuddy/mcp.json：
{
  "mcpServers": {
    "my-weather-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": {}
    }
  }
}
```

---

## MCP 协议详解

### 消息类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `initialize` | 初始化连接 | 客户端发送，服务器响应能力 |
| `tools/list` | 列出可用工具 | 返回工具列表 |
| `tools/call` | 调用工具 | 执行工具并返回结果 |
| `resources/list` | 列出可用资源 | 返回资源列表（如文件） |
| `resources/read` | 读取资源 | 返回资源内容 |

### Tool 定义格式

```json
{
  "name": "get_weather",
  "description": "获取指定城市的天气",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "温度单位"
      }
    },
    "required": ["city"]
  }
}
```

### 返回结果格式

```json
{
  "content": [
    {
      "type": "text",
      "text": "北京的天气：晴，25°C"
    }
  ],
  "isError": false
}
```

---

## 高级功能

### 1. 资源（Resources）

```python
@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri="file:///path/to/document.txt",
            name="My Document",
            description="A sample document",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    if uri == "file:///path/to/document.txt":
        with open("/path/to/document.txt", "r") as f:
            return f.read()
    raise ValueError(f"Unknown resource: {uri}")
```

### 2. 提示词模板（Prompts）

```python
@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="git_commit",
            description="生成 Git 提交信息",
            arguments=[
                PromptArgument(
                    name="changes",
                    description="git diff 的输出",
                    required=True
                )
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "git_commit":
        changes = arguments["changes"]
        return GetPromptResult(
            description="Generate a git commit message",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Based on these changes:\n\n{changes}\n\nGenerate a concise commit message:"
                    )
                )
            ]
        )
    raise ValueError(f"Unknown prompt: {name}")
```

### 3. 采样（Sampling）

让服务器请求客户端（AI模型）生成文本：

```python
@server.create_message()
async def create_message(messages: list[SamplingMessage], maxTokens: int) -> CreateMessageResult:
    # 这里应该调用 AI 模型
    return CreateMessageResult(
        role="assistant",
        content=TextContent(
            type="text",
            text="This is a generated response."
        ),
        model="claude-3-opus-20240229",
        stopReason="end_turn"
    )
```

---

## 调试 MCP 服务器

### 使用 MCP Inspector

```bash
# 安装
npm install -g @modelcontextprotocol/inspector

# 运行
mcp-inspector node /path/to/server.js
```

打开浏览器访问 `http://localhost:3000`，可以：
- 查看工具列表
- 测试工具调用
- 查看服务器日志

### 手动测试

```bash
# 向服务器发送 JSON-RPC 消息
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node server.js
```

---

## 发布 MCP 服务器

### 发布到 npm（Node.js）

```bash
# 1. 确保 package.json 中有 bin 字段
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "bin": {
    "my-mcp-server": "./server.js"
  }
}

# 2. 发布
npm publish
```

### 发布到 PyPI（Python）

```bash
# 1. 创建 setup.py 或 pyproject.toml
# 2. 构建
python -m build

# 3. 发布
python -m twine upload dist/*
```

---

## 与 WorkBuddy 集成

### 配置 MCP 服务器

编辑 `~/.workbuddy/mcp.json`：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### 在 Skill 中使用 MCP 工具

```markdown
---
name: my-skill
description: 使用自定义MCP工具
---

# My Skill

## 可用工具

当用户说"查询天气"时，调用：

```
use tool: mcp__my-server__get_weather
arguments:
  city: 北京
```

## 注意事项

1. MCP 工具名称格式：`mcp__<server-name>__<tool-name>`
2. 确保 MCP 服务器已启动
3. 如果工具调用失败，检查服务器日志
```

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| MCP 服务器启动失败 | 检查 `command` 和 `args` 是否正确 |
| 工具列表为空 | 确保实现了 `tools/list` 处理器 |
| 工具调用失败 | 检查参数格式是否符合 `inputSchema` |
| 连接超时 | 增加超时时间，或检查服务器是否卡住 |
| 权限错误 | 确保服务器有权限访问所需资源 |

---

## 注意事项

1. **安全性** — 不要暴露敏感操作（如删除文件） without proper authorization
2. **错误处理** — 所有工具调用都应该有 try-catch
3. **日志记录** — 使用 `console.error()` 记录日志（stdout 被协议占用）
4. **性能优化** — 避免在工具调用中执行长时间操作
