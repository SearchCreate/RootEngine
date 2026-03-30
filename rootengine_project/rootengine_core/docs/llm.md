

# 其他


# 简介

# 功能
# code
```python
from typing import Optional,Dict,List,Any

from abc import ABC,abstractmethod


class BaseLLM(ABC):


    @abstractmethod

    def call(self,
             messages:List[dict[str,Any]],
             tool_list:Optional[List[Dict[str, Any]]],
             tool_choice: Optional[str],
             **kwargs)\
            -> Dict[str, Any]:
        """

        :param messages: 消息列表
        :param tool_list: 可用工具列表
        :param tool_choice: 工具选择策略
        :param kwargs:
        :return:包含 "content" 和 "tool_calls" 字段的字典，可选 "usage"

        """
        pass
```



# BaseLLM
BaseLLM只提供接口规范，具体插件需额外编写

## 1.输入参数
### messages
消息列表

### tool_registry
工具注册表，格式参照官网tool_registry

### tools_choice
工具选择策略，

###


## 2. 返回的格式（跟 chat_completion_api 不同）
```python
return {
   "content":"llm,tool,system，甚至以后新的角色的内容（list）" ,
   "tool_calls":"工具调用请求（list）",
    "usage":"可选，（dict）"
    
}
```

对应的jsonschema（写成jsonschema只是易于表达，实际返回的是 字典 不是json字符串）

```json
{
  "type": "object",
  "description": "返回格式",
  "properties": {
    "content": {
      "type": "string",
      "description": "储存内容"
    },
    "tool_calls": {
      "type": "array",
      "description": "工具调用请求",
      "item": {
        "pattern": "参考官方tool_call的规范"
      },
      "usage":{
        "prompt_tokens": 13,    // 输入提示
        "completion_tokens": 7, // 生成回答
        "total_tokens": 20      // 总消耗
      }
    }
  }
}
```














