from abc import ABC,abstractmethod
class BaseBufferDB(ABC):
    """
    BaseBufferDB 是一个 运行时 以缓存为数据源 数据库为备份和长期记忆 的数据库的抽象基类
    理想的工作流程如下
    初始时 从初始话从数据库读取数据 ,加载到缓存中
    之后各种活动都更改缓存的数据 同时可以调用 save 方法把数据同步到数据库中
    """
    def __init__(self):
        # 初始话从数据库读取数据 ,加载到缓存中
        self.buffer = self.load()
    @abstractmethod
    def save(self):
        """将内存中的数据覆写到数据库中"""
        pass
    @abstractmethod
    def load(self):
        """将 数据库中数据 覆写到 内存中"""
        pass
    @abstractmethod
    def get(self):
        """返回内容"""
        pass
    @abstractmethod
    def close(self):
        """关闭数据库链接，若不需要，直接写 pass 即可"""
    @abstractmethod
    def change_buffer(self,new_buffer:dict):
        """更改 类中 缓存"""