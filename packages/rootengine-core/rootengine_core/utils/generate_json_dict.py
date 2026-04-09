#!/usr/bin/env python3
"""
生成JSON字典模块，便于运行时加载JSON文件

用法:
    python generate_schema_dict.py <input_dir> [options]

示例:
    python generate_schema_dict.py ./jsons
    python generate_schema_dict.py ./jsons --output-py my_jsons.py --output-json jsons.json

 Python代码调用

 from generate_schema_dict import generate_json_dict

 # 基本用法
 generate_json_dict("path/to/json/files")

 # 完整参数
 generate_json_dict(
     input_dir="path/to/json/files",
     output_py="custom_loader.py",
     output_json="data.json",
     ignore_errors=True
 )


"""
import os
import json
import sys
import argparse
import pprint
from pathlib import Path
from typing import Dict, Any, Optional


def load_json_from_file(file_path: Path) -> Dict[str, Any]:
    """从JSON文件加载数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析错误: 文件 {file_path}: {e}")
    except OSError as e:
        raise OSError(f"文件读取错误: {file_path}: {e}")
    except Exception as e:
        raise RuntimeError(f"未知错误加载文件 {file_path}: {e}")


def scan_jsons_to_dict(root_dir: Path, ignore_errors: bool = False) -> Dict[str, Any]:
    """
    扫描JSON目录，生成扁平化的字典结构

    结构示例:
    {
        'reif_entry': {...JSON内容...},
        'conversation.base_conversation': {...JSON内容...},
        'tool.tool_call': {...JSON内容...},
        ...
    }

    Args:
        root_dir: 要扫描的根目录
        ignore_errors: 如果为True，忽略无法加载的文件；如果为False，抛出异常

    Returns:
        键为点分隔路径、值为JSON内容的字典
    """
    json_dict = {}

    # 递归扫描所有JSON文件
    for json_file in root_dir.rglob('*.json'):
        if json_file.is_file():
            # 计算相对于root_dir的路径
            rel_path = json_file.relative_to(root_dir)

            # 将路径转换为点分隔的键名
            # 例如: conversation/base_conversation.json -> conversation.base_conversation
            key_parts = []
            for part in rel_path.parts:
                if part.endswith('.json'):
                    key_parts.append(part[:-5])  # 移除.json扩展名
                else:
                    key_parts.append(part)

            key = '.'.join(key_parts)

            # 加载JSON
            try:
                json_content = load_json_from_file(json_file)
                json_dict[key] = json_content
            except Exception as e:
                if ignore_errors:
                    # 可以选择打印警告，但为了保持干净，这里不打印
                    # 如果需要警告，可以传递一个logger
                    pass
                else:
                    raise e

    return json_dict




def create_json_loader(json_dict: Dict[str, Any], output_file: Path) -> None:
    """创建JSON加载器模块（无外部依赖）"""
    module_content = '''"""
JSON文件加载器
无需外部依赖
"""

import json

# JSON字典
JSON_DICT = '''

    module_content += pprint.pformat(json_dict, indent=2)
    module_content += '''

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
'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(module_content)


def generate_json_dict(
    input_dir: str,
    output_py: str = "json_loader.py",
    output_json: str = None,
    ignore_errors: bool = False
) -> None:
    """
    生成JSON字典的主函数

    Args:
        input_dir: 包含JSON文件的目录
        output_py: 输出的Python模块文件路径（默认: json_loader.py）
        output_json: 输出的JSON文件路径（可选，如果不提供则不生成）
        ignore_errors: 是否忽略加载错误（默认False，抛出异常）

    Raises:
        FileNotFoundError: 当输入目录不存在时
        ValueError: 当没有找到任何JSON文件时
    """
    # 扫描JSON目录
    json_source_dir = Path(input_dir)

    if not json_source_dir.exists():
        raise FileNotFoundError(f"\n错误: 目录 '{json_source_dir}'\n绝对路径{Path(json_source_dir).resolve()} 不存在\n当前工作目录: {os.getcwd()}")

    # 扫描生成字典
    json_dict = scan_jsons_to_dict(json_source_dir, ignore_errors)

    if not json_dict:
        raise ValueError(f"错误: '{json_source_dir}' 下未找到JSON文件")

    # 生成Python模块
    output_module = Path(output_py)
    create_json_loader(json_dict, output_module)

    print(f"已生成Python模块: {output_module} (包含 {len(json_dict)} 个JSON文件)")

    # 可选：生成JSON文件便于查看
    if output_json:
        output_json_path = Path(output_json)
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_dict, f, indent=2, ensure_ascii=False)
        print(f"已生成JSON文件: {output_json_path}")


# 向后兼容的别名
generate_schema_dict = generate_json_dict


# 向后兼容的旧版main函数
def main(dir: str, out_put_json: bool = False) -> None:
    """
    旧版main函数（已弃用），请使用generate_json_dict代替

    Args:
        dir: 包含JSON文件的目录
        out_put_json: 是否输出JSON文件（固定输出为schemas.json）
    """
    import warnings
    warnings.warn(
        "main(dir, out_put_json) 已弃用，请使用 generate_json_dict() 函数",
        DeprecationWarning,
        stacklevel=2
    )

    output_json = "schemas.json" if out_put_json else None
    generate_schema_dict(
        input_dir=dir,
        output_py="schema_loader.py",
        output_json=output_json,
        ignore_errors=False
    )


def cli_main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description="扫描目录下的JSON文件并生成JSON字典模块",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./jsons
  %(prog)s ./jsons --output-py my_jsons.py --output-json jsons.json
  %(prog)s ./jsons --ignore-errors
        """
    )

    parser.add_argument(
        "input_dir",
        help="包含JSON文件的目录"
    )

    parser.add_argument(
        "--output-py",
        default="json_loader.py",
        help="输出的Python模块文件路径 (默认: json_loader.py)"
    )

    parser.add_argument(
        "--output-json",
        default=None,
        help="输出的JSON文件路径 (可选)"
    )

    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="忽略无法加载的JSON文件（默认：遇到错误时抛出异常）"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0"
    )

    args = parser.parse_args()

    try:
        generate_json_dict(
            input_dir=args.input_dir,
            output_py=args.output_py,
            output_json=args.output_json,
            ignore_errors=args.ignore_errors
        )
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()