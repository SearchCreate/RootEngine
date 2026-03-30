REIF_CONTENT_ARRAY_TOOL_CALL_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "tool_call",
  "description": "单个工具调用的信息",
  "type": "object",
  "properties": {
    "call_id": {
      "type": "string",
      "pattern": "^[0-9a-fA-F]{32}$",
      "description": "工具调用的调用id"
    },
    "call_type":{
      "type": "string"
      "description":"工具的调用方式种类"
      "enum":["function"]
    }
    "registry_id": {
      "type": "string",
      "description": "工具调用时，被调用工具在注册表中的id"
    },
    "arguments": {
      "type": "object",
      "description": "工具所需的参数，直接按给的工具列表的参数给，不用schema规范",
      "properties":{}
    },
    "created_at": {
      "type": "string",
      "description": "创建时间",
      "format": "date-time"
    }
  },
  "required": ["call_id","registry_id","arguments","created_at"]
}"""






REIF_CONTENT_TOOL_REGISTRY_JSON = {
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
        "call_type": { "type": "string", "enum": ["function"], "description": "工具调用方式" },
        "function": { "type": "string", "description": "函数引用，格式为 'module.path:func_name' 或运行时内存中的函数对象" },
        "parameters": { "type": "object", "description": "工具参数的 JSON Schema" }
      },
      "required": ["name", "call_type"],
      "allOf": [
        {
          "if": { "properties": { "call_type": { "const": "function" } } },
          "then": { "required": ["function", "parameters"] }
        }
      ],
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}




REIF_CONTENT_ARRAY_TOOL_RESULT_JSON = {
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
  "required": ["tool_call_id","result_content","created_at"]
}














