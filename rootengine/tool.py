import json

from .utils import ps

class Tool:
    '''
    据一个工具注册表操作
    注册表格式：

[{

    "name" : "工具函数实际名",
    "func_name":适配器函数名（实际函数映射）,
    "description":"描述",
    "parameters":{
        "type":"数据类型(填str/list...)",
        properties:{
                "参数名": {"type":"数据类型（str/list...)"}
                    }
    },

}]

    '''

    def __init__(self, tools_register,agent):
        '''

        :param tools_register:工具注册表(list)
        :param agent 传agent实例
        工具接口：
        尽量返回str
        '''
        self.tools_register = tools_register
        self.agent = agent

    def tool_call_deal(self, tool_calls):
        '''
        搜索并执行工具
        :param tool_calls:
        :return:
        '''
        # 判断是否调用工具
        if tool_calls:

            tool_result_list = []
            ps('调用工具中')
            #遍历tool_calls
            for ii in tool_calls:
                abc = 0
                tool_name = ii.function.name


                try:
                    #解析arguments
                    arg = ii.function.arguments
                    #arguments = universal_params_parser(ii.function.arguments)  #用自己的解析函数
                    arguments = json.loads(arg)
                    print(f"参数：{arguments}")

                    # 调用工具
                    try:
                        result = self.tools_register[tool_name]["function"](agent=self.agent, **arguments)
                    except Exception as e:
                        ps(f'工具{tool_name}执行出错: {e}')
                        result = f'工具{tool_name}执行出错: {str(e)}'

                except Exception as e:
                    #参数解码问题
                    result = f"工具参数解码错误：{e}"
                    ps(e)
                tool_call_id = ii.id


                #生成工具调用结果
                tool_result_list.append({"tool_call_id": tool_call_id, "result": result})

            return tool_result_list
        else:
            #无工具调用终止工具调用进程
            return []
