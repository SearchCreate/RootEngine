
# 其他
- 整个模块的设计思路是，运行时以内存对象为数据源 ，db作为长时间的数据保存

# SimpleConversation(BaseConversation)

## r__init__
```python
    def __init__(self,
                 sql_db_path:str,
                 simple_conversation_entry: dict = None,
                 sql_table_name:str=None,
                 auto_save_db:bool = True
                 ):
        """

        :param sql_db_path:硬盘的 sql 数据库 文件路径
        :param simple_conversation_entry: 初始的 simple_conversation 条目 ，若不传则自动生成新的
        :param sql_table_name: sql 文件中的表名
        :param auto_save_db: 每次修改后自动保存
        """
        self.auto_save_db = auto_save_db

        # 如果未传自动创建新的a
        self.entry = simple_conversation_entry
        if self.entry is None:
            super().create()

        self.metadata = self.entry["reif_metadata"]

        self.messages = self.entry["reif_content"]


        # 建立 sql数据库
        self.db = RootEngineBufferSQL(
            path=sql_db_path,
            category="conversation",
            id=self.metadata["id"],
            table_name=sql_table_name,
            init_create_table=True
        )
        # 将 entry 同步到 db 的 entry_buffer，避免 save() 时 entry_buffer 为 None
        self.db.entry_buffer = self.entry
```
- 仿父类,添加sql数据库
- auto_save_db 是自动保存的开关
## add
```python
    def add(
            self ,
            role: str,
            content: str = None,
            created_at: str = None,
            extra: dict = None,
            )   -> BaseConversation :

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
相比于父类 添加了 tool_refer  
其中，当 assistant处于工具调用时 或 角色为tool 时 content: None

## validate_schema
```python
    def validate_schema(self):
        if self.entry is None:
            raise RuntimeError("无会话可校验")
        validate_reif(self.entry)
        validate(instance=self.messages, schema = SCHEMA)
        return True
```


## delete, load_entry, load_messages
```python
    def delete(self, index: int = None):
        super().delete(index)
        if self.auto_save_db:
            self.db.save()
        return self
    def load_entry(self,entry: dict):
        super().load_entry(entry)
        self.db.entry_buffer = self.entry
        if self.auto_save_db:
            self.db.save()
        return self
    def load_messages(self,messages: list):
        super().load_messages(messages)
        self.db.entry_buffer = self.entry
        if self.auto_save_db:
            self.db.save()
        return self
```

## get
```python
    def get(self) -> dict:
        return self.entry
```

# 具体的

---

## 一、`__init__` 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `sql_db_path` | `str` | SQLite 数据库文件路径，用于存储会话数据 |
| `simple_conversation_entry` | `dict` | 初始的 REIF 条目（即一个完整的会话结构）。不传则自动创建新会话 |
| `sql_table_name` | `str` | 数据库中的表名，用于区分不同类型的对话 |
| `auto_save_db` | `bool` | 每次修改（如添加/删除消息）后是否自动保存到数据库，默认为 `True` |

**说明**：  
- 如果传入了 `simple_conversation_entry`，则会加载该条目作为当前会话内容。  
- 否则，`SimpleConversation` 会基于 `sql_db_path` 和 `sql_table_name` 从数据库读取已有会话，或创建一条新的空会话记录。

---

## 二、实例属性

| 属性 | 说明 |
|------|------|
| `entry` | 完整的 REIF 条目（字典），包含元数据、消息列表等 |
| `metadata` | 快捷访问 `entry["reif_metadata"]`，存储会话元信息 |
| `messages` | 快捷访问 `entry["reif_content"]`，即消息列表 |
| `db` | `RootEngineBufferSQL` 数据库实例，用于底层读写 |
| `auto_save_db` | 自动保存开关，可动态修改 |

**注意**：修改 `messages` 后，若 `auto_save_db` 为 `True`，会自动触发数据库更新。

---

## 三、方法详解

### 1. `add(role, content, tool_refer=None, created_at=None, extra=None)`

**功能**：添加一条消息到会话末尾。  
**返回**：`self`，支持链式调用。

| 参数 | 类型 | 说明 |
|------|------|------|
| `role` | `str` | 消息角色，必须为 `"system"`, `"user"`, `"assistant"`, `"tool"` 之一 |
| `content` | `str` | 消息文本内容（`system`/`user`/`assistant` 角色必填） |
| `tool_refer` | `dict` | 工具调用引用，仅 `assistant` 和 `tool` 角色使用 |
| `created_at` | `str` | 时间戳，不填则自动生成（通常为 ISO 格式） |
| `extra` | `dict` | 扩展数据，可存放任意自定义字段 |

**示例**：
```python
conv = SimpleConversation("chat.db")
conv.add("user", "你好").add("assistant", "你好！有什么可以帮您？")
```

---

### 2. `delete(index=None)`

**功能**：删除指定索引的消息。  
**返回**：`self`。

| 参数 | 类型 | 说明 |
|------|------|------|
| `index` | `int` | 要删除的消息索引（从0开始）。不填则删除最后一条 |

**示例**：
```python
conv.delete(0)      # 删除第一条消息
conv.delete()       # 删除最后一条消息
```

---

### 3. `get()`

**功能**：返回当前会话的完整 `entry` 字典。  
**返回**：`dict`（REIF 格式）。

---

### 4. `load_entry(entry)`

**功能**：用一个新的 REIF 条目替换当前会话的全部内容（包括元数据和消息列表）。  
**参数**：`entry` (dict) – 符合 REIF 格式的条目。  
**注意**：会完全覆盖原有数据，并触发自动保存（若 `auto_save_db=True`）。

---

### 5. `load_messages(messages)`

**功能**：仅替换当前会话的消息列表（即 `reif_content` 字段），保留元数据等其他信息。  
**参数**：`messages` (list) – 消息列表，每条消息为字典结构。  
**注意**：也会触发自动保存。

---

### 6. `validate_schema()`

**功能**：使用 JSON Schema 校验当前会话的 `messages` 列表结构是否合法。  
**返回**：校验通过时返回 `True`；失败时抛出异常（异常类型未给出，通常为 `jsonschema.ValidationError` 或自定义异常）。

**用途**：在保存或修改前确保消息格式符合预期，避免数据库写入脏数据。

---

## 四、使用示例

```python
# 1. 创建新会话（数据库自动创建）
conv = SimpleConversation("my_chat.db", sql_table_name="conversations")

# 2. 添加消息
conv.add("system", "你是一个乐于助人的助手")
conv.add("user", "什么是 REIF？")
conv.add("assistant", "REIF 是一种结构化数据格式，常用于存储对话条目。")

# 3. 删除多余消息（比如删除第二条 user 消息）
conv.delete(1)

# 4. 校验消息格式
conv.validate_schema()   # True 或抛异常

# 5. 获取完整条目
full_entry = conv.get()

# 6. 重新加载其他会话
other_entry = {"reif_metadata": {...}, "reif_content": [...]}
conv.load_entry(other_entry)

# 7. 仅替换消息列表
new_messages = [{"role": "user", "content": "Hello"}]
conv.load_messages(new_messages)
```

---

## 五、注意事项

- **自动保存**：`auto_save_db` 默认为 `True`，每次 `add`、`delete`、`load_entry`、`load_messages` 都会同步写入 SQLite。若批量操作较多，可临时设为 `False` 再手动保存（通过 `db` 属性）。
- **角色约束**：`role` 必须是预定义的四种之一，且 `tool_refer` 通常与 `tool` 角色配合使用。
- **时间戳格式**：若不提供 `created_at`，会自动生成 ISO 8601 格式字符串（如 `"2025-04-12T10:30:00Z"`）。
- **线程安全**：若在多线程中使用，需自行确保数据库连接安全（可使用连接池或锁）。

如果需要更底层的数据库操作，可以直接访问 `conv.db`（`RootEngineBufferSQL` 实例）。