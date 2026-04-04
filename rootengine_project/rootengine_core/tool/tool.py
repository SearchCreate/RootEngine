import json
from ..schema.tool import REIF_CONTENT_TOOL_REGISTRY_JSON
REIF_CONTENT_TOOL_REGISTRY = json.loads(REIF_CONTENT_TOOL_REGISTRY_JSON)
from ..utils.time import get_iso_timestamp

from .adapt_new_farmat import adapt_new_format

from jsonschema import validate
class ToolExistError(Exception):
    pass



class Tool:
    def __init__(self,reif_entry_tool_registry:dict,agent):

        self.entry = reif_entry_tool_registry
        self.metadata = self.entry["metadata"]
        self.conversation = self.entry["conversation"]

        self.now_tool_call= None
        self.agent = agent
        self.tool_registry = reif_entry_tool_registry





    def execute(self,tool_call:dict, vali:bool=True)  -> dict:
        #校验一下格式
        if vali:
            validate(self.tool_registry, REIF_CONTENT_TOOL_REGISTRY)

        self.now_tool_call = tool_call
        """
        接受tool_call
        解析工具的参数
        寻址，执行工具
        返回result

        :param tool_call:
        :return:
        """
        tool_result = {}

        #接受参数
        tool_call_adapted = adapt_new_format(self)

        # 验证调用方是否与工具注册表中注册的调用方法一至
        if tool_call_adapted["type"] == self.tool_registry["type"]:
            raise ValueError(
                f"工具registry_id={tool_call_adapted["function"]["registry_id"]}错误：调用方法与 tool_registry 中不一致")

        #寻址，执行工具




        #传入依赖注入的agent实例，和llm返回的参数
        # 根据调用类型写调用逻辑

        # type == "function"
        if tool_call_adapted["type"] == "function":
            #检索是否有工具
            tool = self.tool_registry.get(tool_call_adapted["function"]["registry_id"])

            # 未知工具的检验
            if tool == None:
                raise ToolExistError(f'工具registry_id={tool_call_adapted["function"]["registry_id"]}错误：未知工具')

            # 解析工具参数
            if isinstance(tool_call_adapted,dict):
                kwargs = tool_call_adapted["function"]["arguments"]
            else:
                kwargs = json.loads(tool_call_adapted["function"]["arguments"])



            tool_func = self.tool_registry.get(tool_call_adapted["function"]["registry_id"])["function"]
            # 执行
            result_cont = str(tool_func(**kwargs,agent = self.agent))




        #返回result
        tool_result["call_id"] = tool_call["id"]
        tool_result["content"] = result_cont
        tool_result["creates_at"] = get_iso_timestamp()

        return tool_result

    def execute_many(self,tool_calls:list) -> list[dict]:
        tool_results = []
        for tool_call in tool_calls:
            tool_result = self.execute(tool_call)
            tool_results.append(tool_result)
        return tool_results















