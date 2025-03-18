#!/usr/bin/env python3
"""
命令生成模块 - 处理单行命令生成
"""

from typing import Dict, Tuple, List, Optional
from src.generators.base_generator import generate_bash_command
from src.log.history import append_to_history

def handle_command_generation(query: str, context: Dict[str, str],
                              file_contents: Optional[List[Tuple[str, str]]] = None,
                              filenames: Optional[List[str]] = None) -> None:
    """
    处理单行命令生成的主要逻辑

    Args:
        query (str): 用户查询
        context (Dict[str, str]): 系统上下文
        file_contents (List[Tuple[str, str]], optional): 文件内容列表
        filenames (List[str], optional): 文件名列表
    """
    print("正在处理请求...")
    success, result = generate_bash_command(
        query, 
        context, 
        is_script=False,
        file_contents=file_contents
    )

    if success:
        append_to_history(
            query, 
            result, 
            "command", 
            None, 
            filenames
        )
        print(f"\033[92m{result}\033[0m")  # 绿色输出命令
    else:
        print(f"错误: {result}")
