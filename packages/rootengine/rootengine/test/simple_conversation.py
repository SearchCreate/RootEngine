import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加根目录到 sys.path
_root_dir = Path(__file__).parent.parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

from rootengine.db.base_buffer_db import BaseBufferDB


class MockDB(BaseBufferDB):
    """Mock BaseBufferDB subclass for testing"""
    def __init__(self, initial_entry=None):
        self.entry_buffer = initial_entry
        self._buffer = initial_entry

    def save(self):
        pass

    def load(self):
        return self

    def get(self):
        return self.entry_buffer

    def close(self):
        pass

    def change_buffer(self, new_buffer):
        self.entry_buffer = new_buffer
        return self

    def get_metadata(self):
        return {"db_obj_name": "MockDB", "path": ":memory:", "category": "conversation", "id": "test-id", "table_name": "test_table"}


class TestSimpleConversationCreate:
    """SimpleConversation.create() 测试"""

    def test_create_no_args(self):
        """不传参数时应自动创建新会话"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db)

        assert conv.entry is not None
        assert conv.entry["reif_metadata"]["category"] == "conversation"
        assert conv.entry["reif_content"] == []
        assert conv.messages == []

    def test_create_returns_dict(self):
        """create() 应返回 entry 字典"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db)
        result = conv.create()

        assert isinstance(result, dict)
        assert result["reif_metadata"]["category"] == "conversation"
        assert result["reif_content"] == []


class TestSimpleConversationAdd:
    """SimpleConversation.add() 测试"""

    @pytest.fixture
    def conv(self):
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        return SimpleConversation(db_obj=mock_db, auto_save_db=False)

    def test_add_user_message(self, conv):
        """添加 user 消息"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("user", "hello")

        assert len(conv.messages) == 1
        assert conv.messages[0]["role"] == "user"
        assert conv.messages[0]["content"] == "hello"
        assert conv.messages[0]["created_at"] == "2024-01-01T00:00:00Z"

    def test_add_system_message(self, conv):
        """添加 system 消息"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("system", "you are helpful")

        assert conv.messages[0]["role"] == "system"
        assert conv.messages[0]["content"] == "you are helpful"

    def test_add_assistant_message(self, conv):
        """添加 assistant 消息"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("assistant", "hello!")

        assert conv.messages[0]["role"] == "assistant"
        assert conv.messages[0]["content"] == "hello!"

    def test_add_assistant_with_tool_refer(self, conv):
        """添加 assistant 消息带 tool_refer"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("assistant", tool_refer={"name": "get_weather", "arguments": {"city": "beijing"}})

        assert conv.messages[0]["role"] == "assistant"
        assert conv.messages[0]["tool_refer"] == {"name": "get_weather", "arguments": {"city": "beijing"}}
        assert conv.messages[0]["content"] is None

    def test_add_tool_message(self, conv):
        """添加 tool 消息"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("tool", tool_refer={"call_id": "call_123"}, content=None)

        assert conv.messages[0]["role"] == "tool"
        assert conv.messages[0]["tool_refer"] == {"call_id": "call_123"}
        assert conv.messages[0]["content"] is None

    def test_add_tool_message_content_not_none_raises(self, conv):
        """tool 角色 content 必须为 None"""
        with pytest.raises(ValueError) as exc_info:
            conv.add("tool", tool_refer={"call_id": "call_123"}, content="some text")

        assert "content 必须为 null" in str(exc_info.value)

    def test_add_tool_message_no_tool_refer_raises(self, conv):
        """tool 角色 tool_refer 不能为空"""
        with pytest.raises(ValueError) as exc_info:
            conv.add("tool", content=None)

        assert "tool_refer 不能为空" in str(exc_info.value)

    def test_add_auto_timestamp(self, conv):
        """未传 created_at 时应自动生成"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("user", "hello")

        assert conv.messages[0]["created_at"] == "2024-01-01T00:00:00Z"

    def test_add_with_extra(self, conv):
        """添加带 extra 的消息"""
        extra = {"key": "value"}
        conv.add("user", "hello", extra=extra)

        assert conv.messages[0]["extra"] == extra

    def test_add_invalid_role(self, conv):
        """无效角色应抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            conv.add("invalid_role", "hello")

        assert "invalid_role" in str(exc_info.value)

    def test_add_returns_self(self, conv):
        """add() 应返回 self，支持链式调用"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            result = conv.add("user", "hello")

        assert result is conv

    def test_add_chain(self, conv):
        """链式调用"""
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("system", "you are helpful").add("user", "hello").add("assistant", "hi!")

        assert len(conv.messages) == 3
        assert [m["role"] for m in conv.messages] == ["system", "user", "assistant"]


class TestSimpleConversationDelete:
    """SimpleConversation.delete() 测试"""

    @pytest.fixture
    def conv_with_messages(self):
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        with patch("rootengine.conversation.simple_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)
            conv.add("system", "sys").add("user", "user1").add("assistant", "asy")
        return conv

    def test_delete_last(self, conv_with_messages):
        """不传索引默认删除最后一条"""
        conv_with_messages.delete()

        assert len(conv_with_messages.messages) == 2
        assert conv_with_messages.messages[-1]["role"] == "user"

    def test_delete_by_index(self, conv_with_messages):
        """按索引删除"""
        conv_with_messages.delete(0)

        assert len(conv_with_messages.messages) == 2
        assert conv_with_messages.messages[0]["role"] == "user"

    def test_delete_returns_self(self, conv_with_messages):
        """delete() 应返回 self"""
        result = conv_with_messages.delete()
        assert result is conv_with_messages


class TestSimpleConversationLoad:
    """SimpleConversation.load_entry() / load_messages() 测试"""

    def test_load_entry(self):
        """加载完整 entry"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "abc123",
                "category": "conversation",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "reif_content": [
                {"role": "user", "content": "hello", "created_at": "2024-01-01T00:00:00Z"}
            ]
        }

        conv.load_entry(entry)

        assert conv.entry is entry
        assert conv.messages == entry["reif_content"]

    def test_load_messages(self):
        """加载消息列表"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)
        messages = [
            {"role": "user", "content": "hello", "created_at": "2024-01-01T00:00:00Z"}
        ]

        conv.load_messages(messages)

        assert conv.messages is messages
        assert conv.entry["reif_content"] is messages

    def test_load_entry_returns_self(self):
        """load_entry() 应返回 self"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {"id": "abc", "category": "conversation", "created_at": "2024-01-01T00:00:00Z"},
            "reif_content": []
        }
        result = conv.load_entry(entry)
        assert result is conv

    def test_load_messages_returns_self(self):
        """load_messages() 应返回 self"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)
        result = conv.load_messages([])
        assert result is conv


class TestSimpleConversationInit:
    """SimpleConversation.__init__() 测试"""

    def test_init_with_db_obj(self):
        """db_obj 应正确赋值给 self.db"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db)

        assert conv.db is mock_db

    def test_init_with_initial_entry(self):
        """有初始 entry 时应直接使用"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        initial_entry = {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "abc123",
                "category": "conversation",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "reif_content": [{"role": "user", "content": "hi", "created_at": "2024-01-01T00:00:00Z"}]
        }
        mock_db = MockDB(initial_entry)
        conv = SimpleConversation(db_obj=mock_db)

        assert conv.entry is initial_entry
        assert conv.messages == initial_entry["reif_content"]

    def test_init_invalid_db_obj_raises(self):
        """非 BaseBufferDB 子类应抛出 TypeError"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        invalid_db = "not a db object"

        with pytest.raises(TypeError) as exc_info:
            SimpleConversation(db_obj=invalid_db)

        assert "不是 BaseConversation 的子类" in str(exc_info.value)


class TestSimpleConversationSave:
    """SimpleConversation.save() 测试"""

    def test_save(self):
        """save() 应调用 db.change_buffer 和 db.save()"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db, auto_save_db=False)

        with patch.object(mock_db, "change_buffer") as mock_change, patch.object(mock_db, "save") as mock_save:
            conv.save()

        mock_change.assert_called_once_with(conv.entry)
        mock_save.assert_called_once()


class TestSimpleConversationGet:
    """SimpleConversation.get() 测试"""

    def test_get_returns_entry(self):
        """get() 应返回 self.entry"""
        from rootengine.conversation.simple_conversation import SimpleConversation
        mock_db = MockDB()
        conv = SimpleConversation(db_obj=mock_db)

        assert conv.get() is conv.entry
