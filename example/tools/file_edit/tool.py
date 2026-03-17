import os
def get_tool_info():
    return {
            "function": file_edit,
            "description": "这个工具是一个文本编辑器，有 读取，写入，追加 模式",
                   "parameters": {
                      "type": "object",
                      "properties": {
                          "path": {
                              "type": "string",
                              "description": "要操作的文件路径"
                          },
                          "mode": {
                              "type": "string",
                              "enum": ["read", "write", "append"],
                              "description": "操作模式：读取（read）、写入（write），若无文件，则新建一个、追加（append），若无文件，则新建"
                          },
                          "content": {
                              "type": "string",
                              "description": "写入或追加的内容（读取模式时无需提供）",
                              "default": ""
                           },
                          "newline_num": {
                             "type": "integer",
                             "description": "追加模式下文本前加的换行符数量",
                             "default": 1
                                    },
                      },
                          "required": ["path", "mode"] #这里填必填参数



        }}
def file_edit(agent, path ,mode, content='',newline_num:int=1):
    '''
    编辑文件，主要面对txt
    :param agent: 主程序的Agent实例，用于调用访问主程序Agent实例的一些方法和属性，不管你能不能用上，都得填这个形参，且形参名固定为agent

    :param path: 文件路径
    :param mode: 模式，有read（读取），write（写入），append（追加）模式
    :param content:要操作的内容，read模式下无用
    :param newline_num:在追加模式下，内容前换行符的数量，默认值为1
    :return:read模式下读取的内容，或操作结果
    '''
    if mode == "read":
        if not os.path.exists(path):
            return f"文件不存在：{path}"
        with open(path, "r", encoding='utf-8') as f:
            return f.read()
    elif mode in ["write", "append"]:
        # 确保目录存在
        dir_name = os.path.dirname(path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(path, "a" if mode == "append" else "w", encoding='utf-8') as f:
            f.write(f"{'\n'*newline_num}{content}")
            return "操作成功"
    else:
        return f"未知模式：{mode}"