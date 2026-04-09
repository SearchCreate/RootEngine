import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# 添加根目录到 sys.path
_root_dir = Path(__file__).parent.parent.parent
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))


class TestToolExecute:
    """Tool.execute() 测试"""

    @pytest.fixture
    def mock_agent(self):
        return MagicMock(name="agent")

    @pytest.fixture
    def mock_tool_func(self):
        def func(**kwargs):
            return "hello world"
        return func

    @pytest.fixture
    def mock_tool_registry(self, mock_tool_func):
        return {
            "abc123def456789012345678901234ab": {
                "name": "test_tool",
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {"type": "object", "properties": {"msg": {"type": "string"}}}
                }
            }
        }

    @pytest.fixture
    def tool_registry_entry(self, mock_tool_registry):
        return {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "a1b2c3d4e5f6789012345678abcdef01",
                "category": "tool_registry",
                "version": "0.1.0",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "reif_content": mock_tool_registry
        }

    @pytest.fixture
    def valid_tool_call(self):
        return {
            "id": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
            "type": "function",
            "function": {
                "registry_id": "abc123def456789012345678901234ab",
                "arguments": {"msg": "test"}
            },
            "created_at": "2024-01-01T00:00:00Z"
        }

    @pytest.fixture
    def tool_instance(self, tool_registry_entry, mock_agent, mock_tool_func):
        from rootengine_core.tool.tool import Tool
        return Tool(
            tool_registry_entry=tool_registry_entry,
            agent=mock_agent,
            tool_func_map={"abc123def456789012345678901234ab": mock_tool_func}
        )

    def test_execute_success(self, tool_instance, valid_tool_call, mock_tool_func):
        """正常执行工具调用"""
        with patch("rootengine_core.tool.tool.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            result = tool_instance.execute(valid_tool_call, vali=False)

        assert result["call_id"] == "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
        assert result["function"]["result_content"] == "hello world"
        assert result["created_at"] == "2024-01-01T00:00:00Z"

    def test_execute_unknown_tool(self, tool_instance, mock_agent):
        """未知工具应抛出 ToolExistError"""
        unknown_call = {
            "id": "b1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d5",
            "type": "function",
            "function": {
                "registry_id": "unknown_id",
                "arguments": {}
            },
            "created_at": "2024-01-01T00:00:00Z"
        }

        from rootengine_core.tool.tool import ToolExistError
        with pytest.raises(ToolExistError) as exc_info:
            tool_instance.execute(unknown_call, vali=False)

        assert "unknown_id" in str(exc_info.value)

    def test_execute_unknown_type(self, tool_instance, mock_agent):
        """未知 type 应抛出 ValueError"""
        unknown_type_call = {
            "id": "c1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d6",
            "type": "unknown_type",
            "created_at": "2024-01-01T00:00:00Z"
        }

        with pytest.raises(ValueError) as exc_info:
            tool_instance.execute(unknown_type_call, vali=False)

        assert "unknown_type" in str(exc_info.value)


class TestToolExecuteMany:
    """Tool.execute_many() 测试"""

    @pytest.fixture
    def mock_agent(self):
        return MagicMock(name="agent")

    @pytest.fixture
    def mock_tool_func(self):
        def func(**kwargs):
            return "result"
        return func

    @pytest.fixture
    def tool_registry_entry(self, mock_tool_func):
        return {
            "reif_version": "1.0",
            "reif_metadata": {
                "id": "a1b2c3d4e5f6789012345678abcdef01",
                "category": "tool_registry",
                "version": "0.1.0",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "reif_content": {
                "a1b2c3d4e5f6789012345678abcdef01": {"name": "tool1", "type": "function", "function": {"name": "tool1", "description": "Tool 1", "parameters": {}}},
                "1234567890abcdef1234567890abcdef": {"name": "tool2", "type": "function", "function": {"name": "tool2", "description": "Tool 2", "parameters": {}}},
            }
        }

    @pytest.fixture
    def tool_instance(self, tool_registry_entry, mock_agent, mock_tool_func):
        from rootengine_core.tool.tool import Tool
        return Tool(
            tool_registry_entry=tool_registry_entry,
            agent=mock_agent,
            tool_func_map={"a1b2c3d4e5f6789012345678abcdef01": mock_tool_func, "1234567890abcdef1234567890abcdef": mock_tool_func}
        )

    def test_execute_many_empty(self, tool_instance):
        """空列表应返回空列表"""
        result = tool_instance.execute_many([])
        assert result == []

    def test_execute_many_single(self, tool_instance):
        """单个调用"""
        call = {
            "id": "d1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d7",
            "type": "function",
            "function": {"registry_id": "a1b2c3d4e5f6789012345678abcdef01", "arguments": {}},
            "created_at": "2024-01-01T00:00:00Z"
        }

        with patch("rootengine_core.tool.tool.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            result = tool_instance.execute_many([call])

        assert len(result) == 1
        assert result[0]["call_id"] == "d1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d7"

    def test_execute_many_multiple(self, tool_instance):
        """多个调用"""
        ids = [
            "f1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d0",
            "f1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d1",
            "f1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d2",
        ]
        calls = [
            {
                "id": id,
                "type": "function",
                "function": {"registry_id": "a1b2c3d4e5f6789012345678abcdef01", "arguments": {}},
                "created_at": "2024-01-01T00:00:00Z"
            }
            for id in ids
        ]

        with patch("rootengine_core.tool.tool.get_iso_timestamp", return_value="2024-01-01T00:00:00Z"):
            result = tool_instance.execute_many(calls)

        assert len(result) == 3
        assert [r["call_id"] for r in result] == ids
