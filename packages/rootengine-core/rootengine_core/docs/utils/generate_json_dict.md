# 注意事项
- 生成时有原来的jsonload , jsondump 变成了用pprint 防止出现生成的python对象Ture用ture这种事情



# 正文
以下是修改后的 `generate_json_dict.py` 使用指南（已删除所有硬编码绝对路径，并将脚本名称统一改为 `generate_json_dict.py`）：

```markdown
# generate_json_dict.py 使用指南

## 上下文

已对 `generate_json_dict.py` 脚本进行了重大改进，使其更通用：

1. **重命名**：将 `schema` 相关名称改为 `json`，使脚本适用于任何 JSON 文件而不仅仅是 JSON Schema。
2. **错误处理**：将打印错误改为抛出异常，提供更好的错误控制。
3. **命令行界面**：添加完整的 `argparse` 支持，便于使用。
4. **向后兼容**：保留了旧版 `generate_schema_dict` 函数作为别名，旧代码仍可工作。

## 主要改进

### 函数重命名

- `load_schema_from_json()` → `load_json_from_file()`
- `scan_schemas_to_dict()` → `scan_jsons_to_dict()`
- `generate_schema_dict()` → `generate_json_dict()`（保留别名）
- `create_simple_loader()` → `create_json_loader()`
- 输出模块中的 `get_schema()` → `get_json()`
- `SCHEMA_DICT` → `JSON_DICT`

### 新功能

- `ignore_errors` 参数：控制是否忽略加载错误
- 灵活的输出文件命名
- 完整的命令行帮助系统

## 使用指南

### 命令行使用

```bash
# 基本用法：扫描目录，生成 json_loader.py
python generate_json_dict.py ./path/to/json/files

# 指定输出文件名
python generate_json_dict.py ./path/to/json/files --output-py custom_loader.py

# 同时生成 JSON 文件
python generate_json_dict.py ./path/to/json/files --output-json data.json

# 忽略加载错误
python generate_json_dict.py ./path/to/json/files --ignore-errors

# 查看帮助
python generate_json_dict.py --help
```

### Python 代码调用

```python
from generate_json_dict import generate_json_dict

# 基本用法
generate_json_dict("path/to/json/files")

# 完整参数
generate_json_dict(
    input_dir="path/to/json/files",
    output_py="custom_loader.py",
    output_json="data.json",
    ignore_errors=True
)

# 向后兼容（仍可用）
from generate_json_dict import generate_schema_dict
generate_schema_dict("path/to/json/files")
```

### 生成的 Python 模块使用

```python
from json_loader import get_json, get_jsons_by_category, list_jsons

# 获取特定 JSON 数据
data = get_json('reif_entry')

# 获取类别下的所有 JSON
conversations = get_jsons_by_category('conversation')

# 列出所有可用的键
all_keys = list_jsons()
```

## 输出文件说明

### 1. Python 模块文件（默认：`json_loader.py`）

包含以下函数：

- `get_json(key)`：根据点分隔路径获取 JSON 数据
- `get_jsons_by_category(category)`：获取特定类别下的所有 JSON
- `list_jsons()`：列出所有可用键名
- `JSON_DICT`：包含所有 JSON 数据的字典

### 2. JSON 文件（可选）

原始字典的 JSON 格式，便于查看和调试。

## 典型使用场景

### 1. 为 RootEngine 项目生成 Schema 加载器

```bash
python generate_json_dict.py "path/to/schema/source" --output-py core2_schemas.py
```

### 2. 集成到构建流程

在项目的 `setup.py` 或构建脚本中调用：

```python
# setup.py
from generate_json_dict import generate_json_dict

def build_schema_module():
    generate_json_dict("schemas", "schemas_loader.py")
```

### 3. 测试不同目录

```bash
# 测试目录是否存在 JSON 文件
python generate_json_dict.py ./test_dir --ignore-errors
```

## 验证计划

1. **语法检查**

   ```bash
   python -m py_compile generate_json_dict.py
   ```

2. **帮助文档测试**

   ```bash
   python generate_json_dict.py --help
   ```

3. **实际使用测试**

   ```bash
   # 使用现有目录测试
   python generate_json_dict.py "path/to/schema/source" --output-py test_loader.py

   # 检查生成的模块
   python -c "from test_loader import list_jsons; print('Keys:', list_jsons())"
   ```

4. **向后兼容性测试**

   ```python
   # 测试旧版 API
   from generate_json_dict import main, generate_schema_dict
   import warnings

   # 应显示弃用警告但正常工作
   main("path/to/schemas", True)
   generate_schema_dict("path/to/schemas")
   ```

## 关键文件路径

- 默认输出：`json_loader.py` 和可选的 `jsons.json`

## 注意事项

1. 如果目录不存在，脚本会抛出 `FileNotFoundError`。
2. 如果没有找到 JSON 文件，会抛出 `ValueError`。
3. 默认不忽略错误，遇到无效 JSON 会抛出异常。
4. 生成的 Python 模块不依赖外部库，可直接使用。
```

主要修改点：
- 所有 `generate_schema_dict.py` 替换为 `generate_json_dict.py`。
- 删除了绝对路径行（如 `D:\GitHub_Project\RootEngine\...`）。
- 保留了占位符 `./path/to/json/files` 等通用路径。
- 在“向后兼容性测试”中保留了旧函数名 `generate_schema_dict` 和 `main`，因为脚本仍提供别名支持。