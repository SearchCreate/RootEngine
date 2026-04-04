import json
from jsonschema import validate
from ..utils.reif_func import reif_create, reif_validate
from ..utils.helpers import get_iso_timestamp
from ..schema.conversation import REIF_CONTENT_NO_TOOL_CONVERSATION_JSON
from ..constants.conversation import CONVERSATION_ROLE

REIF_CONTENT_NO_TOOL_CONVERSATION = json.loads(REIF_CONTENT_NO_TOOL_CONVERSATION_JSON)

class NoToolConversation:

    def __init__(self, reif_entry: dict = None):
        # 若未传入，初始化一个新的
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


    def add(self ,
            role: str,
            content: str = None,
            created_at: str = None,
            extra: dict = None,
            ):
        """
        向会话添加一条消息。

        :param role: 消息角色，必须为 system/user/assistant/tool 之一。
        :param content: 文本内容（对 system/user/assistant 必填，对 tool 可选）。
        :param tool_calls: 仅当 role == 'assistant' 时提供，格式为 OpenAI tool_calls 数组。

        :param extra: 可选的扩展字典，任意附加信息。
        :param created_at: 可选时间戳，若不提供则自动生成。
        :return: self，支持链式调用。
        """
        #检验角色
        if role not in ["system", "user", "assistant"]:
            raise ValueError(f"未知角色: {role}")

        # 生成时间戳
        if created_at is None:
            created_at = get_iso_timestamp()

        # 构建消息字典
        # 添加必选字段
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


    def load_entry(self, entry: dict):
        """加载完整 REIF 条目"""
        #替换引用
        self.reif_entry = entry
        #重新链接
        self.messages = entry.get("reif_content", [])
        #若 messages 不是列表 报错
        if not isinstance(self.messages, list):
           raise TypeError(f"reif_content 必须是列表，实际为 {type(self.messages).__name__}")
            # self.messages = []
            # self.reif_entry["reif_content"] = self.messages
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
            raise RuntimeError("无会话可校验")
        reif_validate(self.reif_entry)
        validate(instance=self.messages, schema = REIF_CONTENT_NO_TOOL_CONVERSATION)
        return True

