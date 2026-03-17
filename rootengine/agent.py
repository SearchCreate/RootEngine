from .utils import oa,ps
from .llm_openai import LlmOpenAI
from .memory import Memory
from .tool import Tool



class Agent:
    '''
    维护一个智能体
    '''


    def __init__(self,
                 agent_name,
                 agent_id,
                 llm_data,
                 system_prompt,
                 memory_path,
                 tool_register,
                 debug_prompt:bool=False
                 ):
        '''

        :param agent_name: 智能体名称（str）
        :param agent_id: 智能体id，id不可以重复，凭id找智能体(str)
        :param llm_data: 大模型的数据（dict）
        :param system_prompt: 系统提示词（str）
        :param memory_path:记忆文件的路径(str)
        :param: tool_register:工具注册表（list）
        :param: debug_prompt:false时不输出调试提示，ture时输出
        agent_llm格式：
        {
            "api_key":"",
            "base_url":"",
            "model":""
        }

        '''
        self.agent_name = agent_name
        self.agent_id = agent_id
        self.memory_path = memory_path
        self.llm_data = llm_data
        self.system_prompt = system_prompt
        self.tool_register = tool_register
        #创建实例
        self.llm = LlmOpenAI(self.llm_data)
        self.client = self.llm.llm_start()
        if debug_prompt:
            ps("chat completion API初始化")

        self.memory_obj = Memory(path = self.memory_path)
        self.memory_obj.memory_creat()
        if debug_prompt:
            ps("memory文件初始化")

        self.tool = Tool(self.tool_register,agent = self)
        if debug_prompt:
            ps('tool初始化')
    def agent_base_chat(self,role,input_data,tool_result_list=None,tool_choice = 'auto'):
        '''
        与大模型基本的输入，输出
        :param role:
        :param input_data:user输入的东西，role=tool时无效（str）
        :param tool_result_list:工具返回结果role = user时无效（str）
        :param tool_choice:见openai官方文档
        :return: reply_data重要数据

        '''
        # 读取记忆
        memory = self.memory_obj.memory_read()

        #与llm交互
        #构建message
        messages = self.llm.llm_message_data(
            role = role,
            system_prompt = self.system_prompt,
            memory = memory,
            input_data = input_data,
            tool_result_list=tool_result_list
        )

        #开始交互
        response =  self.llm.llm_chat(client = self.client,
                                      messages = messages,
                                      tools = self.llm.llm_tool_register(self.tool_register),
                                      tool_choice=tool_choice
                                      )

        #解析数据
        reply_data = self.llm.llm_prsm_data(response)

        #保存记忆

        self.memory_obj.memory_save(role, input_data,tool_result_list)
        self.memory_obj.memory_save("assistant",reply_data["content"],reply_data["tool_calls"])

        return reply_data

    def agent_deal(self,reply_data):
        '''
        处理主循环除了网络反面的部分
        :param reply_data: 重要数据的字典，也是上面那个函数的返回值
        :return: 若llm直接跟user说话（没有tool要返回结果），没有返回ok，若tool要返回result，返回tool_result_list
        '''
        reasoning_content = reply_data.get("reasoning_content",'')
        content = reply_data["content"]
        tool_calls = reply_data["tool_calls"]
        #user分支
        if tool_calls is None:
            #直接打印给user面板,无工具调用
            return None
        #走tool分支
        else:

            tool_result_list = self.tool.tool_call_deal(tool_calls)

            return tool_result_list

    def agent_llm_with_tool_chat(self,user_input):
        '''
        组合了llm和tool调用，实现了user给llm发出指令，llm与tool交互完成后由llm将结果返回给user
        :param user_input:用户输入
        :return:llm与tool交互完，llm给用户返回的结果
        '''
        input_data = user_input
        tool_result_list = None
        role = 'user'
        while 1:
            # tool的result给返回llm
            # 交互
            reply_data = self.agent_base_chat(
                role=role,
                input_data=input_data,
                tool_result_list=tool_result_list,
                tool_choice='auto',

            )

            # 工具调用
            tool_result_list = self.agent_deal(reply_data)
            # 处理分支（返回user/llm给tool参数，tool结果返回llm）
            if tool_result_list is not None:
                #将若有工具调用，则将调用结果作为输入返回给llm
                role = "tool"
            else:
                #返回user
                return reply_data["content"]



    def agent_get_memory_path(self,):
        '''衔接memorize工具函数'''
        return self.memory_path