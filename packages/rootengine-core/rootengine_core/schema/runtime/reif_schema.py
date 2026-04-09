"""
JSON文件加载器
无需外部依赖
"""

import json

# JSON字典
JSON_DICT = { 'conversation.base_conversation': { '$schema': 'http://json-schema.org/draft-07/schema#',
                                         'description': '基础对话消息列表（无工具字段）',
                                         'items': { 'properties': { 'content': { 'type': [ 'string',
                                                                                           'null']},
                                                                    'created_at': { 'format': 'date-time',
                                                                                    'type': 'string'},
                                                                    'extra': { 'additionalProperties': True,
                                                                               'type': [ 'object',
                                                                                         'null']},
                                                                    'role': { 'enum': [ 'system',
                                                                                        'user',
                                                                                        'assistant'],
                                                                              'type': 'string'}},
                                                    'required': [ 'role',
                                                                  'created_at'],
                                                    'type': 'object'},
                                         'title': 'reif_content_base_conversation',
                                         'type': 'array'},
  'llm.llm_message': { '$schema': 'http://json-schema.org/draft-07/schema#',
                       'allOf': [ { 'if': { 'properties': { 'role': { 'const': 'tool'}}},
                                    'then': { 'properties': { 'content': { 'description': 'tool '
                                                                                          '角色的 '
                                                                                          'content '
                                                                                          '必须为 '
                                                                                          'tool_result '
                                                                                          '对象',
                                                                           'type': 'object'},
                                                              'tool_call_id': { 'pattern': '^[0-9a-fA-F]{32}$',
                                                                                'type': 'string'}},
                                              'required': ['tool_call_id']}},
                                  { 'if': { 'properties': { 'role': { 'const': 'assistant'}}},
                                    'then': { 'properties': { 'tool_calls': { 'items': { '$ref': 'tool/tool_call.json'},
                                                                              'type': 'array'}}}}],
                       'description': 'LLM 对话消息单条格式，与 OpenAI 格式解耦',
                       'properties': { 'content': { 'description': '消息内容',
                                                    'oneOf': [ { 'description': 'assistant '
                                                                                '无文字内容时（如纯工具调用）',
                                                                 'type': 'null'},
                                                               { 'description': 'system/user/assistant '
                                                                                '普通文字内容',
                                                                 'type': 'string'},
                                                               { 'description': 'tool '
                                                                                '角色时为 '
                                                                                'tool_result '
                                                                                '对象',
                                                                 'type': 'object'}]},
                                       'created_at': { 'description': '创建时间 '
                                                                      'ISO '
                                                                      '8601',
                                                       'format': 'date-time',
                                                       'type': 'string'},
                                       'extra': { 'additionalProperties': True,
                                                  'description': '扩展数据',
                                                  'type': ['object', 'null']},
                                       'role': { 'description': '消息角色',
                                                 'enum': [ 'system',
                                                           'user',
                                                           'assistant',
                                                           'tool'],
                                                 'type': 'string'},
                                       'tool_call_id': { 'description': 'tool '
                                                                        '角色必填，关联到 '
                                                                        'assistant '
                                                                        '消息 '
                                                                        'tool_calls '
                                                                        '中对应 '
                                                                        'call '
                                                                        '的 id',
                                                         'pattern': '^[0-9a-fA-F]{32}$',
                                                         'type': 'string'},
                                       'tool_calls': { 'description': 'LLM '
                                                                      '工具调用列表，仅 '
                                                                      'assistant '
                                                                      '消息可能包含',
                                                       'items': { '$ref': '../tool/tool_call.json'},
                                                       'type': 'array'}},
                       'required': ['role', 'created_at'],
                       'title': 'llm_message',
                       'type': 'object'},
  'llm.llm_output': { '$schema': 'http://json-schema.org/draft-07/schema#',
                      'description': 'LLM 单次调用的返回格式',
                      'properties': { 'content': { 'description': 'LLM '
                                                                  '回复的文字内容，无文字时为 '
                                                                  'null（纯工具调用场景）',
                                                   'oneOf': [ {'type': 'null'},
                                                              { 'type': 'string'}]},
                                      'created_at': { 'description': 'LLM '
                                                                     '返回时间，ISO '
                                                                     '8601 格式',
                                                      'format': 'date-time',
                                                      'type': 'string'},
                                      'extra': { 'additionalProperties': True,
                                                 'description': '扩展数据',
                                                 'type': ['object', 'null']},
                                      'tool_calls': { 'description': 'LLM '
                                                                     '发起的工具调用列表，无工具调用时为 '
                                                                     'null',
                                                      'items': { '$ref': '../tool/tool_call.json'},
                                                      'type': 'array'},
                                      'usage': { 'description': 'Token 用量统计',
                                                 'properties': { 'completion_tokens': { 'description': '生成回复消耗的 '
                                                                                                       'token '
                                                                                                       '数',
                                                                                        'type': 'integer'},
                                                                 'prompt_tokens': { 'description': '输入 '
                                                                                                   'prompt '
                                                                                                   '消耗的 '
                                                                                                   'token '
                                                                                                   '数',
                                                                                    'type': 'integer'},
                                                                 'total_tokens': { 'description': '总 '
                                                                                                  'token '
                                                                                                  '数',
                                                                                   'type': 'integer'}},
                                                 'type': 'object'}},
                      'title': 'llm_output',
                      'type': 'object'},
  'llm.tool_choice': { '$schema': 'http://json-schema.org/draft-07/schema#',
                       'description': 'Controls how the model uses tools. Can '
                                      'be a simple string mode or an object '
                                      'specifying a forced function call.',
                       'oneOf': [ { 'description': 'Auto: model decides; None: '
                                                   'no tool call; Required: '
                                                   'model must call at least '
                                                   'one tool.',
                                    'enum': ['auto', 'none', 'required'],
                                    'title': 'Simple Mode',
                                    'type': 'string'},
                                  { 'additionalProperties': False,
                                    'properties': { 'function': { 'additionalProperties': False,
                                                                  'properties': { 'registry_id': { 'description': 'tool '
                                                                                                                  '在注册表的 '
                                                                                                                  'registry_id ',
                                                                                                   'format': 'uuid',
                                                                                                   'type': 'string'}},
                                                                  'required': [ 'registry_id'],
                                                                  'type': 'object'},
                                                    'type': { 'const': 'function',
                                                              'description': 'Must '
                                                                             'be '
                                                                             "'function'.",
                                                              'type': 'string'}},
                                    'required': ['type', 'function'],
                                    'title': 'Specific Function Call',
                                    'type': 'object'}],
                       'title': ' Tool Choice Schema(仿openai，其中function.name '
                                '改成了 func.registry_id)',
                       'type': ['string', 'object']},
  'reif_entry': { '$schema': 'http://json-schema.org/draft-07/schema#',
                  'additionalProperties': False,
                  'description': 'RootEngine Information Format 条目',
                  'properties': { 'reif_content': { 'description': '条目内容，具体结构由 '
                                                                   'category '
                                                                   '决定'},
                                  'reif_metadata': { 'additionalProperties': False,
                                                     'description': '条目元数据',
                                                     'properties': { 'category': { 'description': '条目类别',
                                                                                   'enum': [ 'agent_card',
                                                                                             'conversation',
                                                                                             'tool_registry',
                                                                                             'tool_record'],
                                                                                   'type': 'string'},
                                                                     'created_at': { 'description': '创建时间，格式 '
                                                                                                    'ISO '
                                                                                                    '8601',
                                                                                     'format': 'date-time',
                                                                                     'type': 'string'},
                                                                     'description': { 'description': '详细的描述',
                                                                                      'type': [ 'string',
                                                                                                'null']},
                                                                     'extra': { 'additionalProperties': True,
                                                                                'description': '扩展数据',
                                                                                'type': [ 'object',
                                                                                          'null']},
                                                                     'id': { 'description': '唯一识别符',
                                                                             'pattern': '^[0-9a-fA-F]{32}$',
                                                                             'type': 'string'},
                                                                     'name': { 'description': '此条目名称',
                                                                               'type': 'string'},
                                                                     'updated_at': { 'description': '最后修改时间，格式 '
                                                                                                    'ISO '
                                                                                                    '8601',
                                                                                     'format': 'date-time',
                                                                                     'type': [ 'string',
                                                                                               'null']},
                                                                     'version': { 'description': '此条目的版本号',
                                                                                  'pattern': '^[0-9]+\\.[0-9]+\\.[0-9]+$',
                                                                                  'type': 'string'}},
                                                     'required': [ 'id',
                                                                   'category',
                                                                   'created_at'],
                                                     'type': 'object'},
                                  'reif_version': { 'description': 'REIF '
                                                                   '规范的版本，如 '
                                                                   '1.0',
                                                    'pattern': '^1\\.[0-9]+$',
                                                    'type': 'string'}},
                  'required': ['reif_version', 'reif_metadata', 'reif_content'],
                  'title': 'REIF Entry',
                  'type': 'object'},
  'tool.tool_call': { '$schema': 'http://json-schema.org/draft-07/schema#',
                      'additionalProperties': False,
                      'allOf': [ { 'if': { 'properties': { 'type': { 'const': 'function'}}},
                                   'then': {'required': ['function']}}],
                      'description': '单个工具调用的信息，用于存储 LLM 返回的工具调用请求',
                      'properties': { 'created_at': { 'description': '工具调用创建时间（ISO '
                                                                     '8601）',
                                                      'format': 'date-time',
                                                      'type': 'string'},
                                      'extra': { 'additionalProperties': True,
                                                 'description': '扩展元数据',
                                                 'type': 'object'},
                                      'function': { 'additionalProperties': False,
                                                    'properties': { 'arguments': { 'additionalProperties': True,
                                                                                   'description': '工具所需的参数，以键值对形式给出，具体结构由工具定义',
                                                                                   'type': 'object'},
                                                                    'registry_id': { 'description': '工具名称，应与工具注册表中的名称一致',
                                                                                     'type': 'string'}},
                                                    'required': [ 'registry_id',
                                                                  'arguments'],
                                                    'type': 'object'},
                                      'id': { 'description': '工具调用的唯一标识符，通常由 '
                                                             'LLM 生成，用于关联工具结果',
                                              'pattern': '^[0-9a-fA-F]{32}$',
                                              'type': 'string'},
                                      'type': { 'description': '工具调用类型，目前仅支持 '
                                                               "'function'，预留扩展",
                                                'enum': ['function'],
                                                'type': 'string'}},
                      'required': ['id', 'type', 'created_at'],
                      'title': 'tool_call',
                      'type': 'object'},
  'tool.tool_registry': { '$schema': 'http://json-schema.org/draft-07/schema#',
                          'additionalProperties': False,
                          'description': '工具注册表，键为 tool_id（32位十六进制），值为工具信息',
                          'patternProperties': { '^[0-9a-fA-F]{32}$': { 'additionalProperties': False,
                                                                        'allOf': [ { 'if': { 'properties': { 'type': { 'const': 'function'}}},
                                                                                     'then': { 'required': [ 'function']}}],
                                                                        'properties': { 'description': { 'description': '工具描述',
                                                                                                         'type': 'string'},
                                                                                        'function': { 'additionalProperties': False,
                                                                                                      'description': '函数调用',
                                                                                                      'properties': { 'description': { 'description': '工具介绍',
                                                                                                                                       'type': 'string'},
                                                                                                                      'name': { 'description': '工具名称',
                                                                                                                                'type': 'string'},
                                                                                                                      'parameters': { 'description': '工具参数',
                                                                                                                                      'type': 'object'}},
                                                                                                      'type': 'object'},
                                                                                        'name': { 'description': '工具名称',
                                                                                                  'type': 'string'},
                                                                                        'type': { 'description': '工具调用方式',
                                                                                                  'enum': [ 'function'],
                                                                                                  'type': 'string'}},
                                                                        'required': [ 'name',
                                                                                      'type'],
                                                                        'type': 'object'}},
                          'title': 'tool_registry',
                          'type': 'object'},
  'tool.tool_result': { '$schema': 'http://json-schema.org/draft-07/schema#',
                        'allOf': [ { 'if': { 'properties': { 'type': { 'const': 'function'}}},
                                     'then': {'required': ['function']}}],
                        'properties': { 'call_id': { 'description': '工具调用的id',
                                                     'pattern': '^[0-9a-fA-F]{32}$',
                                                     'type': 'string'},
                                        'created_at': { 'description': '创建时间',
                                                        'format': 'date-time',
                                                        'type': 'string'},
                                        'extra': { 'description': '扩展',
                                                   'type': 'object'},
                                        'function': { 'allOf': [ { 'if': { 'properties': { 'status': { 'const': 'error'}}},
                                                                   'then': { 'required': [ 'error_message']}}],
                                                      'description': '函数调用方式',
                                                      'properties': { 'error_message': { 'description': '错误信息，仅 '
                                                                                                        'status：error '
                                                                                                        '时存在',
                                                                                         'type': 'string'},
                                                                      'result_content': { 'description': '工具结果的内容',
                                                                                          'type': 'string'},
                                                                      'status': { 'description': '工具执行情况',
                                                                                  'enum': [ 'success',
                                                                                            'error',
                                                                                            'timeout',
                                                                                            'cancelled',
                                                                                            'pending',
                                                                                            'running'],
                                                                                  'type': 'string'}},
                                                      'required': [ 'result_content',
                                                                    'status'],
                                                      'type': 'object'},
                                        'type': { 'description': '工具调用方式',
                                                  'enum': ['function'],
                                                  'type': 'string'}},
                        'required': ['call_id', 'created_at'],
                        'title': 'tool_result',
                        'type': 'object'}}

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
