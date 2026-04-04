REIF_CONTENT_ARRAY_TOOL_CALL_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "tool_call",
  "description": "单个工具调用的信息，用于存储 LLM 返回的工具调用请求",
  "type": "object",
  "required": ["id", "type", "function", "created_at"],
  "properties": {
    "id": {
      "type": "string",
      "description": "工具调用的唯一标识符，通常由 LLM 生成，用于关联工具结果",
      "pattern": "^[0-9a-fA-F]{32}$"
    },
    "type": {
      "type": "string",
      "enum": ["function"],
      "description": "工具调用类型，目前仅支持 'function'，预留扩展"
    },
    "function": {
      "type": "object",
      "required": ["registry_id", "arguments"],
      "properties": {
        "registry_id": {
          "type": "string",
          "description": "工具名称，应与工具注册表中的名称一致"
        },
        "arguments": {
          "type": "object",
          "description": "工具所需的参数，以键值对形式给出，具体结构由工具定义",
          "additionalProperties": true
        }
      },
      "additionalProperties": false
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "工具调用创建时间（ISO 8601）"
    },
    "extra": {
      "type": "object",
      "additionalProperties": true,
      "description": "扩展元数据"
    }
  },
  "additionalProperties": false
}"""






REIF_CONTENT_TOOL_REGISTRY_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "tool_registry",
  "description": "工具注册表，键为 tool_id（32位十六进制），值为工具信息",
  "type": "object",
  "patternProperties": {
    "^[0-9a-fA-F]{32}$": {
      "type": "object",
      "properties": {
        "name": { "type": "string", "description": "工具名称" },
        "description": { "type": "string", "description": "工具描述" },
        "type": { "type": "string", "enum": ["function"], "description": "工具调用方式" },
        "function": { "type": "string", "description": "函数引用，内存中的函数对象" },
        "parameters": { "type": "object", "description": "工具参数的 JSON Schema" }
      },
      "required": ["name", "type"],
      "allOf": [
        {
          "if": { "properties": { "type": { "const": "function" } } },
          "then": { "required": ["function", "parameters"] }
        }
      ],
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}"""




REIF_CONTENT_ARRAY_TOOL_RESULT_JSON = """{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "tool_result",
  "type": "object",
  "properties": {
    "call_id": {
      "type": "string",
      "pattern": "^[0-9a-fA-F]{32}$",
      "description": "工具调用的id"
    },
    "result_content": {
      "type": "string",
      "description": "工具返回的内容"
    },
    "created_at": {
      "type": "string",
      "description": "创建时间",
      "format": "date-time"
    }
  },
  "required": ["call_id","result_content","created_at"]
}"""














