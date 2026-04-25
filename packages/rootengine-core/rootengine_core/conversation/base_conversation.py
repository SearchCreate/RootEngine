from abc import ABC, abstractmethod
class BaseConversation(ABC):
    """
    BaseConversation 是一个 会话类 的抽象基类
    """
    @abstractmethod
    def append(self, *args, **kwargs):
        """向会话里添加一条信息"""
        pass
    @abstractmethod
    def delete(self,index:int=None, *args, **kwargs):
        """
        删除会话信息
        :param index: if index is None : 默认删除信息列表最后一条信息
                      若 index 不是 None : 则删除该索引的消息
        """
