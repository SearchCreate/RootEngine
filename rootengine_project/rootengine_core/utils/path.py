import sys
from pathlib import Path


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