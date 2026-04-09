"""
LLM Provider 适配器：框架格式 ↔ 各 Provider 格式

用法：
    adapter = OpenAIAdapter(model="gpt-4", api_key="...")
    openai_params = adapter.to_provider(messages, tool_registry, tool_choice)
    # 调用 OpenAI API...
    llm_output = adapter.from_provider(openai_response)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


# ─────────────────────────────────────────────────────────────────────────────
# 基类
# ─────────────────────────────────────────────────────────────────────────────

class BaseLLMAdapter(ABC):
    """LLM 适配器基类，所有 Provider 适配器需继承此类"""

    @abstractmethod
    def to_provider(
        self,
        messages: List[Dict[str, Any]],
        tool_registry: Optional[Dict[str, Any]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        框架格式 → Provider 格式

        :param messages: 框架消息列表 (llm_message[])
        :param tool_registry: 框架工具注册表
        :param tool_choice: 工具选择策略
        :return: Provider API 调用参数
        """
        pass

    @abstractmethod
    def from_provider(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provider 响应格式 → 框架格式 (llm_output)

        :param response: Provider API 返回的原始响应
        :return: 框架 llm_output 格式
        """
        pass

    @abstractmethod
    def message_to_frame(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        单条 Provider 消息 → 框架格式 (llm_message)

        用于把 Provider 返回的消息转成框架格式后再存入 messages 列表

        :param message: Provider 格式的单条消息
        :return: 框架 llm_message 格式
        """
        pass


# ─────────────────────────────────────────────────────────────────────────────
# OpenAI 适配器
# ─────────────────────────────────────────────────────────────────────────────

class OpenAIAdapter(BaseLLMAdapter):
    """OpenAI 兼容 API 适配器"""

    def __init__(
        self,
        model: str = "gpt-4",
        **config
    ):
        """
        :param model: 模型名称
        :param config: 其他 OpenAI API 配置（temperature, timeout 等）
        """
        self.model = model
        self.config = config

    def to_provider(
        self,
        messages: List[Dict[str, Any]],
        tool_registry: Optional[Dict[str, Any]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        result = {
            "model": self.model,
            "messages": self._convert_messages(messages),
        }

        if tool_registry:
            result["tools"] = self._convert_tool_registry(tool_registry)

        if tool_choice is not None:
            result["tool_choice"] = self._convert_tool_choice(tool_choice)

        result.update(self.config)
        result.update(kwargs)
        return result

    def from_provider(self, response: Dict[str, Any]) -> Dict[str, Any]:
        content = response.get("content")
        tool_calls = response.get("tool_calls")

        if content is None and not tool_calls:
            llm_content = None
        else:
            llm_content = content

        llm_tool_calls = None
        if tool_calls:
            llm_tool_calls = self._convert_tool_calls_from_openai(tool_calls)

        return {
            "content": llm_content,
            "tool_calls": llm_tool_calls,
            "usage": self._normalize_usage(response.get("usage")),
            "created_at": response.get("created") or response.get("created_at"),
        }

    def message_to_frame(self, message: Dict[str, Any]) -> Dict[str, Any]:
        role = message["role"]
        frame_msg = {
            "role": role,
            "created_at": message.get("created_at") or message.get("created"),
        }

        if role == "tool":
            frame_msg["tool_call_id"] = message["tool_call_id"]
            frame_msg["content"] = {
                "call_id": message["tool_call_id"],
                "type": "function",
                "function": {
                    "result_content": message["content"],
                    "status": "success",
                },
                "created_at": frame_msg["created_at"],
            }
        else:
            frame_msg["content"] = message.get("content")

            if role == "assistant" and message.get("tool_calls"):
                frame_msg["tool_calls"] = self._convert_tool_calls_from_openai(message["tool_calls"])

        return frame_msg

    # ─────────────────────────────────────────────────────────────────────────
    # 内部转换方法
    # ─────────────────────────────────────────────────────────────────────────

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """框架消息列表 → OpenAI 消息列表"""
        openai_messages = []
        for msg in messages:
            role = msg["role"]
            openai_msg = {"role": role}

            content = msg.get("content")
            if role == "tool":
                if isinstance(content, dict):
                    openai_msg["content"] = content.get("result_content", "")
                else:
                    openai_msg["content"] = content or ""
            else:
                openai_msg["content"] = content

            if role == "assistant" and msg.get("tool_calls"):
                openai_msg["tool_calls"] = self._convert_tool_calls_to_openai(msg["tool_calls"])

            openai_messages.append(openai_msg)
        return openai_messages

    def _convert_tool_calls_to_openai(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """框架 tool_calls → OpenAI tool_calls"""
        return [
            {
                "id": call["id"],
                "type": call["type"],
                "function": {
                    "name": call["function"]["registry_id"],
                    "arguments": call["function"]["arguments"],
                },
            }
            for call in tool_calls
        ]

    def _convert_tool_calls_from_openai(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """OpenAI tool_calls → 框架 tool_calls"""
        from ..utils.time import get_iso_timestamp
        created_at = get_iso_timestamp()
        return [
            {
                "id": call["id"],
                "type": call["type"],
                "function": {
                    "registry_id": call["function"]["name"],
                    "arguments": call["function"]["arguments"],
                },
                "created_at": created_at,
            }
            for call in tool_calls
        ]

    def _convert_tool_registry(self, tool_registry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """框架工具注册表 → OpenAI tools"""
        openai_tools = []
        for registry_id, tool_info in tool_registry.items():
            func_info = tool_info.get("function", {})
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": registry_id,
                    "description": func_info.get("description", ""),
                    "parameters": func_info.get("parameters", {"type": "object", "properties": {}}),
                },
            })
        return openai_tools

    def _convert_tool_choice(self, tool_choice: Union[str, Dict]) -> Union[str, Dict]:
        """工具选择策略转换"""
        if isinstance(tool_choice, str):
            return tool_choice
        return tool_choice

    def _normalize_usage(self, usage: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """标准化 usage"""
        if usage is None:
            return None
        return {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
