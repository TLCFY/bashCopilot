#!/usr/bin/env python3
"""
历史记录日志功能
"""

from datetime import datetime
from typing import List, Optional
from config.constants import HISTORY_FILE

def append_to_history(query: str, answer: str, type_name: str = "command", 
                     script_path: Optional[str] = None, 
                     filenames: Optional[List[str]] = None) -> None:
    """
    将查询和结果追加到历史记录文件

    Args:
        query (str): 用户的查询
        answer (str): 生成的答案
        type_name (str): 记录类型 (command/script)
        script_path (str, optional): 脚本保存路径，仅在type_name为"script"时有效
        filenames (List[str], optional): 包含在提示中的文件名列表
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备要写入的内容
    entry = f"""
=== {timestamp} [{type_name}] ===
查询: {query}
"""
    # 如果指定了文件，添加文件信息
    if filenames:
        entry += f"相关文件: {', '.join(filenames)}\n"
    
    entry += f"结果: {answer}\n"

    # 如果是脚本类型且提供了脚本路径，则添加脚本路径信息
    if type_name == "script" and script_path:
        entry += f"脚本位置: {script_path}\n"
    
    entry += f"{'=' * 60}\n"

    # 追加到历史文件
    with open(HISTORY_FILE, 'a') as f:
        f.write(entry)
