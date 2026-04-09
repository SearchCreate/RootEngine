```markdown
# LLM Message Schema 设计

## 概述

`llm_message.json` 定义了 LLM 对话中单条消息的格式，与 OpenAI API 格式解耦，同时兼容常见的角色类型（`system`, `user`, `assistant`, `tool`）。该 Schema 引用 `tool_call.json` 和 `tool_result` 结构（通过 `$ref` 或内联定义）。

## 消息结构

```json
{
  "role": "assistant",
  "content": null,                          // 或 string，或 tool_result 对象
  "tool_calls": [{...tool_call对象...}],    // 仅 assistant 角色可包含
  "created_at": "2024-01-01T00:00:00Z",
  "extra": {...}
}
```

```json
{
  "role": "tool",
  "content": {                              // tool_result 对象
    "call_id": "a1b2...",
    "result_content": "...",
    "status": "success"
  },
  "tool_call_id": "a1b2...",                // 必填，关联 tool_call.id
  "created_at": "2024-01-01T00:00:00Z",
  "extra": {...}
}
```

## 字段说明

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `role` | string | ✅ | 消息角色，枚举值：`system`, `user`, `assistant`, `tool` |
| `content` | oneOf (`null`, `string`, `object`) | ❌ | 消息内容。`role` 为 `tool` 时，该字段应为 `tool_result` 对象；其他角色可为字符串或 `null` |
| `tool_calls` | array of `tool_call` | ❌ | 仅当 `role` 为 `assistant` 时可出现，表示模型请求调用的工具列表 |
| `tool_call_id` | string | 条件必填 | 当 `role` 为 `tool` 时必填，值为对应 `tool_call.id`，用于关联请求与结果 |
| `created_at` | string (ISO 8601) | ✅ | 消息创建时间 |
| `extra` | object | ❌ | 扩展元数据，任意键值对 |

## 设计要点

1. **`content` 的多样性**  
   使用 `oneOf` 支持三种类型：`null`（无内容）、`string`（普通文本）、`object`（用于 `tool` 角色的 `tool_result` 对象）。

2. **`tool_calls` 引用**  
   通过 `$ref` 引用独立的 `tool_call.json` Schema，保持模块化。

3. **角色约束**  
   - `assistant` 角色可包含 `tool_calls`，此时 `content` 通常为 `null`。
   - `tool` 角色必须提供 `tool_call_id`，且 `content` 应为 `tool_result` 对象。

4. **时间格式**  
   `created_at` 使用 ISO 8601 字符串格式（如 `2024-01-01T00:00:00Z`）。

## 完整 Schema 示例（片段）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "llm_message",
  "description": "LLM 对话消息单条格式，与 OpenAI 格式解耦",
  "type": "object",
  "properties": {
    "role": {
      "type": "string",
      "enum": ["system", "user", "assistant", "tool"]
    },
    "content": {
      "oneOf": [
        { "type": "null" },
        { "type": "string" },
        { "$ref": "tool_result.json" }   // 假设有独立定义
      ]
    },
    "tool_calls": {
      "type": "array",
      "items": { "$ref": "tool_call.json" }
    },
    "tool_call_id": {
      "type": "string",
      "pattern": "^[0-9a-fA-F]{32}$"
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "extra": {
      "type": "object",
      "additionalProperties": true
    }
  },
  "required": ["role", "created_at"],
  "allOf": [
    {
      "if": {
        "properties": { "role": { "const": "assistant" } }
      },
      "then": {
        "properties": { "tool_calls": { "type": "array" } }
      }
    },
    {
      "if": {
        "properties": { "role": { "const": "tool" } }
      },
      "then": {
        "required": ["tool_call_id"],
        "properties": {
          "content": { "$ref": "tool_result.json" }
        }
      }
    }
  ]
}
```

> 以上 Schema 示例中 `tool_result.json` 应单独定义，内容包含 `call_id`、`result_content`、`status` 等字段，与 `tool_result` 结构一致。

## 后续可调整项

- 是否需要将 `tool_result` 直接内联到 `content` 的 `oneOf` 中，而不是外部引用？
- `tool_calls` 是否允许在 `role` 为 `tool` 时出现？当前设计不允许。
- 是否需要增加 `name` 字段（如 OpenAI 格式中的可选名称）？

如有任何调整需求，请随时提出。
```