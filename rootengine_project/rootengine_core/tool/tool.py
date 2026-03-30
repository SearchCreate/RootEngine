import json
from ..schema.tool import REIF_CONTENT_TOOL_REGISTRY_JSON
REIF_CONTENT_TOOL_REGISTRY = json.loads(REIF_CONTENT_TOOL_REGISTRY_JSON)
from ..utils.time import get_iso_timestamp

from jsonschema import validate
class ToolExistError(Exception):
    pass



class Tool:
    def __init__(self,reif_entry_tool_registry:dict,agent):

        self._reif_entry_tool_registry = reif_entry_tool_registry["reif_version"]
        self._reif_metadata_tool_registry = reif_entry_tool_registry["reif_metadata"]
        self._tool_registry = reif_entry_tool_registry["content"]

        self.now_tool_call= None
        self.agent = agent

    def adapt_new_format(self)  -> "适配最新版本的reif_content":
        if self._reif_entry_tool_registry["reif_version"] == "1.0":
            if self._reif_metadata_tool_registry["version"] == "0.1.0":

                adapted_reif_content = self._reif_metadata_tool_registry["content"]

                return adapted_reif_content




    def execute(self,tool_call:dict, vali:bool=True)  -> dict:
        #校验一下格式
        if vali:
            validate(self._tool_registry, REIF_CONTENT_TOOL_REGISTRY)

        self.now_tool_call = tool_call
        """
        接受tool_call
        解析工具的参数
        寻址，执行工具
        返回result

        :param tool_call:
        :return:
        """
        result = {}
        #接受参数

        self.now_tool_call = tool_call
        #解析工具参数

        if isinstance(tool_call,dict):
            kwargs = tool_call["arguments"]
        else:
            kwargs = json.loads(tool_call)["arguments"]

        #寻址，执行工具


        #传入依赖注入的agent实例，和llm返回的参数
        #先判断是否是未知工具
        _tool = self.adapt_new_format().get(self.now_tool_call["registry_id"],None)
        if _tool == None:
            raise ToolExistError(f'工具registry_id={self.now_tool_call["registry_id"]}错误：未知工具')


        #判断工具的调用方式
        if self.now_tool_call == "function":

            # 工具执行
            _tool_func = _tool["function"]
            result_cont = _tool_func(**kwargs, agent=self.agent)





        #返回result
        result["call_id"] = tool_call["call_id"]
        result["content"] = result_cont
        result["creates_at"] = get_iso_timestamp()

        return result

    def execute_many(self,tool_calls:list) -> list[dict]:
        tool_results = []
        for tool_call in tool_calls:
            tool_result = self.execute(tool_call)
            tool_results.append(tool_result)
        return tool_results















