CHAT_LLM_MESSAGES_JSON = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "llm_messages",
  "type": "array",
  "items": {
    "type": "object",
    "description": "llm的返回格式",
    "properties": {
      "role": {
        "type": "string",
        "description": "角色信息",
        "enum": ["system","user","assistant","tool"]
      },
      "content": {
        "type": "string",
        "description": "此条储存的具体内容，当role = user或assistant或system 填内容，当 role = tool 时填tool_result,"
      },
      "tool_calls": {
        "type": ["array","null"],
        "description":"llm的工具调用,具体格式参见官方规范"
      },
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "创建时间 ISO 8601"
      },
      "extra": {
        "type": ["object","null"],
        "description": "扩展"
      }
    },
    "required": ["role","created_at"]
  }
}

TOOL_CHOICE_JSON   = {
  "type":["string","object","null"],
  "description":"工具选择策略，具体看官方规范"
}











CHAT_LLM_RESPONSE_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "llm_response",  
  "type": "object",
  "description": "llm的返回格式",
  "properties": {
    "content": {
      "type": "string",
      "description": "储存内容"
    },
    "tool_calls": {
      "type": "array",
      "description": "工具调用请求",
      "items": {
        "description": "参考官方 tool_call 的规范"
      }
    },
    "usage": {
      "type": "object",
      "properties": {
        "prompt_tokens": {
          "type": "integer",
          "description": "输入提示词用的token数"
        },
        "completion_tokens": {
          "type": "integer",
          "description": "生成回答用的token数"
        },
        "total_tokens": {
          "type": "integer",
          "description": "总token数"
        }
      }
    }
  }
}"""