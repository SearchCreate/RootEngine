from typing import Optional,Dict,List,Any

from abc import ABC,abstractmethod


class BaseLLM(ABC):


    @abstractmethod

    def call(self,
             messages:List[dict[str,Any]],
             tool_registry:Optional[List[Dict[str, Any]]],
             tool_choice: Optional[str],
             **kwargs)\
            -> Dict[str, Any]:
        """

        :param messages: 消息列表
        :param tool_registry: 可用工具列表
        :param tool_choice: 工具选择策略
        :param kwargs:
        :return:包含 "content" 和 "tool_calls" 字段的字典，可选 "usage"

        """
        pass











