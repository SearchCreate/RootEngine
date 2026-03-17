# RootEngine 详细教程与框架构成

**Build from the root, modify with freedom — a lightweight AI agent core**

---

## 📑 目录

- [第一部分：框架构成](#第一部分框架构成)
  - [1.1 整体架构](#11-整体架构)
  - [1.2 核心模块详解](#12-核心模块详解)
  - [1.3 数据流图](#13-数据流图)
- [第二部分：详细教程](#第二部分详细教程)
  - [2.1 安装与配置](#21-安装与配置)
  - [2.2 第一个Agent](#22-第一个agent)
  - [2.3 开发自定义工具](#23-开发自定义工具)
  - [2.4 高级用法](#24-高级用法)
  - [2.5 调试与问题排查](#25-调试与问题排查)

---

# 第一部分：框架构成

## 1.1 整体架构

RootEngine 采用模块化设计，各组件职责明确，相互协作。下图展示了框架的核心架构：

```
┌─────────────────────────────────────────────────────────────┐
│                         Agent                                 │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐ │
│  │   LLM     │  │  Memory   │  │   Tool    │  │  Start    │ │
│  │  OpenAI   │  │           │  │           │  │           │ │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘ │
│         │              │              │              │        │
│         ▼              ▼              ▼              ▼        │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                    ToolRegistry                        │   │
│  │                 工具自动发现与注册                       │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      外部工具包                               │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │ file_edit │  │ memorize  │  │  more...  │               │
│  └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 模块依赖关系

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  Agent  │────▶│  LLM    │     │  Utils  │
└─────────┘     └─────────┘     └─────────┘
     │               │               ▲
     │               │               │
     ▼               ▼               │
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Memory  │     │  Tool   │────▶│ ToolReg │
└─────────┘     └─────────┘     └─────────┘
                      │
                      ▼
                 ┌─────────┐
                 │ Start   │
                 └─────────┘
```

## 1.2 核心模块详解

### 1.2.1 Agent 类（`agent.py`）

**职责**：智能体的核心控制器，协调各组件工作，管理对话流程。

**关键属性**：
- `llm`: LLM 通信实例
- `memory_obj`: 记忆管理实例
- `tool`: 工具调用实例
- `system_prompt`: 系统提示词
- `tool_register`: 工具注册表

**核心方法**：

| 方法 | 描述 |
|------|------|
| `agent_base_chat()` | 基础对话，单次 LLM 调用 |
| `agent_deal()` | 处理 LLM 返回，执行工具调用 |
| `agent_llm_with_tool_chat()` | 主对话循环，自动处理多轮工具调用 |
| `agent_get_memory_path()` | 获取记忆文件路径（工具使用） |

**对话流程**：
```python
用户输入 → agent_llm_with_tool_chat()
    ↓
agent_base_chat() → LLM 调用
    ↓
agent_deal() 解析返回
    ├─ 有工具调用 → tool.tool_call_deal() → 执行工具 → 结果返回 LLM
    └─ 无工具调用 → 直接返回用户
```

### 1.2.2 LlmOpenAI 类（`llm_openai.py`）

**职责**：封装与 OpenAI 兼容 API 的通信。

**关键属性**：
- `api_key`, `base_url`, `model`: 模型配置

**核心方法**：

| 方法 | 描述 |
|------|------|
| `llm_start()` | 初始化 OpenAI 客户端 |
| `llm_message_data()` | 构建符合 OpenAI 格式的消息列表 |
| `llm_chat()` | 执行单次对话 |
| `llm_prsm_data()` | 解析 LLM 返回数据 |
| `llm_tool_register()` | 将内部工具注册表转换为 OpenAI 格式 |

**消息格式转换**：
```python
# 内部格式 → OpenAI 格式
{
    "role": "user",
    "content": "你好"
}

# 工具调用格式
{
    "role": "assistant",
    "tool_calls": [...]
}

# 工具返回格式
{
    "role": "tool",
    "content": "结果",
    "tool_call_id": "call_123"
}
```

### 1.2.3 Memory 类（`memory.py`）

**职责**：管理对话历史记忆，持久化到 JSON 文件。

**关键属性**：
- `path`: 记忆文件路径

**核心方法**：

| 方法 | 描述 |
|------|------|
| `memory_creat()` | 初始化记忆文件（如果不存在） |
| `memory_save()` | 保存一条对话记录 |
| `memory_read()` | 读取所有记忆 |

**记忆文件格式**：
```json
[
    {
        "role": "user",
        "content": "你好"
    },
    {
        "role": "assistant", 
        "content": "你好！我是AI助手"
    },
    {
        "role": "assistant",
        "content": null,
        "tool_calls": [...]
    },
    {
        "role": "tool",
        "content": "工具执行结果",
        "tool_call_id": "call_123"
    }
]
```

### 1.2.4 Tool 类（`tool.py`）

**职责**：执行工具调用，处理参数解析和错误。

**关键属性**：
- `tools_register`: 工具注册表
- `agent`: 关联的 Agent 实例

**核心方法**：

| 方法 | 描述 |
|------|------|
| `tool_call_deal()` | 处理工具调用列表，执行对应函数 |

**执行流程**：
```python
tool_calls → 遍历每个调用
    ↓
解析参数 JSON → json.loads()
    ↓
查找工具函数 → tools_register[tool_name]["function"]
    ↓
执行函数 → func(agent=self.agent, **arguments)
    ↓
收集结果 → 返回 tool_result_list
```

### 1.2.5 ToolRegistry 类（`tools_register.py`）

**职责**：自动发现并加载工具包，构建工具注册表。

**关键属性**：
- `tool_path`: 工具目录路径
- `_my_registry`: 内部注册表

**核心方法**：

| 方法 | 描述 |
|------|------|
| `reg_discover_tool()` | 扫描目录，加载所有工具包 |
| `reg_get_registry()` | 获取注册表 |

**发现机制**：
1. 将工具目录临时加入 `sys.path`
2. 使用 `pkgutil.iter_modules()` 扫描所有包
3. 检查包是否有 `get_tool_info()` 函数
4. 调用该函数获取工具信息
5. 存入注册表

### 1.2.6 Start 类（`start.py`）

**职责**：初始化工厂，整合配置和工具，为 Agent 准备所需数据。

**关键属性**：
- `config`: 配置模块
- `tools_usable`: 工具白名单
- `all_registry`: 完整工具注册表

**核心方法**：

| 方法 | 描述 |
|------|------|
| `start_agent_tool_register()` | 根据白名单筛选工具 |
| `start_deal()` | 返回 Agent 初始化所需字典 |

### 1.2.7 Utils 模块（`utils.py`）

**职责**：提供通用辅助函数。

| 函数 | 描述 |
|------|------|
| `ps(content)` | 打印系统信息（带前缀） |
| `oa(role, content)` | 创建 OpenAI 格式消息 |
| `oat(role, content, tool_calls)` | 创建带工具调用的消息 |

## 1.3 数据流图

### 对话流程时序图

```
用户            Agent           LLM           Tool          Memory
 |               |              |              |              |
 |----输入------>|              |              |              |
 |               |----读取----->|              |              |
 |               |<----记忆-----|              |              |
 |               |----调用----->|              |              |
 |               |              |----返回----->|              |
 |               |<----结果-----|              |              |
 |               |              |              |----执行----->|
 |               |              |              |<----结果-----|
 |               |              |<----返回-----|              |
 |               |----保存----->|              |              |
 |               |              |              |              |
 |<----回复------|              |              |              |
```

### 工具调用循环

```
用户输入
   ↓
LLM 调用
   ↓
有工具调用？───否───→ 直接返回
   ↓是
执行工具
   ↓
将结果作为新消息
   ↓
再次调用 LLM
   ↓
重复直到无工具调用
```

---

# 第二部分：详细教程

## 2.1 安装与配置

### 2.1.1 环境要求

- Python 3.8 或更高版本
- 一个 OpenAI 兼容的 API Key（SiliconFlow、OpenAI、DeepSeek 等）

### 2.1.2 安装方法

#### 方法一：从 PyPI 安装（稳定版）
```bash
pip install rootengine
```

#### 方法二：从 GitHub 安装（最新开发版）
```bash
git clone https://github.com/zimial/RootEngine.git
cd RootEngine
pip install -e .
```

#### 方法三：直接使用（不安装）
如果想先尝试而不安装，可以在项目根目录运行：
```python
import sys
import os
sys.path.insert(0, os.path.abspath("."))
from rootengine import Start, Agent
```

### 2.1.3 验证安装

```python
python -c "from rootengine import Agent; print('安装成功！')"
```

## 2.2 第一个 Agent

### 2.2.1 创建配置文件 `config.py`

```python
import os

# 大模型配置
llm_data = {
    "api_key": os.environ["API_KEY"],          # 从环境变量读取
    "base_url": "https://api.siliconflow.cn/v1", # API 地址
    "model": "Qwen/Qwen3-8B"                    # 模型名称
}

# 记忆文件路径（相对路径或绝对路径）
memory_path = "memory1.txt"

# 系统提示词（定义 Agent 的行为和角色）
system_prompt = '''
# 身份
你是 AI 操作系统的调度器，负责帮用户调度这个操作系统

# 技能
1. 陪用户聊天
2. 调用工具完成任务
3. 当需要工具时，使用 tool_calls 格式返回

# 限制
- 返回的 argument 必须是 JSON 字符串
- 不要添加无关的后缀
'''

# 工具白名单（填写 tools/ 目录下已注册的工具名称）
tools_usable_list = []  # 暂时没有工具
```

### 2.2.2 创建主程序 `main.py`

```python
from rootengine import Start, Agent

# 初始化（config_path 是配置文件模块名，不含 .py）
start_dict = Start(
    config_path="config",
    tools_path="tools"      # 工具目录，暂时用不到
).start_deal()

# 创建 Agent 实例
agent = Agent(
    llm_data=start_dict["llm_data"],
    agent_name="my_first_agent",
    agent_id=1,
    memory_path=start_dict["memory_path"],
    system_prompt=start_dict["system_prompt"],
    tool_register=start_dict["tool_register"],
    debug_prompt=True        # 开启调试输出
)

# 开始对话
print("开始对话（输入 'exit' 退出）")
while True:
    user_input = input("\n你：")
    if user_input.lower() in ['exit', 'quit']:
        break
    
    reply = agent.agent_llm_with_tool_chat(user_input)
    print(f"助手：{reply}")
```

### 2.2.3 运行

```bash
export API_KEY="your-api-key-here"  # Linux/macOS
# 或
set API_KEY=your-api-key-here       # Windows

python main.py
```

### 2.2.4 理解输出

当 `debug_prompt=True` 时，你会看到：
```
系统：chat completion API初始化
系统：memory文件初始化
系统：tool初始化

开始对话（输入 'exit' 退出）

你：你好
系统：调用工具中
参数：{}
助手：你好！我是AI助手，有什么可以帮你的吗？
```

## 2.3 开发自定义工具

### 2.3.1 工具开发规范

每个工具必须满足：
1. 放在 `tools/工具名/` 目录下
2. 包含 `__init__.py` 和 `tool.py`
3. `__init__.py` 必须导出 `get_tool_info`
4. `tool.py` 必须包含 `get_tool_info()` 函数和工具函数

### 2.3.2 创建第一个工具：文件编辑器

#### 步骤 1：创建目录结构

```
你的项目/
├── tools/
│   └── file_edit/          # 工具名（也是调用时的 name）
│       ├── __init__.py
│       └── tool.py
├── config.py
└── main.py
```

#### 步骤 2：编写 `tools/file_edit/tool.py`

```python
import os

def get_tool_info():
    """
    返回工具元数据
    必须包含：function, description, parameters
    """
    return {
        "function": file_edit,  # 工具函数对象
        "description": "文本编辑器，支持读取、写入、追加文件",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "要操作的文件路径（支持绝对或相对路径）"
                },
                "mode": {
                    "type": "string",
                    "enum": ["read", "write", "append"],
                    "description": "操作模式：read（读取）、write（写入）、append（追加）"
                },
                "content": {
                    "type": "string",
                    "description": "要写入或追加的内容（读取模式时无需提供）",
                    "default": ""
                },
                "newline_num": {
                    "type": "integer",
                    "description": "追加模式下，内容前添加的换行符数量",
                    "default": 1
                }
            },
            "required": ["path", "mode"]  # 必填参数
        }
    }

def file_edit(agent, path, mode, content='', newline_num=1):
    """
    文件编辑函数
    
    参数说明：
    - agent: Agent 实例（必须保留，即使未使用）
    - path: 文件路径
    - mode: read/write/append
    - content: 写入或追加的内容
    - newline_num: 追加时的前置换行符数量
    
    返回：
    - read 模式：文件内容
    - write/append 模式：操作结果信息
    """
    try:
        if mode == "read":
            if not os.path.exists(path):
                return f"错误：文件不存在 - {path}"
            with open(path, "r", encoding='utf-8') as f:
                content = f.read()
                return f"文件内容：\n{content}"
                
        elif mode == "write":
            # 确保目录存在
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            
            with open(path, "w", encoding='utf-8') as f:
                f.write(content)
            return f"写入成功：{path}"
            
        elif mode == "append":
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
            
            with open(path, "a", encoding='utf-8') as f:
                # 添加指定数量的换行符
                f.write(f"{'\n' * newline_num}{content}")
            return f"追加成功：{path}"
            
        else:
            return f"错误：未知模式 '{mode}'，支持的模式：read/write/append"
            
    except Exception as e:
        return f"文件操作出错：{str(e)}"
```

#### 步骤 3：编写 `tools/file_edit/__init__.py`

```python
from .tool import get_tool_info
```

#### 步骤 4：在配置文件中启用工具

修改 `config.py`，添加工具白名单：

```python
tools_usable_list = ["file_edit"]  # 启用 file_edit 工具
```

#### 步骤 5：测试工具

运行 `main.py`，尝试使用工具：

```
你：帮我创建一个文件 test.txt，内容是 Hello World
助手：写入成功：test.txt

你：读取 test.txt 的内容
助手：文件内容：
Hello World

你：在 test.txt 后面追加一行，内容是 "这是第二行"，前面加两个换行
助手：追加成功：test.txt

你：再读一次看看
助手：文件内容：
Hello World

这是第二行
```

### 2.3.3 工具开发最佳实践

#### 1. 参数命名一致性
`get_tool_info()` 中的参数名必须与工具函数的参数名完全一致。

✅ 正确：
```python
"properties": {
    "path": { ... }      # 参数名 path
}
def file_edit(agent, path, ...):  # 函数参数也是 path
```

❌ 错误：
```python
"properties": {
    "file": { ... }      # 参数名 file
}
def file_edit(agent, path, ...):  # 函数参数是 path
```

#### 2. 返回值格式
工具返回值会直接传递给 LLM，建议：
- 成功时返回清晰的结果信息
- 失败时返回错误信息（LLM 会理解并告知用户）
- 尽量返回字符串，方便 LLM 处理

#### 3. 错误处理
在工具函数内部做好异常捕获，返回友好的错误信息。

```python
try:
    # 工具逻辑
    return "成功信息"
except Exception as e:
    return f"操作失败：{str(e)}"
```

#### 4. 参数验证
即使 LLM 通常会按要求传参，也建议在工具函数内做基本验证：

```python
if not isinstance(path, str):
    return "错误：path 必须是字符串"
if mode not in ["read", "write", "append"]:
    return f"错误：不支持的模式 {mode}"
```

### 2.3.4 开发第二个工具：天气查询

这个示例展示如何调用外部 API。

```python
import requests

def get_tool_info():
    return {
        "function": get_weather,
        "description": "查询指定城市的实时天气",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如 北京、上海"
                }
            },
            "required": ["city"]
        }
    }

def get_weather(agent, city):
    """
    查询天气（示例使用公开 API）
    """
    try:
        # 这里使用示例 API，实际使用时请替换为真实的天气 API
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": "your_api_key",  # 需要注册获取
            "units": "metric",
            "lang": "zh_cn"
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            return f"{city} 当前天气：{weather}，温度：{temp}°C"
        else:
            return f"查询失败：{city}，请检查城市名称"
    except Exception as e:
        return f"天气查询出错：{str(e)}"
```

## 2.4 高级用法

### 2.4.1 多工具协同

可以在配置文件中启用多个工具：

```python
tools_usable_list = ["file_edit", "weather", "calculator", "search"]
```

LLM 会根据用户需求自动选择合适的工具，甚至组合使用。

### 2.4.2 自定义系统提示词

系统提示词对 Agent 的行为影响很大。以下是一个更专业的提示词示例：

```python
system_prompt = '''
# 角色定义
你是一个专业的 AI 助手，擅长使用各种工具解决问题。

# 工作原则
1. 首先理解用户需求，判断是否需要使用工具
2. 如果需要工具，优先调用最合适的工具
3. 工具调用格式必须严格遵循 OpenAI 规范
4. 工具执行结果返回后，用自然语言总结给用户

# 工具使用规范
- 调用工具时，arguments 必须是 JSON 字符串
- 一个回复中可以调用多个工具
- 工具结果返回后，根据结果继续对话或调用其他工具

# 回答风格
- 专业、准确、简洁
- 对于工具执行结果，给出清晰的解释
- 如果工具调用失败，向用户说明原因并提供建议
'''
```

### 2.4.3 记忆管理

记忆文件（如 `memory1.txt`）保存了完整的对话历史。你可以：

#### 查看记忆
```python
import json
with open("memory1.txt", "r") as f:
    memory = json.load(f)
    for msg in memory:
        print(f"{msg['role']}: {msg.get('content', '[工具调用]')}")
```

#### 清空记忆
```python
with open("memory1.txt", "w") as f:
    json.dump([], f)
```

#### 使用不同的记忆文件
```python
# 为不同场景使用不同记忆
agent_chat = Agent(..., memory_path="chat_memory.txt")
agent_file = Agent(..., memory_path="file_ops_memory.txt")
```

### 2.4.4 调试模式

创建 Agent 时设置 `debug_prompt=True` 可以查看内部流程：

```python
agent = Agent(..., debug_prompt=True)
```

输出示例：
```
系统：chat completion API初始化
系统：memory文件初始化
系统：tool初始化
系统：调用工具中
参数：{'path': 'test.txt', 'mode': 'read'}
```

### 2.4.5 创建多个 Agent

```python
# 不同角色的 Agent
assistant1 = Agent(
    agent_name="助手1",
    agent_id=1,
    llm_data=llm_data,
    system_prompt="你是一个友好的聊天助手",
    memory_path="chat_memory.txt",
    tool_register={}  # 无工具
)

assistant2 = Agent(
    agent_name="工具助手",
    agent_id=2,
    llm_data=llm_data,
    system_prompt="你是一个擅长使用工具的助手",
    memory_path="tool_memory.txt",
    tool_register=tool_register
)
```

## 2.5 调试与问题排查

### 2.5.1 常见错误及解决方法

#### 错误 1：工具参数不匹配
```
工具参数解码错误：Expecting property name enclosed in double quotes
```
**原因**：LLM 返回的参数字符串格式错误。  
**解决**：检查系统提示词，确保说明要求返回 JSON 字符串。

#### 错误 2：找不到工具
```
KeyError: 'file_edit'
```
**原因**：工具未正确注册或白名单名称错误。  
**解决**：
- 检查工具目录名是否与白名单一致
- 确认工具包中有 `get_tool_info` 函数
- 检查 `tools_usable_list` 中的名称

#### 错误 3：记忆文件损坏
```
ValueError: 记忆文件 memory1.txt 损坏，无法解析为 JSON
```
**原因**：记忆文件被手动修改导致 JSON 格式错误。  
**解决**：删除或修复记忆文件，框架会自动重建。

### 2.5.2 调试技巧

#### 开启调试输出
```python
agent = Agent(..., debug_prompt=True)
```

#### 打印工具注册表
```python
print("可用工具：", list(start_dict["tool_register"].keys()))
```

#### 查看 LLM 返回的原始数据
```python
reply_data = agent.agent_base_chat(...)
print("原始返回：", reply_data["all"])
```

#### 手动测试工具函数
```python
from tools.file_edit.tool import file_edit

# 直接调用测试
result = file_edit(agent=None, path="test.txt", mode="read")
print(result)
```

### 2.5.3 性能优化建议

1. **记忆文件大小**：定期清理或归档旧对话，避免记忆文件过大。
2. **工具调用**：工具函数应尽量快速返回，避免耗时操作。
3. **并发使用**：如需同时处理多个对话，为每个会话创建独立的 Agent 实例。

---

## 结语

RootEngine 的设计理念是简单、透明、可修改。通过本教程，你应该已经掌握了：

- ✅ 框架的模块构成和各组件职责
- ✅ 如何快速搭建第一个 Agent
- ✅ 如何开发自定义工具
- ✅ 高级用法和调试技巧

现在，你可以基于 RootEngine 构建属于你自己的智能体应用了！如果在使用过程中遇到任何问题，欢迎提交 issue 或贡献代码。

**Happy Building!** 🚀