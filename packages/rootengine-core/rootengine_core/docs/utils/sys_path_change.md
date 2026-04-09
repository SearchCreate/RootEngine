# 其他
接口函数定义：
函数名：discover_package
函数返回值:  
格式：
```python
def discover_plugin():
    return{
        "key":"在注册表里的唯一键（str）",
        "value":"此件所对应的值(数据种类不限)"
    }
```

# 简介
扫描一个目录下的包，并形成映射子字典
# 功能
扫描这个目录  
执行约定的接口函数（discover_plugin）获取约定格式的信息
# code
## sys_path_change

```python
class sys_path_change:
    """
    负责临时跳转到另一个路径去运行程序
    """

    def __init__(self,enter_path):
        self._original_path = sys.path.copy()
        self.enter_path = str(Path(enter_path).resolve())

    def __enter__(self):
        sys.path.insert(0,self.enter_path)
        return self

    def __exit__(self,exc_type,exc_value,traceback):
        sys.path[:] = self._original_path
        return False

```

临时跳转到另一个路径执行程序，
在目录扫描等领域有应用



使用试例
```python
with sys_path_change(your_enter_path):
    pass
```