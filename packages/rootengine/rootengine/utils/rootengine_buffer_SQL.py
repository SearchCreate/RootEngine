import sqlite3
import os
from rootengine_core.utils import get_iso_timestamp,create_reif
import json

import uuid

class SqliteFormatError(Exception):
    pass


class RecordRepeatError(Exception):
    pass


class RecordExistError(Exception):
    pass



def is_sqlite_db(file_path):
    """判断文件是否为 SQLite 数据库文件
    :param file_path:
    return:若是，则返回Ture，若不是则返回
    """
    if not os.path.isfile(file_path):
        raise FileExistsError(f"文件不存在：{file_path}")

    # SQLite 数据库文件头固定是这16个字节
    SQLite_HEADER = b"SQLite format 3\x00"

    try:
        with open(file_path, "rb") as f:
            header = f.read(16)  # 只读取前16个字节
            result1092 = header == SQLite_HEADER
            if result1092:
                return True
            else:
                raise SqliteFormatError(f"非sqlite_db文件：{file_path}")
    except Exception as e:
        raise e





class RootEngineBufferSQL:


    def __init__(self,path:str,category:str,id:str=None,table_name:str="reif_entries",init_create_table:bool=True):
        self.path = path
        self.table_name = table_name

        self.category = category

        self.id = id if id is not None else uuid.uuid4().hex

        self.entry_buffer = None



        #自动连接/创建文件(sqlite3)
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()

        self.cursor.row_factory = sqlite3.Row



        #在 init_create_table:bool=True) 时自动创建表（若表不存在）
        if init_create_table:
            self.create_table()




    def create_table(self):
        #创建表
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        entry TEXT NOT NULL,
        
        name TEXT,
        description TEXT,
        
        created_at TEXT NOT NULL,
        updated_at TEXT
        )
        """)
        self.conn.commit()

        return self


    def create_entry(self):
        '''
        自动生成一个 此类的 新 entry
        :return:
        '''
        entry = create_reif({
            "category": self.category,
            "id": self.id,
            "extra": {},

        })
        return entry


    def save(self):
        '''
        将类（内存）维护的entry_buffer覆写数据库中的数据
        :return:
        '''
        if self.entry_buffer is None:
            raise RuntimeError("没有数据可保存，请先调用 load()")


        #处理各种参数
        entry_json = json.dumps(self.entry_buffer)

        created_at_befor = self.entry_buffer.get("reif_metadata").get("created_at")

        if created_at_befor:
            created_at = created_at_befor
        else:
            created_at = get_iso_timestamp()

        updated_at = self.entry_buffer.get("reif_metadata").get("updated_at")
        name = self.entry_buffer.get("reif_metadata").get("name")
        description = self.entry_buffer.get("reif_metadata").get("description")

        #覆写数据库中数据
        self.cursor.execute(
            f"""
            INSERT OR REPLACE INTO {self.table_name} 
            (id, category, entry, name, description, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?)
            """,
            (self.id, self.category, entry_json, name, description, created_at, updated_at )
        )
        self.conn.commit()
        return self


    def load(self):
        """
        将 数据库中数据 覆写到 类（内存）维护的entry_buffer
        :return:
        """
        #寻址
        self.cursor.execute(f"""
        SELECT * FROM {self.table_name} 
        WHERE id = ? AND category = ?
        """,(self.id,self.category,))

        row = self.cursor.fetchone()

        if row:  #已有该记录，从数据库中读取数据，覆写到内存中
            self.entry_buffer = json.loads(row["entry"])

        else:    #未有该记录
            #构建该记录，覆写内存
            self.entry_buffer = self.create_entry()

            #覆写数据库中数据
            self.save()

        return self


    def close(self):
        self.cursor.close()
        self.conn.close()
        return self

    def get(self) -> dict:
            """
            查询数据

            :return sql (设置了 row_factory = sqlite3.Row) 返回的 字典
            """


            self.cursor.execute(f"""
            SELECT * FROM {self.table_name} 
            WHERE id = ?
            AND category = ? 
            """,(self.id,self.category))

            row = self.cursor.fetchone()

            row_dict = dict(row)

            return row_dict["entry"] # 如果不加["entry"] 会返回一堆 列名 的 数据







