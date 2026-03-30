# from ..tool.tool import Tool
# class Agent:
#     pass
#
# def tool_test(agent,active ):
#     if active == "test":
#         return True
#     else:
#         return False
#
# tool_registry_cont ={
#   "a1b2c3d4e5f67890a1b2c3d4e5f67890": {
#     "name": "test_tool",
#     "function": tool_test,
#     "parameters": {
#       "type": "object",
#       "properties": {
#         "active": {
#           "type": "string",
#           "description": "需输入test"
#         }
#       },
#       "required": ["active"]
#     },
#     "extra": {
#       "author": "rootengine",
#       "version": "1.0.0"
#     }
#   },
#   "f9e8d7c6b5a40987f9e8d7c6b5a40987": {
#     "name": "search_web",
#     "function": "<function object>",
#     "parameters": {
#       "type": "object",
#       "properties": {
#         "query": {
#           "type": "string",
#           "description": "搜索关键词"
#         },
#         "max_results": {
#           "type": "integer",
#           "description": "最大返回条数"
#         }
#       },
#       "required": ["query"]
#     },
#     "extra": {}
#   }
# }
#
# tool = Tool(tool_registry_cont,agent=Agent)
#
# tool_call = {
#     "call_id": "aaa",
#     "registry_id": "a1b2c3d4e5f67890a1b2c3d4e5f67890",
#     "arguments": {
#         "active":"test"
#     },
#     "created_at": "2026-03-28T08:12:34.123456Z"
# }
#
# def test_tool():
#     result = tool.execute(tool_call)
#     assert result["content"] == True
