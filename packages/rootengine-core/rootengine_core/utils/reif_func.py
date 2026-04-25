from ..constants.framework import VERSION,REIF_CATEGORY
from .helpers import get_iso_timestamp
from uuid import uuid4
import json
from jsonschema import validate,SchemaError,ValidationError

from ..schema.runtime.reif_schema import get_json

SCHEMA = get_json("reif_entry")


from jsonschema import validate, ValidationError, SchemaError
from typing import Union

def more_ValidationError(error: Union[ValidationError, SchemaError]) -> str:
    """
    美化 jsonschema 错误信息，支持 ValidationError 和 SchemaError
    """
    if isinstance(error, ValidationError):
        path = list(error.path) if error.path else ["根节点"]
        return (
            f"\n数据不符合 reif_schema 规范：\n"
            f"错误信息：{error.message}\n"
            f"错误路径：{path}"
        )
    elif isinstance(error, SchemaError):
        return (
            f"\nSchema 格式非法：\n"
            f"错误信息：{error.message}"
        )
    else:
        return f"\n未知验证错误：{str(error)}"

def validate_pro(instance, schema:dict):
    """
    增强版 JSON Schema 验证
    :param instance: 待验证数据（dict/str）
    :param schema: JSON Schema（ dict）
    :raises ValueError: 数据不符合 Schema
    :raises SchemaError: Schema 本身非法
    """
    try:
        validate(instance=instance, schema=schema)
    except ValidationError as e:
        # 包装为 ValueError，保留原始异常链（关键修复）
        raise ValueError(more_ValidationError(e)) from e
    except SchemaError as e:
        # Schema 错误单独处理，同样保留异常链
        raise SchemaError(more_ValidationError(e)) from e



#处理 RootEngine information form （REIF）的函数

def create_reif(reif_params,tojson:bool = False):
    '''

    :param reif_params:
    格式：
    {
    "reif_version": 选择的reif格式的版本（选填，默认最新版）（str）(例：1.0) ,
    "category": 条目类别,（选项："agent_card" , "conversation" , "tool_registry" , "tool_execution"）（str),
    "version":选择的该类别(如tool_registry) 的版本（选填，默认最新版）（str）(例：0.1.0),
    "description": 条目描述(选填，默认为None)（str）,
    "id":uuid,32位无连字符，（选填，自动生成）（str）
    "name":此条目名称（选填，默认为id值）（str）,
    "created_at":创立时间，(选填，默认为目前时间)ISO 8601（str）,
    "updated_at":最后修改时间(选填，默认为None)，ISO 8601（str）,
    "extra":其他，拓展元数据(选填，默认为空字典)（dict）,
    }
    "reif_content":条目所储存的内容（选填，默认None）"
    必填：，"category"
    :param tojson:False -> python字典 | Ture -> json字符串
    :return:配置好的REIF格式的 python字典 或 json字符串
    '''
    if isinstance(reif_params, str):
        rp = json.loads(reif_params)
    else:
        rp = reif_params.copy()


    # 查找，解析



    #必填category：
    if rp.get("category"):
        cate = rp.get("category")
        if cate in REIF_CATEGORY:
            category = cate
        else:
            raise KeyError(f"'category':{cate} 有未知字段：category的可选值为{REIF_CATEGORY}")
    else:
        raise KeyError(f"此reif条目 缺少必填参数：category")


    id = rp.get("id",uuid4().hex)
    reif_version = rp.get("reif_version",VERSION["reif_version"])
    version = rp.get("version",VERSION[category])
    description = rp.get("description",None)
    name = rp.get("name",id)
    created_at = rp.get("created_at",get_iso_timestamp())
    updated_at = rp.get("updated_at",None)
    extra = rp.get("extra",{})




    #返回reif_entry条目
    reif_entry = {
        "reif_version": reif_version,
        "reif_metadata": {
            "id": id,
            "category": category,
            "version": version,
            "description": description,
            "name": name,
            "created_at": created_at,
            "updated_at": updated_at,
            "extra": extra
            },
        "reif_content":None
        }
    if tojson:
        return json.dumps(reif_entry)
    else:
        return reif_entry

def validate_reif(reif_params):
    '''

    :param reif_params:尽量是json字符串,reif格式的条目，字典和json字符串均兼容,
    :return: 若没问题返回True，若有问题会报错
    '''

    if isinstance(reif_params, str):
        rp = json.loads(reif_params)
    else:
        rp = reif_params.copy()

    validate(instance=rp, schema=SCHEMA)
    return True


def load_reif(reif_params,reif_content):
    """加载reif entry ,用 reif_content 替换 reif_params 生成的reif entry 的 ’reif_content‘字段"""
    reif_entry = reif_create(reif_params)
    reif_entry["reif_content"] = reif_content
    return reif_entry

reif_create = create_reif
reif_load = load_reif
reif_validate = validate_reif





# 建立 REIFFunction 类 ，方便以后扩展
class REIFFunction:
    def __init__(self,reif_schema=None):
        self.reif_schema = reif_schema if reif_schema else SCHEMA
    def create(self,reif_params,tojson:bool = False):
        '''

        :param reif_params:
        格式：
        {
        "reif_version": 选择的reif格式的版本（选填，默认最新版）（str）(例：1.0) ,
        "category": 条目类别,（选项："agent_card" , "conversation" , "tool_registry" , "tool_execution"）（str),
        "version":选择的该类别(如tool_registry) 的版本（选填，默认最新版）（str）(例：0.1.0),
        "description": 条目描述(选填，默认为None)（str）,
        "id":uuid,32位无连字符，（选填，自动生成）（str）
        "name":此条目名称（选填，默认为id值）（str）,
        "created_at":创立时间，(选填，默认为目前时间)ISO 8601（str）,
        "updated_at":最后修改时间(选填，默认为None)，ISO 8601（str）,
        "extra":其他，拓展元数据(选填，默认为空字典)（dict）,
        }
        "reif_content":条目所储存的内容（选填，默认None）"
        必填：，"category"
        :param tojson:False -> python字典 | Ture -> json字符串
        :return:配置好的REIF格式的 python字典(默认) 或 json字符串（:param tojson is Ture）
        '''
        return create_reif(reif_params,tojson)

    def load(self, reif_params):
        """加载reif entry ,用 reif_content 替换 reif_params 生成的reif entry 的 ’reif_content‘字段"""
        return load_reif(self, reif_params)

    def validate(self, reif_params):
        '''
        :param reif_params:尽量是json字符串,reif格式的条目，字典和json字符串均兼容,
        :return: 若没问题返回True，若有问题会报错
        '''
        def vali(_reif_params,_reif_schema):
            """内置检验函数"""

            if isinstance(reif_params, str):
                rp = json.loads(reif_params)
            else:
                rp = reif_params.copy()

            validate(instance=rp, schema=_reif_schema)
            return True
        return vali(reif_params,self.reif_schema)

