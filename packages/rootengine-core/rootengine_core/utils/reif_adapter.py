from .reif_func import reif_validate
def adapt(entry):

    if entry["reif_version"] == "1.0":
        adapted_cont = entry
        reif_validate(adapted_cont)
        return adapted_cont
    else:
        raise ValueError(f"错误: 未知的 reif_version: {entry['reif_version']}")