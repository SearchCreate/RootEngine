"""
JSON文件加载器
无需外部依赖
"""

import json

# JSON字典
JSON_DICT = { 'conversation.simple_conversation': { '$schema': 'http://json-schema.org/draft-07/schema#',
                                        'description': '基础对话消息列表 schema  '
                                                       '约束说明：\n'
                                                       '  - role = assistant '
                                                       '且有工具调用时：content 为 '
                                                       'null，tool_refer 存在\n'
                                                       '  - role = assistant '
                                                       '无工具调用时：content '
                                                       '有值，tool_refer 不存在\n'
                                                       '  - role = tool '
                                                       '时：content 为 '
                                                       'null，tool_refer 存在",',
                                        'items': { 'properties': { 'content': { 'description': '消息内容。assistant '
                                                                                               '有工具调用时为 '
                                                                                               'null，tool '
                                                                                               '时为 '
                                                                                               'null',
                                                                                'type': [ 'string',
                                                                                          'null']},
                                                                   'created_at': { 'format': 'date-time',
                                                                                   'type': 'string'},
                                                                   'extra': { 'type': [ 'object',
                                                                                        'null']},
                                                                   'role': { 'enum': [ 'system',
                                                                                       'user',
                                                                                       'assistant',
                                                                                       'tool'],
                                                                             'type': 'string'},
                                                                   'tool_refer': { 'description': '工具调用信息。role '
                                                                                                  '= '
                                                                                                  'assistant '
                                                                                                  '或 '
                                                                                                  'role '
                                                                                                  '= '
                                                                                                  'tool '
                                                                                                  '时存在',
                                                                                   'items': { 'properties': { 'tool_record_id': { 'description': '工具操作 '
                                                                                                                                                 'ID',
                                                                                                                                  'type': 'string'},
                                                                                                              'tool_record_path': { 'description': '工具操作记录的路径',
                                                                                                                                    'type': 'string'},
                                                                                                              'type': { 'description': 'call=LLM '
                                                                                                                                       '请求工具，result=工具返回结果',
                                                                                                                        'enum': [ 'call',
                                                                                                                                  'result'],
                                                                                                                        'type': 'string'}},
                                                                                              'required': [ 'tool_record_id',
                                                                                                            'tool_record_path',
                                                                                                            'type'],
                                                                                              'type': 'object'},
                                                                                   'type': 'array'}},
                                                   'required': [ 'role',
                                                                 'created_at'],
                                                   'type': 'object'},
                                        'title': 'simple_conversation',
                                        'type': 'array'}}

def get_json(key: str):
    """根据键名获取JSON数据

    Args:
        key: JSON键名，如 'reif_entry', 'conversation.base_conversation'

    Returns:
        JSON字典或None（如果不存在）
    """
    return JSON_DICT.get(key)


def get_jsons_by_category(category: str):
    """根据类别获取JSON数据

    Args:
        category: 类别名，如 'conversation', 'tool'

    Returns:
        该类别下的所有JSON字典
    """
    result = {}
    for key, json_data in JSON_DICT.items():
        if key.startswith(category + '.'):
            result[key] = json_data
        elif key == category:
            result[key] = json_data
    return result


def list_jsons() -> list:
    """返回所有可用的JSON键名列表"""
    return list(JSON_DICT.keys())
