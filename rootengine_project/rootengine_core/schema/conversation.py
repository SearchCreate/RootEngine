REIF_CONTENT_CONVERSATION_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "reif_content_conversation",
  "description": "memory数据格式,//此表位于reif_content下",
  "type": "array",
  "items": {
    "type": "object",
    "description": "存每条会话记录",
    "properties": {
      "role": {
        "type": "string",
        "description": "本条会话的角色",
        "enum": [
          "system",
          "user",
          "assistant",
          "tool"
        ]
      },
      "content": {
        "type": ["string","null"],
        "description": "文本内容（role = assistant 或 role = tool 可为 null）"
      },
      
      "tools":{
        "type": "array",
        "description": "工具相关信息",
        "items": {
          "description": "具体格式为保持兼容，暂不给予具体格式"
        }  
      },
      
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "创建时间 ISO 8601"
      },
        
      "extra": {
        "type": ["object","null"],
        "additionalProperties": true,
        "description": "扩展数据"
      }
    },
    "required": ["role","created_at"]
  }
}
"""








REIF_CONTENT_NO_TOOL_CONVERSATION_JSON = r"""{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "reif_content_base_conversation",
  "description": "基础对话消息列表（无工具字段）",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "role": {
        "type": "string",
        "enum": ["system", "user", "assistant", "tool"]
      },
      "content": { "type": ["string", "null"] },
      "created_at": { "type": "string", "format": "date-time" },
      "extra": { "type": ["object", "null"], "additionalProperties": true }
    },
    "required": ["role", "created_at"]
  }
}"""



















