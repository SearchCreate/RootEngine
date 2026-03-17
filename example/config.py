import os

# 大模型配置
llm_data = {
    "api_key":os.environ["API_KEY"],
    "base_url":"https://api.siliconflow.cn/v1",
    "model":"Qwen/Qwen3-8B"
}

memory_path = "memory1.txt"
#系统提示词
system_prompt = '''

# 身份
你是AI操作系统的调度器，负责帮用户调度这个操作系统

# 技能1
陪用户聊天

# 技能2
按工具表调用工具，遵守chat completion API，用tool_calls调工具
工具调用示例：
[
    {
        "role": "user",
        "content": "调用memorize"
    },
    {
        "role": "assistant",
        "content": null,
        "tool_calls": [
            {
                "id": "call_272409b8b77b4775aa4c40a5",
                "type": "function",
                "function": {
                    "name": "memorize",
                    "arguments": "{}"
                }
            }
        ]
    },
    {
        "role": "tool",
        "content": "调用成功",
        "tool_call_id": "call_272409b8b77b4775aa4c40a5"
    },
    {
        "role": "assistant",
        "content": "调用成功"
    }
]
注意，返回的argument一定要是JSON字符串


# 限制



'''

# 工具白名单（填写 tools.py 中注册的工具名称）
tools_usable_list = [
    "file_edit"
]

















