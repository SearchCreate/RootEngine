# 注意事项
- self.entry["reif_content"] 与 self.messages 要值向同一内存地址
- add , delete 都未涉及 self.entry ， self.message 的链接问题
# NoToolConversation

## r__init__
```python
    def __init__(self, reif_entry: dict = None):
        # 如果未传自动创建新的
        if reif_entry is None:
            self.create()

        self.messages = self.reif_entry["reif_content"]
```
传入 entry ( conversation 条目)，为传则创建新的，  
初始化 self.messages , self.entry["reif_content"] 与 self.messages 要值向同一内存地址

## add
```python
    def add(
            self ,
            role: str,
            content: str = None,
            created_at: str = None,
            extra: dict = None,
            )   -> NoToolConversation :

        """
        向会话添加一条消息。

        :param role: 消息角色，必须为 system/user/assistant/tool 之一。
        :param content: 文本内容（对 system/user/assistant 必填，对 tool 可选）。

        :param extra: 可选的扩展字典，任意附加信息。
        :param created_at: 可选时间戳，若不提供则自动生成。
        :return: self，支持链式调用。
        """
        #检验角色
        if role not in CONVERSATION_ROLE:
            raise ValueError(f"未知角色: {role}")

        # 生成时间戳
        if created_at is None:
            created_at = get_iso_timestamp()


        # 构造消息字典
        item = {
            "role": role,
            "content": content,
            "created_at": created_at
        }

        if extra:
            item["extra"] = extra

        self.messages.append(item)
        return self
    
```

## delete
```python
    def delete(self, index: int = None):
        """

        :param index: 索引，若不填默认删除最后一个
        :return:
        """

        if index is None:
            self.messages.pop()
        else:
            self.messages.pop(index)
        return self
```
看源码注释吧

##
















