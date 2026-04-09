import pytest
import os
from pathlib import Path
from ..conversation.simple_conversation import SimpleConversation


class TestSimpleConversationInit:
    def test_new_conversation_creates_entry(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        assert conv.entry is not None
        assert conv.entry["reif_metadata"]["category"] == "conversation"
        assert conv.entry["reif_content"] == []

    def test_init_with_entry(self, tmp_path):
        db_path = tmp_path / "test.db"
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "test-id-123",
                "category": "conversation",
                "version": "0.1.0",
                "description": None,
                "name": "test-name",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": None,
                "extra": {},
            },
            "reif_content": [{"role": "system", "content": "hello", "created_at": "2026-01-01T00:00:00Z"}],
        }
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=entry,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        assert conv.entry["reif_metadata"]["id"] == "test-id-123"
        assert len(conv.messages) == 1

    def test_entry_buffer_synced_to_db(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        assert conv.db.entry_buffer is conv.entry


class TestSimpleConversationAdd:
    def test_add_user_message(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="你好")
        assert len(conv.messages) == 1
        assert conv.messages[0]["role"] == "user"
        assert conv.messages[0]["content"] == "你好"
        assert "created_at" in conv.messages[0]

    def test_add_system_message(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="system", content="你是一个助手")
        assert conv.messages[0]["role"] == "system"
        assert conv.messages[0]["content"] == "你是一个助手"

    def test_add_assistant_message(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="assistant", content="你好，我是助手")
        assert conv.messages[0]["role"] == "assistant"
        assert conv.messages[0]["content"] == "你好，我是助手"

    def test_add_assistant_with_tool_call(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        tool_refer = [
            {"type": "call", "tool_record_id": "tool-1", "tool_record_path": "tools/weather"}
        ]
        conv.add(role="assistant", tool_refer=tool_refer)
        assert conv.messages[0]["role"] == "assistant"
        assert conv.messages[0]["content"] is None
        assert conv.messages[0]["tool_refer"] == tool_refer

    def test_add_tool_message(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        tool_refer = [
            {"type": "result", "tool_record_id": "tool-1", "tool_record_path": "tools/weather"}
        ]
        conv.add(role="tool", tool_refer=tool_refer)
        assert conv.messages[0]["role"] == "tool"
        assert conv.messages[0]["content"] is None
        assert conv.messages[0]["tool_refer"] == tool_refer

    def test_add_invalid_role_raises(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        with pytest.raises(ValueError, match="未知角色"):
            conv.add(role="invalid_role", content="hello")

    def test_add_tool_without_tool_refer_raises(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        with pytest.raises(ValueError, match="tool_refer 不能为空"):
            conv.add(role="tool", content="some result")

    def test_add_tool_with_non_null_content_raises(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        tool_refer = [
            {"type": "result", "tool_record_id": "tool-1", "tool_record_path": "tools/weather"}
        ]
        with pytest.raises(ValueError, match="content 必须为 null"):
            conv.add(role="tool", content="not null", tool_refer=tool_refer)

    def test_add_with_extra(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello", extra={"key": "value"})
        assert conv.messages[0]["extra"] == {"key": "value"}

    def test_add_with_created_at(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello", created_at="2026-01-01T00:00:00Z")
        assert conv.messages[0]["created_at"] == "2026-01-01T00:00:00Z"

    def test_add_chainable(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        result = (
            conv.add(role="system", content="you are helpful")
            .add(role="user", content="hello")
            .add(role="assistant", content="hi")
        )
        assert result is conv
        assert len(conv.messages) == 3


class TestSimpleConversationDelete:
    def test_delete_last_message(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello")
        conv.add(role="assistant", content="hi")
        assert len(conv.messages) == 2
        conv.delete()
        assert len(conv.messages) == 1
        assert conv.messages[0]["role"] == "user"

    def test_delete_by_index(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="system", content="sys")
        conv.add(role="user", content="user")
        conv.add(role="assistant", content="asst")
        conv.delete(0)
        assert len(conv.messages) == 2
        assert conv.messages[0]["role"] == "user"


class TestSimpleConversationGet:
    def test_get_returns_entry(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello")
        entry = conv.get()
        assert entry is conv.entry
        assert entry["reif_content"][0]["content"] == "hello"


class TestSimpleConversationLoadEntry:
    def test_load_entry_replaces_entry(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="original")
        new_entry = {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "new-id",
                "category": "conversation",
                "version": "0.1.0",
                "description": None,
                "name": "new-name",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": None,
                "extra": {},
            },
            "reif_content": [{"role": "system", "content": "loaded", "created_at": "2026-01-01T00:00:00Z"}],
        }
        conv.load_entry(new_entry)
        assert conv.entry["reif_metadata"]["id"] == "new-id"
        assert len(conv.messages) == 1
        assert conv.messages[0]["content"] == "loaded"


class TestSimpleConversationLoadMessages:
    def test_load_messages_replaces_messages(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="original")
        new_messages = [
            {"role": "system", "content": "sys1", "created_at": "2026-01-01T00:00:00Z"},
            {"role": "user", "content": "user1", "created_at": "2026-01-01T00:00:01Z"},
        ]
        conv.load_messages(new_messages)
        assert len(conv.messages) == 2
        assert conv.messages[0]["content"] == "sys1"


class TestSimpleConversationValidateSchema:
    def test_validate_schema_valid(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello")
        assert conv.validate_schema() is True

    def test_validate_schema_no_entry(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.entry = None
        with pytest.raises(RuntimeError, match="无会话可校验"):
            conv.validate_schema()


class TestSimpleConversationAutoSave:
    def test_auto_save_db_saves_after_add(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=True,
        )
        conv.add(role="user", content="hello")
        # 如果 save 成功（没抛异常），说明 db.entry_buffer 被正确同步
        assert os.path.exists(db_path)

    def test_auto_save_false_does_not_save(self, tmp_path):
        db_path = tmp_path / "test.db"
        conv = SimpleConversation(
            sql_db_path=str(db_path),
            simple_conversation_entry=None,
            sql_table_name="test_conv",
            auto_save_db=False,
        )
        conv.add(role="user", content="hello")
        # auto_save=False 时不会调用 db.save()，但如果 entry_buffer 有问题则 add 会抛异常
        # 这里主要验证 add 不抛异常即可
        assert len(conv.messages) == 1
