# simple_conversation 规范文档

基础对话消息列表的 JSON Schema 定义。

## 概述

`simple_conversation` 是一个用于存储对话消息的数组结构，每个元素代表一条消息。支持：
- 系统提示、用户消息、助手回复、工具调用四种角色
- 工具调用时的双向通信（call/result）
- 可扩展的 extra 字段

## 完整示例

```json
[
  {
    "role": "system",
    "content": "你是一个有帮助的助手",
    "created_at": "2026-04-11T10:00:00Z"
  },
  {
    "role": "user",
    "content": "帮我查询天气",
    "created_at": "2026-04-11T10:00:05Z"
  },
  {
    "role": "assistant",
    "content": null,
    "tool_refer": [
      {
        "tool_record_id": "abc123def456",
        "tool_record_path": "data/tools/abc123def456.json",
        "type": "call"
      }
    ],
    "created_at": "2026-04-11T10:00:10Z"
  },
  {
    "role": "tool",
    "content": null,
    "tool_refer": [
      {
        "tool_record_id": "abc123def456",
        "tool_record_path": "data/tools/abc123def456.json",
        "type": "result"
      }
    ],
    "created_at": "2026-04-11T10:00:15Z"
  },
  {
    "role": "assistant",
    "content": "今天北京天气晴朗，温度 15-25 度",
    "created_at": "2026-04-11T10:00:20Z"
  }
]
```

## 字段说明

### role

| 值 | 说明 |
|----|------|
| `system` | 系统提示消息 |
| `user` | 用户消息 |
| `assistant` | 助手回复 |
| `tool` | 工具返回结果 |

### content

消息的文本内容。

**规则**：
- `system` / `user`：必须有内容
- `assistant` 无工具调用：有内容
- `assistant` 有工具调用：`null`
- `tool`：`null`

### tool_refer

工具调用相关信息。

**存在条件**：
- `role = assistant` 且有工具调用时存在
- `role = tool` 时存在

**子字段**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `tool_record_id` | string | 是 | 工具操作 ID，用于关联 call 和 result |
| `tool_record_path` | string | 是 | 工具操作记录的路径（指向数据库或文件） |
| `type` | string | 是 | `call`=LLM 请求调用工具，`result`=工具返回结果 |

**配对规则**：
- 一个 `call` 必须对应一个 `result`
- `tool_record_id` 相同表示是同一次工具调用

### created_at

ISO 8601 格式的时间戳，必填。

### extra

扩展字段，类型为对象或 null，可存储任意附加信息。

## 工具调用流程

```
用户消息
    │
    ▼
assistant (content=null, tool_refer.type=call)
    │
    ▼
tool (content=null, tool_refer.type=result)
    │
    ▼
assistant (content=结果描述)
```


工具结果实际保存在 `tool_record_path` 指向的位置，这里只做引用。

## Schema 文件

原始定义：[simple_conversation.json](../../schema/source/conversation/simple_conversation.json)
