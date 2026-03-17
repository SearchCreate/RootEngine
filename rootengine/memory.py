from .utils import ps, oa
import json
import sys






class Memory:
    '''
    维护一个以文档为单位的记忆库
    '''

    def __init__(self, path):
        '''
        创建一个记忆库
        :param path: 文件路径
        '''
        self.path = path

    def memory_creat(self):
        # 确保文件存在
        open(self.path, mode='a', encoding='utf-8').close()

        # 确保文件是json格式
        with open(self.path, mode='r', encoding='utf-8') as f:

            con = f.read()
            # 防止新建文件为空
            if not con:
                f1 = open(self.path, mode='w', encoding='utf-8')
                json.dump([], f1, ensure_ascii=False, indent=4)
                f1.close()
                ps("已新建记忆文件")
            else:
                # 防止文件格式错误

                try:
                    json.loads(con)
                except json.JSONDecodeError:
                    raise ValueError(f"记忆文件 {self.path} 损坏，无法解析为 JSON,具体格式请见官网")

    def memory_save(self, role,content,other=None):
        '''
        将一条角色和文本对应的记忆保存起来
        :param:role:此文本的角色user/tool/assistant
        :param content:user:用户说的话，tool:tool_result_list,assistant:llm返回时的content文本
        :param other role=user不用填，
                role=tool填tool_result_list,是列表
                格式：
                    {"tool_call_id":123456,"result":"XXX"}
                role=assistant填tool_calls,是一个列表，
                    tools_calls具体格式见相关api的官网
        :return:ok
        '''
        # 读取记忆文件

        with open(self.path, mode='r', encoding='utf-8') as f:
            content_list = json.load(f)
        #更新
            #user
            if role == "user":
                content_list.append(oa('user', content))
            #tool
            elif role == "tool":
                if other is None:
                    other = []  #如果tool_result_list是None，返回空列表

                tool_result_list = other    #工具返回结果的列表
                #遍历tool_result_list得到每个tool的id和result
                for tool_result in tool_result_list:
                    a3 = {'role': 'tool',
                          'content':str(tool_result['result']),
                          "tool_call_id":tool_result['tool_call_id']
                          }
                    content_list.append(a3)
            #assistant
            elif role == "assistant":
                tool_calls = other  #调用工具的call
                #不调用工具
                if tool_calls is None:
                    content_list.append({'role': 'assistant', "content": content})
                else :
                    # 将 tool_calls 对象转换为可 JSON 序列化的字典列表
                    tool_calls_dicts = []
                    for tc in tool_calls:
                        tool_calls_dicts.append({
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        })
                    content_list.append({
                        'role': 'assistant',
                        "content": None,
                        'tool_calls': tool_calls_dicts
                    })




        #重新写入
        with open(self.path, mode='w', encoding='utf-8') as f:
            json.dump(content_list, f, ensure_ascii=False, indent=4)
        return 'ok'

    def memory_read(self):
        '''
        读取记忆文件
        若文件格式不对则直接退出程序
        :return:对应文件的list格式
        '''
        # 防止记忆文件不存在
        open(self.path, mode='a', encoding='utf-8').close()
        # 防止记忆文件格式错误
        with open(self.path, mode='r', encoding='utf-8') as f:
            try:
                content_list = json.load(f)
                return content_list
            except json.JSONDecodeError:
                raise ValueError(f"记忆文件 {self.path} 损坏，无法解析为 JSON,具体格式请见官网")
