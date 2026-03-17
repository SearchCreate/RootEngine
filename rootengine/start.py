from .tools_register import ToolRegistry
import importlib


class Start:
    def __init__(self,config_path,tools_path):
        '''
        :param tools: 工具文件目录
        :param config: 配置文件路径
        
        '''
        #加载工具白名单
        self.config = importlib.import_module(config_path)
        self.tools_usable = self.config.tools_usable_list


        #加载tools_registry

        #1.创建注册中心实例
        reg_obg = ToolRegistry(tools_path)
        #2.加载所有工具 的注册表
        self.all_registry = reg_obg.reg_discover_tool()



    def start_agent_tool_register(self):
        '''
        通过对工具文件、配置文件的解析，合成给agent的带函数映射的tool注册表

        :return: 完好的工具注册表（带函数映射）
        例：
        "name":{
            “function”:function
            "data":{
                "description": "调出对话历史，直接打印到用户屏幕上，不会给llm返回结果",
                "parameters": {
                    "type": "object",
                    "properties": {}
                               }
            }

        }
        '''

        # 获取原注册表

        agent_tool_register = {}
        for usable in self.tools_usable:
            try:
                #将tool_usable中可用的工具名，
                agent_tool_register[usable] = self.all_registry[usable]
            except KeyError:
                print(f"工具{usable}错误：工具白名单中填写未知工具")
        return agent_tool_register


    def start_deal(self):
        start_dict = {}
        start_dict["llm_data"] = self.config.llm_data
        start_dict["memory_path"] = self.config.memory_path
        start_dict["system_prompt"] = self.config.system_prompt
        start_dict["tool_register"] = self.start_agent_tool_register()
        return start_dict

