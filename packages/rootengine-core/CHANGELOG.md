## [0.5.0] 2026-04-09
- 上传了内部多次迭代后的代码

## [0.5.5] 2026-04-14
- 之前出现了git 版本混乱 ，恢复后 ，重新开始版本管理。
- 小幅度更改了部分 api（向后兼容），主要是reif_func.py 里的

## [0.5.6] 2026-04-15
- packages/rootengine-core/rootengine_core/utils/reif_func.py ,增加了 REIFFunc 类，进一步封装了 关于reif的函数 ，并做了向后兼容

## [0.5.7] 2026-4-19
- 将 base_conversation.json 重命名为 no_tool_conversation.json
- BaseConversation 改为抽象基类，仅定义接口
- 新增 NoToolConversation(BaseConversation) 实现具体逻辑
- 更新 reif_schema.py 中的 JSON_DICT key 和 title
- 更新测试文件，从 BaseConversation 迁移至 NoToolConversation
- 更新 generate_json_dict.py 注释示例
- 修复 create() 返回类型（返回 entry dict 而非 self）
- 微调 CHANGELOG 格式

## [0.5.8] 2026-4-25

- 把 conversation 的 add 方法 改成了 append ，更符合语义。删掉了add，关于这个add方法，不向后兼容