from .utils import oa
import sys
try:
    from openai import OpenAI
except ImportError:
    print(" 错误：没有安装 openai 库，请运行：pip install openai")
    sys.exit(1)     



class LlmOpenAI:
    '''
    维护一个大模型的连接
    配置步骤
    配置
    初始化
    配置完成
    '''

    def __init__(self, llm_data):
        '''
        初始化openai客户端
        :param llm_data:大模型配置
        llm_data格式
        {
            "api_key":"",
            "base_url":"",
            "model":""
        }
        '''

        self.api_key = llm_data.get('api_key')
        self.base_url = llm_data.get('base_url')
        self.model = llm_data.get('model')

    # openai客户单初始化
    def llm_start(self):
        # API接口
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        return client

    def llm_message_data(self, role, system_prompt, memory, input_data, tool_result_list=None):
        '''
        :param role角色
        :param system_prompt:系统提示词（str）
        :param memory:历史对话记忆（list）
        :param input_data:要说的话（str）
        :param tool_result_list:如果tool要向llm返回数据，填它，列表形式
        tool_result_list格式：
        [
            {
                "tool_call_id":"",
                "result":''
            }
        ]
        如果你的role是user，你会进入跟llm聊天的模式，此时tool_result_list没用
        如果你的role是tool，你将会进入tool向llm返回结果的模式,此时input_data没用:
        :return:message（消息列表list）
        '''
        # 初始化
        # 系统提示词
        system1 = [oa("system", system_prompt)]

        # 用户、工具提示词
        now = []
        # 如果是user的分支
        if role == "user":
            now.append(oa('user', input_data))
        # 如果是 tool返回数据 的分支
        if role == "tool":
            # 解析tool_call_dict：
            for tool_result in tool_result_list:
                now_dict_tool = {"role": "tool",
                                 'content': str(tool_result['result']),
                                 "tool_call_id": tool_result["tool_call_id"]}
                now.append(now_dict_tool)

        # 构建消息列表
        messages = system1 + memory + now
        return messages

    def llm_chat(self, client, messages, tools=None, tool_choice="auto", ):
        '''
        单词对话
        :param client:（初始化）
        :param role:对话角色（str）
        :param 工具列表（list，json反序列化）
        :param tool_choice:见openai文档

        :return：对象response
        '''

        # 与llm交互
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            stream=False,
            extra_body = {"enable_search": True}
        )
        return response

    def llm_prsm_data(self, response):
        '''

        :param response: llm返回的对象
        :return: reasoning_content:推理过程
                "content":直接回答
                "tool_calls"：tool列表
        '''
        # 解析
        reasoning_content = getattr(response.choices[0].message, "reasoning_content", None)  # 思考过程
        content = response.choices[0].message.content  # 正式回答
        tool_calls = response.choices[0].message.tool_calls

        reply_data = {
            "reasoning_content": reasoning_content,
            "content": content,
            "tool_calls": tool_calls,
            "all":response
        }
        return reply_data

    def llm_tool_register(self, tool_register):
        '''
        把工具注册表转换成openai的格式
        :param tool_register:

        :return:转换好的格式,若没有可用工具（tool是空列表），会返回None
        '''
        tools = []
        for id in tool_register:  #这里id就是name。  type(id) = str
            tool = {
                "type": "function",
                "function": {
                    "name": id,
                    "description": tool_register[id]["data"]["description"],
                    "parameters": tool_register[id]["data"]["parameters"]
                }
            }
            tools.append(tool)
        if tools == []:
            return None
        else:
            return tools