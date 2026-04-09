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

        :param messages: 消息列表 参考 ../schema/source/llm/llm_message.json
        :param tool_registry: 工具注册表 参考 ../schema/source/tool/tool_registry.json
        :param tool_choice: 工具选择策略 参考 ../schema/source/llm/tool_choice.json
        :param kwargs: 拓展任意字段
        :return: 参考 ../schema/source/llm/llm_output.json

        """
        pass











