
import sys
import importlib
import pkgutil
from .path import sys_path_change



class Registrar:
    def __init__(self):
        self.now_directory = None
        self._sys_path_change = None
        self._registry= {}

    def register(self,directory,clear:bool=False) ->dict:
        '''

        扫描
        调用函数（discover_package）
        把key和value储存与_registry中
        返回_registry
        :param path 被扫描目录路径
        :param clear 若为Ture，清除self.directory后进行扫描
        :return:self
        '''
        self.now_directory = directory
        self._sys_path_change = sys_path_change(self.now_directory)
        if clear:
            self._registry.clear()

        #跳转到被扫描目录
        with self._sys_path_change:
            for finder, name, ispkg in pkgutil.iter_modules([self.now_directory]):
                #扫描

                package = importlib.import_module(name)

                #判断该包是否有为提供discover_package函数
                if not hasattr(package,"discover_plugin"):
                    continue

                #调用函数（discover_package）
                package_info = package.discover_plugin()

                #把key和value储存于_registry中
                key = package_info["key"]
                value = package_info["value"]
                self._registry[key] = value

        return self

    def clear(self):
        self._registry.clear()
        return self

