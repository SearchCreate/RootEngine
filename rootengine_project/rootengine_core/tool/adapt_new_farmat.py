def adapt_new_format(obj:object) -> "适配最新版本的reif_content":
    """适配最新版本
    :param obj:填 Tool 对象
    """

    if obj.entry["reif_version"] == "1.0":
        if obj.metadata["version"] == "0.1.0":
            # 目前是最新版本，直接返回原
            adapted = obj.now_tool_call

            return adapted