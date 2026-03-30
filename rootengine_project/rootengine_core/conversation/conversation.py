import json
from jsonschema import validate
from ..utils.reif_func import reif_create, reif_validate
from ..utils.helpers import get_iso_timestamp
from ..schema.conversation import REIF_CONTENT_CONVERSATION_JSON
from ..constants.conversation import CONVERSATION_ROLE

REIF_CONTENT_CONVERSATION = json.loads(REIF_CONTENT_CONVERSATION_JSON)

class Conversation:
    def __init__(self, reif_entry: dict = None):
        #若未传入，初始化一个新的
        if reif_entry is None:
            self.create()

        elif reif_entry is not None:

            self.reif_entry = reif_entry

        self.messages = self.reif_entry.get("reif_content")
        # 确保 messages 是列表,原本新创建的 reif_entry["reif_content"] 是 None
        if not isinstance(self.messages, list):
            self.messages = []
            self.reif_entry["reif_content"] = self.messages

    def create(self):
        """创建新会话"""
        self.reif_entry = reif_create({"category": "conversation"})
        # 确保 reif_content 存在且为空列表
        self.reif_entry["reif_content"] = []
        # 链接
        self.messages = self.reif_entry["reif_content"]

        return self

    def add(self, role: str,
            content: str = None,
            tool_refer: dict = None,
            extra: dict = None,
            created_at: str = None):
        """
        向会话列表追加信息


        :param role:
        :param content:
        :param tool_refer: 工具指代
        :param extra:
        :param created_at: 生成时间
        :return:
        """
        if role not in CONVERSATION_ROLE:
            raise ValueError(f"未知角色: {role}")
        if created_at is None:
            created_at = get_iso_timestamp()


        if role == "system":
            #提供 role , content , created_at
            item = {"role": role, "content" : content , "created_at": created_at}

        if role == "assistant":
            # 提供 role , created_at ;content , tool_refer 二选一
            item = {"role": role , "created_at": created_at}
            if content:
                item["content"] = content
            if tool_refer:
                item["tool_refer"] = tool_refer



        if role == "user":
            # 提供 role , content , created_at
            item = {"role": role , "content":content , "created_at": created_at}

        if role == "tool":
            # 提供 role , content , created_at , tool_refer
            item = {"role": role , "created_at": created_at}
            if tool_refer:
                item["tool_refer"] = tool_refer



        if extra:   # 非空字典才添加
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


    def load_entry(self, entry: dict):
        """加载完整 REIF 条目"""
        self.reif_entry = entry
        self.messages = entry.get("reif_content", [])
        if not isinstance(self.messages, list):
            self.messages = []
            self.reif_entry["reif_content"] = self.messages
        return self


    def load_reif_metadata(self, metadata: dict):
        """加载元数据"""
        if self.reif_entry is None:
            raise RuntimeError("未初始化会话")
        self.reif_entry["reif_metadata"] = metadata
        return self


    def load_content(self, content: list):
        """加载消息列表"""
        if self.reif_entry is None:
            raise RuntimeError("未初始化会话")
        self.reif_entry["reif_content"] = content
        self.messages = content
        return self



    def validate_schema(self) -> bool:
        if self.reif_entry is None:
            raise RuntimeError("无会话可验证")
        reif_validate(self.reif_entry)
        validate(instance=self.messages, schema=REIF_CONTENT_CONVERSATION)
        return True