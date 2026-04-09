from rootengine_core import BaseConversation
from rootengine_core.utils import get_iso_timestamp,validate_reif
from ..utils import RootEngineBufferSQL
from ..constants.conversation import CONVERSATION_ROLE
from jsonschema import validate
from ..schema.runtime.frame_schema import get_json
SCHEMA = get_json("conversation.simple_conversation")




class SimpleConversation(BaseConversation):
    def __init__(self,
                 sql_db_path:str,
                 simple_conversation_entry: dict = None,
                 sql_table_name:str=None,
                 auto_save_db:bool = True
                 ):
        """

        :param sql_db_path:硬盘的 sql 数据库 文件路径
        :param simple_conversation_entry: 初始的 simple_conversation 条目 ，若不传则自动生成新的
        :param sql_table_name: sql 文件中的表名
        :param auto_save_db: 每次修改后自动保存
        """
        self.auto_save_db = auto_save_db

        # 如果未传自动创建新的a
        self.entry = simple_conversation_entry
        if self.entry is None:
            super().create()

        self.metadata = self.entry["reif_metadata"]

        self.messages = self.entry["reif_content"]


        # 建立 sql数据库
        self.db = RootEngineBufferSQL(
            path=sql_db_path,
            category="conversation",
            id=self.metadata["id"],
            table_name=sql_table_name,
            init_create_table=True
        )
        # 将 entry 同步到 db 的 entry_buffer，避免 save() 时 entry_buffer 为 None
        self.db.entry_buffer = self.entry

    def add(
            self,
            role: str,
            content: str = None,
            tool_refer:dict = None,
            created_at: str = None,
            extra: dict = None,
        ) -> SimpleConversation:
        """
        向会话添加一条消息。

        :param role: 消息角色，必须为 system/user/assistant/tool 之一。
        :param content: 文本内容（对 system/user/assistant 必填，对 tool 可选）。
        :param tool_refer: 工具操作指代

        :param extra: 可选的扩展字典，任意附加信息。
        :param created_at: 可选时间戳，若不提供则自动生成。
        :return: self，支持链式调用。
        """
        # 检验角色
        if role not in CONVERSATION_ROLE:
            raise ValueError(f"未知角色: {role}")

        # 生成时间戳
        if created_at is None:
            created_at = get_iso_timestamp()

        # 构造消息字典，必填字段
        item = {
            "role": role,

            "created_at": created_at
        }
        #选填字段

        if role in ["system", "user"]:
            item["content"] = content


        elif role == "assistant":

            # 若有工具调用则 content 为 None ，若没有 则正常
            if tool_refer:
                item["tool_refer"] = tool_refer
                item["content"] = None
            else :
                item["content"] = content

        elif role == "tool":

            if not tool_refer:
                raise  ValueError(f"错误：tool 角色的 tool_refer 不能为空")
            item["tool_refer"] = tool_refer

            # 校验 content 必须为 None ，之后写入
            if content is None:
                item["content"] = None
            else:
                raise ValueError("tool 角色的 content 必须为 null")


        if extra:
            item["extra"] = extra



        self.messages.append(item)
        if self.auto_save_db:
            self.db.save()
        return self

    def delete(self, index: int = None):
        super().delete(index)
        if self.auto_save_db:
            self.db.save()
        return self
    def load_entry(self,entry: dict):
        super().load_entry(entry)
        self.db.entry_buffer = self.entry
        if self.auto_save_db:
            self.db.save()
        return self
    def load_messages(self,messages: list):
        super().load_messages(messages)
        self.db.entry_buffer = self.entry
        if self.auto_save_db:
            self.db.save()
        return self


    def validate_schema(self):
        if self.entry is None:
            raise RuntimeError("无会话可校验")
        validate_reif(self.entry)
        validate(instance=self.messages, schema = SCHEMA)
        return True






    def get(self) -> dict:
        return self.entry




















