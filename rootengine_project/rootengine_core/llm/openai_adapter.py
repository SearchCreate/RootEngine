from typing import Any, Dict, List, Optional







"""
正向的适配：框架 -> openai
逆向向的适配：openai -> 框架

"""

def call_adapt_to_openai(self,
         messages:List[dict[str,Any]],
         tool_registry:Optional[List[Dict[str, Any]]],
         tool_choice: Optional[str],
         **kwargs)\
        -> Dict[str, Any]:
    #转换messages

    #初始化
    reif_message = messages.copy()
    reif_tool_registry = tool_registry.copy()
    reif_tool_choice = tool_choice.copy()




    openai_messages = []

    #处理message
    for reif_message in reif_messages:

        role = reif_message["role"]

        reif_message.pop("created_at")

        # if role == "system":
        #     message = {
        #         "relo":role,
        #         "content":reif_message["content"]
        #         }
        #
        # elif role == "user":
        #     message = {
        #         "relo":role,
        #         "content":reif_message["content"]
        #         }
        #
        # elif role == "assistant":
        #     message = {
        #         "relo":role,
        #         "content":reif_message["content"],
        #         "tool_calls":reif_message["tool_calls"]
        #         }
        # elif role == "tool":
        #     message = {
        #         "relo":role,
        #         "content":reif_message["content"]
        #     }

        openai_messages.append(reif_message)

    #处理tool_registry

    openai_tools = []
    for registry_id in reif_tool_registry:
        tool_data = reif_tool_registry[registry_id]


        tool = {
            
        }























