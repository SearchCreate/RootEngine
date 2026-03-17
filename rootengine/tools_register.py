import os
import sys
import pkgutil
import importlib

class ToolRegistry:
    def __init__(self,tool_path):
        '''

        :param tool_path:.py文件的路径，

        文件中每个工具需包含get_tool_info函数
        例
        from .tool import memorize

        def get_tool_info():
            return {
                "name": "memorize",
                "description": "打印所有对话历史",
                "parameters": {
                    "type": "object",
                    "properties": {}
                },
                "function": memorize
    }
    return:完整的工具注册表，用reg_get_registry调取
        '''
        self.tool_path = tool_path
        self._my_registry = {}



        #备份原目录
        self.before_sys_path = sys.path
        #访问tools的目录
        self.tool_path = os.path.abspath(tool_path)

    def reg_discover_tool(self):
        '''

        :return:完整的工具注册表
        '''
        # 将python搜索目录改成tools目录，让程序从tools目录里扫描
        if self.tool_path not in sys.path:
            sys.path.insert(0, self.tool_path)


        # 扫描tool_path下所有包
        for finder, name, ispkg in pkgutil.iter_modules([self.tool_path]):

            if not ispkg:
                continue

            #导入包
            model = importlib.import_module(name)

            #检测工具包是否有get_tool_infor函数
            if not hasattr(model,"get_tool_info"):
                print({f"跳过工具{name}：缺少get_tool_infor函数"})
                continue

            #获取工具信息
            info = model.get_tool_info()

            #存入注册表
            self._my_registry[name] = {
                "function": info['function'],
                "data": {
                    "description": info.get('description', ''),
                    "parameters": info.get('parameters', {})
                }
            }

        #修改回原来的根目录
        sys.path = self.before_sys_path

        return self._my_registry

    def reg_get_registry(self):
        return self._my_registry














