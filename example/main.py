import sys
import os

from rootengine import Start, Agent


## 如果未手动安装 此包 至虚拟环境，直接运行此文件，需取消下面两行的注释（若这样，不可改变示例文件的位置），目前未上传pypi，需手动安装至虚拟环境
# 将当前文件的父目录（即项目根目录）加入搜索路径
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))









start_dict = Start(config_path="config",tools_path="tools").start_deal()
#创建Agent实例
ass2 = Agent(
    llm_data = start_dict["llm_data"],
    agent_name= "check",
    agent_id= 1,
    memory_path= start_dict["memory_path"],
    system_prompt = start_dict["system_prompt"],
    tool_register = start_dict["tool_register"]
)   #ass是assistant的简写
#主循环
while 1:
    user_input = input("你：")

    reply_content = ass2.agent_llm_with_tool_chat(user_input)
    print(f"助手：{reply_content}")

