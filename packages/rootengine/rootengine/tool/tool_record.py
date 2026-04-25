from rootengine_core.utils import REIFFunction
from ..db import RootEngineBufferSQL, BaseBufferDB




class ToolRecord:
    def __init__(self,db_obj):
        self.reif_function = REIFFunction()

        self.db_obj = db_obj

        _init_entry = self.read()
        # 若没有，自动新建
        if not _init_entry:
            _init_entry = self.create()
            # 把 "reif_content" 初始化 成空字典
            _init_entry["reif_content"] = {}

        self.entry = _init_entry
        self.tool_record = self.entry["reif_content"]

    def create(self):
        """创建一个 tool_record 条目"""
        return self.reif_function.create({"category": "tool_record"})


    def update(self, call_id:str, tool_call:dict, tool_result:dict):
        """存入新的工具记录"""
        self.tool_record[call_id] = {
            "tool_call": tool_call,
            "tool_result": tool_result
        }
        return self

    def delete(self, call_id:str):
        self.tool_record.pop(call_id)
        return self

    def get(self, call_id:str):
        """按工具的 call_id 返回 调用记录"""
        return self.tool_record.get(call_id)

    def save(self):
        """想数据库覆写内存数据"""
        self.db_obj.save()
        return self

    def read(self):
        """从数据库中读取"""
        return self.db_obj.get()

    def load(self):
        """从数据库中读取把并加载"""
        self.entry = self.db_obj.get()
        self.tool_record = self.entry["reif_content"]
        return self










