import pytest
from unittest.mock import patch, MagicMock
import json

# 假设模块路径
from rootengine_core.conversation.no_tool_conversation import NoToolConversation

# ========== 模拟外部依赖 ==========
@pytest.fixture(autouse=True)
def mock_deps():
    with patch('rootengine_core.utils.reif_func.reif_create') as mock_create, \
         patch('rootengine_core.utils.reif_func.reif_validate') as mock_validate, \
         patch('rootengine_core.utils.time.get_iso_timestamp') as mock_time, \
         patch('rootengine_core.utils.reif_func.validate') as mock_schema_validate:

        # 模拟 reif_create 返回一个标准 REIF 条目
        def fake_create(params):
            return {
                "reif_version": "1.0",
                "reif_metadata": {
                    "id": "test-id",
                    "category": "conversation",
                    "version": "1.0.0",
                    "created_at": "2025-03-31T12:00:00Z",
                    "updated_at": "2025-03-31T12:00:00Z",
                    "extra": {}
                },
                "reif_content": []
            }
        mock_create.side_effect = fake_create

        # 模拟时间返回一个动态值（实际测试不关心具体值）
        mock_time.return_value = "2025-03-31T12:00:00Z"

        # 模拟验证函数什么都不做
        mock_validate.return_value = None
        mock_schema_validate.return_value = None

        yield mock_create, mock_validate, mock_time, mock_schema_validate


# ========== 测试类 ==========
class TestNoToolConversation:

    def test_create_new_conversation(self):
        conv = NoToolConversation()
        assert conv.reif_entry is not None
        assert conv.messages == []
        assert conv.reif_entry["reif_content"] == []

    def test_init_with_existing_entry(self):
        entry = {
            "reif_version": "1.0",
            "reif_metadata": {"id": "123"},
            "reif_content": [{"role": "user", "content": "hi", "created_at": "now"}]
        }
        conv = NoToolConversation(entry)
        assert conv.reif_entry is entry
        assert conv.messages == entry["reif_content"]

    def test_init_with_bad_content_makes_list(self):
        entry = {"reif_content": None}
        conv = NoToolConversation(entry)
        assert conv.messages == []
        assert conv.reif_entry["reif_content"] == []

    def test_add_user_message(self, mock_deps):
        conv = NoToolConversation()
        conv.add("user", "Hello")
        assert len(conv.messages) == 1
        msg = conv.messages[0]
        assert msg["role"] == "user"
        assert msg["content"] == "Hello"
        # 只检查 created_at 字段存在，不关心具体值
        assert "created_at" in msg
        assert "extra" not in msg

    def test_add_assistant_message(self):
        conv = NoToolConversation()
        conv.add("assistant", "Hi there")
        msg = conv.messages[0]
        assert msg["role"] == "assistant"
        assert msg["content"] == "Hi there"
        assert "created_at" in msg

    def test_add_system_message(self):
        conv = NoToolConversation()
        conv.add("system", "You are a helpful assistant")
        msg = conv.messages[0]
        assert msg["role"] == "system"
        assert msg["content"] == "You are a helpful assistant"
        assert "created_at" in msg

    def test_add_message_with_extra(self):
        conv = NoToolConversation()
        conv.add("user", "test", extra={"key": "value"})
        msg = conv.messages[0]
        assert msg["extra"] == {"key": "value"}
        assert "created_at" in msg

    def test_add_message_without_extra(self):
        conv = NoToolConversation()
        conv.add("user", "test")
        assert "extra" not in conv.messages[0]
        assert "created_at" in conv.messages[0]

    def test_add_message_custom_created_at(self):
        conv = NoToolConversation()
        custom_time = "2024-01-01T00:00:00Z"
        conv.add("user", "test", created_at=custom_time)
        assert conv.messages[0]["created_at"] == custom_time

    def test_add_invalid_role_raises(self):
        conv = NoToolConversation()
        with pytest.raises(ValueError, match="未知角色"):
            conv.add("invalid", "test")

    def test_add_tool_role_not_allowed(self):
        conv = NoToolConversation()
        with pytest.raises(ValueError):
            conv.add("tool", "result")

    def test_delete_last_message(self):
        conv = NoToolConversation()
        conv.add("user", "first")
        conv.add("user", "second")
        conv.delete()
        assert len(conv.messages) == 1
        assert conv.messages[0]["content"] == "first"

    def test_delete_by_index(self):
        conv = NoToolConversation()
        conv.add("user", "first")
        conv.add("user", "second")
        conv.add("user", "third")
        conv.delete(1)
        assert [m["content"] for m in conv.messages] == ["first", "third"]

    def test_load_entry(self):
        conv = NoToolConversation()
        entry = {
            "reif_version": "1.0",
            "reif_content": [{"role": "user", "content": "hi", "created_at": "now"}]
        }
        conv.load_entry(entry)
        assert conv.reif_entry is entry
        assert conv.messages == entry["reif_content"]

    def test_load_entry_with_bad_content_raises(self):
        conv = NoToolConversation()
        entry = {"reif_content": "not a list"}
        with pytest.raises(TypeError, match="reif_content 必须是列表"):
            conv.load_entry(entry)

    def test_load_reif_metadata(self):
        conv = NoToolConversation()
        conv.create()
        new_meta = {"id": "new-id", "version": "2.0.0"}
        conv.load_reif_metadata(new_meta)
        assert conv.reif_entry["reif_metadata"] == new_meta



    def test_load_content(self):
        conv = NoToolConversation()
        conv.create()
        new_content = [{"role": "user", "content": "hello", "created_at": "now"}]
        conv.load_content(new_content)
        assert conv.messages == new_content
        assert conv.reif_entry["reif_content"] == new_content



    def test_validate_schema_passes(self, mock_deps):
        conv = NoToolConversation()
        conv.create()
        conv.add("user", "test")
        assert conv.validate_schema() is True



    def test_validate_schema_fails_on_validation_error(self, mock_deps):
        conv = NoToolConversation()
        conv.create()
        conv.add("user", "test")
        from jsonschema import ValidationError
        with patch('rootengine_core.utils.reif_func.validate', side_effect=ValidationError("bad")):
            with pytest.raises(ValidationError):
                conv.validate_schema()