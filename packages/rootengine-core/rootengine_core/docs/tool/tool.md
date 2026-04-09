# 注意事项

# Tool
## r__intit__
```python
class Tool:
    def __init__(self,entry:dict,agent):

        self.entry = entry
        self.tool_registry = self.entry["reif_content"]

        self.now_tool_call= None
        self.agent = agent
```
- self.agent 是依赖注入

## execute
```python
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
                    raise ToolExistError(f"错误： '工具 registry_id': '{registry_id}' 未知工具")
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
                    "call_id": self.now_tool_call["call_id"],
                    "type": "function",
                    "function": {
                    "result_content": result_cont,
                    "status": status
                    }
                }

                if status ==  "error":
                    tool_result["error_message"] = error_message
                tool_result["created_at"] = get_iso_timestamp()


                return tool_result

            tool_result = func_call()

        else:
            raise ValueError(f"错误： 未知的调用方式 '{self.now_tool_call["type"]}'")


        return tool_result

```
- 仅支持传入最新的tool_call
- 会有调用方式的判断
- 这里把函数工具的调用改成了函数
## execute_many
```python
    def execute_many(self,tool_calls:list) -> list[dict]:
        tool_results = []
        for tool_call in tool_calls:
            tool_result = self.execute(tool_call)
            tool_results.append(tool_result)
        return tool_results
```
- tool_calls，tool_results 是由组成的tool_call，tool_result 的列表