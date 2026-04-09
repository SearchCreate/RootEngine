# RootEngine Core

AI Agent 框架的底层组件库。

## 这是什么

RootEngine Core 是一个用于**构建 Agent 框架的框架**。它提供：

- **REIF 格式** - 结构化的 Agent 信息交换格式，统一对话、工具调用、结果的规范
- **核心组件** - 对话管理、工具系统、LLM 适配器
- **可组合** - 自由组合这些组件来构建你自己的 Agent

如果你想从零搭建一个 Agent 系统，这是一个不错的起点。如果你想要一个开箱即用的 Agent，可能还不适合你。

## 安装

```bash
pip install rootengine-core
```

要求：Python >= 3.8

## REIF 是什么

REIF（RootEngine Information Format）是一套信息格式规范，定义了 Agent 内部和组件之间如何交换数据：

- **conversation** - 对话历史
- **tool_registry** - 工具注册表
- **tool_call** - 工具调用请求
- **tool_result** - 工具执行结果

使用统一格式的好处是：组件之间接口稳定，方便替换和扩展。

## 快速开始

### 对话管理

```python
from rootengine_core import BaseConversation

conv = BaseConversation()
conv.add("system", "你是一个有帮助的助手")
conv.add("user", "你好")

print(conv.messages)
# [
#   {"role": "system", "content": "你是一个有帮助的助手", "created_at": "..."},
#   {"role": "user", "content": "你好", "created_at": "..."}
# ]
```

### 工具调用

```python
from rootengine_core import Tool
from rootengine_core.utils import create_reif

# 定义一个工具
def greeting(name, agent=None):
    return f"Hello, {name}!"

# 工具注册表（REIF 格式）
registry = create_reif({"category": "tool_registry"})
registry["reif_content"] = {
    "a1b2c3d4e5f6789012345678abcdef01": {
        "name": "greeting",
        "type": "function",
        "function": {
            "name": "greeting",
            "description": "打招呼",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        }
    }
}

# 初始化工具
tool = Tool(
    tool_registry_entry=registry,
    agent=None,
    tool_func_map={"a1b2c3d4e5f6789012345678abcdef01": greeting}
)

# 执行工具调用
result = tool.execute({
    "id": "call_001",
    "type": "function",
    "function": {
        "registry_id": "a1b2c3d4e5f6789012345678abcdef01",
        "arguments": {"name": "Alice"}
    },
    "created_at": "2024-01-01T00:00:00Z"
})

print(result)
# {"call_id": "call_001", "type": "function",
#  "function": {"result_content": "Hello, Alice!", "status": "success"},
#  "created_at": "..."}
```

### LLM 适配器

```python
from rootengine_core import OpenAIAdapter

adapter = OpenAIAdapter(model="gpt-4o-mini")
# adapter.from_provider(llm_response)  # 解析 LLM 返回
```

## 状态

这是一个早期项目，核心组件可用，但：
- 文档还不完整
- 工具系统示例较少
- 尚未经过大规模生产验证

## 模块一览

| 模块 | 说明 |
|------|------|
| `conversation` | 对话管理 |
| `tool` | 工具注册与执行 |
| `llm` | LLM 适配器 |
| `utils/reif_func` | REIF 格式创建与验证 |

## 其他
- utils 里有很多好玩的东西
## 许可证

MIT
