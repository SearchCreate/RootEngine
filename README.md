# RootEngine 🌱

**Build from the root, modify with freedom — a lightweight AI agent core**

RootEngine 是一个极简、透明的 AI 智能体（Agent）框架。它不追求大而全的功能，而是专注于提供构建智能体所需的**最核心、最基础**的组件。它的设计哲学是：**简单到你可以轻松理解整个源码，并根据自己的需求自由修改**。

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## ✨ 核心特点

- **🎯 基层（Core Layer）**：只负责管理大模型通信、记忆存储和工具调用等最基础的功能，不捆绑任何具体的应用场景。
- **🔓 自由修改（Hackable）**：代码结构清晰，注释详尽。你可以像拆解乐高一样，深入修改每一块逻辑，打造完全属于你自己的智能体。
- **🚀 开箱即用**：只需配置好 API Key，即可快速启动一个拥有基础对话和工具调用能力的智能体。
- **📦 极简依赖**：仅依赖 OpenAI Python 库（或任何兼容接口），最大限度地减少外部干扰。
- **🧩 插件式工具**：工具以独立包的形式放置，框架自动发现并注册，扩展新工具只需编写一个包和一个描述函数。

---

## 🚀 快速开始

### 1. 安装

目前推荐通过 GitHub 克隆安装：

```bash
git clone https://github.com/SearchCreate/RootEngine.git
cd RootEngine
pip install -e .                # 开发模式安装，方便修改源码
```

### 2. 配置环境变量

RootEngine 使用 `API_KEY` 环境变量来存储你的 API 密钥（例如 SiliconFlow、OpenAI 等）。在终端中设置：

```bash
export API_KEY="your-api-key-here"
```

或者在 Python 中临时设置（仅用于测试）：

```python
import os
os.environ["API_KEY"] = "your-api-key"
```

### 3. 编写配置文件

在 `example/config.py` 中（或你自己的配置文件），定义大模型参数、系统提示词和可用工具列表：

```python
import os

# 大模型配置
llm_data = {
    "api_key": os.environ["API_KEY"],
    "base_url": "https://api.siliconflow.cn/v1",   # 可替换为任何 OpenAI 兼容接口
    "model": "Qwen/Qwen3-8B"
}

memory_path = "memory1.txt"          # 记忆文件路径

system_prompt = '''
# 身份
你是 AI 操作系统的调度器，负责帮用户调度这个操作系统
...
'''

# 工具白名单（填写 tools/ 目录下已注册的工具名称）
tools_usable_list = ["file_edit"]
```

### 4. 运行示例

在 `example/` 目录下有一个完整的示例 `main.py`：

```python
import sys
import os
# 将项目根目录加入 Python 路径（仅示例需要，实际安装后可直接 import）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rootengine import Start, Agent

# 初始化配置和工具
start_dict = Start(config="config", tools_path="tools").start_deal()

# 创建 Agent 实例
agent = Agent(
    llm_data=start_dict["llm_data"],
    agent_name="demo",
    agent_id=1,
    memory_path=start_dict["memory_path"],
    system_prompt=start_dict["system_prompt"],
    tool_register=start_dict["tool_register"]
)

# 开始对话
while True:
    user_input = input("你：")
    reply = agent.agent_llm_with_tool_chat(user_input)
    print(f"助手：{reply}")
```

运行示例：

```bash
cd example
python main.py
```

---

## 🛠️ 开发自己的工具

RootEngine 支持将工具以独立包的形式放置在 `tools/` 目录下（或任意路径），并通过 `Start` 类自动发现。

### 工具包结构

```
tools/
└── your_tool_name/          # 工具名（也是工具调用时的 name）
    ├── __init__.py           # 只需导出 get_tool_info
    └── tool.py               # 工具实现
```

### 编写工具

每个工具包必须提供一个 `get_tool_info()` 函数，返回包含工具元数据和函数对象的字典。

以 `file_edit` 工具为例（`example/tools/file_edit/tool.py`）：

```python
import os

def get_tool_info():
    return {
        "function": file_edit,           # 工具函数对象
        "description": "文本编辑器，支持读取、写入、追加",
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "要操作的文件路径"
                },
                "mode": {
                    "type": "string",
                    "enum": ["read", "write", "append"],
                    "description": "操作模式：读取、写入、追加"
                },
                "content": {
                    "type": "string",
                    "description": "写入或追加的内容（读取模式时无需提供）",
                    "default": ""
                },
                "new_line_num": {
                    "type": "integer",
                    "description": "追加模式下文本前加的换行符数量",
                    "default": 1
                }
            },
            "required": ["file", "mode"]
        }
    }

def file_edit(agent, file, mode, content='', new_line_num=1):
    """
    编辑文件，主要面对 txt
    :param agent: Agent 实例（即使不用也需保留此参数）
    :param file: 文件路径
    :param mode: read / write / append
    :param content: 要写入或追加的内容
    :param new_line_num: 追加时前置换行符数量
    :return: 读取的内容或操作结果
    """
    if mode == "read":
        if not os.path.exists(file):
            return f"文件不存在：{file}"
        with open(file, "r", encoding='utf-8') as f:
            return f.read()
    elif mode in ["write", "append"]:
        dir_name = os.path.dirname(file)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        with open(file, "a" if mode == "append" else "w", encoding='utf-8') as f:
            f.write(f"{'\n' * new_line_num}{content}")
        return "操作成功"
    else:
        return f"未知模式：{mode}"
```

然后在 `__init__.py` 中导出该函数：

```python
from .tool import get_tool_info
```

### 工具注册

配置文件的 `tools_usable_list` 只需填写工具包的名称（即 `your_tool_name`），`Start` 类会自动加载并构建注册表。

---

## 📁 项目结构

```
RootEngine/
├── rootengine/                 # 核心包
│   ├── __init__.py              # 导出主要类
│   ├── agent.py                  # Agent 类
│   ├── llm_openai.py             # LLM 通信封装
│   ├── memory.py                  # 记忆管理
│   ├── tool.py                     # 工具调用执行器
│   ├── start.py                    # 初始化工厂
│   ├── tools_register.py           # 工具自动发现
│   └── utils.py                    # 辅助函数
├── example/                       # 示例
│   ├── config.py                   # 配置文件示例
│   ├── main.py                     # 主程序示例
│   └── tools/                       # 示例工具
│       └── file_edit/
│           ├── __init__.py
│           └── tool.py
├── .gitignore
├── LICENSE
├── README.md
└── setup.py                        # 安装脚本
```

---

## 📄 配置说明

### `config.py` 必需变量

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `llm_data` | dict | 包含 `api_key`、`base_url`、`model` 的字典 |
| `memory_path` | str | 记忆文件路径（JSON 格式） |
| `system_prompt` | str | 系统提示词 |
| `tools_usable_list` | list | 工具名称列表（与 `tools/` 下的子目录名对应） |

### `llm_data` 示例

```python
llm_data = {
    "api_key": os.environ["API_KEY"],
    "base_url": "https://api.openai.com/v1",  # 或其他兼容接口
    "model": "gpt-3.5-turbo"
}
```

---

## 📖 文档

更详细的文档正在编写中。目前你可以通过阅读源码和示例快速上手。

---

## 🤝 贡献

欢迎任何形式的贡献！如果你发现了 bug，或者有好的想法，请提交 issue 或 pull request。

---

## 📜 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

**RootEngine** — 从根源构建，自由修改。