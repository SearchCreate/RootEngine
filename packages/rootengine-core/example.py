from rootengine_core import BaseConversation, OpenAIAdapter, Tool
from rootengine_core.utils import create_reif

# 工具定义
def example_tool(param_1, agent=None):
    return "success" if param_1 == "example" else "fail"

# tool_registry（reif_entry 格式）
tool_registry_entry = create_reif({
    "category": "tool_registry",
    "name": "我的工具集"
})

tool_registry_entry["reif_content"] = {
    "a1b2c3d4e5f6789012345678abcdef01": {
        "name": "example_tool",
        "description": "输入 'example' 返回 success",
        "type": "function",
        "function": {
            "name": "example_tool",
            "description": "输入 'example' 返回 success，否则返回 'fail'",
            "parameters": {
                "type": "object",
                "properties": {"param_1": {"type": "string"}},
                "required": ["param_1"]
            }
        }
    }
}

tool_func_map = {
    "a1b2c3d4e5f6789012345678abcdef01": example_tool
}

# 初始化
agent = None  # 将来注入智能体
tool = Tool(tool_registry_entry, agent, tool_func_map)

conv = BaseConversation()
conv.append("system", "你是一个有帮助的助手")
conv.append("user", "请调用 example_tool，参数为 'example'")

# 模拟 LLM 返回工具调用
mock_llm_response = {
    "id": "chatcmpl-123",
    "model": "gpt-4o-mini",
    "choices": [{
        "message": {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "5f3d78a29c0b4e61872d9503f1e2a6c4",
                "type": "function",
                "function": {
                    "name": "a1b2c3d4e5f6789012345678abcdef01",
                    "arguments": {"param_1": "example"}
                }
            }]
        }
    }]
}

# 执行工具
adapter = OpenAIAdapter(model="gpt-4o-mini")
llm_output = adapter.from_provider(mock_llm_response["choices"][0]["message"])

# 添加工具调用到对话
tool_result = tool.execute(llm_output["tool_calls"][0])
print(f"工具返回: {tool_result}")

# 把工具结果加入对话
#临时修改下全局变量 CONVERSATION_ROLE
class ChangeCONVERSATION_ROLE:
    def __init__(self, add_roles:list):
        from rootengine_core.constants.conversation import CONVERSATION_ROLE
        self.CONVERSATION_ROLE = CONVERSATION_ROLE
        self.add_role = add_roles
    def __enter__(self,):
        self.CONVERSATION_ROLE += [role for role in self.add_role]
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.CONVERSATION_ROLE.pop()

with ChangeCONVERSATION_ROLE(["tool"]):
    conv.append("tool", str(tool_result["function"]["result_content"]))



print(conv.messages)
