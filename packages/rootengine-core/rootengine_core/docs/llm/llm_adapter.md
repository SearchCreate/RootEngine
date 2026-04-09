```markdown
# OpenAI 适配器教程

## 简介

`llm/openai_adapter.py` 实现了两套格式的互转：

- **框架格式** — 符合你的 REIF 规范
- **OpenAI 格式** — 兼容 OpenAI API

---

## 核心类

| 类 | 说明 |
|---|---|
| `BaseLLMAdapter` | 抽象基类，定义接口 |
| `OpenAIAdapter` | OpenAI 兼容 API 的适配器实现 |

---

## 快速开始

```python
from rootengine_core_2.llm.openai_adapter import OpenAIAdapter

# 初始化
adapter = OpenAIAdapter(
    model="gpt-4",
    temperature=0.7,
    timeout=60
)
```

---

## 正向适配：框架 → OpenAI

### 单次调用

```python
# 框架格式的消息列表
messages = [
    {"role": "system", "content": "你是一个助手", "created_at": "..."},
    {"role": "user", "content": "你好", "created_at": "..."},
]

# 框架格式的工具注册表
tool_registry = {
    "abc123": {
        "name": "get_weather",
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询天气",
            "parameters": {"type": "object", "properties": {...}}
        }
    }
}

# 转换为 OpenAI API 参数
openai_params = adapter.to_provider(
    messages=messages,
    tool_registry=tool_registry,
    tool_choice="auto"
)

# openai_params 包含: model, messages, tools, tool_choice, temperature, timeout
```

### 框架 → OpenAI 的转换规则

| 字段 | 框架格式 | OpenAI 格式 |
|------|----------|--------------|
| 消息角色 | `role` | `role` (不变) |
| 工具 ID | `function.registry_id` | `function.name` |
| 工具注册表 | `{registry_id: {...}}` | `{tools: [{type, function: {...}}]}` |

---

## 逆向适配：OpenAI → 框架

### 转换 LLM 返回

```python
# 假设这是 OpenAI API 的原始返回
openai_response = {
    "content": "你好！",
    "tool_calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": {"city": "北京"}
            }
        }
    ],
    "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    "created": 1704067200
}

# 转换为框架格式 (llm_output)
llm_output = adapter.from_provider(openai_response)
```

### 转换单条消息

```python
# OpenAI 返回的消息
openai_message = {
    "role": "assistant",
    "content": "好的，我去查一下天气",
    "tool_calls": [...]
}

# 转换为框架格式 (llm_message)，用于存入消息列表
frame_message = adapter.message_to_frame(openai_message)
```

### OpenAI → 框架的转换规则

| 场景 | OpenAI 格式 | 框架格式 |
|------|-------------|----------|
| assistant 消息 | `"content": "你好"` | `"content": "你好"` |
| 纯工具调用 | `"content": null` | `"content": null` |
| tool 消息 | `"content": "结果字符串"` | `"content": {tool_result对象}` |
| 工具调用 ID | `"function.name"` | `"function.registry_id"` |

---

## 完整对话流程示例

```python
from rootengine_core_2.llm.openai_adapter import OpenAIAdapter

adapter = OpenAIAdapter(model="gpt-4")

# 1. 构建消息列表（框架格式）
messages = [
    {"role": "system", "content": "你是一个助手", "created_at": "..."},
    {"role": "user", "content": "北京天气怎么样？", "created_at": "..."},
]

# 2. 转换为 OpenAI 格式并调用 API
openai_params = adapter.to_provider(messages, tool_registry, tool_choice="auto")
# 调用 openai_api.chat.completions.create(**openai_params)

# 3. 假设 LLM 返回了工具调用
llm_output = adapter.from_provider(openai_response)

# 4. 将 assistant 消息存入列表
messages.append(adapter.message_to_frame({
    "role": "assistant",
    "content": llm_output["content"],
    "tool_calls": llm_output.get("tool_calls"),
    "created": "..."
}))

# 5. 执行工具后，将 tool 消息存入列表
tool_result_message = {
    "role": "tool",
    "tool_call_id": "call_abc123",
    "content": "结果字符串",
    "created": "..."
}
messages.append(tool_result_message)
```

---

## 扩展其他 Provider

```python
class AnthropicAdapter(BaseLLMAdapter):
    def __init__(self, model: str = "claude-3-opus", **config):
        self.model = model
        self.config = config

    def to_provider(self, messages, tool_registry, tool_choice, **kwargs): ...
    def from_provider(self, response): ...
    def message_to_frame(self, message): ...
```

继承 `BaseLLMAdapter`，实现三个抽象方法即可。
```