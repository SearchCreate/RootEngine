import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加根目录到 sys.path
_root_dir = Path(__file__).parent.parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))


class TestBaseConversationCreate:
    """BaseConversation.create() 测试"""

    def test_create_no_args(self):
        """不传参数时应自动创建新会话"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        conv = BaseConversation()

        assert conv.entry is not None
        assert conv.entry["reif_metadata"]["category"] == "conversation"
        assert conv.entry["reif_content"] == []
        assert conv.messages == []

    def test_create_returns_self(self):
        """create() 应返回 self"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        conv = BaseConversation()
        result = conv.create()

        assert result is conv

    def test_create_replaces_existing(self):
        """已存在的会话调用 create() 应替换为新的空会话"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        conv = BaseConversation()
        conv.add("user", "hello")
        assert len(conv.messages) == 1

        conv.create()
        assert len(conv.messages) == 0


class TestBaseConversationAdd:
    """BaseConversation.add() 测试"""

    @pytest.fixture
    def conv(self):
        from rootengine_core.conversation.base_conversation import BaseConversation
        return BaseConversation()

    def test_add_user_message(self, conv):
        """添加 user 消息"""
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("user", "hello")

        assert len(conv.messages) == 1
        assert conv.messages[0]["role"] == "user"
        assert conv.messages[0]["content"] == "hello"
        assert conv.messages[0]["created_at"] == "2024-01-01T00:00:00Z"

    def test_add_system_message(self, conv):
        """添加 system 消息"""
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("system", "you are helpful")

        assert conv.messages[0]["role"] == "system"
        assert conv.messages[0]["content"] == "you are helpful"

    def test_add_assistant_message(self, conv):
        """添加 assistant 消息"""
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("assistant", "hello!")

        assert conv.messages[0]["role"] == "assistant"

    def test_add_auto_timestamp(self, conv):
        """未传 created_at 时应自动生成"""
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
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
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            result = conv.add("user", "hello")

        assert result is conv

    def test_add_chain(self, conv):
        """链式调用"""
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv.add("system", "you are helpful").add("user", "hello").add("assistant", "hi!")

        assert len(conv.messages) == 3
        assert [m["role"] for m in conv.messages] == ["system", "user", "assistant"]


class TestBaseConversationDelete:
    """BaseConversation.delete() 测试"""

    @pytest.fixture
    def conv_with_messages(self):
        from rootengine_core.conversation.base_conversation import BaseConversation
        with patch("rootengine_core.conversation.base_conversation.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            conv = BaseConversation()
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


class TestBaseConversationLoad:
    """BaseConversation.load_entry() / load_messages() 测试"""

    def test_load_entry(self):
        """加载完整 entry"""
        from rootengine_core.conversation.base_conversation import BaseConversation
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

        conv = BaseConversation()
        conv.load_entry(entry)

        assert conv.entry is entry
        assert conv.messages == entry["reif_content"]

    def test_load_messages(self):
        """加载消息列表"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        messages = [
            {"role": "user", "content": "hello", "created_at": "2024-01-01T00:00:00Z"}
        ]

        conv = BaseConversation()
        conv.load_messages(messages)

        assert conv.messages is messages
        assert conv.entry["reif_content"] is messages

    def test_load_entry_returns_self(self):
        """load_entry() 应返回 self"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {"id": "abc", "category": "conversation", "created_at": "2024-01-01T00:00:00Z"},
            "reif_content": []
        }
        conv = BaseConversation()
        result = conv.load_entry(entry)
        assert result is conv

    def test_load_messages_returns_self(self):
        """load_messages() 应返回 self"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        conv = BaseConversation()
        result = conv.load_messages([])
        assert result is conv


class TestBaseConversationInit:
    """BaseConversation.__init__() 测试"""

    def test_init_with_entry(self):
        """传入 conversation_entry 时应直接使用"""
        from rootengine_core.conversation.base_conversation import BaseConversation
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "abc123",
                "category": "conversation",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "reif_content": [{"role": "user", "content": "hi", "created_at": "2024-01-01T00:00:00Z"}]
        }

        conv = BaseConversation(conversation_entry=entry)

        assert conv.entry is entry
        assert conv.messages == entry["reif_content"]
