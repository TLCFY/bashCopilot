#!/usr/bin/env python3
"""
脚本生成模块
"""

import os
from datetime import datetime
from typing import Dict, Tuple, List, Optional
from src.generators.base_generator import generate_bash_command
from src.log.history import append_to_history

def create_script_file(content: str, query: str) -> str:
    """
    创建可执行脚本文件，保存在用户当前工作目录

    Args:
        content (str): 脚本内容
        query (str): 用户的原始查询，用于生成默认文件名
    
    Returns:
        str: 脚本文件路径
    """
    # 尝试从内容中提取脚本名称
    script_name = None
    if "[SCRIPT_NAME:" in content:
        try:
            start = content.find("[SCRIPT_NAME:") + 13
            end = content.find("]", start)
            if end > start:
                script_name = content[start:end].strip()
                # 清理名称，确保只包含有效字符
                script_name = "".join(c for c in script_name if c.isalnum() or c == '_').lower()
                # 移除从内容中提取的脚本名称部分
                content = content[end+1:].strip()
        except:
            script_name = None

    # 如果没有成功提取脚本名称，使用默认名称
    if not script_name or len(script_name) < 2:
        # 默认名称: script_日期时间
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = f"script_{timestamp}"

    # 提取代码块，如果输出包含Markdown代码块
    if "```bash" in content or "```sh" in content:
        try:
            start = content.find("```") + 3
            start = content.find("\n", start) + 1
            end = content.find("```", start)
            if end > start:
                content = content[start:end].strip()
        except:
            # 如果提取失败，则使用原始内容
            pass

    # 确保文件名不重复
    script_path = os.path.join(os.getcwd(), f"{script_name}.sh")
    counter = 1
    while os.path.exists(script_path):
        script_path = os.path.join(os.getcwd(), f"{script_name}_{counter}.sh")
        counter += 1

    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# 由Bash-Copilot生成的脚本\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 查询内容: {query}\n\n")
        f.write(content)

    # 使脚本可执行
    os.chmod(script_path, 0o755)

    return script_path

def handle_script_generation(query: str, context: Dict[str, str], 
                            file_contents: Optional[List[Tuple[str, str]]] = None,
                            filenames: Optional[List[str]] = None) -> None:
    """
    处理脚本生成的主要逻辑

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
        is_script=True,
        file_contents=file_contents
    )

    if success:
        script_path = create_script_file(result, query)
        append_to_history(
            query, 
            result, 
            "script", 
            script_path, 
            filenames
        )
        print(f"\n脚本已创建: {script_path}")
        print("您可以使用以下命令运行脚本:")
        print(f"\033[92m{script_path}\033[0m")
    else:
        print(f"错误: {result}")
