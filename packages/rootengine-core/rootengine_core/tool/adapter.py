from ..schema_runtime.reif_schema import get_json
TOOL_REGISTRY_SCHEMA = get_json("tool.tool_registry")
TOOL_CALL_SCHEMA = get_json("tool.tool_call")
TOOL_RESULT_SCHEMA = get_json("tool.tool_result")
from ..utils.reif_adapter import adapt as reif_adapt

from jsonschema import validate

def tool_registry_entry_adapt(tool_registry):

    tool_registry = reif_adapt(tool_registry)

    if tool_registry["reif_metadata"]["version"] == "0.1.0":
        adapted_cont = tool_registry
        validate(instance=tool_registry["reif_content"], schema=TOOL_REGISTRY_SCHEMA)

        return adapted_cont
    else:
        raise ValueError(f"错误: 未知的 tool_registry_version: {tool_registry["reif_metadata"]["version"]}")