
from ..constants.conversation import CONVERSATION_ROLE
from pathlib import Path
from ..utils.reif_func import reif_create,reif_validate
from ..utils.time import get_iso_timestamp


from jsonschema import validate


from ..schema_runtime.reif_schema import get_json
SCHEMA = get_json("conversation.no_tool_conversation")

class NoToolConversation:
    def __init__(self, conversation_entry: dict = None):
        # 如果未传自动创建新的
        if conversation_entry is None:
             self.create()
        else:
            self.entry = conversation_entry

        self.messages = self.entry["reif_content"]


    def create(self)   -> NoToolConversation:
        """创建新会话"""
        self.entry = reif_create({"category": "conversation"})
        # 确保 reif_content 存在且为空列表
        self.entry["reif_content"] = []
        # 链接
        self.messages = self.entry["reif_content"]

        return self

    def add(
            self ,
            role: str,
            content: str = None,
            created_at: str = None,
            extra: dict = None,
            )   -> NoToolConversation :

        """
        向会话添加一条消息。

        :param role: 消息角色，必须为 system/user/assistant/tool 之一。
        :param content: 文本内容（对 system/user/assistant 必填，对 tool 可选）。

        :param extra: 可选的扩展字典，任意附加信息。
        :param created_at: 可选时间戳，若不提供则自动生成。
        :return: self，支持链式调用。
        """
        #检验角色
        if role not in CONVERSATION_ROLE:
            raise ValueError(f"未知角色: {role}")

        # 生成时间戳
        if created_at is None:
            created_at = get_iso_timestamp()


        # 构造消息字典
        item = {
            "role": role,
            "content": content,
            "created_at": created_at
        }

        if extra:
            item["extra"] = extra

        self.messages.append(item)
        return self

    def delete(self, index: int = None):
        """

        :param index: 索引，若不填默认删除最后一个
        :return:
        """

        if index is None:
            self.messages.pop()
        else:
            self.messages.pop(index)
        return self



    def load_entry(self,entry: dict) -> NoToolConversation :
        """加载整个 conversation 条目"""
        self.entry = entry
        self.messages = self.entry["reif_content"]
        return self
    def load_messages(self,messages: list) -> NoToolConversation :
        self.messages = messages
        self.entry["reif_content"] = self.messages
        return self

    def validate_schema(self) -> bool:
        if self.reif_entry is None:
            raise RuntimeError("无会话可校验")
        reif_validate(self.entry)
        validate(instance=self.messages, schema = SCHEMA)
        return True

