    

def print_system(content):
    print(f"系统：{content}")
ps = print_system

# 返回openai的字典格式
def oa(role, content):
    return {'role': role, 'content': content}
def oat(role, content,tool_calls):
    return {'role': role, 'content': content,'tool_calls': tool_calls}