# 其他

# 简介
维护一个工具执行的进行
# 功能

# code
## ToolExeProcessData



## Tool
### 属性
### 方法

#### 1. r__init__(self,tool_registry,agent)

:pram tool_registry : 工具注册表  
:pram agent : agent实例
#### 2. execute(self,tool_call)
执行一个工具调用 

接受tool_call
解析工具的参数（有时候工具参数的json的转义符太多，可能得自己写暴力解码的函数，现在用的是json.load）
寻址，执行工具 
返回result
:pram tool_call

用json解析参数

寻址
1. 首先判断是否存在此工具
2. 不存在：报错  
3. 存在：去找从tool_registry找对应的函数  

工具执行

构造result

返回result

# schema
tool_call中的 id 表示 llm 返回的调用id ，表示其自身的 id  
tool_result 中的 call_id 也表示 llm 返回的id，表示其引用的调用id


