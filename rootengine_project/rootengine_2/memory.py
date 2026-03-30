import uuid

from utils import reif_create,more_ValidationError
from .framework_env import LATEST_VERSION

MEMORY_DB_FORMAT_PATH = "RootEngine_Information_Format(REIF)/category/memory_db.json"
with open(MEMORY_DB_FORMAT_PATH,'r',encoding='utf-8') as f:
    MEMORY_DB_FORMAT = f.read()         #json字符串

from jsonschema import validate, ValidationError,SchemaError

from ..utils import reif_check,reif_create
class Memory:
    '''

    '''
    def __init__(self,path):
        self.path = path
        self.reif_version = None
        self.version = None
        self.category = 'memory_db'

        self.id = None
        self.name = None
        self.description = None

        self.create_at = None
        self.updated_at = None
        self.extra = {}

    def check(self):
        #检查文件是否存在，用append
        #读取文件
        #检查文件，用reif_check（）
        #返回文件

        #确保文件存在
        with open(self.path,'a',encoding='utf-8') as f:
            f.write('')
        with open(self.path,"r",encoding='utf-8') as f:
            entry = f.read()
            #确保该memory_db符合reif_schema规范
            try:
                entry = reif_check(entry)
            except Exception as e:
                raise e(f"{more_ValidationError(e)}\n来自：{self.path}")
            #检查是否符合memory_db的格式
            try:
                validate(entry,MEMORY_DB_FORMAT)
            except ValidationError as e:
                raise ValueError(more_ValidationError(e))
            except SchemaError as e:
                raise e

    def create(self,reif_version=None,version=None,name:str="该函数自动生成的uuid",description:str=None,extra:dict=None) -> dict:
        self.reif_version = reif_version
        self.version = version
        self.name = name
        self.description = description
        '''
        
        :param reif_version: reif_schema 版本
        :param version: 此类别（memory_db）的版本
        :param name: 此记忆库的名称
        :param description: 此记忆库的描述
        :param extra: 可扩展
        :return: 新建的memory_db(dict)
        '''
        #名确各项参数
        #构造reif_schema元数据
        #更改其reif_content为空列表
        #得到其memory_db条目，写入文件


        #名确各项参数
        self.id = uuid.uuid4().hex
        self.reif_version = reif_version
        self.version = version
        self.name = name if name else self.id    #如果name没填，以其id作为name
        self.description = description
        self.extra = extra

        #构造reif_schema元数据
        reif_prams = {
            "reif_version":self.reif_version,
            "version":self.version,
            "category":self.category,
            "name":self.name,
            "description":self.description,
            "id":self.id,
            "extra":self.extra
        }
        reif_dict = reif_create(reif_prms,) #返回dict

        #更改其reif_content为空列表
        reif_dict["reif_content"] = []

        # 得到其memory_db条目，写入文件
        json.dump(reif_dict,self.path,ensure_ascii=False,indent=2)

        return self


    def read(self,tojson=False):

        with open(self.path,"r",encoding='utf-8') as f:
            reif_json = f.read()
        if tojson:
            return reif_json
        else:
            return json.loads(reif_json)

    def init(self,reif_version=None,version=None,name=None,description=None,extra=None):
        #确保文件存在
        #检查文件格式
        #if 文件之前未创建：
            #调用create
        #更新实例属性

        # 确保文件存在
        with open(self.path,"a",encoding='utf-8') as f:
            reif_dict = f.write()
        #检查文件是否符合格式
        self.check()
        #若是新建的文件，调用self.create建造
        with open(self.path,'r',encoding='utf-8') as f:
            if reif_dict == '':
                self.create(reif_version,version,name,description,extra)
        #更新此实例属性(若未新建文件，则以self.init()的参数更新，若是新建的文件，则按self.create()创建的参数更新，self.create()也源于self.init（）的参数)
        self.name = name if name else self.id  # 如果name没填，以其id作为name
        self.description = description
        self.extra = extra
        #返回实例
        return self

    def save(self,role):



