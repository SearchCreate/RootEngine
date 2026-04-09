

import json
from jsonschema import validate
from ..schema.runtime.reif_schema import get_json
TOOL_REGISTRY_SCHEMA = get_json("tool.tool_registry")
TOOL_CALL_SCHEMA = get_json("tool.tool_call")
TOOL_RESULT_SCHEMA = get_json("tool.tool_result")
TOOL_FUNC_MAP_SCHEMA = get_json("tool.tool_func_map")

from typing import Dict
from ..utils.time import get_iso_timestamp
from .adapter import tool_registry_entry_adapt


class ToolExistError(Exception):
    pass

class Tool:
    def __init__(self,tool_registry_entry:dict, agent, tool_func_map: dict = None, ):
        """
        :param entry: tool_registry 的 reif_entry
        :param tool_func_map: 与 tool_registry 对应的 工具映射字典（tool_registry 的工具在 tool_func_map 必须有 ） 格式参照 ../schema/source/tool/tool_func_map.json,(可已没有)
        """

        self.entry = tool_registry_entry_adapt(tool_registry_entry)
        self.tool_registry = self.entry["reif_content"]
        self.tool_func_map = tool_func_map

        # # 判断 tool_registry 是否有在 tool_func_map 未知的工具
        # tool_func_map_list = [i for i in self.tool_func_map]
        # for tool_registry_id in self.tool_registry:
        #     if tool_registry_id not in tool_func_map_list:
        #         raise ToolExistError(f"错误： tool_registry 中的 工具'{tool_registry_id} 在 tool_func_map 不存在'")

        self.now_tool_call= None
        self.agent = agent



    def execute(self,tool_call:dict, vali:bool=True)  -> Dict:
        #校验一下格式


        self.now_tool_call = tool_call
        if vali:
            validate(self.now_tool_call, TOOL_CALL_SCHEMA)


        """
        接受tool_call
        解析工具的参数
        寻址，执行工具
        返回result

        :param tool_call:
        :return:
        """
        tool_result = {}

        # 判断调用方法
        if self.now_tool_call["type"] == "function":

            def func_call():

                registry_id = self.now_tool_call["function"]["registry_id"]

                # 检查，寻址
                #判断是否 在tool_registry 里是未知工具
                if self.tool_registry.get(registry_id) is None:
                    raise ToolExistError(f"错误： '工具 registry_id': '{registry_id}' 在 tool_registry 不存在")
                #解析参数

                kwargs = self.now_tool_call["function"]["arguments"]

                # 在tool_func_map 里找 工具的函数
                tool_func = self.tool_func_map.get(registry_id)
                if tool_func is None:
                    raise ToolExistError(f"错误： tool_registry 中的 工具'{registry_id} 在 tool_func_map 不存在'")


                # 执行
                try:
                    result_cont = str(tool_func(**kwargs, agent=self.agent))
                    status = "success"
                except Exception as e:
                    result_cont = None
                    status = "error"
                    error_message = e

                # 返回result
                tool_func_result = {
                    "call_id": self.now_tool_call["id"],
                    "type": "function",
                    "function": {
                    "result_content": result_cont,
                    "status": status
                    }
                }

                if status ==  "error":
                    tool_func_result["error_message"] = error_message



                return tool_func_result

            tool_result = func_call()

        else:
            raise ValueError(f"错误： 未知的调用方式 '{self.now_tool_call["type"]}'")
        # 最后加上时间
        tool_result["created_at"] = get_iso_timestamp()

        return tool_result

    def execute_many(self,tool_calls:list) -> list[dict]:
        tool_results = []
        for tool_call in tool_calls:
            tool_result = self.execute(tool_call)
            tool_results.append(tool_result)
        return tool_results



















